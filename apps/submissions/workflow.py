"""Hand-written finite-state machine for the editorial workflow.

Every transition performs, in order: a permission check, the state change with
timestamps, an :class:`~apps.core.models.AuditLog` entry, a system message in
the submission's discussion thread, and asynchronous e-mail notification.

The transition table below is the single source of truth for what may follow
what (SPEC §5.3).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.accounts.models import Role
from apps.core.models import AuditLog
from apps.core.services import log_action
from apps.submissions.models import (
    Discussion,
    DiscussionMessage,
    EditorialDecision,
    ReviewAssignment,
    ReviewRound,
    RevisionRequest,
    Submission,
    SubmissionStatus,
)

logger = logging.getLogger(__name__)

EDITOR_ROLES = (Role.SECTION_EDITOR, Role.EDITOR_IN_CHIEF, Role.ADMIN)
EIC_ROLES = (Role.EDITOR_IN_CHIEF, Role.ADMIN)
PRODUCTION_ROLES = (Role.PRODUCTION_EDITOR, Role.EDITOR_IN_CHIEF, Role.ADMIN)


@dataclass(frozen=True)
class Transition:
    """One legal move through the workflow."""

    name: str
    sources: tuple[str, ...]
    target: str
    roles: tuple[str, ...]
    label: str


TRANSITIONS: dict[str, Transition] = {
    t.name: t
    for t in [
        Transition("submit", (SubmissionStatus.DRAFT,), SubmissionStatus.SUBMITTED, (), _("Submit")),
        Transition(
            "assign_editor",
            (SubmissionStatus.SUBMITTED,),
            SubmissionStatus.SCREENING,
            EDITOR_ROLES,
            _("Assign editor"),
        ),
        Transition(
            "desk_reject",
            (SubmissionStatus.SCREENING, SubmissionStatus.SUBMITTED),
            SubmissionStatus.REJECTED,
            EDITOR_ROLES,
            _("Desk reject"),
        ),
        Transition(
            "send_to_review",
            (SubmissionStatus.SCREENING, SubmissionStatus.RESUBMITTED),
            SubmissionStatus.UNDER_REVIEW,
            EDITOR_ROLES,
            _("Send to review"),
        ),
        Transition(
            "reviews_complete",
            (SubmissionStatus.UNDER_REVIEW,),
            SubmissionStatus.AWAITING_DECISION,
            EDITOR_ROLES,
            _("All reviews received"),
        ),
        Transition(
            "request_minor_revision",
            (SubmissionStatus.AWAITING_DECISION,),
            SubmissionStatus.REVISION_REQUESTED,
            EDITOR_ROLES,
            _("Request minor revision"),
        ),
        Transition(
            "request_major_revision",
            (SubmissionStatus.AWAITING_DECISION,),
            SubmissionStatus.REVISION_REQUESTED,
            EDITOR_ROLES,
            _("Request major revision"),
        ),
        Transition(
            "resubmit",
            (SubmissionStatus.REVISION_REQUESTED,),
            SubmissionStatus.RESUBMITTED,
            (),
            _("Submit revision"),
        ),
        Transition(
            "accept",
            (SubmissionStatus.AWAITING_DECISION, SubmissionStatus.RESUBMITTED),
            SubmissionStatus.ACCEPTED,
            EDITOR_ROLES,
            _("Accept"),
        ),
        Transition(
            "reject",
            (SubmissionStatus.AWAITING_DECISION, SubmissionStatus.RESUBMITTED),
            SubmissionStatus.REJECTED,
            EDITOR_ROLES,
            _("Reject"),
        ),
        Transition(
            "start_copyediting",
            (SubmissionStatus.ACCEPTED,),
            SubmissionStatus.COPYEDITING,
            PRODUCTION_ROLES,
            _("Start copyediting"),
        ),
        Transition(
            "send_proof",
            (SubmissionStatus.COPYEDITING,),
            SubmissionStatus.AUTHOR_PROOF,
            PRODUCTION_ROLES,
            _("Send proof to author"),
        ),
        Transition(
            "start_typesetting",
            (SubmissionStatus.AUTHOR_PROOF,),
            SubmissionStatus.TYPESETTING,
            PRODUCTION_ROLES,
            _("Start typesetting"),
        ),
        Transition(
            "mark_ready",
            (SubmissionStatus.TYPESETTING,),
            SubmissionStatus.READY_TO_PUBLISH,
            PRODUCTION_ROLES,
            _("Mark ready to publish"),
        ),
        Transition(
            "publish_online_first",
            (SubmissionStatus.READY_TO_PUBLISH,),
            SubmissionStatus.PUBLISHED_ONLINE_FIRST,
            PRODUCTION_ROLES,
            _("Publish Online First"),
        ),
        Transition(
            "publish",
            (SubmissionStatus.READY_TO_PUBLISH, SubmissionStatus.PUBLISHED_ONLINE_FIRST),
            SubmissionStatus.PUBLISHED,
            PRODUCTION_ROLES,
            _("Publish in issue"),
        ),
        Transition(
            "withdraw",
            (
                SubmissionStatus.DRAFT,
                SubmissionStatus.SUBMITTED,
                SubmissionStatus.SCREENING,
                SubmissionStatus.UNDER_REVIEW,
                SubmissionStatus.AWAITING_DECISION,
                SubmissionStatus.REVISION_REQUESTED,
                SubmissionStatus.RESUBMITTED,
            ),
            SubmissionStatus.WITHDRAWN,
            (),
            _("Withdraw"),
        ),
    ]
}


class TransitionError(ValidationError):
    """Raised when a workflow transition is not allowed."""


def can(submission: Submission, name: str, user) -> bool:
    """True when ``user`` may run transition ``name`` on ``submission`` now."""
    transition = TRANSITIONS.get(name)
    if transition is None or submission.status not in transition.sources:
        return False
    if not transition.roles:
        # Author-driven transitions: only the submitter (or an editor).
        return submission.submitter_id == getattr(user, "pk", None) or user.has_role(*EDITOR_ROLES)
    return user.has_role(*transition.roles)


def available_transitions(submission: Submission, user) -> list[Transition]:
    """Every transition the user may currently perform."""
    return [t for name, t in TRANSITIONS.items() if can(submission, name, user)]


@transaction.atomic
def perform(
    submission: Submission,
    name: str,
    user,
    *,
    request=None,
    comment: str = "",
    **kwargs: Any,
) -> Submission:
    """Execute a workflow transition, or raise :class:`TransitionError`."""
    transition = TRANSITIONS.get(name)
    if transition is None:
        raise TransitionError(_("Unknown transition: %(name)s") % {"name": name})
    if submission.status not in transition.sources:
        raise TransitionError(
            _("Cannot %(action)s a submission that is %(status)s.")
            % {"action": transition.label, "status": submission.get_status_display()}
        )
    if not can(submission, name, user):
        raise PermissionDenied(_("You may not perform this action."))

    previous = submission.status
    handler = globals().get(f"_on_{name}")
    if handler is not None:
        handler(submission, user, **kwargs)

    submission.status = transition.target
    submission.last_activity_at = timezone.now()
    submission.save()

    log_action(
        AuditLog.Action.WORKFLOW,
        actor=user,
        target=f"Submission {submission.reference or submission.pk}",
        changes={"transition": name, "from": previous, "to": submission.status},
        request=request,
    )
    system_message(
        submission,
        _("Status changed from %(old)s to %(new)s.")
        % {
            "old": dict(SubmissionStatus.choices)[previous],
            "new": submission.get_status_display(),
        }
        + (f" {comment}" if comment else ""),
        user=user,
    )
    _notify(submission, name, user)
    return submission


# ---------------------------------------------------------------------------
# Transition side effects
# ---------------------------------------------------------------------------
def _on_submit(submission: Submission, user, **kwargs) -> None:
    """Stamp the submission date, assign a reference, auto-assign an editor."""
    submission.submitted_at = timezone.now()
    if not submission.reference:
        submission.reference = submission.build_reference()
    editors = list(submission.section.editors.all())
    if len(editors) == 1 and submission.assigned_editor_id is None:
        submission.assigned_editor = editors[0]


def _on_assign_editor(submission: Submission, user, editor=None, **kwargs) -> None:
    """Record the handling editor chosen by the editor-in-chief."""
    if editor is not None:
        submission.assigned_editor = editor
        submission.assigned_by = user


def _on_send_to_review(submission: Submission, user, **kwargs) -> None:
    """Open a new review round once the plagiarism gate is satisfied."""
    from apps.core.services import get_site_settings

    site = get_site_settings()
    override = bool(submission.similarity_override_reason)
    if submission.similarity_percent is None and not override:
        raise TransitionError(
            _("A similarity check result is required before sending to review.")
        )
    if (
        submission.similarity_percent is not None
        and submission.similarity_percent > site.similarity_threshold
        and not override
    ):
        raise TransitionError(
            _("Similarity is above the %(threshold)s%% threshold; an EIC override is required.")
            % {"threshold": site.similarity_threshold}
        )
    submission.current_round += 1
    ReviewRound.objects.get_or_create(
        submission=submission, number=submission.current_round, defaults={"status": ReviewRound.Status.OPEN}
    )


def _on_request_minor_revision(submission: Submission, user, **kwargs) -> None:
    """Create a 30-day revision request."""
    _create_revision_request(submission, is_major=False)


def _on_request_major_revision(submission: Submission, user, **kwargs) -> None:
    """Create a 60-day revision request."""
    _create_revision_request(submission, is_major=True)


def _create_revision_request(submission: Submission, *, is_major: bool) -> RevisionRequest:
    """Persist a revision request with the policy due date."""
    days = settings.MAJOR_REVISION_DUE_DAYS if is_major else settings.MINOR_REVISION_DUE_DAYS
    round_obj = submission.latest_round
    if round_obj is not None and round_obj.status == ReviewRound.Status.OPEN:
        round_obj.status = ReviewRound.Status.CLOSED
        round_obj.closed_at = timezone.now()
        round_obj.save(update_fields=["status", "closed_at", "updated_at"])
    return RevisionRequest.objects.create(
        submission=submission,
        round=round_obj,
        is_major=is_major,
        due_at=timezone.now() + timedelta(days=days),
    )


def _on_resubmit(submission: Submission, user, response_letter: str = "", **kwargs) -> None:
    """Close the open revision request when the author uploads a revision."""
    request_obj = submission.revision_requests.filter(submitted_at__isnull=True).first()
    if request_obj is not None:
        request_obj.submitted_at = timezone.now()
        request_obj.response_letter = response_letter
        request_obj.save(update_fields=["submitted_at", "response_letter", "updated_at"])


def _on_accept(submission: Submission, user, **kwargs) -> None:
    """Stamp acceptance and create the production checklist."""
    from apps.production.services import create_production_tasks

    submission.accepted_at = timezone.now()
    round_obj = submission.latest_round
    if round_obj is not None and round_obj.status == ReviewRound.Status.OPEN:
        round_obj.status = ReviewRound.Status.CLOSED
        round_obj.closed_at = timezone.now()
        round_obj.save(update_fields=["status", "closed_at", "updated_at"])
    create_production_tasks(submission)


def _on_withdraw(submission: Submission, user, reason: str = "", **kwargs) -> None:
    """Record the withdrawal reason and cancel outstanding review work."""
    submission.is_withdrawn = True
    submission.withdraw_reason = reason
    ReviewAssignment.objects.filter(
        round__submission=submission,
        status__in=[ReviewAssignment.Status.INVITED, ReviewAssignment.Status.ACCEPTED],
    ).update(status=ReviewAssignment.Status.CANCELLED)


def _on_reject(submission: Submission, user, **kwargs) -> None:
    """Cancel outstanding review assignments on rejection."""
    ReviewAssignment.objects.filter(
        round__submission=submission,
        status__in=[ReviewAssignment.Status.INVITED, ReviewAssignment.Status.ACCEPTED],
    ).update(status=ReviewAssignment.Status.CANCELLED)


def _on_desk_reject(submission: Submission, user, **kwargs) -> None:
    """Nothing extra beyond the decision record."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def system_message(submission: Submission, body: str, *, user=None) -> DiscussionMessage:
    """Append a system message to the submission's editorial thread."""
    discussion, _created = Discussion.objects.get_or_create(
        submission=submission,
        visibility=Discussion.Visibility.EDITORS_ONLY,
        defaults={"subject": _("Workflow history"), "created_by": user},
    )
    return DiscussionMessage.objects.create(
        discussion=discussion, author=user, body=body, is_system=True
    )


def record_decision(
    submission: Submission,
    *,
    decision: str,
    user,
    letter: str = "",
    request=None,
) -> EditorialDecision:
    """Persist an :class:`EditorialDecision` and run the matching transition."""
    mapping = {
        EditorialDecision.Decision.DESK_REJECT: "desk_reject",
        EditorialDecision.Decision.SEND_TO_REVIEW: "send_to_review",
        EditorialDecision.Decision.ACCEPT: "accept",
        EditorialDecision.Decision.MINOR_REVISION: "request_minor_revision",
        EditorialDecision.Decision.MAJOR_REVISION: "request_major_revision",
        EditorialDecision.Decision.REJECT: "reject",
        EditorialDecision.Decision.RESUBMIT: "reject",
    }
    transition_name = mapping[decision]
    record = EditorialDecision.objects.create(
        submission=submission,
        round=submission.latest_round,
        decided_by=user,
        decision=decision,
        letter=letter,
    )
    submission.decision_letter = letter
    perform(submission, transition_name, user, request=request)
    log_action(
        AuditLog.Action.DECISION,
        actor=user,
        target=f"Submission {submission.reference or submission.pk}",
        changes={"decision": decision},
        request=request,
    )
    from apps.submissions.tasks import send_decision_email

    send_decision_email.delay(record.pk)
    return record


def _notify(submission: Submission, transition_name: str, user) -> None:
    """Queue the notification e-mails belonging to a transition."""
    from apps.submissions import tasks

    try:
        if transition_name == "submit":
            tasks.notify_submission_received.delay(submission.pk)
        elif transition_name == "assign_editor":
            tasks.notify_editor_assigned.delay(submission.pk)
        elif transition_name in {"publish", "publish_online_first"}:
            tasks.notify_published.delay(submission.pk)
    except Exception:  # pragma: no cover - broker outage must not block the UI
        logger.exception("Could not queue notification for %s", transition_name)
