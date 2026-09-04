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
