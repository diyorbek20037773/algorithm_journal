"""Production dashboard: stages, galleys, DOI, Online First and issue builder."""

from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.accounts.permissions import ProductionRequiredMixin
from apps.journal.models import Article, Galley, Issue, Volume
from apps.production import services
from apps.submissions import workflow
from apps.submissions.models import (
    PRODUCTION_STATES,
    ProductionTask,
    Submission,
    SubmissionFile,
    SubmissionStatus,
)

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


class ProductionQueueView(ProductionRequiredMixin, TemplateView):
    """Queue of accepted manuscripts moving through production."""

    template_name = "production/queue.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Group submissions by production stage."""
        context = super().get_context_data(**kwargs)
        queryset = Submission.objects.filter(status__in=PRODUCTION_STATES).with_related()
        context["queues"] = [
            {"status": status, "label": dict(SubmissionStatus.choices)[status],
             "items": [s for s in queryset if s.status == status]}
            for status in PRODUCTION_STATES
        ]
        context["ready"] = Article.objects.filter(status=Article.Status.DRAFT).with_related()
        context["online_first"] = Article.objects.online_first().with_related()
        context["draft_issues"] = Issue.objects.filter(is_published=False).select_related("volume")
        return context


@login_required
def submission_production(request: HttpRequest, pk: int) -> HttpResponse:
    """Production detail page for one accepted submission."""
    if not request.user.has_role("production_editor", "editor_in_chief", "admin"):
        return redirect("dashboard:home")
    submission = get_object_or_404(Submission.objects.with_related(), pk=pk)
    article = submission.article or (
        services.create_article_from_submission(submission)
        if submission.status in PRODUCTION_STATES
        else None
    )
    context: dict[str, Any] = {
        "submission": submission,
        "article": article,
        "tasks": submission.production_tasks.order_by("id"),
        "files": submission.files.order_by("kind", "-version"),
        "completeness": services.metadata_completeness(article) if article else [],
        "blockers": services.completeness_blockers(article) if article else [],
        "galleys": article.galleys.all() if article else [],
        "issues": Issue.objects.filter(is_published=False).select_related("volume"),
        "transitions": workflow.available_transitions(submission, request.user),
    }
    return TemplateResponse(request, "production/submission_detail.html", context)


@login_required
@require_POST
def advance_stage(request: HttpRequest, pk: int) -> HttpResponse:
    """Run a production workflow transition."""
    submission = get_object_or_404(Submission, pk=pk)
    transition = request.POST.get("transition", "")
    try:
        workflow.perform(submission, transition, request.user, request=request)
        messages.success(request, _("The manuscript has moved to the next stage."))
        if transition == "send_proof":
            from apps.submissions.tasks import send_proof_request

            send_proof_request.delay(submission.pk)
    except ValidationError as exc:
        messages.error(request, "; ".join(exc.messages))
    return redirect("production:submission", pk=submission.pk)


@login_required
@require_POST
def complete_task(request: HttpRequest, pk: int) -> HttpResponse:
    """Mark one production checklist item as done."""
    task = get_object_or_404(ProductionTask, pk=pk)
    task.status = ProductionTask.Status.DONE
    task.completed_at = timezone.now()
    task.assignee = task.assignee or request.user
    task.save(update_fields=["status", "completed_at", "assignee", "updated_at"])
    messages.success(request, _("Stage marked as complete."))
    return redirect("production:submission", pk=task.submission_id)


@login_required
@require_POST
def upload_production_file(request: HttpRequest, pk: int) -> HttpResponse:
    """Upload a copyedited, proof or final file."""
    submission = get_object_or_404(Submission, pk=pk)
    kind = request.POST.get("kind", SubmissionFile.Kind.COPYEDITED)
    uploaded = request.FILES.get("file")
    if uploaded is None:
        messages.error(request, _("No file was selected."))
        return redirect("production:submission", pk=submission.pk)
    version = submission.files.filter(kind=kind).count() + 1
    SubmissionFile.objects.create(
        submission=submission,
        kind=kind,
        file=uploaded,
        original_name=uploaded.name[:255],
        uploaded_by=request.user,
        version=version,
        size=uploaded.size,
    )
    messages.success(request, _("File uploaded."))
    return redirect("production:submission", pk=submission.pk)


@login_required
@require_POST
def upload_galley(request: HttpRequest, pk: int) -> HttpResponse:
    """Attach a galley (PDF or JATS XML) to the article."""
    article = get_object_or_404(Article, pk=pk)
    uploaded = request.FILES.get("file")
    if uploaded is None:
        messages.error(request, _("No file was selected."))
        return redirect("production:article", pk=article.pk)
    label = request.POST.get("label", Galley.Label.PDF)
    mime = "application/pdf" if label.startswith("PDF") else "application/xml"
    is_primary = label == Galley.Label.PDF
    if is_primary:
        Galley.objects.filter(article=article, is_primary=True).update(is_primary=False)
    Galley.objects.create(
        article=article,
        label=label,
        language=request.POST.get("language", "en"),
        file=uploaded,
        mime=mime,
        size=uploaded.size,
        is_primary=is_primary,
        order=article.galleys.count() + 1,
    )
    messages.success(request, _("Galley uploaded."))
    return redirect("production:article", pk=article.pk)


@login_required
def article_production(request: HttpRequest, pk: int) -> HttpResponse:
    """Production view of one article: metadata, galleys, DOI, scheduling."""
    article = get_object_or_404(Article.objects.with_related(), pk=pk)
    return TemplateResponse(
        request,
        "production/article_detail.html",
        {
            "article": article,
            "completeness": services.metadata_completeness(article),
            "blockers": services.completeness_blockers(article),
            "issues": Issue.objects.filter(is_published=False).select_related("volume"),
            "galleys": article.galleys.all(),
        },
    )


@login_required
@require_POST
def assign_doi(request: HttpRequest, pk: int) -> HttpResponse:
    """Reserve the article's DOI."""
    article = get_object_or_404(Article, pk=pk)
    doi = services.reserve_doi(article, user=request.user, request=request)
    messages.success(request, _("DOI reserved: %(doi)s") % {"doi": doi})
    return redirect("production:article", pk=article.pk)


@login_required
@require_POST
def publish_online_first(request: HttpRequest, pk: int) -> HttpResponse:
    """Publish the article ahead of its issue."""
    article = get_object_or_404(Article.objects.with_related(), pk=pk)
    try:
        services.publish_online_first(article, user=request.user, request=request)
        messages.success(request, _("The article is published as Online First."))
    except ValidationError as exc:
        messages.error(request, "; ".join(exc.messages))
    return redirect("production:article", pk=article.pk)


@login_required
@require_POST
def schedule_to_issue(request: HttpRequest, pk: int) -> HttpResponse:
    """Place the article into an issue with pagination."""
    article = get_object_or_404(Article.objects.with_related(), pk=pk)
    issue = get_object_or_404(Issue, pk=request.POST.get("issue"))
    services.assign_to_issue(
        article,
        issue,
        pages_start=request.POST.get("pages_start", ""),
        pages_end=request.POST.get("pages_end", ""),
        user=request.user,
    )
    messages.success(request, _("The article has been scheduled into %(issue)s.") % {"issue": issue.label})
    return redirect("production:issue_builder", pk=issue.pk)


@login_required
def issue_builder(request: HttpRequest, pk: int) -> HttpResponse:
    """Assemble an issue: order articles, set pages, publish."""
    issue = get_object_or_404(Issue.objects.select_related("volume"), pk=pk)
    assigned = (
        Article.objects.filter(issue=issue)
        .with_related()
        .order_by("section__order", "article_number", "id")
    )
    unassigned = (
        Article.objects.filter(issue__isnull=True)
        .exclude(status=Article.Status.PUBLISHED)
        .with_related()
    )
    blockers: dict[int, list[str]] = {a.pk: services.completeness_blockers(a) for a in assigned}
    return TemplateResponse(
        request,
        "production/issue_builder.html",
        {
            "issue": issue,
            "assigned": assigned,
            "unassigned": unassigned,
            "blockers": blockers,
            "can_publish": bool(assigned) and not any(blockers.values()),
        },
    )


@login_required
@require_POST
def reorder_issue(request: HttpRequest, pk: int) -> HttpResponse:
    """Save the article order and page ranges of an issue."""
    issue = get_object_or_404(Issue, pk=pk)
    for article in Article.objects.filter(issue=issue):
        prefix = f"article_{article.pk}"
        number = request.POST.get(f"{prefix}_number")
        article.article_number = int(number) if number and number.isdigit() else article.article_number
        article.pages_start = request.POST.get(f"{prefix}_pages_start", article.pages_start)
        article.pages_end = request.POST.get(f"{prefix}_pages_end", article.pages_end)
        article.save(update_fields=["article_number", "pages_start", "pages_end", "updated_at"])
    messages.success(request, _("The issue order has been saved."))
    return redirect("production:issue_builder", pk=issue.pk)


@login_required
@require_POST
def publish_issue(request: HttpRequest, pk: int) -> HttpResponse:
    """Publish an issue and every article in it."""
    issue = get_object_or_404(Issue, pk=pk)
    try:
        services.publish_issue(issue, user=request.user, request=request)
        messages.success(request, _("Issue %(label)s is published.") % {"label": issue.label})
    except ValidationError as exc:
        messages.error(request, "; ".join(exc.messages))
    return redirect("production:issue_builder", pk=issue.pk)


@login_required
@require_POST
def create_issue(request: HttpRequest) -> HttpResponse:
    """Create a new (unpublished) issue in a volume."""
    volume_number = int(request.POST.get("volume", 1))
    year = int(request.POST.get("year", timezone.now().year))
    number = int(request.POST.get("number", 1))
    volume, _created = Volume.objects.get_or_create(number=volume_number, defaults={"year": year})
    issue, created = Issue.objects.get_or_create(volume=volume, number=number)
    messages.success(
        request,
        _("Issue %(label)s created.") if created else _("Issue %(label)s already exists."),
    )
    return redirect("production:issue_builder", pk=issue.pk)


# Function view wrapper so the queue keeps the mixin's role check.
queue = method_decorator(login_required, name="dispatch")(ProductionQueueView).as_view()
