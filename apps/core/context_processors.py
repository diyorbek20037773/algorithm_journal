"""Template context processors providing journal-wide data."""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.db import OperationalError, ProgrammingError
from django.http import HttpRequest
from django.urls import translate_url
from django.utils import translation

from apps.core.models import Page
from apps.core.services import get_site_settings


def site_settings(request: HttpRequest) -> dict[str, Any]:
    """Expose the journal settings singleton and site-level constants."""
    site = getattr(request, "site_settings", None) or get_site_settings()
    return {
        "site_settings": site,
        "site_url": settings.SITE_URL,
        "site_domain": settings.SITE_DOMAIN,
        "matomo_url": settings.MATOMO_URL,
        "matomo_site_id": site.matomo_site_id or settings.MATOMO_SITE_ID,
        "current_year": __import__("datetime").date.today().year,
    }


def navigation(request: HttpRequest) -> dict[str, Any]:
    """Expose the CMS-driven menus used by the header and footer."""
    try:
        pages = list(Page.objects.published().only("slug", "title", "menu_group", "menu_order"))
    except (OperationalError, ProgrammingError):  # pragma: no cover - pre-migrate
        pages = []
    grouped: dict[str, list[Page]] = {"about": [], "authors": [], "reviewers": [], "footer": []}
    for page in sorted(pages, key=lambda p: (p.menu_order, p.title)):
        if page.menu_group in grouped:
            grouped[page.menu_group].append(page)
    return {
        "menu_about": grouped["about"],
        "menu_authors": grouped["authors"],
        "menu_reviewers": grouped["reviewers"],
        "menu_footer": grouped["footer"],
        "active_nav": active_nav(request),
    }


# Which primary tab a URL name belongs to; CMS pages fall back to their menu group.
_NAV_BY_URL_NAME: dict[str, str] = {
    "issue_current": "current",
    "archive": "archive",
    "issue_detail": "archive",
    "online_first": "online_first",
    "for_authors": "authors",
    "author_guidelines": "authors",
    "checklist": "authors",
    "templates": "authors",
    "fees": "authors",
    "ai_policy": "authors",
    "for_reviewers": "reviewers",
    "about": "about",
    "aims_and_scope": "about",
    "peer_review": "about",
    "publication_ethics": "about",
    "open_access": "about",
    "archiving": "about",
    "indexing": "about",
    "privacy": "about",
    "contact": "about",
    "editorial_board": "about",
    "reviewer_board": "about",
    "statistics": "about",
}


def active_nav(request: HttpRequest) -> str:
    """Name the primary navigation tab that the current URL belongs to."""
    match = getattr(request, "resolver_match", None)
    if match is None:
        return ""
    if match.namespace == "core" and match.url_name == "page":
        slug = match.kwargs.get("slug", "")
        try:
            page = Page.objects.only("menu_group").get(slug=slug)
        except (Page.DoesNotExist, OperationalError, ProgrammingError):
            return ""
        return {"about": "about", "authors": "authors", "reviewers": "reviewers"}.get(
            page.menu_group, ""
        )
    return _NAV_BY_URL_NAME.get(match.url_name or "", "")


def language_links(request: HttpRequest) -> dict[str, Any]:
    """Build the language switcher and ``hreflang`` alternates for this path."""
    current = translation.get_language() or settings.LANGUAGE_CODE
    path = request.path
    links = []
    for code, name in settings.LANGUAGES:
        try:
            url = translate_url(path, code)
        except Exception:  # pragma: no cover - non-translatable URLs
            url = path
        links.append(
            {
                "code": code,
                "name": name,
                "url": url,
                "absolute_url": f"{settings.SITE_URL}{url}",
                "is_current": code == current,
                "short": {"en": "EN", "uz": "UZ", "uz-cyrl": "ЎЗ", "ru": "RU"}.get(code, code),
            }
        )
    return {"language_links": links, "current_language": current}
