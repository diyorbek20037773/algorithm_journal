"""Dashboard data services.

The editorial dashboard exists to answer one question: *what needs me today?*
A list of counts cannot answer it — six queues of five manuscripts each look
identical whether every one arrived this morning or has been sitting for a
month. So everything here is built around elapsed time: how long a manuscript
has waited, how far past its deadline a review is, and whether that is inside
the journal's stated targets.

Thresholds are policy, not physics, so they live in one place and are stated in
days. The turnaround target follows the published medians for economics and
finance journals — the American Finance Association reports a median of 47 days
to first decision across all submissions and 64 days for those that survive
desk screening — so 60 days is a defensible line for a new journal to hold
itself to.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from django.db.models import Min
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.submissions.models import ReviewAssignment, Submission, SubmissionStatus

if TYPE_CHECKING:
    from apps.accounts.models import User

#: Days after which each situation stops being normal and starts being a problem.
THRESHOLDS: dict[str, int] = {
    "screening": 5,
    "reviewer_no_response": 7,
    "decision_pending": 14,
    "stalled": 21,
}

#: Median days from submission to first decision the journal holds itself to.
FIRST_DECISION_TARGET_DAYS = 60

#: Severity names map onto the design system's colour tokens.
DANGER = "danger"
WARNING = "warning"
NEUTRAL = "accent"


@dataclass(slots=True)
class AttentionItem:
    """One thing an editor should deal with, and why it is being raised."""

    kind: str
    severity: str
    submission_pk: int
    title: str
    reference: str
    reason: Any
    days: int
    action_label: Any
    action_url: str
    #: "post" when the action changes state and must be a form, "get" for a link.
    method: str = "get"
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def is_late(self) -> bool:
        """True when the item is past its threshold rather than approaching it."""
        return self.severity == DANGER


def _days_since(moment) -> int:
    """Whole days between ``moment`` and now, floored at zero."""
    if moment is None:
        return 0
    return max((timezone.now() - moment).days, 0)


def overdue_reviews(user: User) -> list[AttentionItem]:
    """Accepted reviews that are past their due date.

    This is the single most useful signal on an editorial dashboard: a review
    nobody chases is the usual reason a manuscript sits for months.
    """
    submissions = Submission.objects.for_editor(user)
    assignments = (
        ReviewAssignment.objects.filter(
            round__submission__in=submissions,
            status__in=[ReviewAssignment.Status.ACCEPTED, ReviewAssignment.Status.OVERDUE],
            due_at__lt=timezone.now(),
        )
        .select_related("round__submission", "reviewer")
        .order_by("due_at")
    )
    items = []
    for assignment in assignments:
        submission = assignment.round.submission
        late = _days_since(assignment.due_at)
        items.append(
            AttentionItem(
                kind="overdue_review",
                severity=DANGER,
                submission_pk=submission.pk,
                title=submission.title,
                reference=submission.reference or "",
                reason=_("Review overdue"),
                days=late,
                action_label=_("Send reminder"),
                action_url=reverse("dashboard:remind_reviewer", args=[assignment.pk]),
                method="post",
                extra={
                    "reviewer": assignment.reviewer.get_full_name() or assignment.reviewer.email
                },
            )
        )
    return items


def silent_invitations(user: User) -> list[AttentionItem]:
    """Reviewer invitations that have gone unanswered for too long.

    Editorial Manager gives these their own queue for good reason: an invitation
    nobody declined is indistinguishable from one nobody read, and the manuscript
    is stalled either way.
    """
    cutoff = timezone.now() - timedelta(days=THRESHOLDS["reviewer_no_response"])
    submissions = Submission.objects.for_editor(user)
    assignments = (
        ReviewAssignment.objects.filter(
            round__submission__in=submissions,
            status=ReviewAssignment.Status.INVITED,
            responded_at__isnull=True,
            invited_at__lt=cutoff,
        )
        .select_related("round__submission", "reviewer")
        .order_by("invited_at")
    )
    return [
        AttentionItem(
            kind="silent_invitation",
            severity=WARNING,
            submission_pk=assignment.round.submission.pk,
            title=assignment.round.submission.title,
            reference=assignment.round.submission.reference or "",
            reason=_("Invitation unanswered"),
            days=_days_since(assignment.invited_at),
            action_label=_("Find another reviewer"),
            action_url=reverse("dashboard:reviewer_finder", args=[assignment.round.submission.pk]),
            extra={"reviewer": assignment.reviewer.get_full_name() or assignment.reviewer.email},
        )
        for assignment in assignments
    ]


def _submissions_waiting(
    user: User, statuses: list[str], threshold_key: str, reason: Any, severity: str
) -> list[AttentionItem]:
    """Submissions sitting in ``statuses`` longer than the matching threshold."""
    cutoff = timezone.now() - timedelta(days=THRESHOLDS[threshold_key])
    queryset = (
        Submission.objects.for_editor(user)
        .filter(status__in=statuses, last_activity_at__lt=cutoff)
        .with_related()
        .order_by("last_activity_at")
    )
    return [
        AttentionItem(
            kind=threshold_key,
            severity=severity,
            submission_pk=submission.pk,
            title=submission.title,
            reference=submission.reference or "",
            reason=reason,
            days=_days_since(submission.last_activity_at),
            action_label=_("Open"),
            action_url=reverse("dashboard:submission_detail", args=[submission.pk]),
        )
        for submission in queryset
    ]


def attention_items(user: User, limit: int = 8) -> list[AttentionItem]:
    """Everything that is late, worst first.

    Ordering is by severity and then by how long the item has waited, so the
    manuscript that has been ignored longest is always at the top.
    """
    if not user.is_editorial_staff:
        return []
    items = [
        *overdue_reviews(user),
        *_submissions_waiting(
            user,
            [SubmissionStatus.AWAITING_DECISION],
            "decision_pending",
            _("Awaiting your decision"),
            DANGER,
        ),
        *_submissions_waiting(
            user,
            [SubmissionStatus.SUBMITTED, SubmissionStatus.SCREENING],
            "screening",
            _("Not yet screened"),
            WARNING,
        ),
        *silent_invitations(user),
        *_submissions_waiting(
            user,
            [SubmissionStatus.UNDER_REVIEW, SubmissionStatus.RESUBMITTED],
            "stalled",
            _("No activity"),
            WARNING,
        ),
    ]
    items.sort(key=lambda item: (item.severity != DANGER, -item.days))
    # One manuscript, one row: a paper that is both stalled and waiting on an
    # overdue review should be raised once, under the more urgent reason.
    seen: set[int] = set()
    unique = []
    for item in items:
        if item.submission_pk in seen:
            continue
        seen.add(item.submission_pk)
        unique.append(item)
    return unique[:limit]


def queue_summary(
    user: User, definitions: list[tuple[str, Any, list[str]]]
) -> list[dict[str, Any]]:
    """Queue counts with the age of the oldest manuscript in each.

    A count on its own hides the only thing that matters. Twelve manuscripts
    that all arrived today are a good morning; two that arrived in March are an
    apology owed to two authors.
    """
    queryset = Submission.objects.for_editor(user)
    summary = []
    for key, label, statuses in definitions:
        rows = queryset.filter(status__in=statuses)
        oldest = rows.aggregate(first=Min("last_activity_at"))["first"]
        waiting = _days_since(oldest) if oldest else 0
        threshold = THRESHOLDS["stalled"]
        if waiting >= threshold:
            severity = DANGER
        elif waiting >= threshold // 2:
            severity = WARNING
        else:
            severity = NEUTRAL
        summary.append(
            {
                "key": key,
                "label": label,
                "count": rows.count(),
                "oldest_days": waiting,
                "severity": severity if rows.exists() else NEUTRAL,
                "items": list(rows.with_related()[:3]),
            }
        )
    return summary


def kpi_scorecard(kpis: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Turnaround figures paired with the target they are judged against.

    A number with no baseline is decoration. Each card carries the journal's
    target and whether the current figure meets it.
    """
    if not kpis:
        return []
    median = kpis.get("median_days_to_first_decision")
    cards = [
        {
            "label": _("Median days to first decision"),
            "value": median if median is not None else "—",
            "target": _("target ≤ %(days)s days") % {"days": FIRST_DECISION_TARGET_DAYS},
            "severity": (
                NEUTRAL
                if median is None
                else DANGER
                if median > FIRST_DECISION_TARGET_DAYS
                else "success"
            ),
        },
        {
            "label": _("Acceptance rate"),
            "value": f"{kpis['acceptance_rate']}%" if kpis.get("acceptance_rate") else "—",
            "target": _("share of decided manuscripts accepted"),
            "severity": NEUTRAL,
        },
    ]
    return cards
