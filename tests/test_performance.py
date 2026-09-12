"""Query-count and caching assertions (SPEC §12, §15.12)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.django_db

MAX_QUERIES = 15


def test_home_page_query_count(
    client_anon, article, about_pages, site_settings, django_assert_max_num_queries
) -> None:
    """The home page stays within the query budget."""
    with django_assert_max_num_queries(MAX_QUERIES):
        response = client_anon.get("/en/")
    assert response.status_code == 200


def test_issue_page_query_count(
    client_anon, article, about_pages, site_settings, django_assert_max_num_queries
) -> None:
    """The issue table of contents stays within the query budget."""
    issue = article.issue
    with django_assert_max_num_queries(MAX_QUERIES):
        response = client_anon.get(f"/en/issues/{issue.volume.number}/{issue.number}/")
    assert response.status_code == 200


def test_article_page_query_count(
    client_anon, article, about_pages, site_settings, django_assert_max_num_queries
) -> None:
    """The article landing page stays within the query budget."""
    with django_assert_max_num_queries(MAX_QUERIES):
        response = client_anon.get(f"/en/article/{article.pk}/{article.slug}/")
    assert response.status_code == 200


def test_article_page_does_not_scale_with_authors(
    client_anon, article, about_pages, site_settings, django_assert_max_num_queries
) -> None:
    """Adding authors does not add queries (prefetching works)."""
    from apps.journal.models import Author

    for index in range(8):
        Author.objects.create(
            article=article,
            order=10 + index,
            given_name=f"Extra{index}",
            family_name="Author",
            affiliation="Somewhere",
            country="UZ",
        )
    with django_assert_max_num_queries(MAX_QUERIES):
        client_anon.get(f"/en/article/{article.pk}/{article.slug}/")


def test_search_page_query_count(
    client_anon, article, about_pages, site_settings, django_assert_max_num_queries
) -> None:
    """Search stays within a reasonable budget."""
    with django_assert_max_num_queries(MAX_QUERIES + 5):
        response = client_anon.get("/en/search/", {"q": "competition"})
    assert response.status_code == 200


def test_static_bundle_sizes() -> None:
    """Tailwind, HTMX and Alpine stay within the documented budgets."""
    import gzip
    from pathlib import Path

    from django.conf import settings

    static = Path(settings.BASE_DIR) / "static"
    css = static / "css" / "output.css"
    assert css.exists(), "run `make tailwind` before the performance tests"
    css_gz = len(gzip.compress(css.read_bytes()))
    assert css_gz < 60 * 1024, f"CSS bundle is {css_gz} bytes gzipped"

    js_gz = sum(
        len(gzip.compress((static / "js" / name).read_bytes()))
        for name in ("htmx.min.js", "alpine.min.js")
    )
    assert js_gz < 60 * 1024, f"JS bundle is {js_gz} bytes gzipped"


# --- whole-page cache for anonymous readers ---------------------------------


@pytest.fixture
def _clear_cache():
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()


def test_public_pages_are_served_from_cache_for_anonymous_readers(
    _clear_cache, client_anon, article, about_pages, site_settings
) -> None:
    """The second anonymous request for a public page does not render again."""
    first = client_anon.get(f"/en/article/{article.pk}/")
    assert first.status_code == 200
    assert first["X-Cache"] == "MISS"

    second = client_anon.get(f"/en/article/{article.pk}/")
    assert second.status_code == 200
    assert second["X-Cache"] == "HIT"
    assert second.content == first.content


def test_signed_in_users_bypass_the_page_cache(
    _clear_cache, client_anon, client_author, article, about_pages, site_settings
) -> None:
    """A signed-in user's page carries their name; it must never be shared."""
    client_anon.get(f"/en/article/{article.pk}/")  # warm the anonymous entry
    response = client_author.get(f"/en/article/{article.pk}/")
    assert response.status_code == 200
    assert not response.has_header("X-Cache")


def test_publishing_invalidates_every_cached_page(
    _clear_cache, client_anon, article, about_pages, site_settings
) -> None:
    """After a publish, the very next anonymous request re-renders."""
    from apps.production.services import invalidate_public_caches

    client_anon.get("/en/")
    assert client_anon.get("/en/")["X-Cache"] == "HIT"

    invalidate_public_caches()

    assert client_anon.get("/en/")["X-Cache"] == "MISS"


def test_language_variants_are_cached_separately(
    _clear_cache, client_anon, article, about_pages, site_settings
) -> None:
    """A Russian reader must not be handed the cached English page."""
    en = client_anon.get(f"/en/article/{article.pk}/").content.decode()
    ru = client_anon.get(f"/ru/article/{article.pk}/").content.decode()
    assert 'lang="en"' in en
    assert 'lang="ru"' in ru
    assert client_anon.get(f"/ru/article/{article.pk}/")["X-Cache"] == "HIT"


def test_article_views_are_still_counted_when_the_page_is_cached(
    _clear_cache, client_anon, article, site_settings
) -> None:
    """The count moved to a beacon so caching the page does not lose it."""
    from apps.metrics.models import AccessEvent

    before = AccessEvent.objects.filter(article=article, kind="view").count()
    client_anon.get(f"/en/article/{article.pk}/")
    client_anon.get(f"/en/article/{article.pk}/")  # cache hit: no view recorded here
    assert AccessEvent.objects.filter(article=article, kind="view").count() == before

    beacon = client_anon.get(f"/en/article/{article.pk}/view/")
    assert beacon.status_code == 204
    assert beacon["Cache-Control"].startswith("no-store")
    assert AccessEvent.objects.filter(article=article, kind="view").count() == before + 1
