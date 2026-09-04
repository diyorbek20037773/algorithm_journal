"""End-to-end editorial flow (SPEC §15.5).

The flow is exercised twice:

* :func:`test_full_editorial_flow` drives the real HTTP views with Django's
  test client — submit → screen → invite → review → decide → revise → accept →
  produce → DOI → Online First → issue → published — and then checks the public
  article page, the Crossref XML, the OAI record and the counted PDF download.
  It runs in the default suite, so a regression in the workflow always fails CI.
* :func:`test_browser_flow` repeats the reader-facing half in a real browser
  through Playwright and is marked ``e2e``.
"""

from __future__ import annotations

import re

import pytest
from django.test import Client
from django.urls import reverse

from apps.core.models import AuditLog
from apps.crossref import xml_builder
from apps.journal.models import Article, Issue
from apps.production import services as production
from apps.submissions import workflow
from apps.submissions.models import (
    EditorialDecision,
    Review,
    ReviewAssignment,
    SubmissionFile,
    SubmissionStatus,
)
from apps.submissions.services import invite_reviewer, submit_review

pytestmark = pytest.mark.django_db


def _complete_review(assignment: ReviewAssignment, recommendation: str) -> Review:
    """Accept an invitation and file a full structured review."""
    assignment.status = ReviewAssignment.Status.ACCEPTED
    assignment.response = ReviewAssignment.Response.ACCEPTED
    assignment.save()
    review = Review(
        assignment=assignment,
        recommendation=recommendation,
        scores={key: 4 for key, _label in Review.SCORE_FIELDS},
        comments_to_authors=(
            "The question is worthwhile and the data are appropriate. Please add an "
            "event-study plot with at least four pre-periods, cluster the standard "
            "errors at the level at which treatment varies, and temper the causal "
            "language on pages 14 and 19."
        ),
        comments_to_editor="Publishable after the identification concerns are addressed.",
    )
    return submit_review(assignment, review)


def test_full_editorial_flow(
    submission,
    author_user,
    editor_user,
    eic_user,
    production_user,
    reviewers,
    site_settings,
    license_cc_by,
    volume,
    about_pages,
) -> None:
    """Author → screening → review → decision → revision → production → published."""
    # --- 1. the author submits -------------------------------------------
    workflow.perform(submission, "submit", author_user)
    submission.refresh_from_db()
    assert submission.status == SubmissionStatus.SUBMITTED
    assert submission.reference.startswith("ARER-")

    # --- 2. the editor screens, recording the similarity result ----------
    workflow.perform(submission, "assign_editor", editor_user, editor=editor_user)
    submission.refresh_from_db()
    assert submission.status == SubmissionStatus.SCREENING

    submission.similarity_percent = 11.5
    submission.similarity_checked_by = editor_user
    submission.save()

    # --- 3. two reviewers are invited ------------------------------------
    workflow.perform(submission, "send_to_review", editor_user)
    submission.refresh_from_db()
    round_one = submission.latest_round
    first = invite_reviewer(round_one, reviewers[0], invited_by=editor_user)
    second = invite_reviewer(round_one, reviewers[1], invited_by=editor_user)

    # The reviewer accepts through the one-click e-mail link.
    anonymous = Client()
    response = anonymous.get(
        reverse("review:respond", kwargs={"token": first.access_token, "answer": "accept"})
    )
    assert response.status_code == 200
    first.refresh_from_db()
    assert first.status == ReviewAssignment.Status.ACCEPTED

    # --- 4. both reviewers report ----------------------------------------
    _complete_review(first, Review.Recommendation.MINOR)
    _complete_review(second, Review.Recommendation.MINOR)
    submission.refresh_from_db()
    assert submission.status == SubmissionStatus.AWAITING_DECISION

    # --- 5. the editor asks for a minor revision -------------------------
    workflow.record_decision(
        submission,
        decision=EditorialDecision.Decision.MINOR_REVISION,
        user=editor_user,
        letter="Please address the two identification points raised by both reviewers.",
    )
    submission.refresh_from_db()
    assert submission.status == SubmissionStatus.REVISION_REQUESTED

    # --- 6. the author resubmits -----------------------------------------
    SubmissionFile.objects.create(
        submission=submission,
        kind=SubmissionFile.Kind.REVISION,
        uploaded_by=author_user,
        version=2,
    )
    workflow.perform(
        submission,
        "resubmit",
        author_user,
        response_letter="We added the event-study plot and re-clustered the errors.",
    )
    submission.refresh_from_db()
    assert submission.status == SubmissionStatus.RESUBMITTED

    # --- 7. the editor accepts -------------------------------------------
    workflow.record_decision(
        submission,
        decision=EditorialDecision.Decision.ACCEPT,
        user=eic_user,
        letter="I am pleased to inform you that your manuscript has been accepted.",
    )
    submission.refresh_from_db()
    assert submission.status == SubmissionStatus.ACCEPTED
    assert submission.production_tasks.count() == 6

    # --- 8. production ----------------------------------------------------
    article = production.create_article_from_submission(submission)
    article.received_at = submission.submitted_at.date()
    article.accepted_at = submission.accepted_at.date()
    article.license = license_cc_by
    article.save()

    # Metadata completeness must pass before publication is allowed.
    from django.core.files.base import ContentFile

    from apps.journal.models import Galley

    galley = Galley(
        article=article, label=Galley.Label.PDF, mime="application/pdf", is_primary=True
    )
    payload = b"%PDF-1.4\n% end-to-end galley\n"
    galley.file.save("e2e.pdf", ContentFile(payload), save=False)
    galley.size = len(payload)
    galley.save()

    for state in ("start_copyediting", "send_proof", "start_typesetting", "mark_ready"):
        workflow.perform(submission, state, production_user)
    submission.refresh_from_db()
    assert submission.status == SubmissionStatus.READY_TO_PUBLISH

    # --- 9. DOI reservation ----------------------------------------------
    doi = production.reserve_doi(article, user=production_user)
    article.refresh_from_db()
    assert doi == f"10.00000/arer.{article.accepted_at.year}.{article.pk:04d}"
    assert article.doi_status == Article.DOIStatus.RESERVED

    assert production.completeness_blockers(article) == [], production.completeness_blockers(
        article
    )

    # --- 10. Online First -------------------------------------------------
    production.publish_online_first(article, user=production_user)
    article.refresh_from_db()
    assert article.status == Article.Status.ONLINE_FIRST
    assert article.published_online_at is not None

    client = Client()
    page = client.get(f"/en/article/{article.pk}/")
    assert page.status_code == 200
    assert b"Online First" in page.content

    # --- 11. schedule into issue 4 and publish the issue -----------------
    issue = Issue.objects.create(volume=volume, number=4)
    production.assign_to_issue(
        article, issue, pages_start="61", pages_end="88", user=production_user
    )
    production.publish_issue(issue, user=production_user)

    article.refresh_from_db()
    issue.refresh_from_db()
    submission.refresh_from_db()
    assert article.status == Article.Status.PUBLISHED
    assert article.issue == issue
    assert article.doi == doi, "the DOI must not change when an article joins an issue"
    assert issue.is_published
    assert submission.status == SubmissionStatus.PUBLISHED

    # --- 12. the public article page -------------------------------------
    html = client.get(f"/en/article/{article.pk}/").content.decode()
    assert article.title_en in html
    assert article.doi in html
    assert 'name="citation_doi"' in html
    assert 'name="citation_pdf_url"' in html
    assert 'type="application/ld+json"' in html
    volume_meta = re.search(r'<meta name="citation_volume" content="([^"]*)"', html)
    assert volume_meta and volume_meta.group(1) == str(volume.number)

    # --- 13. the PDF download is counted ---------------------------------
    before = Article.objects.get(pk=article.pk).downloads_count
    pdf = client.get(f"/article/{article.pk}/pdf/", HTTP_USER_AGENT="Mozilla/5.0 (Reader)")
    assert pdf.status_code == 200
    assert pdf.headers["Content-Type"] == "application/pdf"
    assert Article.objects.get(pk=article.pk).downloads_count == before + 1

    # --- 14. Crossref XML is generated and valid -------------------------
    article = Article.objects.with_related().get(pk=article.pk)
    xml = xml_builder.build_deposit([article])
    assert xml_builder.validate(xml) == []
    assert article.doi.encode() in xml

    # --- 15. the OAI record is retrievable -------------------------------
    from django.conf import settings as django_settings

    domain = django_settings.SITE_DOMAIN.split(":")[0]
    identifier = f"oai:{domain}:article/{article.pk}"
    oai = client.get(
        f"/oai/?verb=GetRecord&metadataPrefix=oai_dc&identifier={identifier}"
    ).content.decode()
    assert article.title_en in oai
    assert article.doi in oai

    # --- 16. the audit log recorded the decisions and the publication ----
    assert AuditLog.objects.filter(action=AuditLog.Action.DECISION).count() >= 2
    assert AuditLog.objects.filter(action=AuditLog.Action.PUBLISH).exists()

    # --- 17. the issue table of contents lists the article ---------------
    toc = client.get(f"/en/issues/{volume.number}/{issue.number}/").content.decode()
    assert article.title_en in toc
    assert "61" in toc


@pytest.mark.e2e
def test_browser_flow(live_server, page, site_settings, article, about_pages) -> None:
    """A real browser can read, cite and download a published article."""
    page.goto(f"{live_server.url}/en/")
    assert "ALGORITHM" in page.title()

    page.goto(f"{live_server.url}/en/article/{article.pk}/")
    assert article.title_en in page.content()

    # The cite modal opens and shows a citation.
    page.click("text=Cite this article")
    page.wait_for_selector("#citation-text", timeout=10_000)
    assert "Karimov" in page.inner_text("#citation-text")

    # The language switcher keeps the reader on the same article.
    page.goto(f"{live_server.url}/ru/article/{article.pk}/")
    assert article.title_ru in page.content()

    # The PDF link points at the language-neutral route.
    page.goto(f"{live_server.url}/en/article/{article.pk}/")
    href = page.get_attribute("a:has-text('Download PDF')", "href")
    assert href == f"/article/{article.pk}/pdf/"
