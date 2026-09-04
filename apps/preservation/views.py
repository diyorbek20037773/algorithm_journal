"""LOCKSS/CLOCKSS permission manifests."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.decorators.http import require_GET

from apps.journal.models import Article, Volume

#: The exact wording LOCKSS crawlers look for.
LOCKSS_PERMISSION = (
    "LOCKSS system has permission to collect, preserve, and serve this Archival Unit."
)


@require_GET
def manifest_index(request: HttpRequest) -> HttpResponse:
    """List every volume that a preservation network may harvest."""
    volumes = (
        Volume.objects.filter(issues__is_published=True).distinct().order_by("-number")
    )
    return TemplateResponse(
        request,
        "preservation/manifest_index.html",
        {"volumes": volumes, "permission": LOCKSS_PERMISSION},
    )


@require_GET
def manifest_volume(request: HttpRequest, volume: int) -> HttpResponse:
    """List every article and PDF of one volume, with the permission statement."""
    volume_obj = get_object_or_404(Volume, number=volume)
    articles = (
        Article.objects.public()
        .filter(issue__volume=volume_obj, issue__is_published=True)
        .with_related()
        .order_by("issue__number", "article_number")
    )
    return TemplateResponse(
        request,
        "preservation/manifest_volume.html",
        {"volume": volume_obj, "articles": articles, "permission": LOCKSS_PERMISSION},
    )
