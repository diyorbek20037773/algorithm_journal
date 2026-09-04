"""Citation rendering and bibliographic export tests (SPEC §15.10)."""

from __future__ import annotations

import json

import pytest

from apps.citations.services import (
    available_styles,
    csl_json,
    export_article,
    render_citation,
    to_bibtex,
    to_endnote,
    to_ris,
)

pytestmark = pytest.mark.django_db


def test_six_styles_are_offered() -> None:
    """The cite modal offers APA, MLA, Chicago, Harvard, Vancouver and GOST."""
    codes = {style["code"] for style in available_styles()}
    assert codes == {"apa", "mla", "chicago", "harvard", "vancouver", "gost"}


@pytest.mark.parametrize("style", ["apa", "mla", "chicago", "harvard", "vancouver", "gost"])
def test_every_style_renders(article, site_settings, style) -> None:
    """Each style produces a non-empty citation naming the authors and year."""
    citation = render_citation(article, style)
    assert citation
    assert "Karimov" in citation
    assert "2026" in citation


def test_apa_citation_contains_doi(article, site_settings) -> None:
    """The APA string carries the resolvable DOI."""
    assert article.doi in render_citation(article, "apa")


def test_csl_json_structure(article, site_settings) -> None:
    """CSL-JSON has the fields a reference manager expects."""
    item = csl_json(article)
    assert item["type"] == "article-journal"
    assert item["DOI"] == article.doi
    assert item["issued"]["date-parts"][0][0] == 2026
    assert len(item["author"]) == 2
    assert item["author"][0]["family"] == "Karimov"


def test_bibtex_parses(article, site_settings) -> None:
    """The BibTeX export is parseable by bibtexparser."""
    import bibtexparser

    database = bibtexparser.loads(to_bibtex(article))
    assert len(database.entries) == 1
    entry = database.entries[0]
    assert entry["ENTRYTYPE"] == "article"
    assert "Karimov" in entry["author"]
    assert entry["doi"] == article.doi
    assert entry["year"] == "2026"


def test_ris_parses(article, site_settings) -> None:
    """The RIS export is parseable by rispy."""
    import rispy

    entries = rispy.loads(to_ris(article))
    assert len(entries) == 1
    entry = entries[0]
    assert entry["type_of_reference"] == "JOUR"
    assert entry["doi"] == article.doi
    assert any("Karimov" in a for a in entry["authors"])


def test_endnote_export(article, site_settings) -> None:
    """The EndNote export uses the tagged refer format."""
    text = to_endnote(article)
    assert text.startswith("%0 Journal Article")
    assert "%A Karimov, Aziz" in text
    assert f"%R {article.doi}" in text


@pytest.mark.parametrize("fmt", ["bibtex", "ris", "enw", "json"])
def test_export_article_returns_mime_and_filename(article, site_settings, fmt) -> None:
    """Every export format returns content, a MIME type and a file name."""
    content, mime, filename = export_article(article, fmt)
    assert content
    assert mime
    assert filename.startswith(f"ARER-{article.pk}")


def test_unknown_export_format_raises(article, site_settings) -> None:
    """An unsupported format is rejected."""
    with pytest.raises(ValueError):
        export_article(article, "docx")


def test_csl_json_export_parses(article, site_settings) -> None:
    """The downloaded CSL-JSON is valid JSON."""
    content, _mime, _name = export_article(article, "json")
    assert json.loads(content)["DOI"] == article.doi


def test_cite_endpoint_returns_the_modal(client_anon, article, about_pages, site_settings) -> None:
    """The HTMX cite endpoint renders the modal with the citation."""
    response = client_anon.get(f"/en/article/{article.pk}/cite/", {"style": "vancouver"})
    assert response.status_code == 200
    assert b"Karimov" in response.content


def test_cite_endpoint_falls_back_for_unknown_style(
    client_anon, article, about_pages, site_settings
) -> None:
    """An unknown style silently falls back to APA rather than erroring."""
    response = client_anon.get(f"/en/article/{article.pk}/cite/", {"style": "nonsense"})
    assert response.status_code == 200


def test_article_page_shows_the_apa_citation_without_javascript(
    client_anon, article, about_pages, site_settings
) -> None:
    """The How-to-cite box is server-rendered for Google Scholar."""
    html = client_anon.get(f"/en/article/{article.pk}/").content.decode()
    assert "How to cite" in html
    assert "Karimov" in html
