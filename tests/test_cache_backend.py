"""The cache degrades gracefully when Redis is unreachable."""

from __future__ import annotations

import pytest

from apps.core.cache_backend import ResilientRedisCache

pytestmark = pytest.mark.django_db


@pytest.fixture
def dead_cache() -> ResilientRedisCache:
    """A backend pointed at a port nothing listens on."""
    return ResilientRedisCache(
        "redis://127.0.0.1:1", {"KEY_PREFIX": "t", "OPTIONS": {"socket_connect_timeout": 0.2}}
    )


def test_reads_and_writes_do_not_raise(dead_cache) -> None:
    """Every operation answers like an empty cache instead of raising."""
    assert dead_cache.get("k") is None
    assert dead_cache.get("k", "fallback") == "fallback"
    assert dead_cache.set("k", 1) is False
    assert dead_cache.add("k", 1) is False
    assert dead_cache.delete("k") is False
    assert dead_cache.get_many(["a", "b"]) == {}
    assert dead_cache.has_key("k") is False
    assert dead_cache.incr("k") == 0


def test_public_pages_survive_without_redis(client_anon, article, about_pages, settings) -> None:
    """The home page renders (uncached) when the cache is down."""
    settings.CACHES = {
        "default": {
            "BACKEND": "apps.core.cache_backend.ResilientRedisCache",
            "LOCATION": "redis://127.0.0.1:1",
            "OPTIONS": {"socket_connect_timeout": 0.2},
        }
    }
    from django.core.cache import caches

    caches._connections.__dict__.pop("default", None)  # rebuild with the new settings
    response = client_anon.get("/en/")
    assert response.status_code == 200
