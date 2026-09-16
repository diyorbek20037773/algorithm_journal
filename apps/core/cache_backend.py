"""A Redis cache backend that degrades to "no cache" when Redis is unreachable.

Every public page consults the cache (site settings, whole-page cache, KPI
numbers).  With Django's stock backend a Redis outage — or a staging service
whose ``REDIS_URL`` is not wired yet — turns into a 500 on the home page.  This
backend logs the failure and answers as an empty cache would, so the site stays
up (slower, but up) and the operator sees one clear warning per process.
"""

from __future__ import annotations

import functools
import logging
from typing import Any

from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache.backends.redis import RedisCache

logger = logging.getLogger(__name__)

_warned = False


def _resilient(default: Any = None):
    """Wrap a cache method so Redis connection errors return ``default``."""

    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except Exception as exc:  # redis.exceptions.* and OS-level socket errors
                if not _is_connection_error(exc):
                    raise
                _warn_once(exc)
                return default() if callable(default) else default

        return wrapper

    return decorator


def _warn_once(exc: BaseException) -> None:
    """Log the outage once per process, not once per request."""
    global _warned
    if not _warned:
        _warned = True
        logger.error("Redis cache unavailable (%s); serving without cache until it returns", exc)


def _is_connection_error(exc: BaseException) -> bool:
    """True for the errors a missing or unreachable Redis raises."""
    try:
        import redis.exceptions as rexc
    except ImportError:  # pragma: no cover - redis is always installed
        return isinstance(exc, OSError)
    return isinstance(exc, (rexc.ConnectionError, rexc.TimeoutError, OSError))


class ResilientRedisCache(RedisCache):
    """``RedisCache`` whose reads and writes never raise on connection failure."""

    def get(self, key, default=None, version=None):
        try:
            return super().get(key, default, version)
        except Exception as exc:
            if not _is_connection_error(exc):
                raise
            _warn_once(exc)
            return default

    @_resilient(False)
    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        return super().set(key, value, timeout, version)

    @_resilient(False)
    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        return super().add(key, value, timeout, version)

    @_resilient(False)
    def delete(self, key, version=None):
        return super().delete(key, version)

    @_resilient(dict)
    def get_many(self, keys, version=None):
        return super().get_many(keys, version)

    @_resilient(list)
    def set_many(self, data, timeout=DEFAULT_TIMEOUT, version=None):
        return super().set_many(data, timeout, version)

    @_resilient(False)
    def delete_many(self, keys, version=None):
        return super().delete_many(keys, version)

    @_resilient(False)
    def has_key(self, key, version=None):
        return super().has_key(key, version)

    @_resilient(0)
    def incr(self, key, delta=1, version=None):
        return super().incr(key, delta, version)

    @_resilient(False)
    def touch(self, key, timeout=DEFAULT_TIMEOUT, version=None):
        return super().touch(key, timeout, version)

    @_resilient(False)
    def clear(self):
        return super().clear()
