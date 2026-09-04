"""Tests for the journal models and their computed properties."""

from __future__ import annotations

import pytest

from apps.journal.models import Article, Issue, Reference

pytestmark = pytest.mark.django_db


def test_article_slug_is_derived_from_english_title(article) -> None:
    """The slug comes from the English title."""
    assert article.slug.startswith("bank-competition")


def test_article_urls(article, site_settings) -> None:
    """Canonical, PDF and DOI URLs are built from the model."""
    assert article.get_absolute_url().endswith(f"/article/{article.pk}/{article.slug}/")
    assert article.pdf_url == f"/article/{article.pk}/pdf/"
    assert article.doi_url == "https://doi.org/10.00000/arer.2026.0001"
    assert article.absolute_pdf_url.startswith("http")


def test_article_pages_property(article) -> None:
    """The page range is rendered with an en dash."""
    assert article.pages == "1–24"


def test_article_primary_galley(article) -> None:
    """The primary PDF galley is returned."""
    assert article.primary_galley is not None
    assert article.primary_galley.mime == "application/pdf"


def test_public_queryset_excludes_drafts(article, section) -> None:
    """Draft articles are invisible to readers."""
    draft = Article.objects.create(section=section, status=Article.Status.DRAFT, title="Draft")
    public = list(Article.objects.public())
    assert article in public
    assert draft not in public


def test_issue_current_is_unique(volume, issue) -> None:
    """Marking a second issue current clears the first."""
    second = Issue.objects.create(volume=volume, number=2, is_published=True, is_current=True)
    issue.refresh_from_db()
    assert second.is_current
    assert not issue.is_current


def test_issue_label(issue) -> None:
    """The issue label matches the citation convention."""
    assert issue.label == "Vol. 1 No. 1 (2026)"


def test_reference_detects_doi(article) -> None:
    """A DOI inside the raw reference text is detected on save."""
    reference = Reference.objects.create(
        article=article,
        order=99,
        raw_text="Smith, J. (2021). A paper. Journal, 1(1), 1-9. https://doi.org/10.1016/j.test.2021.01.001",
    )
    assert reference.doi == "10.1016/j.test.2021.01.001"
    assert reference.doi_url.startswith("https://doi.org/")


def test_author_citation_name_and_slug(article) -> None:
    """Author names render for Highwire tags and author pages."""
    author = article.author_list()[0]
    assert author.citation_name == "Karimov, Aziz"
    assert author.slug == "aziz-karimov"
    assert author.orcid_url == "https://orcid.org/0000-0002-1000-0031"
    assert "Tashkent" in author.affiliation_display


def test_galley_size_display(article) -> None:
    """File sizes render in human-readable units."""
    assert article.primary_galley.size_display.endswith("B")


def test_online_first_has_no_issue(online_first_article) -> None:
    """Online First articles have a DOI but no issue."""
    assert online_first_article.issue is None
    assert online_first_article.is_online_first
    assert online_first_article.doi
