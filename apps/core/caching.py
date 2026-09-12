"""Whole-response caching for the public site.

An anonymous reader's home page, issue table of contents or article page is
the same for every anonymous reader, and readers are the bulk of a journal's
traffic — Google Scholar sends them straight to article pages. Rendering the
same page a thousand times a minute is what pushed the load test's p50 into
seconds, so those responses are cached whole in Redis.

Why not Django's ``cache_page``: it keys on the ``Vary: Cookie`` header, and
the CSRF cookie a visitor picks up on the first form they see gives every
visitor a private cache entry — the cache fills and never hits. This decorator
ignores cookies entirely and instead refuses to cache when there is anything
personal about the request: a signed-in user, a live session, or a non-GET
method.

Invalidation is a generation counter folded into every key. Publishing an
article, an issue, a CMS page or an announcement bumps it, and every cached
page is stale at once — no pattern deletes, no listing keys.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from functools import wraps

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.utils.translation import get_language

GENERATION_KEY = "public_page_generation"
#: Default lifetime, seconds. Short enough that even a missed invalidation
#: is a two-minute inconvenience, long enough to absorb a traffic spike.
DEFAULT_TIMEOUT = 120


def generation() -> int:
    """Current generation; every publish increments it."""
    value = cache.get(GENERATION_KEY)
    if value is None:
        cache.set(GENERATION_KEY, 1, None)
        return 1
    return int(value)


def bump_public_cache_generation() -> None:
    """Invalidate every cached public page at once."""
    try:
        cache.incr(GENERATION_KEY)
    except ValueError:
        cache.set(GENERATION_KEY, 2, None)


def _is_cacheable(request: HttpRequest) -> bool:
    if request.method not in {"GET", "HEAD"}:
        return False
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        return False
    session = getattr(request, "session", None)
    if session is not None and session.session_key:
        return False
    # Django's messages framework stores flashes in the cookie or session; a
    # page carrying one is personal.
    if request.COOKIES.get("messages"):
        return False
    # HTMX partial requests render fragments the full page does not.
    return not request.headers.get("HX-Request")


def _key(request: HttpRequest) -> str:
    raw = f"{get_language()}|{request.get_host()}|{request.get_full_path()}"
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()
    return f"public_page:{generation()}:{digest}"


def cache_public_page(
    timeout: int = DEFAULT_TIMEOUT,
) -> Callable[[Callable[..., HttpResponse]], Callable[..., HttpResponse]]:
    """Cache the full response of a public view for anonymous readers.

    Only 200 responses are stored. Responses that set cookies are not, since
    replaying a Set-Cookie to a different visitor would be wrong.
    """

    def decorator(view: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
        @wraps(view)
        def wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            if not _is_cacheable(request):
                return view(request, *args, **kwargs)
            key = _key(request)
            hit = cache.get(key)
            if hit is not None:
                response = HttpResponse(
                    hit["content"], status=200, content_type=hit["content_type"]
                )
                for header, value in hit["headers"]:
                    response[header] = value
                response["X-Cache"] = "HIT"
                return response

            response = view(request, *args, **kwargs)
            # TemplateResponse renders lazily; force it so the body is real.
            if hasattr(response, "render") and callable(response.render):
                response = response.render()
            if (
                response.status_code == 200
                and not response.cookies
                and not getattr(response, "streaming", False)
            ):
                headers = [
                    (h, response[h])
                    for h in ("Content-Language", "Vary", "Cache-Control", "Link")
                    if response.has_header(h)
                ]
                cache.set(
                    key,
                    {
                        "content": response.content,
                        "content_type": response["Content-Type"],
                        "headers": headers,
                    },
                    timeout,
                )
                response["X-Cache"] = "MISS"
            return response

        return wrapped

    return decorator
