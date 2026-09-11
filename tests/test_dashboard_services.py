"""The dashboard's attention logic (apps/dashboard/services.py).

These tests fix the behaviour that makes the dashboard useful rather than
decorative: that something late is raised, that something recent is not, that a
manuscript is raised once however many ways it is late, and that a turnaround
figure is judged against the journal's target instead of being displayed bare.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.dashboard import services
from apps.submissions.models import (
    ReviewAssignment,
    ReviewRound,
    Submission,
    SubmissionStatus,
)

pytestmark = pytest.mark.django_db


def _age(submission: Submission, days: int, status: str) -> Submission:
    """Put ``submission`` into ``status`` and backdate its last activity."""
    moment = timezone.now() - timedelta(days=days)
    Submission.objects.filter(pk=submission.pk).update(
        status=status, last_activity_at=moment, submitted_at=moment
    )
    submission.refresh_from_db()
    return submission


def test_fresh_submission_is_not_raised(editor_user, submission) -> None:
    """A manuscript that arrived today is not a problem."""
    _age(submission, 0, SubmissionStatus.SUBMITTED)
    assert services.attention_items(editor_user) == []


def test_unscreened_submission_is_raised_after_the_threshold(editor_user, submission) -> None:
    """Past the screening threshold, an unscreened manuscript surfaces."""
    days = services.THRESHOLDS["screening"] + 3
    _age(submission, days, SubmissionStatus.SUBMITTED)

    items = services.attention_items(editor_user)

    assert len(items) == 1
    assert items[0].kind == "screening"
    assert items[0].days == days
    assert items[0].severity == services.WARNING


def test_submission_awaiting_decision_is_urgent(editor_user, submission) -> None:
    """A decision the editor owes the author is raised as late, not merely aging."""
    days = services.THRESHOLDS["decision_pending"] + 1
    _age(submission, days, SubmissionStatus.AWAITING_DECISION)

    item = services.attention_items(editor_user)[0]

    assert item.severity == services.DANGER
    assert item.is_late


def test_overdue_review_is_raised_with_the_reviewer_named(
    editor_user, submission, reviewers
) -> None:
    """An overdue review names the reviewer, so the editor can chase a person."""
    _age(submission, 30, SubmissionStatus.UNDER_REVIEW)
    round_ = ReviewRound.objects.create(submission=submission, number=1)
    ReviewAssignment.objects.create(
        round=round_,
        reviewer=reviewers[0],
        status=ReviewAssignment.Status.ACCEPTED,
        due_at=timezone.now() - timedelta(days=9),
    )

    items = services.attention_items(editor_user)
    overdue = [item for item in items if item.kind == "overdue_review"]

    assert len(overdue) == 1
    assert overdue[0].days == 9
    assert overdue[0].severity == services.DANGER
    assert reviewers[0].get_full_name() in overdue[0].extra["reviewer"]
    # Chasing a reviewer changes state, so it must not be a bare link.
    assert overdue[0].method == "post"


def test_a_manuscript_is_raised_once(editor_user, submission, reviewers) -> None:
    """Stalled *and* waiting on an overdue review is still one row."""
    _age(submission, 40, SubmissionStatus.UNDER_REVIEW)
    round_ = ReviewRound.objects.create(submission=submission, number=1)
    ReviewAssignment.objects.create(
        round=round_,
        reviewer=reviewers[0],
        status=ReviewAssignment.Status.ACCEPTED,
        due_at=timezone.now() - timedelta(days=12),
    )

    items = services.attention_items(editor_user)

    assert len(items) == 1
    # The more urgent reason wins.
    assert items[0].kind == "overdue_review"


def test_unanswered_invitation_is_raised(editor_user, submission, reviewers) -> None:
    """An invitation nobody answered stalls the manuscript just as surely."""
    _age(submission, 2, SubmissionStatus.UNDER_REVIEW)
    round_ = ReviewRound.objects.create(submission=submission, number=1)
    assignment = ReviewAssignment.objects.create(
        round=round_,
        reviewer=reviewers[0],
        status=ReviewAssignment.Status.INVITED,
        due_at=timezone.now() + timedelta(days=14),
    )
    ReviewAssignment.objects.filter(pk=assignment.pk).update(
        invited_at=timezone.now() - timedelta(days=services.THRESHOLDS["reviewer_no_response"] + 2)
    )

    items = services.attention_items(editor_user)

    assert [item.kind for item in items] == ["silent_invitation"]


def test_authors_see_no_editorial_attention_list(author_user, submission) -> None:
    """The attention list is an editorial tool and must not leak to authors."""
    _age(submission, 90, SubmissionStatus.AWAITING_DECISION)
    assert services.attention_items(author_user) == []


def test_items_are_ordered_worst_first(editor_user, section, author_user) -> None:
    """Late items precede aging ones, and the longest wait leads."""
    old = Submission.objects.create(
        title="Old", submitter=author_user, section=section, status=SubmissionStatus.SUBMITTED
    )
    urgent = Submission.objects.create(
        title="Urgent", submitter=author_user, section=section, status=SubmissionStatus.SUBMITTED
    )
    _age(old, 60, SubmissionStatus.SUBMITTED)
    _age(urgent, 20, SubmissionStatus.AWAITING_DECISION)

    items = services.attention_items(editor_user)

    assert [item.title for item in items] == ["Urgent", "Old"]


def test_queue_summary_reports_the_oldest_wait(editor_user, submission) -> None:
    """A queue carries the age of its oldest manuscript, not just a count."""
    _age(submission, 33, SubmissionStatus.SUBMITTED)

    summary = services.queue_summary(editor_user, [("new", "New", [SubmissionStatus.SUBMITTED])])

    assert summary[0]["count"] == 1
    assert summary[0]["oldest_days"] == 33
    assert summary[0]["severity"] == services.DANGER


def test_empty_queue_is_never_flagged(editor_user) -> None:
    """An empty queue is neutral however the arithmetic falls out."""
    summary = services.queue_summary(editor_user, [("new", "New", [SubmissionStatus.SUBMITTED])])

    assert summary[0]["count"] == 0
    assert summary[0]["severity"] == services.NEUTRAL


@pytest.mark.parametrize(
    ("median", "expected"),
    [
        (services.FIRST_DECISION_TARGET_DAYS - 1, "success"),
        (services.FIRST_DECISION_TARGET_DAYS + 1, services.DANGER),
        (None, services.NEUTRAL),
    ],
)
def test_turnaround_is_judged_against_the_target(median, expected) -> None:
    """The median is scored against the journal's target, not shown bare."""
    cards = services.kpi_scorecard(
        {"median_days_to_first_decision": median, "acceptance_rate": 40.0}
    )

    assert cards[0]["severity"] == expected


def test_scorecard_is_empty_without_data() -> None:
    """No KPI window means no cards, rather than a row of dashes."""
    assert services.kpi_scorecard(None) == []


def test_summary_reports_the_true_total_when_truncated(editor_user, section, author_user) -> None:
    """The cap must be visible: three shown out of five late, not "three late"."""
    for index in range(5):
        submission = Submission.objects.create(
            title=f"Late {index}",
            submitter=author_user,
            section=section,
            status=SubmissionStatus.AWAITING_DECISION,
        )
        _age(submission, 20 + index, SubmissionStatus.AWAITING_DECISION)

    items, total = services.attention_summary(editor_user, limit=3)

    assert len(items) == 3
    assert total == 5


# --- author progress -------------------------------------------------------


def test_draft_shows_zero_progress(submission) -> None:
    """A draft has not started the journey."""
    _age(submission, 0, SubmissionStatus.DRAFT)
    progress = services.submission_progress(submission)
    assert progress.percent == 0
    assert all(step.state == "todo" for step in progress.steps)


@pytest.mark.parametrize(
    ("status", "percent", "current"),
    [
        (SubmissionStatus.SUBMITTED, 17, "submitted"),
        (SubmissionStatus.SCREENING, 33, "screening"),
        (SubmissionStatus.UNDER_REVIEW, 50, "review"),
        (SubmissionStatus.REVISION_REQUESTED, 50, "review"),
        (SubmissionStatus.AWAITING_DECISION, 67, "decision"),
        (SubmissionStatus.COPYEDITING, 83, "production"),
        (SubmissionStatus.READY_TO_PUBLISH, 83, "production"),
    ],
)
def test_progress_maps_statuses_onto_six_milestones(submission, status, percent, current) -> None:
    """Sixteen internal states read as six steps and a percentage."""
    _age(submission, 1, status)
    progress = services.submission_progress(submission)

    assert progress.percent == percent
    assert not progress.is_terminal
    assert not progress.is_published
    states = {step.key: step.state for step in progress.steps}
    assert states[current] == "current"
    reached = [s.key for s in progress.steps].index(current)
    assert all(step.state == "done" for step in progress.steps[:reached])
    assert all(step.state == "todo" for step in progress.steps[reached + 1 :])


def test_published_is_complete(submission) -> None:
    """Published means every milestone done and 100 %."""
    _age(submission, 1, SubmissionStatus.PUBLISHED)
    progress = services.submission_progress(submission)

    assert progress.percent == 100
    assert progress.is_published
    assert all(step.state == "done" for step in progress.steps)


def test_rejection_keeps_the_progress_it_reached(submission, reviewers) -> None:
    """A rejected manuscript stops where it stopped rather than snapping to zero."""
    _age(submission, 1, SubmissionStatus.REJECTED)
    ReviewRound.objects.create(submission=submission, number=1)
    progress = services.submission_progress(submission)

    assert progress.is_terminal
    assert progress.percent == 50  # reached peer review, then rejected
    assert str(progress.terminal_label) == "Rejected"


def test_desk_rejection_stops_at_screening(submission) -> None:
    """Rejected without a review round: the bar stops at screening."""
    _age(submission, 1, SubmissionStatus.REJECTED)
    progress = services.submission_progress(submission)

    assert progress.is_terminal
    assert progress.percent == 33
