"""Tests for the editorial workflow finite-state machine."""

from __future__ import annotations

import datetime as dt

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from apps.core.models import AuditLog
from apps.submissions import workflow
from apps.submissions.models import (
    EditorialDecision,
    Review,
    ReviewAssignment,
    ReviewRound,
    RevisionRequest,
    SubmissionStatus,
)
from apps.submissions.services import invite_reviewer, submit_review

pytestmark = pytest.mark.django_db


def test_submit_assigns_reference_and_date(submission, author_user, site_settings) -> None:
    """Submitting stamps the date and allocates ARER-YYYY-NNNN."""
    workflow.perform(submission, "submit", author_user)
    submission.refresh_from_db()
    assert submission.status == SubmissionStatus.SUBMITTED
    assert submission.submitted_at is not None
    assert submission.reference.startswith("ARER-")
    assert len(submission.reference.rsplit("-", 1)[1]) == 4


def test_submit_auto_assigns_the_only_section_editor(
    submission, author_user, editor_user, site_settings
) -> None:
    """A section with exactly one editor gets that editor assigned."""
    workflow.perform(submission, "submit", author_user)
    submission.refresh_from_db()
    assert submission.assigned_editor == editor_user


def test_transition_writes_an_audit_entry(submission, author_user, site_settings) -> None:
    """Every transition is recorded in the audit log (SPEC §15.16)."""
    workflow.perform(submission, "submit", author_user)
    entry = AuditLog.objects.filter(action=AuditLog.Action.WORKFLOW).first()
    assert entry is not None
    assert entry.changes["transition"] == "submit"
    assert entry.changes["to"] == SubmissionStatus.SUBMITTED


def test_transition_adds_a_system_message(submission, author_user, site_settings) -> None:
    """A system message documents the state change."""
    workflow.perform(submission, "submit", author_user)
    messages = [
        m.body for d in submission.discussions.all() for m in d.messages.all() if m.is_system
    ]
    assert any("Status changed" in m for m in messages)


def test_illegal_transition_is_rejected(submission, editor_user, site_settings) -> None:
    """A transition whose source state does not match raises."""
    with pytest.raises(ValidationError):
        workflow.perform(submission, "accept", editor_user)


def test_author_cannot_run_an_editor_transition(
    submission, author_user, editor_user, site_settings
) -> None:
    """Role checks stop authors from screening their own manuscript."""
    workflow.perform(submission, "submit", author_user)
    submission.refresh_from_db()
    with pytest.raises(PermissionDenied):
        workflow.perform(submission, "assign_editor", author_user)


def test_send_to_review_requires_a_similarity_result(
    submission, author_user, editor_user, site_settings
) -> None:
    """The plagiarism gate blocks review until a result exists (SPEC §5.6)."""
    workflow.perform(submission, "submit", author_user)
    workflow.perform(submission, "assign_editor", editor_user, editor=editor_user)
    with pytest.raises(ValidationError):
        workflow.perform(submission, "send_to_review", editor_user)


def test_send_to_review_blocks_above_the_threshold(
    submission, author_user, editor_user, site_settings
) -> None:
    """Similarity above the threshold requires an EIC override."""
    workflow.perform(submission, "submit", author_user)
    workflow.perform(submission, "assign_editor", editor_user, editor=editor_user)
    submission.similarity_percent = 42.0
    submission.save()
    with pytest.raises(ValidationError):
        workflow.perform(submission, "send_to_review", editor_user)

    submission.similarity_override_reason = "Overlap is entirely in the standard methods section."
    submission.save()
    workflow.perform(submission, "send_to_review", editor_user)
    submission.refresh_from_db()
    assert submission.status == SubmissionStatus.UNDER_REVIEW


def test_send_to_review_opens_a_round(submission, author_user, editor_user, site_settings) -> None:
    """A review round is created when the manuscript goes out for review."""
    workflow.perform(submission, "submit", author_user)
    workflow.perform(submission, "assign_editor", editor_user, editor=editor_user)
    submission.similarity_percent = 8.0
    submission.save()
    workflow.perform(submission, "send_to_review", editor_user)
    submission.refresh_from_db()
    assert submission.current_round == 1
    assert ReviewRound.objects.filter(submission=submission, number=1).exists()


def _to_under_review(submission, author_user, editor_user):
    """Helper: move a draft all the way to ``under_review``."""
    workflow.perform(submission, "submit", author_user)
    workflow.perform(submission, "assign_editor", editor_user, editor=editor_user)
    submission.similarity_percent = 7.5
    submission.save()
    workflow.perform(submission, "send_to_review", editor_user)
    submission.refresh_from_db()
    return submission.latest_round


def test_two_completed_reviews_move_to_awaiting_decision(
    submission, author_user, editor_user, reviewers, site_settings
) -> None:
    """When every accepted reviewer has reported, the state advances."""
    round_obj = _to_under_review(submission, author_user, editor_user)
    for reviewer in reviewers[:2]:
        assignment = invite_reviewer(round_obj, reviewer, invited_by=editor_user)
        assignment.status = ReviewAssignment.Status.ACCEPTED
        assignment.save()
        review = Review(
            assignment=assignment,
            recommendation=Review.Recommendation.MINOR,
            scores={key: 4 for key, _ in Review.SCORE_FIELDS},
            comments_to_authors="A" * 200,
        )
        submit_review(assignment, review)

    submission.refresh_from_db()
    assert submission.status == SubmissionStatus.AWAITING_DECISION


def test_minor_revision_creates_a_thirty_day_request(
    submission, author_user, editor_user, reviewers, site_settings, settings
) -> None:
    """A minor revision decision sets a 30-day deadline."""
    round_obj = _to_under_review(submission, author_user, editor_user)
    invite_reviewer(round_obj, reviewers[0], invited_by=editor_user)
    submission.status = SubmissionStatus.AWAITING_DECISION
    submission.save()

    workflow.record_decision(
        submission,
        decision=EditorialDecision.Decision.MINOR_REVISION,
        user=editor_user,
        letter="Please revise.",
    )
    submission.refresh_from_db()
    request = RevisionRequest.objects.get(submission=submission)
    assert submission.status == SubmissionStatus.REVISION_REQUESTED
    assert not request.is_major
    assert 29 <= (request.due_at - timezone.now()).days <= 30


def test_major_revision_creates_a_sixty_day_request(
    submission, author_user, editor_user, site_settings
) -> None:
    """A major revision decision sets a 60-day deadline."""
    _to_under_review(submission, author_user, editor_user)
    submission.status = SubmissionStatus.AWAITING_DECISION
    submission.save()
    workflow.record_decision(
        submission,
        decision=EditorialDecision.Decision.MAJOR_REVISION,
        user=editor_user,
        letter="Substantial revision required.",
    )
    request = RevisionRequest.objects.get(submission=submission)
    assert request.is_major
    assert 59 <= (request.due_at - timezone.now()).days <= 60


def test_resubmission_closes_the_revision_request(
    submission, author_user, editor_user, site_settings
) -> None:
    """Uploading a revision records the response and advances the state."""
    _to_under_review(submission, author_user, editor_user)
    submission.status = SubmissionStatus.AWAITING_DECISION
    submission.save()
    workflow.record_decision(
        submission,
        decision=EditorialDecision.Decision.MINOR_REVISION,
        user=editor_user,
        letter="Please revise.",
    )
    submission.refresh_from_db()
    workflow.perform(
        submission, "resubmit", author_user, response_letter="We addressed every point."
    )
    submission.refresh_from_db()
    request = RevisionRequest.objects.get(submission=submission)
    assert submission.status == SubmissionStatus.RESUBMITTED
    assert request.submitted_at is not None
    assert "every point" in request.response_letter


def test_accept_creates_the_production_checklist(
    submission, author_user, editor_user, site_settings
) -> None:
    """Acceptance stamps the date and builds the production tasks."""
    _to_under_review(submission, author_user, editor_user)
    submission.status = SubmissionStatus.AWAITING_DECISION
    submission.save()
    workflow.record_decision(
        submission,
        decision=EditorialDecision.Decision.ACCEPT,
        user=editor_user,
        letter="Accepted.",
    )
    submission.refresh_from_db()
    assert submission.status == SubmissionStatus.ACCEPTED
    assert submission.accepted_at is not None
    assert submission.production_tasks.count() == 6


def test_reject_cancels_outstanding_invitations(
    submission, author_user, editor_user, reviewers, site_settings
) -> None:
    """Rejecting cancels invitations that are still open."""
    round_obj = _to_under_review(submission, author_user, editor_user)
    assignment = invite_reviewer(round_obj, reviewers[0], invited_by=editor_user)
    submission.status = SubmissionStatus.AWAITING_DECISION
    submission.save()
    workflow.record_decision(
        submission,
        decision=EditorialDecision.Decision.REJECT,
        user=editor_user,
        letter="Not accepted.",
    )
    assignment.refresh_from_db()
    assert assignment.status == ReviewAssignment.Status.CANCELLED


def test_withdraw_records_the_reason(submission, author_user, site_settings) -> None:
    """The author may withdraw before acceptance."""
    workflow.perform(submission, "submit", author_user)
    workflow.perform(submission, "withdraw", author_user, reason="Data problem found.")
    submission.refresh_from_db()
    assert submission.status == SubmissionStatus.WITHDRAWN
    assert submission.is_withdrawn
    assert "Data problem" in submission.withdraw_reason


def test_decision_is_audited(submission, author_user, editor_user, site_settings) -> None:
    """Decisions appear in the audit log (SPEC §15.16)."""
    _to_under_review(submission, author_user, editor_user)
    submission.status = SubmissionStatus.AWAITING_DECISION
    submission.save()
    workflow.record_decision(
        submission,
        decision=EditorialDecision.Decision.ACCEPT,
        user=editor_user,
        letter="Accepted.",
    )
    assert AuditLog.objects.filter(action=AuditLog.Action.DECISION).exists()


def test_available_transitions_depend_on_role(
    submission, author_user, editor_user, site_settings
) -> None:
    """Authors and editors see different actions."""
    workflow.perform(submission, "submit", author_user)
    submission.refresh_from_db()
    author_actions = {t.name for t in workflow.available_transitions(submission, author_user)}
    editor_actions = {t.name for t in workflow.available_transitions(submission, editor_user)}
    assert "withdraw" in author_actions
    assert "assign_editor" in editor_actions
    assert "assign_editor" not in author_actions


def test_reviewer_cannot_be_an_author(submission, author_user, editor_user, site_settings) -> None:
    """The submitter cannot be invited to review their own manuscript."""
    round_obj = _to_under_review(submission, author_user, editor_user)
    with pytest.raises(ValidationError):
        invite_reviewer(round_obj, author_user, invited_by=editor_user)


def test_duplicate_invitation_is_rejected(
    submission, author_user, editor_user, reviewers, site_settings
) -> None:
    """The same reviewer cannot be invited twice to one round."""
    round_obj = _to_under_review(submission, author_user, editor_user)
    invite_reviewer(round_obj, reviewers[0], invited_by=editor_user)
    with pytest.raises(ValidationError):
        invite_reviewer(round_obj, reviewers[0], invited_by=editor_user)


def test_review_due_date_defaults_to_21_days(
    submission, author_user, editor_user, reviewers, site_settings
) -> None:
    """Reviews are due 21 days after the invitation (D6)."""
    round_obj = _to_under_review(submission, author_user, editor_user)
    assignment = invite_reviewer(round_obj, reviewers[0], invited_by=editor_user)
    assert 20 <= (assignment.due_at - timezone.now()).days <= 21


def test_overdue_detection(submission, author_user, editor_user, reviewers, site_settings) -> None:
    """An accepted assignment past its due date is overdue."""
    round_obj = _to_under_review(submission, author_user, editor_user)
    assignment = invite_reviewer(round_obj, reviewers[0], invited_by=editor_user)
    assignment.status = ReviewAssignment.Status.ACCEPTED
    assignment.due_at = timezone.now() - dt.timedelta(days=2)
    assignment.save()
    assert assignment.is_overdue
