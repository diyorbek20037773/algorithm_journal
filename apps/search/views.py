"""Full-text search over published articles using PostgreSQL FTS."""

from __future__ import annotations

from typing import Any

from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramSimilarity,
)
from django.core.paginator import Paginator
from django.db.models import F, Q, QuerySet, Value
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.http import require_GET

from apps.journal.models import Article, JELCode, Keyword, Section, Volume

PAGE_SIZE = 10

#: Postgres text search configuration per interface language.
LANGUAGE_CONFIG = {
    "en": "english",
    "ru": "russian",
    "uz": "simple",
    "uz-cyrl": "simple",
}

SORT_OPTIONS = {
    "relevance": None,
    "newest": ("-published_at", "-id"),
    "oldest": ("published_at", "id"),
    "most_viewed": ("-views_count",),
}


def _base_queryset() -> QuerySet[Article]:
    """Only publicly visible articles participate in search."""
    return Article.objects.public().with_related()


def _apply_filters(queryset: QuerySet[Article], params) -> QuerySet[Article]:
    """Apply the facet filters carried in the query string."""
    year = params.get("year")
    if year and year.isdigit():
        queryset = queryset.filter(issue__volume__year=int(year))
    volume = params.get("volume")
    if volume and volume.isdigit():
        queryset = queryset.filter(issue__volume__number=int(volume))
    issue = params.get("issue")
    if issue and issue.isdigit():
        queryset = queryset.filter(issue__number=int(issue))
    section = params.get("section")
    if section:
        queryset = queryset.filter(section__slug=section)
    jel = params.get("jel")
    if jel:
        queryset = queryset.filter(jel_codes__code__iexact=jel)
    keyword = params.get("keyword")
    if keyword:
        queryset = queryset.filter(keywords__slug=keyword)
    author = params.get("author")
    if author:
        queryset = queryset.annotate(
            author_similarity=TrigramSimilarity(F("authors__family_name"), Value(author))
        ).filter(
            Q(author_similarity__gt=0.25)
            | Q(authors__family_name__icontains=author)
            | Q(authors__given_name__icontains=author)
        )
    return queryset.distinct()


def _search(queryset: QuerySet[Article], query: str, language: str) -> QuerySet[Article]:
    """Rank the queryset by full-text relevance against ``query``."""
    config = LANGUAGE_CONFIG.get(language, "simple")
    vector = (
        SearchVector("title", weight="A", config=config)
        + SearchVector("abstract", weight="B", config=config)
        + SearchVector("keywords__name", weight="B", config=config)
        + SearchVector("authors__family_name", weight="C", config=config)
        + SearchVector("authors__given_name", weight="C", config=config)
        + SearchVector("references__raw_text", weight="D", config=config)
    )
    search_query = SearchQuery(query, config=config, search_type="websearch")
    return (
        queryset.annotate(rank=SearchRank(vector, search_query))
        .filter(rank__gt=0.01)
        .annotate(
            headline=SearchHeadline(
                "abstract",
                search_query,
                config=config,
                start_sel="<mark>",
                stop_sel="</mark>",
                max_words=45,
                min_words=20,
            )
        )
        .order_by("-rank", "-published_at")
        .distinct()
    )


@require_GET
def search(request: HttpRequest) -> HttpResponse:
    """Search page with HTMX-updated results and shareable URLs."""
    from django.utils.translation import get_language

    params = request.GET
    query = (params.get("q") or "").strip()
    sort = params.get("sort", "relevance")
    if sort not in SORT_OPTIONS:
        sort = "relevance"

    queryset = _apply_filters(_base_queryset(), params)
    if query:
        queryset = _search(queryset, query, get_language() or "en")
        if sort != "relevance":
            queryset = queryset.order_by(*SORT_OPTIONS[sort])
    else:
        queryset = queryset.order_by(*(SORT_OPTIONS[sort] or ("-published_at", "-id")))

    paginator = Paginator(queryset, PAGE_SIZE)
    page = paginator.get_page(params.get("page"))

    context: dict[str, Any] = {
        "query": query,
        "sort": sort,
        "page_obj": page,
        "results": page.object_list,
        "result_count": paginator.count,
        "sections": Section.objects.filter(is_active=True),
        "years": list(
            Volume.objects.filter(issues__is_published=True)
            .values_list("year", flat=True)
            .distinct()
            .order_by("-year")
        ),
        "jel_top_level": JELCode.objects.filter(level=1).order_by("code"),
        "popular_keywords": Keyword.objects.all()[:24],
        "filters": {
            "year": params.get("year", ""),
            "section": params.get("section", ""),
            "jel": params.get("jel", ""),
            "keyword": params.get("keyword", ""),
            "author": params.get("author", ""),
        },
        "querystring": _querystring_without_page(params),
        "meta_description": "Search the journal's published articles.",
    }

    template = (
        "search/partials/results.html"
        if request.headers.get("HX-Request")
        else "search/search.html"
    )
    return TemplateResponse(request, template, context)


def _querystring_without_page(params) -> str:
    """Rebuild the query string without the ``page`` parameter."""
    pairs = [(k, v) for k, v in params.items() if k != "page" and v]
    from urllib.parse import urlencode

    return urlencode(pairs)
