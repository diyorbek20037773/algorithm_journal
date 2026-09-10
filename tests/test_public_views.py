"""Tests for the public site: pages, metadata and multilingual rendering."""

from __future__ import annotations

import json
import re

import pytest

pytestmark = pytest.mark.django_db

LANGUAGES = ["en", "uz", "uz-cyrl", "ru"]


@pytest.mark.parametrize("language", LANGUAGES)
def test_home_renders_in_every_language(client_anon, article, about_pages, language) -> None:
    """The home page returns 200 in all four languages."""
    response = client_anon.get(f"/{language}/")
    assert response.status_code == 200
    assert response.content


@pytest.mark.parametrize("language", LANGUAGES)
def test_article_page_in_every_language(client_anon, article, about_pages, language) -> None:
    """The article landing page renders in all four languages."""
    response = client_anon.get(f"/{language}/article/{article.pk}/")
    assert response.status_code == 200


def test_article_page_has_all_abstract_languages(client_anon, article, about_pages) -> None:
    """Abstracts in EN, UZ, UZ-Cyrl and RU appear on the page (SPEC §15.9)."""
    html = client_anon.get(f"/en/article/{article.pk}/").content.decode()
    assert article.abstract_en[:40] in html
    assert article.abstract_uz[:40] in html
    assert article.abstract_ru[:40] in html
    assert article.abstract_uz_cyrl[:20] in html


def test_wrong_slug_redirects_to_canonical(client_anon, article, about_pages) -> None:
    """An incorrect slug issues a permanent redirect to the canonical URL."""
    response = client_anon.get(f"/en/article/{article.pk}/wrong-slug/")
    assert response.status_code == 301
    assert response.headers["Location"].endswith(f"/article/{article.pk}/{article.slug}/")


def test_draft_article_is_not_public(client_anon, section, about_pages) -> None:
    """Draft articles return 404."""
    from apps.journal.models import Article

    draft = Article.objects.create(section=section, status=Article.Status.DRAFT, title="Hidden")
    assert client_anon.get(f"/en/article/{draft.pk}/").status_code == 404


def test_issue_toc_groups_by_section(client_anon, article, about_pages) -> None:
    """The issue table of contents lists the article under its section."""
    from django.utils.html import escape

    issue = article.issue
    html = client_anon.get(f"/en/issues/{issue.volume.number}/{issue.number}/").content.decode()
    assert article.title_en in html
    assert escape(article.section.name_en) in html


def test_archive_lists_published_issues(client_anon, article, about_pages) -> None:
    """The archive shows the published volume and issue."""
    html = client_anon.get("/en/issues/").content.decode()
    assert "Vol" in html or "Volume" in html


def test_online_first_page(client_anon, online_first_article, about_pages) -> None:
    """The Online First page lists ahead-of-issue articles."""
    html = client_anon.get("/en/issues/online-first/").content.decode()
    assert online_first_article.title_en in html


def test_editorial_board_page(client_anon, about_pages, db) -> None:
    """The board page renders member details (SPEC §15.4)."""
    from apps.journal.models import EditorialBoardMember

    member = EditorialBoardMember.objects.create(
        full_name_en="DEMO — replace: Prof. Test Member",
        full_name="DEMO — replace: Prof. Test Member",
        role=EditorialBoardMember.Role.EDITOR_IN_CHIEF,
        degree_en="Doctor of Economics (DSc)",
        degree="Doctor of Economics (DSc)",
        affiliation_en="Institute of Economic Research",
        affiliation="Institute of Economic Research",
        country="UZ",
        orcid="0000-0002-0000-0001",
        email="eic@example.org",
        is_active=True,
        is_demo=True,
    )
    html = client_anon.get("/en/about/editorial-board/").content.decode()
    assert member.full_name_en in html
    assert "Doctor of Economics" in html
    assert "Uzbekistan" in html
    assert "0000-0002-0000-0001" in html
    assert "eic [at] example.org" in html


def test_reviewer_board_route_exists(client_anon, about_pages) -> None:
    """The reviewer board has its own route, before the CMS catch-all."""
    assert client_anon.get("/en/about/reviewer-board/").status_code == 200


def test_highwire_tags_match_the_model(client_anon, article, site_settings, about_pages) -> None:
    """Every Highwire tag reproduces the stored value (SPEC §15.7)."""
    html = client_anon.get(f"/en/article/{article.pk}/").content.decode()

    def meta(name: str) -> list[str]:
        return re.findall(rf'<meta name="{re.escape(name)}" content="([^"]*)"', html)

    assert meta("citation_title") == [article.title_en]
    assert meta("citation_doi") == [article.doi]
    assert meta("citation_journal_title") == [site_settings.journal_name_en]
    assert meta("citation_journal_abbrev") == ["ARER"]
    assert meta("citation_issn") == [site_settings.eissn]
    assert meta("citation_volume") == [str(article.issue.volume.number)]
    assert meta("citation_issue") == [str(article.issue.number)]
    assert meta("citation_firstpage") == [article.pages_start]
    assert meta("citation_lastpage") == [article.pages_end]
    assert meta("citation_publication_date") == [article.published_at.strftime("%Y/%m/%d")]
    assert meta("citation_language") == [article.language]
    assert meta("citation_pdf_url") == [article.absolute_pdf_url]
    authors = meta("citation_author")
    assert authors == [a.citation_name for a in article.author_list()]
    assert meta("citation_author_orcid")[0].endswith("0000-0002-1000-0031")
    assert meta("DC.title") == [article.title_en]


def test_json_ld_is_valid_and_complete(client_anon, article, about_pages) -> None:
    """The JSON-LD block parses and describes a ScholarlyArticle."""
    html = client_anon.get(f"/en/article/{article.pk}/").content.decode()
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    assert blocks
    data = json.loads(blocks[0])
    assert data["@type"] == "ScholarlyArticle"
    assert data["headline"] == article.title_en
    assert data["isAccessibleForFree"] is True
    assert data["sameAs"] == article.doi_url
    assert data["isPartOf"]["@type"] == "PublicationIssue"
    assert data["isPartOf"]["isPartOf"]["@type"] == "PublicationVolume"
    assert len(data["author"]) == 2


def test_hreflang_alternates_present(client_anon, article, about_pages) -> None:
    """Every page carries hreflang alternates for all four languages."""
    html = client_anon.get(f"/en/article/{article.pk}/").content.decode()
    for language in LANGUAGES:
        assert f'hreflang="{language}"' in html
    assert 'hreflang="x-default"' in html


def test_canonical_link(client_anon, article, about_pages) -> None:
    """A canonical link points at the article's own URL."""
    html = client_anon.get(f"/en/article/{article.pk}/").content.decode()
    assert 'rel="canonical"' in html


def test_pdf_download_is_language_neutral(client_anon, article) -> None:
    """The PDF route works without a language prefix and returns a PDF."""
    response = client_anon.get(f"/article/{article.pk}/pdf/")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"


def test_pdf_download_is_counted(client_anon, article) -> None:
    """Downloading increments the article's download counter."""
    from apps.journal.models import Article

    before = Article.objects.get(pk=article.pk).downloads_count
    client_anon.get(f"/article/{article.pk}/pdf/", HTTP_USER_AGENT="Mozilla/5.0 (Test Reader)")
    after = Article.objects.get(pk=article.pk).downloads_count
    assert after == before + 1


def test_article_view_is_counted(client_anon, article, about_pages) -> None:
    """Opening the landing page increments the view counter."""
    from apps.journal.models import Article

    before = Article.objects.get(pk=article.pk).views_count
    client_anon.get(f"/en/article/{article.pk}/", HTTP_USER_AGENT="Mozilla/5.0 (Test Reader)")
    after = Article.objects.get(pk=article.pk).views_count
    assert after == before + 1


def test_bot_traffic_is_not_counted(client_anon, article, about_pages) -> None:
    """Requests from a crawler user agent do not change the counters."""
    from apps.journal.models import Article

    before = Article.objects.get(pk=article.pk).views_count
    client_anon.get(f"/en/article/{article.pk}/", HTTP_USER_AGENT="Googlebot/2.1")
    assert Article.objects.get(pk=article.pk).views_count == before


def test_feeds(client_anon, article, site_settings, about_pages) -> None:
    """RSS and Atom feeds contain the published article."""
    for path in ("/feed/rss/", "/feed/atom/"):
        response = client_anon.get(path)
        assert response.status_code == 200
        assert article.title_en in response.content.decode()


def test_language_switcher_keeps_path(client_anon, article, about_pages) -> None:
    """The language switcher links to the same path in every language."""
    html = client_anon.get(f"/en/article/{article.pk}/{article.slug}/").content.decode()
    assert f"/uz/article/{article.pk}/" in html
    assert f"/ru/article/{article.pk}/" in html


def test_search_finds_article(client_anon, article, about_pages) -> None:
    """Full-text search returns the article for a title word."""
    html = client_anon.get("/en/search/", {"q": "competition"}).content.decode()
    assert article.title_en in html


def test_search_filters_by_section(client_anon, article, about_pages) -> None:
    """The section facet narrows the result set."""
    response = client_anon.get("/en/search/", {"section": article.section.slug})
    assert response.status_code == 200
    assert article.title_en in response.content.decode()


def test_search_empty_state(client_anon, article, about_pages) -> None:
    """A query with no matches shows a helpful empty state."""
    html = client_anon.get("/en/search/", {"q": "zzzznotfoundzzz"}).content.decode()
    assert "Nothing matched" in html or "0 results" in html


def test_author_page_lists_articles(client_anon, article, about_pages) -> None:
    """The author page lists every article by that person."""
    author = article.author_list()[0]
    html = client_anon.get(f"/en/authors/{author.slug}/").content.decode()
    assert article.title_en in html


def test_statistics_page(client_anon, article, about_pages) -> None:
    """The public statistics page renders."""
    assert client_anon.get("/en/statistics/").status_code == 200


def test_error_page_404(client_anon, about_pages) -> None:
    """An unknown URL returns 404."""
    assert client_anon.get("/en/no-such-page-here/").status_code == 404


def test_article_page_shows_html_full_text(client_anon, article, site_settings) -> None:
    """The client's TZ §6.1 requires an HTML full text beside the PDF."""
    from django.core.files.base import ContentFile

    from apps.journal.models import Galley

    galley = Galley(
        article=article,
        label=Galley.Label.HTML,
        language="en",
        mime="text/html",
        order=2,
    )
    body = b"<h2>1. Introduction</h2><p>Body text.</p><script>alert(1)</script>"
    galley.file.save("full.html", ContentFile(body), save=False)
    galley.size = len(body)
    galley.save()

    html = client_anon.get(f"/en/article/{article.pk}/").content.decode()

    assert "1. Introduction" in html
    assert "Body text." in html
    # Galley HTML goes through the same allow-list as every editor-authored
    # fragment, so a stray script tag cannot reach a published page.
    assert "alert(1)" not in html
    assert "citation_fulltext_html_url" in html


def test_article_page_without_html_galley_has_no_full_text_section(
    client_anon, article, site_settings
) -> None:
    """Articles that ship only a PDF must not render an empty full-text block."""
    html = client_anon.get(f"/en/article/{article.pk}/").content.decode()
    assert 'id="full-text"' not in html
    assert "citation_fulltext_html_url" not in html


def test_no_multiline_django_comments_in_templates() -> None:
    """``{# … #}`` is single-line only; spanning lines renders it as text.

    Django's short comment tag does not span newlines, so a multi-line one is
    printed verbatim into the page. It has bitten this project three times:
    once as visible text on the dashboard, and twice inside flex rows, where
    the stray text became an anonymous flex item ~100 px wide and pushed the
    header off the side of every phone screen. Use ``{% comment %}`` instead.
    """
    import re
    from pathlib import Path

    from django.conf import settings

    offenders = []
    for path in (Path(settings.BASE_DIR) / "templates").rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\{#", text):
            rest = text[match.start() :]
            close = rest.find("#}")
            if close != -1 and "\n" in rest[:close]:
                line = text[: match.start()].count("\n") + 1
                offenders.append(f"{path.name}:{line}")
    assert not offenders, f"multi-line {{# #}} comments: {offenders}"
