"""Public views owned by the core app: home, CMS pages, contact, machine files."""

from __future__ import annotations

import json
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseNotFound,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from apps.core.models import Announcement, Page
from apps.core.services import get_site_settings


# ---------------------------------------------------------------------------
# Health & machine endpoints
# ---------------------------------------------------------------------------
@never_cache
@require_GET
def healthz(request: HttpRequest) -> JsonResponse:
    """Liveness probe reporting database and cache connectivity."""
    status: dict[str, Any] = {"status": "ok", "database": "ok", "cache": "ok"}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception as exc:  # pragma: no cover - failure path
        status["database"] = f"error: {exc.__class__.__name__}"
        status["status"] = "degraded"
    try:
        cache.set("healthz", "1", 5)
        if cache.get("healthz") != "1":
            raise RuntimeError("cache round-trip failed")
    except Exception as exc:  # pragma: no cover - failure path
        status["cache"] = f"error: {exc.__class__.__name__}"
        status["status"] = "degraded"
    return JsonResponse(status, status=200 if status["status"] == "ok" else 503)


@require_GET
def robots_txt(request: HttpRequest) -> HttpResponse:
    """``robots.txt`` allowing every crawler and advertising the sitemaps."""
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /dashboard/",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "",
        f"Sitemap: {settings.SITE_URL}/sitemap.xml",
        "",
        "# OAI-PMH endpoint for metadata harvesting",
        f"# {settings.SITE_URL}/oai/",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


# ---------------------------------------------------------------------------
# Error pages
# ---------------------------------------------------------------------------
def bad_request(request: HttpRequest, exception: Exception | None = None) -> HttpResponse:
    """Custom 400 page."""
    return _error(request, 400, _("Bad request"), _("The request could not be understood."))


def permission_denied(request: HttpRequest, exception: Exception | None = None) -> HttpResponse:
    """Custom 403 page."""
    return _error(
        request, 403, _("Access denied"), _("You do not have permission to view this page.")
    )


def page_not_found(request: HttpRequest, exception: Exception | None = None) -> HttpResponse:
    """Custom 404 page."""
    return _error(request, 404, _("Page not found"), _("This page does not exist or has moved."))


def server_error(request: HttpRequest) -> HttpResponse:
    """Custom 500 page."""
    return _error(
        request,
        500,
        _("Server error"),
        _("Something went wrong on our side. The editorial office has been notified."),
    )


def _error(request: HttpRequest, code: int, title: str, message: str) -> HttpResponse:
    """Render the shared error template with a status code."""
    response = render(
        request,
        "errors/error.html",
        {"code": code, "error_title": title, "error_message": message},
        status=code,
    )
    return response


# ---------------------------------------------------------------------------
# CMS pages
# ---------------------------------------------------------------------------
def page_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """Render a published CMS page with its About sub-navigation."""
    page = get_object_or_404(Page.objects.published(), slug=slug)
    siblings = Page.objects.in_menu(page.menu_group)
    return TemplateResponse(
        request,
        "core/page_detail.html",
        {"page": page, "siblings": siblings, "meta_description": page.seo_description},
    )


def announcement_list(request: HttpRequest) -> HttpResponse:
    """List live announcements, newest and pinned first."""
    announcements = Announcement.objects.live()
    return TemplateResponse(
        request, "core/announcement_list.html", {"announcements": announcements}
    )


def announcement_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """Render a single announcement."""
    announcement = get_object_or_404(Announcement.objects.live(), slug=slug)
    return TemplateResponse(
        request, "core/announcement_detail.html", {"announcement": announcement}
    )


def sitemap_index(request: HttpRequest) -> HttpResponse:
    """Placeholder replaced by the real sitemap in :mod:`apps.core.sitemaps`."""
    from apps.core.sitemaps import render_sitemap_index

    return render_sitemap_index(request)


def sitemap_section(request: HttpRequest, section: str) -> HttpResponse:
    """Render one sitemap section (``static``, ``articles``, ``issues``…)."""
    from apps.core.sitemaps import render_sitemap_section

    return render_sitemap_section(request, section)


def json_debug(request: HttpRequest) -> HttpResponse:  # pragma: no cover - dev helper
    """Dump the resolved site settings as JSON (development aid)."""
    if not settings.DEBUG:
        return HttpResponseNotFound()
    site = get_site_settings()
    return HttpResponse(
        json.dumps({"journal_name": site.journal_name, "eissn": site.eissn}, ensure_ascii=False),
        content_type="application/json",
    )


def home_redirect(request: HttpRequest) -> HttpResponse:
    """Redirect the language-neutral root to the negotiated language."""
    return redirect("/en/", permanent=False)
