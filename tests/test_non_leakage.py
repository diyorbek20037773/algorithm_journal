"""Double-blind guarantees: reviewers and authors must not learn identities."""

from __future__ import annotations

import pytest
from django.test import Client

from apps.submissions import workflow
from apps.submissions.models import Review, ReviewAssignment, SubmissionFile
from apps.submissions.services import invite_reviewer, submit_review

pytestmark = pytest.mark.django_db


def _under_review(submission, author_user, editor_user, reviewers):
    """Move a submission to review and invite two reviewers."""
    workflow.perform(submission, "submit", author_user)
    workflow.perform(submission, "assign_editor", editor_user, editor=editor_user)
    submission.similarity_percent = 6.0
    submission.save()
    workflow.perform(submission, "send_to_review", editor_user)
    submission.refresh_from_db()
    round_obj = submission.latest_round
    first = invite_reviewer(round_obj, reviewers[0], invited_by=editor_user)
    second = invite_reviewer(round_obj, reviewers[1], invited_by=editor_user)
    for assignment in (first, second):
        assignment.status = ReviewAssignment.Status.ACCEPTED
        assignment.save()
    return first, second


def test_reviewer_page_contains_no_author_identity(
    submission, author_user, editor_user, reviewers, site_settings
) -> None:
    """The reviewer's manuscript page leaks no author name, e-mail or affiliation."""
    first, _second = _under_review(submission, author_user, editor_user, reviewers)
    client = Client()
    client.force_login(reviewers[0])
    html = client.get(f"/en/review/assignment/{first.pk}/").content.decode()

    author = submission.authors.first()
    for secret in (
        author.family_name,
        author.given_name,
        author.email,
        author.affiliation,
        author.orcid,
        author_user.email,
        submission.cover_letter[:30] if submission.cover_letter else "cover-letter-marker",
    ):
        assert secret not in html, f"reviewer page leaked {secret!r}"


def test_reviewer_form_contains_no_author_identity(
    submission, author_user, editor_user, reviewers, site_settings
) -> None:
    """The review form is equally anonymised."""
    first, _second = _under_review(submission, author_user, editor_user, reviewers)
    client = Client()
    client.force_login(reviewers[0])
    html = client.get(f"/en/review/assignment/{first.pk}/form/").content.decode()
    author = submission.authors.first()
    assert author.family_name not in html
    assert author.email not in html


def test_reviewer_sees_no_other_reviewer(
    submission, author_user, editor_user, reviewers, site_settings
) -> None:
    """One reviewer never learns who the other reviewers are."""
    first, second = _under_review(submission, author_user, editor_user, reviewers)
    client = Client()
    client.force_login(reviewers[0])
    html = client.get(f"/en/review/assignment/{first.pk}/").content.decode()
    assert second.reviewer.email not in html
    assert (
        second.reviewer.last_name not in html or second.reviewer.last_name == reviewers[0].last_name
    )


def test_reviewer_cannot_download_the_title_page(
    submission, author_user, editor_user, reviewers, site_settings
) -> None:
    """Only anonymised files are downloadable by reviewers."""
    _under_review(submission, author_user, editor_user, reviewers)
    title_page = submission.files.get(kind=SubmissionFile.Kind.TITLE_PAGE)
    manuscript = submission.files.get(kind=SubmissionFile.Kind.MANUSCRIPT_ANON)
    assert not title_page.is_visible_to_reviewers
    assert manuscript.is_visible_to_reviewers

    client = Client()
    client.force_login(reviewers[0])
    assert client.get(f"/en/review/file/{title_page.pk}/").status_code == 403
    assert client.get(f"/en/review/file/{manuscript.pk}/").status_code == 200


def test_author_view_contains_no_reviewer_identity(
    submission, author_user, editor_user, reviewers, site_settings
) -> None:
    """The author's submission page never names a reviewer."""
    first, _second = _under_review(submission, author_user, editor_user, reviewers)
    review = Review(
        assignment=first,
        recommendation=Review.Recommendation.MINOR,
        scores={key: 4 for key, _ in Review.SCORE_FIELDS},
        comments_to_authors="B" * 200,
        comments_to_editor="Confidential note for the editor only.",
    )
    submit_review(first, review)

    client = Client()
    client.force_login(author_user)
    html = client.get(f"/en/dashboard/submission/{submission.pk}/?tab=summary").content.decode()
    for reviewer in reviewers:
        assert reviewer.email not in html
    assert "Confidential note for the editor only." not in html


def test_author_cannot_open_the_reviewers_tab(
    submission, author_user, editor_user, reviewers, site_settings
) -> None:
    """The reviewers and reviews tabs render nothing for a non-editor."""
    _under_review(submission, author_user, editor_user, reviewers)
    client = Client()
    client.force_login(author_user)
    for tab in ("reviewers", "reviews", "decision"):
        html = client.get(f"/en/dashboard/submission/{submission.pk}/?tab={tab}").content.decode()
        for reviewer in reviewers:
            assert reviewer.email not in html


def test_author_cannot_open_the_reviewer_finder(
    submission, author_user, editor_user, site_settings
) -> None:
    """Only editors may search for reviewers."""
    workflow.perform(submission, "submit", author_user)
    client = Client()
    client.force_login(author_user)
    assert client.get(f"/en/dashboard/submission/{submission.pk}/reviewers/").status_code == 403


def test_api_exposes_only_public_data(client_anon, submission, article, site_settings) -> None:
    """The JSON API never exposes submissions or unpublished work."""
    payload = client_anon.get("/api/v1/articles/").json()
    titles = [row["title"] for row in payload["results"]]
    assert article.title_en in titles
    assert submission.title_en not in titles


def test_oai_exposes_only_published_records(
    client_anon, submission, article, site_settings
) -> None:
    """OAI-PMH lists published articles only."""
    body = client_anon.get("/oai/?verb=ListRecords&metadataPrefix=oai_dc").content.decode()
    assert article.title_en in body
    assert submission.title_en not in body


def test_other_users_cannot_read_a_submission(
    submission, author_user, editor_user, reviewers, site_settings
) -> None:
    """A reviewer who is not assigned cannot open the submission page."""
    workflow.perform(submission, "submit", author_user)
    client = Client()
    client.force_login(reviewers[2])
    assert client.get(f"/en/dashboard/submission/{submission.pk}/").status_code == 403
