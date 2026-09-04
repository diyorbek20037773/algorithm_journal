"""Production stage tests: DOI, completeness, stamping and publication."""

from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError

from apps.core.models import AuditLog
from apps.journal.models import Article, Issue
from apps.production import services

pytestmark = pytest.mark.django_db


def test_reserve_doi_is_issue_independent(article, site_settings) -> None:
    """The DOI suffix uses the year and the article ID, never the issue (D8)."""
    article.doi = ""
    article.save()
    doi = services.reserve_doi(article)
    assert doi == f"10.00000/arer.{article.accepted_at.year}.{article.pk:04d}"
    article.refresh_from_db()
    assert article.doi_status == Article.DOIStatus.RESERVED


def test_reserve_doi_is_idempotent(article, site_settings) -> None:
    """Reserving twice keeps the original DOI."""
    original = article.doi
    assert services.reserve_doi(article) == original


def test_completeness_flags_missing_metadata(article, site_settings) -> None:
    """A missing Russian title is reported as a blocker."""
    article.title_ru = ""
    article.save()
    blockers = services.completeness_blockers(article)
    assert any("Russian" in b for b in blockers)


def test_complete_article_has_no_blockers(article, site_settings) -> None:
    """The fully populated fixture passes the completeness check."""
    assert services.completeness_blockers(article) == []


def test_orcid_is_only_a_warning(article, site_settings) -> None:
    """Missing ORCID is a warning, not a publication blocker."""
    article.authors.update(orcid="")
    checks = services.metadata_completeness(article)
    orcid_check = next(c for c in checks if "ORCID" in str(c["label"]))
    assert orcid_check["level"] == "warning"
    assert services.completeness_blockers(article) == []


def test_publish_online_first(online_first_article, article, site_settings) -> None:
    """Publishing Online First sets the date, the DOI and the status."""
    target = article
    target.status = Article.Status.DRAFT
    target.issue = None
    target.published_at = None
    target.save()

    services.publish_online_first(target)
    target.refresh_from_db()
    assert target.status == Article.Status.ONLINE_FIRST
    assert target.published_online_at is not None
    assert target.doi
    assert AuditLog.objects.filter(action=AuditLog.Action.PUBLISH).exists()


def test_publish_online_first_blocked_by_incomplete_metadata(article, site_settings) -> None:
    """Publication is refused while required metadata is missing."""
    article.status = Article.Status.DRAFT
    article.abstract_uz = ""
    article.save()
    with pytest.raises(ValidationError):
        services.publish_online_first(article)


def test_assign_to_issue_keeps_the_doi(article, volume, site_settings) -> None:
    """Moving an Online First article into an issue does not change its DOI."""
    original_doi = article.doi
    article.status = Article.Status.ONLINE_FIRST
    article.issue = None
    article.save()

    issue = Issue.objects.create(volume=volume, number=5)
    services.assign_to_issue(article, issue, pages_start="101", pages_end="126")
    article.refresh_from_db()
    assert article.issue == issue
    assert article.pages_start == "101"
    assert article.doi == original_doi


def test_publish_issue_publishes_every_article(article, site_settings) -> None:
    """Publishing an issue moves its articles to ``published``."""
    issue = article.issue
    issue.is_published = False
    issue.save()
    article.status = Article.Status.DRAFT
    article.save()

    services.publish_issue(issue)
    issue.refresh_from_db()
    article.refresh_from_db()
    assert issue.is_published
    assert issue.is_current
    assert article.status == Article.Status.PUBLISHED
    assert article.published_at is not None


def test_publish_empty_issue_is_refused(volume, site_settings) -> None:
    """An issue with no articles cannot be published."""
    issue = Issue.objects.create(volume=volume, number=9)
    with pytest.raises(ValidationError):
        services.publish_issue(issue)


def test_pdf_stamping_adds_header_and_footer(article, site_settings) -> None:
    """Stamping rewrites the galley and keeps the unstamped original."""
    import io as _io

    from django.core.files.base import ContentFile
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    buffer = _io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.drawString(72, 720, "Body text of the manuscript.")
    pdf.showPage()
    pdf.save()

    galley = article.primary_galley
    galley.file.save("original.pdf", ContentFile(buffer.getvalue()), save=True)

    assert services.stamp_article_pdf(article) is True
    galley.refresh_from_db()
    assert galley.original_file

    from pypdf import PdfReader

    galley.file.open("rb")
    text = PdfReader(galley.file).pages[0].extract_text()
    galley.file.close()
    assert article.doi in text
    assert "CC BY 4.0" in text


def test_create_article_from_submission(
    submission, author_user, site_settings, license_cc_by
) -> None:
    """Accepted submissions become draft articles with their metadata copied."""
    from apps.submissions.models import SubmissionStatus

    submission.status = SubmissionStatus.ACCEPTED
    submission.save()
    created = services.create_article_from_submission(submission)
    assert created.title_en == submission.title_en
    assert created.abstract_en == submission.abstract_en
    assert created.authors.count() == submission.authors.count()
    assert created.keywords.count() >= 5
    assert created.jel_codes.count() == submission.jel_codes.count()
    # Idempotent.
    assert services.create_article_from_submission(submission).pk == created.pk


def test_production_tasks_are_created_once(submission, author_user, site_settings) -> None:
    """The production checklist has one task per stage."""
    services.create_production_tasks(submission)
    services.create_production_tasks(submission)
    assert submission.production_tasks.count() == 6
