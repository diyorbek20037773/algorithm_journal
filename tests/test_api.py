"""Read-only public API tests (SPEC §9)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.django_db


def test_api_root_lists_endpoints(client_anon, site_settings) -> None:
    """The discovery document names every endpoint."""
    payload = client_anon.get("/api/v1/").json()
    for key in ("articles", "issues", "sections", "search", "doaj_export", "oai_pmh"):
        assert key in payload


def test_article_list(client_anon, article, site_settings) -> None:
    """The article list returns the published article with its metadata."""
    payload = client_anon.get("/api/v1/articles/").json()
    assert payload["count"] == 1
    row = payload["results"][0]
    assert row["doi"] == article.doi
    assert row["title"] == article.title_en
    assert row["volume"] == 1
    assert len(row["authors"]) == 2
    assert row["pdf_url"].endswith(f"/article/{article.pk}/pdf/")


def test_article_detail_includes_references_and_statements(
    client_anon, article, site_settings
) -> None:
    """The detail endpoint exposes the full record."""
    row = client_anon.get(f"/api/v1/articles/{article.pk}/").json()
    assert len(row["references"]) == article.references.count()
    assert row["license"]["code"] == "CC-BY-4.0"
    assert "en" in row["titles"] and "uz" in row["titles"] and "ru" in row["titles"]
    assert row["ai_use_statement"]


def test_non_corresponding_author_email_is_hidden(client_anon, article, site_settings) -> None:
    """Only the corresponding author's e-mail is exposed."""
    row = client_anon.get(f"/api/v1/articles/{article.pk}/").json()
    corresponding = [a for a in row["authors"] if a["is_corresponding"]]
    others = [a for a in row["authors"] if not a["is_corresponding"]]
    assert corresponding[0]["email"]
    assert all(a["email"] == "" for a in others)


def test_issue_and_section_endpoints(client_anon, article, site_settings) -> None:
    """Issues and sections are listed."""
    assert client_anon.get("/api/v1/issues/").json()["count"] == 1
    assert client_anon.get("/api/v1/sections/").json()["count"] == 1


def test_search_endpoint(client_anon, article, site_settings) -> None:
    """The search endpoint returns matching articles."""
    payload = client_anon.get("/api/v1/search/", {"q": "competition"}).json()
    assert payload["count"] >= 1


def test_doaj_export_shape(client_anon, article, site_settings) -> None:
    """The DOAJ export follows the bibjson article schema."""
    payload = client_anon.get("/api/v1/doaj-export/").json()
    assert payload
    bibjson = payload[0]["bibjson"]
    assert bibjson["title"] == article.title_en
    assert bibjson["journal"]["title"] == site_settings.journal_name_en
    assert any(link["type"] == "fulltext" for link in bibjson["link"])
    assert any(i["type"] == "doi" for i in bibjson["identifier"])


def test_cors_headers_for_get(client_anon, article, site_settings) -> None:
    """The API is CORS-open for GET requests."""
    response = client_anon.get("/api/v1/articles/", HTTP_ORIGIN="https://example.org")
    assert response.headers.get("Access-Control-Allow-Origin") == "*"


def test_api_filters(client_anon, article, site_settings) -> None:
    """Filtering by section slug works."""
    payload = client_anon.get("/api/v1/articles/", {"section__slug": article.section.slug}).json()
    assert payload["count"] == 1
