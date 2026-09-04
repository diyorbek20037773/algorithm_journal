"""Public views: home, archive, issue TOC, article landing and browse pages."""

from __future__ import annotations

from typing import Any

from django.db.models import Count, Prefetch, Q
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET
from django.views.generic import DetailView, ListView, TemplateView

from apps.core.models import Announcement
from apps.journal.models import (
    Article,
    Author,
    EditorialBoardMember,
    Issue,
    JELCode,
    Keyword,
    Section,
    Volume,
)

PAGE_SIZE = 20


class HomeView(TemplateView):
    """The journal home page (SPEC §6.1)."""

    template_name = "journal/home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Assemble every home page band in a small number of queries."""
        from apps.metrics.services import home_kpis, most_read

        context = super().get_context_data(**kwargs)
        current_issue = Issue.current()
        context["current_issue"] = current_issue
        context["current_issue_articles"] = (
            list(
                Article.objects.public()
                .filter(issue=current_issue)
                .for_cards()
                .order_by("article_number", "id")[:6]
            )
            if current_issue
            else []
        )
        context["online_first"] = list(
            Article.objects.online_first()
            .select_related("section")
            .prefetch_related("authors")
            .order_by("-published_online_at")[:4]
        )
        context["sections"] = list(
            Section.objects.filter(is_active=True, is_research=True)
            .annotate(
                published_count=Count(
                    "articles",
                    filter=Q(
                        articles__status__in=[
                            Article.Status.PUBLISHED,
                            Article.Status.ONLINE_FIRST,
                        ]
                    ),
                )
            )
            .order_by("order")
        )
        context["jel_top_level"] = list(JELCode.objects.filter(level=1).order_by("code"))
        context["most_read"] = most_read(limit=5)
        context["announcements"] = list(Announcement.objects.live()[:3])
        context["kpis"] = home_kpis()
        from apps.core.models import IndexingService

        context["indexing_services"] = list(IndexingService.objects.filter(is_active=True))
        context["meta_description"] = self.request.site_settings.journal_subtitle
        from apps.journal.metadata import periodical_json_ld

        context["periodical_json_ld"] = periodical_json_ld()
        return context


class ArchiveView(TemplateView):
    """Archive of every published volume and issue (SPEC §6.4)."""

    template_name = "journal/archive.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Group published issues by volume, newest first."""
        context = super().get_context_data(**kwargs)
        year = self.request.GET.get("year")
        volumes = Volume.objects.prefetch_related(
            Prefetch(
                "issues",
                queryset=Issue.objects.published()
                .annotate(article_count=Count("articles"))
                .order_by("-number"),
            )
        ).order_by("-number")
        if year and year.isdigit():
            volumes = volumes.filter(year=int(year))
        context["volumes"] = [v for v in volumes if v.issues.all()]
        context["years"] = list(
            Volume.objects.filter(issues__is_published=True)
            .values_list("year", flat=True)
            .distinct()
            .order_by("-year")
        )
        context["selected_year"] = int(year) if year and year.isdigit() else None
        context["meta_description"] = _("Complete archive of published issues.")
        return context


@require_GET
def current_issue(request: HttpRequest) -> HttpResponse:
    """Redirect to the current issue's table of contents."""
    issue = Issue.current()
    if issue is None:
        return TemplateResponse(request, "journal/issue_empty.html", {}, status=200)
    return redirect(issue.get_absolute_url())


class OnlineFirstView(ListView):
    """Articles published ahead of an issue."""

    template_name = "journal/online_first.html"
    context_object_name = "articles"
    paginate_by = PAGE_SIZE

    def get_queryset(self):
        """Online First articles, newest first."""
        return Article.objects.online_first().with_related().order_by("-published_online_at", "-id")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add a page description."""
        context = super().get_context_data(**kwargs)
        context["meta_description"] = _(
            "Peer-reviewed articles published ahead of their issue, already citable by DOI."
        )
        return context


class IssueDetailView(DetailView):
    """Table of contents of one issue (SPEC §6.3)."""

    template_name = "journal/issue_detail.html"
    context_object_name = "issue"

    def get_object(self, queryset=None) -> Issue:
        """Look the issue up by volume and issue number."""
        return get_object_or_404(
            Issue.objects.published().select_related("volume"),
            volume__number=self.kwargs["volume"],
            number=self.kwargs["issue"],
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Group the issue's articles by section, in section order."""
        context = super().get_context_data(**kwargs)
        issue: Issue = context["issue"]
        articles = list(
            Article.objects.public()
            .filter(issue=issue)
            .with_related()
            .order_by("section__order", "article_number", "id")
        )
        grouped: list[dict[str, Any]] = []
        for article in articles:
            if not grouped or grouped[-1]["section"].pk != article.section_id:
                grouped.append({"section": article.section, "articles": []})
            grouped[-1]["articles"].append(article)
        context["grouped_articles"] = grouped
        context["article_count"] = len(articles)
        context["previous_issue"] = (
            Issue.objects.published()
            .filter(
                Q(volume__number__lt=issue.volume.number)
                | Q(volume__number=issue.volume.number, number__lt=issue.number)
            )
            .select_related("volume")
            .first()
        )
        context["next_issue"] = (
            Issue.objects.published()
            .filter(
                Q(volume__number__gt=issue.volume.number)
                | Q(volume__number=issue.volume.number, number__gt=issue.number)
            )
            .select_related("volume")
            .order_by("volume__number", "number")
            .first()
        )
        context["meta_description"] = f"{issue.label} — {context['article_count']} articles."
        return context


class ArticleDetailView(DetailView):
    """The article landing page — the most important page of the site."""

    template_name = "journal/article_detail.html"
    context_object_name = "article"

    def get_queryset(self):
        """Only publicly visible articles, with everything prefetched."""
        return (
            Article.objects.public()
            .with_related()
            .prefetch_related("references", "authors", "keywords", "jel_codes")
        )

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Redirect to the canonical slug URL when the slug is wrong."""
        self.object = self.get_object()
        expected = self.object.slug
        given = kwargs.get("slug")
        if expected and given is not None and given != expected:
            return redirect(self.object.get_absolute_url(), permanent=True)
        context = self.get_context_data(object=self.object)
        response = self.render_to_response(context)
        self._record_view(request)
        return response

    def _record_view(self, request: HttpRequest) -> None:
        """Register an article view for the metrics app."""
        from apps.metrics.services import record_access

        record_access(request, self.object, kind="view")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add related articles, translated abstracts and citation metadata."""
        from apps.citations.services import available_styles
        from apps.journal.metadata import highwire_tags, json_ld

        context = super().get_context_data(**kwargs)
        article: Article = context["article"]
        context["authors"] = article.author_list()
        context["references"] = list(article.references.all())
        context["galleys"] = list(article.galleys.all())
        context["primary_galley"] = article.primary_galley
        context["highwire_tags"] = highwire_tags(article)
        context["json_ld"] = json_ld(article)
        context["citation_styles"] = available_styles()
        context["abstract_translations"] = self._abstract_translations(article)
        context["title_translations"] = self._title_translations(article)
        context["related_articles"] = self._related(article)
        context["meta_description"] = article.abstract_plain[:300]
        return context

    @staticmethod
    def _abstract_translations(article: Article) -> list[dict[str, str]]:
        """Abstract in each language that has content."""
        out = []
        for code, label in (
            ("en", "English"),
            ("uz", "Oʻzbekcha"),
            ("uz_cyrl", "Ўзбекча"),
            ("ru", "Русский"),
        ):
            value = getattr(article, f"abstract_{code}", None)
            if value:
                out.append({"code": code.replace("_", "-"), "label": label, "text": value})
        return out

    @staticmethod
    def _title_translations(article: Article) -> list[dict[str, str]]:
        """Title in each language that has content."""
        out = []
        for code, label in (
            ("en", "English"),
            ("uz", "Oʻzbekcha"),
            ("uz_cyrl", "Ўзбекча"),
            ("ru", "Русский"),
        ):
            value = getattr(article, f"title_{code}", None)
            if value:
                out.append({"code": code.replace("_", "-"), "label": label, "text": value})
        return out

    @staticmethod
    def _related(article: Article) -> list[Article]:
        """Up to four related articles sharing keywords or JEL codes."""
        keyword_ids = list(article.keywords.values_list("id", flat=True))
        jel_ids = list(article.jel_codes.values_list("id", flat=True))
        if not keyword_ids and not jel_ids:
            return []
        return list(
            Article.objects.public()
            .exclude(pk=article.pk)
            .filter(Q(keywords__in=keyword_ids) | Q(jel_codes__in=jel_ids))
            .with_related()
            .distinct()[:4]
        )


@require_GET
def article_cite(request: HttpRequest, pk: int) -> HttpResponse:
    """HTMX partial rendering the citation in the requested style."""
    from apps.citations.services import available_styles, render_citation

    article = get_object_or_404(Article.objects.public().with_related(), pk=pk)
    style = request.GET.get("style", "apa")
    valid = {s["code"] for s in available_styles()}
    if style not in valid:
        style = "apa"
    return TemplateResponse(
        request,
        "journal/partials/cite_modal.html",
        {
            "article": article,
            "style": style,
            "citation": render_citation(article, style),
            "citation_styles": available_styles(),
        },
    )


@require_GET
def article_export(request: HttpRequest, pk: int, fmt: str) -> HttpResponse:
    """Download the article's metadata as BibTeX, RIS, EndNote or CSL-JSON."""
    from apps.citations.services import export_article

    article = get_object_or_404(Article.objects.public().with_related(), pk=pk)
    try:
        content, mime, filename = export_article(article, fmt)
    except ValueError as exc:
        raise Http404(str(exc)) from exc
    response = HttpResponse(content, content_type=mime)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


class SectionDetailView(ListView):
    """Articles published in one section."""

    template_name = "journal/section_detail.html"
    context_object_name = "articles"
    paginate_by = PAGE_SIZE

    def get_queryset(self):
        """Public articles of the section, newest first."""
        self.section = get_object_or_404(Section, slug=self.kwargs["slug"], is_active=True)
        return Article.objects.public().filter(section=self.section).with_related()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Expose the section object and a description."""
        context = super().get_context_data(**kwargs)
        context["section"] = self.section
        context["meta_description"] = self.section.description[:300]
        return context


class KeywordDetailView(ListView):
    """Articles carrying one keyword."""

    template_name = "journal/keyword_detail.html"
    context_object_name = "articles"
    paginate_by = PAGE_SIZE

    def get_queryset(self):
        """Public articles tagged with the keyword."""
        self.keyword = get_object_or_404(Keyword, slug=self.kwargs["slug"])
        return Article.objects.public().filter(keywords=self.keyword).with_related()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Expose the keyword object."""
        context = super().get_context_data(**kwargs)
        context["keyword"] = self.keyword
        return context


class JELIndexView(TemplateView):
    """Browse the JEL classification tree."""

    template_name = "journal/jel_index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Top-level JEL codes with their children and article counts."""
        context = super().get_context_data(**kwargs)
        top = list(
            JELCode.objects.filter(level=1)
            .prefetch_related("children")
            .annotate(
                article_total=Count(
                    "articles",
                    filter=Q(
                        articles__status__in=[
                            Article.Status.PUBLISHED,
                            Article.Status.ONLINE_FIRST,
                        ]
                    ),
                    distinct=True,
                )
            )
            .order_by("code")
        )
        context["jel_top_level"] = top
        return context


class JELDetailView(ListView):
    """Articles classified under one JEL code."""

    template_name = "journal/jel_detail.html"
    context_object_name = "articles"
    paginate_by = PAGE_SIZE

    def get_queryset(self):
        """Articles carrying the JEL code or any of its descendants."""
        self.jel = get_object_or_404(JELCode, code__iexact=self.kwargs["code"])
        descendants = [self.jel.pk, *self.jel.children.values_list("pk", flat=True)]
        return Article.objects.public().filter(jel_codes__in=descendants).with_related().distinct()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Expose the JEL code object."""
        context = super().get_context_data(**kwargs)
        context["jel"] = self.jel
        return context


class AuthorDetailView(ListView):
    """Every article by one author, aggregated by ORCID or normalised name."""

    template_name = "journal/author_detail.html"
    context_object_name = "articles"
    paginate_by = PAGE_SIZE

    def get_queryset(self):
        """Articles whose authorship rows match this author slug."""
        slug = self.kwargs["slug"]
        matches = [a for a in Author.objects.select_related("article") if a.slug == slug]
        if not matches:
            raise Http404(_("Author not found."))
        self.author = matches[0]
        orcids = {a.orcid for a in matches if a.orcid}
        query = Q(authors__in=[a.pk for a in matches])
        if orcids:
            query |= Q(authors__orcid__in=orcids)
        return Article.objects.public().filter(query).with_related().distinct()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Expose the representative author row."""
        context = super().get_context_data(**kwargs)
        context["author"] = self.author
        context["meta_description"] = _("Articles by %(name)s") % {"name": self.author.full_name}
        return context


def _board_context(roles: list[str]) -> dict[str, Any]:
    """Group active board members by role, preserving the canonical order."""
    members = list(
        EditorialBoardMember.objects.filter(is_active=True, role__in=roles).order_by(
            "order", "full_name"
        )
    )
    groups = []
    for role in EditorialBoardMember.ROLE_ORDER:
        if role not in roles:
            continue
        in_role = [m for m in members if m.role == role]
        if in_role:
            groups.append(
                {
                    "role": role,
                    "label": dict(EditorialBoardMember.Role.choices)[role],
                    "members": in_role,
                }
            )
    countries = {m.country.code for m in members if m.country}
    return {
        "groups": groups,
        "member_count": len(members),
        "country_count": len(countries),
        "has_demo": any(m.is_demo for m in members),
    }


@require_GET
def editorial_board(request: HttpRequest) -> HttpResponse:
    """Editorial board page grouped by role (SPEC §6.6)."""
    roles = [
        EditorialBoardMember.Role.EDITOR_IN_CHIEF,
        EditorialBoardMember.Role.DEPUTY_EDITOR,
        EditorialBoardMember.Role.MANAGING_EDITOR,
        EditorialBoardMember.Role.SECTION_EDITOR,
        EditorialBoardMember.Role.BOARD_MEMBER,
        EditorialBoardMember.Role.ADVISORY,
    ]
    context = _board_context(roles)
    context["board_title"] = _("Editorial Board")
    context["meta_description"] = _("Editorial board of the journal.")
    return TemplateResponse(request, "journal/editorial_board.html", context)


@require_GET
def reviewer_board(request: HttpRequest) -> HttpResponse:
    """Reviewer board page (explicit route, declared before the CMS catch-all)."""
    context = _board_context([EditorialBoardMember.Role.REVIEWER_BOARD])
    context["board_title"] = _("Reviewer Board")
    context["meta_description"] = _("Standing reviewer board of the journal.")
    return TemplateResponse(request, "journal/editorial_board.html", context)


@require_GET
def article_json(request: HttpRequest, pk: int) -> JsonResponse:
    """Small JSON representation used by HTMX widgets."""
    article = get_object_or_404(Article.objects.public().with_related(), pk=pk)
    return JsonResponse(
        {
            "id": article.pk,
            "title": article.title,
            "doi": article.doi,
            "url": article.canonical_url,
            "authors": [a.full_name for a in article.author_list()],
        }
    )
