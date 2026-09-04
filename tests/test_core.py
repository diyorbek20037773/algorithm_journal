"""Tests for site settings, Markdown rendering and machine endpoints."""

from __future__ import annotations

import json

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.core.markdown import render_markdown, strip_markdown
from apps.core.models import Announcement, ContactMessage, Page, SiteSettings
from apps.core.services import get_site_settings

pytestmark = pytest.mark.django_db


def test_site_settings_is_a_singleton(site_settings) -> None:
    """Saving always writes to primary key 1 and never creates a second row."""
    other = SiteSettings(journal_name="Another journal")
    other.save()
    assert SiteSettings.objects.count() == 1
    assert SiteSettings.load().pk == SiteSettings.SINGLETON_PK


def test_site_settings_cannot_be_deleted(site_settings) -> None:
    """The settings row is protected against deletion."""
    with pytest.raises(ValidationError):
        site_settings.delete()


def test_get_site_settings_is_cached(site_settings) -> None:
    """The cached accessor returns the singleton."""
    assert get_site_settings().short_code == "ARER"


def test_eissn_display_falls_back(db) -> None:
    """A missing e-ISSN renders as a clear pending marker rather than blank."""
    site = SiteSettings.load()
    site.eissn = ""
    site.save()
    assert site.eissn_display


def test_markdown_is_sanitised() -> None:
    """Scripts and event handlers are stripped, safe markup is kept."""
    html = render_markdown("**bold** <script>alert(1)</script> [x](https://example.org)")
    assert "<strong>bold</strong>" in html
    assert "script" not in html
    assert 'rel="noopener noreferrer"' in html


def test_markdown_tables_render() -> None:
    """Tables from the policy pages survive rendering."""
    html = render_markdown("| a | b |\n|---|---|\n| 1 | 2 |")
    assert "<table>" in html and "<td>1</td>" in html


def test_strip_markdown_truncates() -> None:
    """Plain-text extraction respects the length limit."""
    text = strip_markdown("# Title\n\n" + "word " * 100, limit=40)
    assert len(text) <= 41


def test_healthz(client_anon) -> None:
    """The health endpoint reports database and cache status."""
    response = client_anon.get("/healthz/")
    payload = json.loads(response.content)
    assert response.status_code == 200
    assert payload["status"] == "ok"
    assert payload["database"] == "ok"


def test_robots_txt_allows_crawling(client_anon, site_settings) -> None:
    """robots.txt permits all agents and advertises the sitemap."""
    response = client_anon.get("/robots.txt")
    body = response.content.decode()
    assert response.status_code == 200
    assert "User-agent: *" in body
    assert "Allow: /" in body
    assert "Sitemap:" in body


def test_sitemap_lists_articles(client_anon, article, site_settings) -> None:
    """The article sitemap section contains the published article."""
    response = client_anon.get("/sitemap-articles.xml")
    assert response.status_code == 200
    assert f"/article/{article.pk}/" in response.content.decode()


def test_page_absolute_url(about_pages) -> None:
    """CMS pages resolve to their About URL."""
    page = Page.objects.get(slug="aims-and-scope")
    assert page.get_absolute_url().endswith("/about/aims-and-scope/")


def test_announcement_live_filter(db) -> None:
    """Expired announcements are excluded from the live queryset."""
    import datetime as dt

    from django.utils import timezone

    now = timezone.now()
    live = Announcement.objects.create(
        slug="live", title="Live", body="x", published_at=now - dt.timedelta(days=1)
    )
    Announcement.objects.create(
        slug="expired",
        title="Expired",
        body="x",
        published_at=now - dt.timedelta(days=10),
        expires_at=now - dt.timedelta(days=1),
    )
    assert list(Announcement.objects.live()) == [live]


def test_contact_form_creates_message(client_anon, about_pages, site_settings) -> None:
    """A valid contact form submission is stored."""
    response = client_anon.post(
        reverse("core:contact"),
        {
            "name": "Reader",
            "email": "reader@example.org",
            "subject": "A question about scope",
            "body": "I would like to ask whether my topic is within the journal's scope.",
            "website": "",
        },
    )
    assert response.status_code in (200, 302)
    assert ContactMessage.objects.filter(email="reader@example.org").count() == 1


def test_contact_form_honeypot_blocks_spam(client_anon, about_pages, site_settings) -> None:
    """Filling the hidden field rejects the submission."""
    client_anon.post(
        reverse("core:contact"),
        {
            "name": "Spam",
            "email": "spam@example.org",
            "subject": "Buy now",
            "body": "This message is long enough to pass the length validator.",
            "website": "http://spam.example",
        },
    )
    assert not ContactMessage.objects.filter(email="spam@example.org").exists()


def test_auto_transliteration_fills_uz_cyrl(db) -> None:
    """Saving a model with Uzbek Latin text fills the Cyrillic field."""
    page = Page(slug="translit-demo", menu_group="none")
    page.title_en = "Aims and scope"
    page.title_uz = "Maqsad va yoʻnalishlar"
    page.title = page.title_en
    page.save()
    page.refresh_from_db()
    assert page.title_uz_cyrl == "Мақсад ва йўналишлар"
    assert "title_uz_cyrl" in page.auto_translit


def test_auto_transliteration_does_not_overwrite_human_text(db) -> None:
    """A hand-written Cyrillic value is preserved."""
    page = Page(slug="translit-manual", menu_group="none")
    page.title_uz = "Maqsad"
    page.title_uz_cyrl = "Мақсад (қўлда)"
    page.title = "Aim"
    page.save()
    page.refresh_from_db()
    assert page.title_uz_cyrl == "Мақсад (қўлда)"
