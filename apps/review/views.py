"""Reviewer-facing views: invitations, the review form and certificates."""

from __future__ import annotations

import io
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_POST

from apps.submissions.forms import ReviewForm
from apps.submissions.models import Review, ReviewAssignment, SubmissionFile
from apps.submissions.services import submit_review


def _assignment_for(request: HttpRequest, pk: int) -> ReviewAssignment:
    """Fetch an assignment belonging to the signed-in reviewer."""
    assignment = get_object_or_404(
        ReviewAssignment.objects.select_related("round__submission__section"), pk=pk
    )
    if assignment.reviewer_id != request.user.pk:
        raise PermissionDenied
    return assignment


def anonymised_context(assignment: ReviewAssignment) -> dict[str, Any]:
    """Context for reviewer templates with every author detail removed.

    The reviewer must never see author names, e-mails, affiliations, the cover
    letter, the title page, or the identities of the other reviewers.
    """
    submission = assignment.round.submission
    files = submission.files.filter(
        kind__in=SubmissionFile.REVIEWER_VISIBLE_KINDS, is_visible_to_reviewers=True
    ).order_by("kind", "-version")
    return {
        "assignment": assignment,
        "manuscript_title": submission.title,
        "manuscript_abstract": submission.abstract,
        "manuscript_keywords": submission.keywords_list,
        "manuscript_language": submission.get_language_display(),
        "section_name": submission.section.name,
        "article_type": submission.get_article_type_display(),
        "jel_codes": list(submission.jel_codes.all()),
        "word_count": submission.word_count,
        "round_number": assignment.round.number,
        "files": files,
        "due_at": assignment.due_at,
        "days_remaining": assignment.days_remaining,
    }


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Reviewer home: invitations, active reviews and completed history."""
    assignments = ReviewAssignment.objects.filter(reviewer=request.user).select_related(
        "round__submission"
    )
    return TemplateResponse(
        request,
        "review/dashboard.html",
        {
            "invitations": assignments.filter(status=ReviewAssignment.Status.INVITED),
            "active": assignments.filter(
                status__in=[ReviewAssignment.Status.ACCEPTED, ReviewAssignment.Status.OVERDUE]
            ),
            "completed": assignments.filter(status=ReviewAssignment.Status.SUBMITTED),
            "declined": assignments.filter(status=ReviewAssignment.Status.DECLINED),
        },
    )


@login_required
def assignment_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Anonymised manuscript view with the accept/decline actions."""
    assignment = _assignment_for(request, pk)
    context = anonymised_context(assignment)
    context["review"] = getattr(assignment, "review", None)
    return TemplateResponse(request, "review/assignment_detail.html", context)


@require_GET
def respond(request: HttpRequest, token: str, answer: str) -> HttpResponse:
    """One-click accept/decline from the invitation e-mail."""
    assignment = get_object_or_404(ReviewAssignment, access_token=token)
    if assignment.status not in {ReviewAssignment.Status.INVITED, ReviewAssignment.Status.OVERDUE}:
        return TemplateResponse(
            request,
            "review/respond_done.html",
            {"assignment": assignment, "already": True},
        )
    if answer == "accept":
        assignment.status = ReviewAssignment.Status.ACCEPTED
        assignment.response = ReviewAssignment.Response.ACCEPTED
    elif answer == "decline":
        assignment.status = ReviewAssignment.Status.DECLINED
        assignment.response = ReviewAssignment.Response.DECLINED
    else:
        raise Http404
    assignment.responded_at = timezone.now()
    assignment.save(update_fields=["status", "response", "responded_at", "updated_at"])
    return TemplateResponse(
        request, "review/respond_done.html", {"assignment": assignment, "answer": answer}
    )


@login_required
@require_POST
def respond_dashboard(request: HttpRequest, pk: int) -> HttpResponse:
    """Accept or decline an invitation from inside the dashboard."""
    assignment = _assignment_for(request, pk)
    answer = request.POST.get("answer")
    if answer == "accept":
        assignment.status = ReviewAssignment.Status.ACCEPTED
        assignment.response = ReviewAssignment.Response.ACCEPTED
        messages.success(request, _("Thank you for accepting the review invitation."))
    elif answer == "decline":
        assignment.status = ReviewAssignment.Status.DECLINED
        assignment.response = ReviewAssignment.Response.DECLINED
        assignment.decline_reason = request.POST.get("reason", "")
        messages.info(request, _("The invitation has been declined."))
        profile = getattr(request.user, "profile", None)
        if profile is not None:
            profile.reviews_declined += 1
            profile.save(update_fields=["reviews_declined", "updated_at"])
    else:
        raise Http404
    assignment.responded_at = timezone.now()
    assignment.save()
    return redirect("review:dashboard")


@login_required
def review_form(request: HttpRequest, pk: int) -> HttpResponse:
    """The structured review form, with autosave of drafts."""
    assignment = _assignment_for(request, pk)
    if assignment.status not in {
        ReviewAssignment.Status.ACCEPTED,
        ReviewAssignment.Status.OVERDUE,
    }:
        raise PermissionDenied(_("Accept the invitation before writing a review."))

    review = getattr(assignment, "review", None)
    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES, instance=review)
        is_draft = request.POST.get("action") == "save_draft"
        if is_draft:
            # Drafts are saved without full validation.
            review = review or Review(assignment=assignment, recommendation="")
            review.comments_to_authors = request.POST.get("comments_to_authors", "")
            review.comments_to_editor = request.POST.get("comments_to_editor", "")
            review.recommendation = request.POST.get("recommendation", "") or review.recommendation
            review.scores = {
                key: int(request.POST[f"score_{key}"])
                for key, _label in Review.SCORE_FIELDS
                if request.POST.get(f"score_{key}", "").isdigit()
            }
            review.is_draft = True
            review.save()
            messages.success(request, _("Draft saved."))
            return redirect("review:review_form", pk=assignment.pk)
        if form.is_valid():
            review = form.save(commit=False)
            review.assignment = assignment
            submit_review(assignment, review)
            messages.success(request, _("Thank you — your review has been submitted."))
            return redirect("review:dashboard")
    else:
        form = ReviewForm(instance=review)

    context = anonymised_context(assignment)
    context["form"] = form
    context["review"] = review
    return TemplateResponse(request, "review/review_form.html", context)


@login_required
def download_file(request: HttpRequest, pk: int) -> HttpResponse:
    """Serve a reviewer-visible manuscript file."""
    submission_file = get_object_or_404(SubmissionFile, pk=pk)
    allowed = ReviewAssignment.objects.filter(
        reviewer=request.user,
        round__submission=submission_file.submission,
        status__in=[
            ReviewAssignment.Status.ACCEPTED,
            ReviewAssignment.Status.SUBMITTED,
            ReviewAssignment.Status.OVERDUE,
        ],
    ).exists()
    if not allowed or not submission_file.is_visible_to_reviewers:
        raise PermissionDenied
    response = FileResponse(submission_file.file.open("rb"))
    response["Content-Disposition"] = f'inline; filename="manuscript-{submission_file.pk}.pdf"'
    return response


@login_required
def certificate(request: HttpRequest) -> HttpResponse:
    """Generate a PDF certificate listing the reviewer's completed reviews."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    from apps.core.services import get_site_settings

    completed = ReviewAssignment.objects.filter(
        reviewer=request.user, status=ReviewAssignment.Status.SUBMITTED
    ).count()
    if completed == 0:
        messages.info(request, _("A certificate becomes available after your first review."))
        return redirect("review:dashboard")

    site = get_site_settings()
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(width / 2, height - 60 * mm, "CERTIFICATE OF REVIEW")
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(width / 2, height - 75 * mm, site.journal_name_en or site.journal_name)
    pdf.setFont("Helvetica", 11)
    pdf.drawCentredString(width / 2, height - 95 * mm, "This is to certify that")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, height - 107 * mm, request.user.get_full_name())
    pdf.setFont("Helvetica", 11)
    pdf.drawCentredString(
        width / 2,
        height - 120 * mm,
        f"has completed {completed} peer review(s) for the journal.",
    )
    pdf.drawCentredString(width / 2, height - 132 * mm, f"Issued on {timezone.now():%d %B %Y}")
    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(width / 2, 30 * mm, f"{site.publisher_name} · {site.contact_email}")
    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    response = FileResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="arer-reviewer-certificate.pdf"'
    return response
