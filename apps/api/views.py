"""Read-only public JSON API (SPEC §9)."""

from __future__ import annotations

from typing import Any

from django.http import JsonResponse
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from apps.api.serializers import (
    ArticleDetailSerializer,
    ArticleListSerializer,
    IssueListSerializer,
    SectionSerializer,
)
from apps.core.services import get_site_settings
from apps.journal.models import Article, Issue, Section


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """Published and Online First articles."""

    queryset = Article.objects.public().with_related()
    filterset_fields = ["section__slug", "issue__number", "issue__volume__number", "status"]

    def get_serializer_class(self):
        """Full representation for detail, summary for list."""
        return ArticleDetailSerializer if self.action == "retrieve" else ArticleListSerializer


class IssueViewSet(viewsets.ReadOnlyModelViewSet):
    """Published issues."""

    queryset = Issue.objects.published().select_related("volume")
    serializer_class = IssueListSerializer
    filterset_fields = ["volume__number", "number"]


class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    """Active journal sections."""

    queryset = Section.objects.filter(is_active=True)
    serializer_class = SectionSerializer
    lookup_field = "slug"


@api_view(["GET"])
def search(request: Request) -> Response:
    """Simple keyword search over published articles."""
    from apps.search.views import _apply_filters, _base_queryset, _search

    query = (request.query_params.get("q") or "").strip()
    queryset = _apply_filters(_base_queryset(), request.query_params)
    if query:
        queryset = _search(queryset, query, "en")
    queryset = queryset[:50]
    serializer = ArticleListSerializer(queryset, many=True, context={"request": request})
    return Response({"count": len(serializer.data), "results": serializer.data})


@api_view(["GET"])
def doaj_export(request: Request) -> Response:
    """Export article metadata in the DOAJ article-upload JSON shape."""
    site = get_site_settings()
    articles = Article.objects.published().with_related()[:1000]
    payload: list[dict[str, Any]] = []
    for article in articles:
        record: dict[str, Any] = {
            "bibjson": {
                "title": article.title_en or article.title,
                "abstract": article.abstract_plain,
                "author": [
                    {
                        "name": author.full_name,
                        "affiliation": author.affiliation_display,
                        "orcid_id": author.orcid_url or None,
                    }
                    for author in article.author_list()
                ],
                "keywords": [k.name for k in article.keywords.all()][:6],
                "identifier": [{"type": "doi", "id": article.doi} for _ in [1] if article.doi]
                + ([{"type": "eissn", "id": site.eissn}] if site.eissn else []),
                "journal": {
                    "title": site.journal_name_en or site.journal_name,
                    "publisher": site.publisher_name,
                    "language": ["EN", "UZ", "RU"],
                    "volume": str(article.issue.volume.number) if article.issue_id else "",
                    "number": str(article.issue.number) if article.issue_id else "",
                    "start_page": article.pages_start,
                    "end_page": article.pages_end,
                },
                "link": [
                    {
                        "type": "fulltext",
                        "url": request.build_absolute_uri(article.pdf_url),
                        "content_type": "PDF",
                    },
                    {
                        "type": "fulltext",
                        "url": request.build_absolute_uri(article.get_absolute_url()),
                        "content_type": "HTML",
                    },
                ],
                "year": str(article.display_date.year) if article.display_date else "",
                "month": f"{article.display_date.month:02d}" if article.display_date else "",
            }
        }
        payload.append(record)
    return Response(payload)


def api_root(request) -> JsonResponse:
    """Discovery document listing the available endpoints."""
    return JsonResponse(
        {
            "articles": request.build_absolute_uri(reverse("api:article-list")),
            "issues": request.build_absolute_uri(reverse("api:issue-list")),
            "sections": request.build_absolute_uri(reverse("api:section-list")),
            "search": request.build_absolute_uri(reverse("api:search")),
            "doaj_export": request.build_absolute_uri(reverse("api:doaj_export")),
            "oai_pmh": request.build_absolute_uri("/oai/"),
        }
    )
