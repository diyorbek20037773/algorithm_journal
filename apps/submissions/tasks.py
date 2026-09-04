"""Celery tasks: editorial notifications and scheduled reminders."""

from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.core.services import absolute_url, get_site_settings, send_templated_email
from apps.submissions.models import (
    EditorialDecision,
    ReviewAssignment,
    RevisionRequest,
    Submission,
)

logger = logging.getLogger(__name__)


def _language(user) -> str:
    """Preferred interface language of a recipient."""
    return getattr(user, "preferred_language", None) or "en"


@shared_task(name="apps.submissions.tasks.notify_submission_received")
def notify_submission_received(submission_id: int) -> str:
    """Confirm receipt to the author and alert the section's editors."""
    submission = Submission.objects.select_related("section", "submitter").get(pk=submission_id)
    site = get_site_settings()
    context = {
        "reference": submission.reference,
        "title": submission.title,
        "journal": site.journal_name,
        "section": submission.section.name,
        "dashboard_url": absolute_url(reverse("dashboard:home")),
    }
    send_templated_email(
        "submission_received_author",
        to=[submission.submitter.email],
        context=context,
        language=_language(submission.submitter),
        fallback_subject=_("Your submission %(ref)s has been received")
        % {"ref": submission.reference},
        fallback_body=_(
            "Dear author,\n\nThank you for submitting **{title}** ({reference}) to {journal}.\n\n"
            "You can follow its progress in your dashboard: {dashboard_url}"
        ),
    )

    editors = list(submission.section.editors.all())
    if submission.assigned_editor and submission.assigned_editor not in editors:
        editors.append(submission.assigned_editor)
    for editor in editors:
        send_templated_email(
            "submission_received_editor",
            to=[editor.email],
            context={
                **context,
                "detail_url": absolute_url(submission.get_absolute_url()),
            },
            language=_language(editor),
            fallback_subject=_("New submission %(ref)s") % {"ref": submission.reference},
            fallback_body=_(
                "A new manuscript **{title}** ({reference}) was submitted to the section "
                "{section}.\n\nOpen it here: {detail_url}"
            ),
        )
    return f"notified {submission.reference}"


@shared_task(name="apps.submissions.tasks.notify_editor_assigned")
def notify_editor_assigned(submission_id: int) -> str:
    """Tell the handling editor that a manuscript is waiting for screening."""
    submission = Submission.objects.select_related("assigned_editor").get(pk=submission_id)
    if submission.assigned_editor is None:
        return "no editor"
    send_templated_email(
        "editor_assigned",
        to=[submission.assigned_editor.email],
        context={
            "reference": submission.reference,
            "title": submission.title,
            "detail_url": absolute_url(submission.get_absolute_url()),
        },
        language=_language(submission.assigned_editor),
        fallback_subject=_("You are handling %(ref)s") % {"ref": submission.reference},
        fallback_body=_(
            "You have been assigned as handling editor for **{title}** ({reference}).\n\n"
            "Open it here: {detail_url}"
        ),
    )
    return "ok"


@shared_task(name="apps.submissions.tasks.send_reviewer_invitation")
def send_reviewer_invitation(assignment_id: int) -> str:
    """Send the double-blind review invitation with one-click links."""
    assignment = ReviewAssignment.objects.select_related(
        "reviewer", "round__submission__section"
    ).get(pk=assignment_id)
    submission = assignment.round.submission
    site = get_site_settings()
    accept_url = absolute_url(
        reverse("review:respond", kwargs={"token": assignment.access_token, "answer": "accept"})
    )
    decline_url = absolute_url(
        reverse("review:respond", kwargs={"token": assignment.access_token, "answer": "decline"})
    )
    send_templated_email(
        "reviewer_invite",
        to=[assignment.reviewer.email],
        context={
            "title": submission.title,
            "abstract": submission.abstract,
            "section": submission.section.name,
            "due_date": assignment.due_at.date().isoformat(),
            "accept_url": accept_url,
            "decline_url": decline_url,
            "journal": site.journal_name,
        },
        language=_language(assignment.reviewer),
        fallback_subject=_("Invitation to review for %(journal)s") % {"journal": site.journal_name},
        fallback_body=_(
            "Dear colleague,\n\nWe invite you to review the manuscript **{title}** for "
            "{journal} (section: {section}). Reviews are due by {due_date}.\n\n"
            "[Accept]({accept_url}) · [Decline]({decline_url})\n\n"
            "The review is double-blind: the manuscript contains no author information."
        ),
    )
    return "ok"


@shared_task(name="apps.submissions.tasks.send_review_thanks")
def send_review_thanks(assignment_id: int) -> str:
    """Thank a reviewer once their review is submitted."""
    assignment = ReviewAssignment.objects.select_related("reviewer", "round__submission").get(
        pk=assignment_id
    )
    send_templated_email(
        "reviewer_thanks",
        to=[assignment.reviewer.email],
        context={
            "title": assignment.round.submission.title,
            "certificate_url": absolute_url(reverse("review:certificate")),
        },
        language=_language(assignment.reviewer),
        fallback_subject=_("Thank you for your review"),
        fallback_body=_(
            "Thank you for reviewing **{title}**. Your work is essential to the journal.\n\n"
            "You can download a reviewer certificate here: {certificate_url}"
        ),
    )
    return "ok"


@shared_task(name="apps.submissions.tasks.send_decision_email")
def send_decision_email(decision_id: int) -> str:
    """Send the editorial decision letter to the submitting author."""
    decision = EditorialDecision.objects.select_related("submission__submitter").get(pk=decision_id)
    submission = decision.submission
    send_templated_email(
        "decision",
        to=[submission.submitter.email],
        context={
            "reference": submission.reference,
            "title": submission.title,
            "decision": decision.get_decision_display(),
            "letter": decision.letter,
            "dashboard_url": absolute_url(reverse("dashboard:home")),
        },
        language=_language(submission.submitter),
        fallback_subject=_("Decision on %(ref)s") % {"ref": submission.reference},
        fallback_body="{letter}",
    )
    decision.emailed_at = timezone.now()
    decision.save(update_fields=["emailed_at", "updated_at"])
    return "ok"


@shared_task(name="apps.submissions.tasks.notify_published")
def notify_published(submission_id: int) -> str:
    """Tell every author that their article is online."""
    submission = (
        Submission.objects.select_related("article")
        .prefetch_related("authors")
        .get(pk=submission_id)
    )
    article = submission.article
    if article is None:
        return "no article"
    recipients = {submission.submitter.email}
    recipients.update(a.email for a in submission.authors.all() if a.email)
    for email in recipients:
        send_templated_email(
            "published",
            to=[email],
            context={
                "title": article.title,
                "doi": article.doi,
                "url": article.canonical_url,
            },
            language=_language(submission.submitter),
            fallback_subject=_("Your article is published"),
            fallback_body=_("Your article **{title}** is now published.\n\nDOI: {doi}\nURL: {url}"),
        )
    return "ok"


@shared_task(name="apps.submissions.tasks.send_account_invitation")
def send_account_invitation(user_id: int) -> str:
    """Invite a newly created reviewer account to set a password."""
    from apps.accounts.models import User

    user = User.objects.get(pk=user_id)
    send_templated_email(
        "signup_verify",
        to=[user.email],
        context={"reset_url": absolute_url(reverse("account_reset_password"))},
        language=_language(user),
        fallback_subject=_("An account has been created for you"),
        fallback_body=_(
            "An editorial account has been created for you. Set your password here: {reset_url}"
        ),
    )
    return "ok"


@shared_task(name="apps.submissions.tasks.send_review_reminders")
def send_review_reminders() -> str:
    """Remind reviewers three days before, on, and seven days after the due date."""
    now = timezone.now()
    windows = [
        (now + timedelta(days=3), now + timedelta(days=4), "before"),
        (now - timedelta(days=1), now, "due"),
        (now - timedelta(days=8), now - timedelta(days=7), "overdue"),
    ]
    sent = 0
    for start, end, kind in windows:
        assignments = ReviewAssignment.objects.filter(
            status__in=[ReviewAssignment.Status.INVITED, ReviewAssignment.Status.ACCEPTED],
            due_at__gte=start,
            due_at__lt=end,
        ).select_related("reviewer", "round__submission")
        for assignment in assignments:
            send_templated_email(
                "reviewer_reminder",
                to=[assignment.reviewer.email],
                context={
                    "title": assignment.round.submission.title,
                    "due_date": assignment.due_at.date().isoformat(),
                    "review_url": absolute_url(assignment.get_absolute_url()),
                    "kind": kind,
                },
                language=_language(assignment.reviewer),
                fallback_subject=_("Reminder: review due %(date)s")
                % {"date": assignment.due_at.date().isoformat()},
                fallback_body=_(
                    "This is a reminder that your review of **{title}** is due on {due_date}.\n\n"
                    "Open the review form: {review_url}"
                ),
            )
            assignment.reminders_sent += 1
            assignment.last_reminder_at = now
            assignment.save(update_fields=["reminders_sent", "last_reminder_at", "updated_at"])
            sent += 1
    return f"{sent} reminders"


@shared_task(name="apps.submissions.tasks.flag_overdue_reviews")
def flag_overdue_reviews() -> str:
    """Mark accepted assignments whose due date has passed as overdue."""
    count = ReviewAssignment.objects.filter(
        status__in=[ReviewAssignment.Status.INVITED, ReviewAssignment.Status.ACCEPTED],
        due_at__lt=timezone.now(),
    ).update(status=ReviewAssignment.Status.OVERDUE)
    return f"{count} overdue"


@shared_task(name="apps.submissions.tasks.send_revision_reminders")
def send_revision_reminders() -> str:
    """Remind authors seven days before a revision deadline."""
    now = timezone.now()
    due_soon = RevisionRequest.objects.filter(
        submitted_at__isnull=True,
        reminder_sent_at__isnull=True,
        due_at__lte=now + timedelta(days=7),
        due_at__gte=now,
    ).select_related("submission__submitter")
    sent = 0
    for request_obj in due_soon:
        submission = request_obj.submission
        send_templated_email(
            "revision_reminder",
            to=[submission.submitter.email],
            context={
                "reference": submission.reference,
                "title": submission.title,
                "due_date": request_obj.due_at.date().isoformat(),
                "dashboard_url": absolute_url(reverse("dashboard:home")),
            },
            language=_language(submission.submitter),
            fallback_subject=_("Revision of %(ref)s due soon") % {"ref": submission.reference},
            fallback_body=_(
                "Your revision of **{title}** ({reference}) is due on {due_date}.\n\n"
                "Upload it here: {dashboard_url}"
            ),
        )
        request_obj.reminder_sent_at = now
        request_obj.save(update_fields=["reminder_sent_at", "updated_at"])
        sent += 1
    return f"{sent} reminders"


@shared_task(name="apps.submissions.tasks.send_proof_request")
def send_proof_request(submission_id: int) -> str:
    """Ask the corresponding author to approve the typeset proof."""
    submission = Submission.objects.select_related("submitter").get(pk=submission_id)
    send_templated_email(
        "proof_request",
        to=[submission.submitter.email],
        context={
            "reference": submission.reference,
            "title": submission.title,
            "dashboard_url": absolute_url(reverse("dashboard:home")),
            "deadline": (timezone.now() + timedelta(days=5)).date().isoformat(),
        },
        language=_language(submission.submitter),
        fallback_subject=_("Proof ready for %(ref)s") % {"ref": submission.reference},
        fallback_body=_(
            "The proof of **{title}** ({reference}) is ready for your approval.\n\n"
            "Please review it by {deadline}: {dashboard_url}"
        ),
    )
    return "ok"


@shared_task(name="apps.submissions.tasks.cleanup_stale_drafts")
def cleanup_stale_drafts(days: int = 180) -> str:
    """Delete abandoned draft submissions older than ``days``."""
    cutoff = timezone.now() - timedelta(days=days)
    stale = Submission.objects.filter(status="draft", last_activity_at__lt=cutoff)
    count = stale.count()
    stale.delete()
    logger.info("Deleted %s stale drafts older than %s days", count, days)
    return f"{count} drafts deleted"
