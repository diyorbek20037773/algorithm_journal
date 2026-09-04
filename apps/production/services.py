"""Production services: stages, DOI reservation, publication and issue building."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext as _

from apps.core.models import AuditLog
from apps.core.services import get_site_settings, log_action
from apps.journal.models import Article, Author, Issue, Keyword, License, Reference
from apps.submissions.models import (
    ProductionTask,
    Submission,
    SubmissionFile,
    SubmissionStatus,
)

logger = logging.getLogger(__name__)


def create_production_tasks(submission: Submission) -> list[ProductionTask]:
    """Create the production checklist for a newly accepted manuscript."""
    tasks = []
    for offset, stage in enumerate(ProductionTask.STAGE_ORDER):
        task, _created = ProductionTask.objects.get_or_create(
            submission=submission,
            stage=stage,
            defaults={"due_at": timezone.now() + timedelta(days=7 * (offset + 1))},
        )
        tasks.append(task)
    return tasks


@transaction.atomic
def create_article_from_submission(submission: Submission) -> Article:
    """Materialise a draft :class:`Article` from an accepted submission.

    Copies the multilingual metadata, authors, keywords, JEL codes and
    references.  Idempotent: calling it twice returns the same article.
    """
    if submission.article_id:
        return submission.article

    metadata = submission.metadata or {}
    article = Article(
        section=submission.section,
        article_type=submission.article_type,
        language=submission.language,
        status=Article.Status.DRAFT,
        received_at=submission.submitted_at.date() if submission.submitted_at else None,
        accepted_at=submission.accepted_at.date() if submission.accepted_at else None,
        funding_statement=submission.funding_statement,
        conflict_of_interest_statement=submission.conflict_of_interest_statement
        or "The authors declare no conflict of interest.",
        data_availability_statement=submission.data_availability_statement,
        ai_use_statement=submission.ai_use_statement
        or "No generative AI tools were used in the preparation of this article.",
        license=License.default(),
        submission=submission,
    )
    for language in ("en", "uz", "uz_cyrl", "ru"):
        title = metadata.get("title", {}).get(language.replace("_", "-"))
        abstract = metadata.get("abstract", {}).get(language.replace("_", "-"))
        if title:
            setattr(article, f"title_{language}", title)
        if abstract:
            setattr(article, f"abstract_{language}", abstract)
    if not article.title_en:
        article.title_en = submission.title
    article.title = article.title_en
    if not article.abstract_en:
        article.abstract_en = submission.abstract
    article.abstract = article.abstract_en
    article.save()

    for order, author in enumerate(submission.authors.order_by("order"), start=1):
        Author.objects.create(
            article=article,
            order=order,
            user=author.user,
            given_name=author.given_name,
            family_name=author.family_name,
            email=author.email,
            is_corresponding=author.is_corresponding,
            orcid=author.orcid,
            orcid_verified=author.orcid_verified,
            affiliation=author.affiliation,
            affiliation_ror=author.affiliation_ror,
            city=author.city,
            country=author.country,
            credit_roles=author.credit_roles,
        )

    _copy_keywords(article, metadata.get("keywords", {}), submission.keywords_list)

    article.jel_codes.set(submission.jel_codes.all())

    for order, line in enumerate(_reference_lines(submission), start=1):
        Reference.objects.create(article=article, order=order, raw_text=line)

    submission.article = article
    submission.save(update_fields=["article", "updated_at"])
    return article


def _copy_keywords(article: Article, keywords: dict[str, list[str]], fallback: list[str]) -> None:
    """Attach one :class:`Keyword` per concept, carrying every language.

    The wizard stores parallel lists per language, so the lists are aligned by
    index: position *i* of the English list is the same keyword as position *i*
    of the Uzbek and Russian lists.  Creating a separate row per language would
    push the article past the 5–8 keyword policy.
    """
    english = keywords.get("en") or fallback
    article.keywords.clear()
    for position, name_en in enumerate(english):
        slug = slugify(name_en)[:130] or f"kw-{article.pk}-{position}"
        keyword, _created = Keyword.objects.get_or_create(slug=slug)
        keyword.name_en = name_en
        for code in ("uz", "uz-cyrl", "ru"):
            values = keywords.get(code) or []
            if position < len(values):
                setattr(keyword, f"name_{code.replace('-', '_')}", values[position])
        keyword.name = name_en
        keyword.save()
        article.keywords.add(keyword)


def _reference_lines(submission: Submission) -> list[str]:
    """Split the reference list captured in the submission metadata."""
    raw = (submission.metadata or {}).get("references", "")
    if isinstance(raw, list):
        return [line.strip() for line in raw if line.strip()]
    return [line.strip() for line in str(raw).splitlines() if line.strip()]


def reserve_doi(article: Article, *, user=None, request=None) -> str:
    """Reserve the immutable, issue-independent DOI for an article (D8)."""
    if article.doi:
        return article.doi
    site = get_site_settings()
    prefix = site.doi_prefix or settings.DOI_PREFIX
    year = (article.accepted_at or timezone.now().date()).year
    article.doi = f"{prefix}/arer.{year}.{article.pk:04d}"
    article.doi_status = Article.DOIStatus.RESERVED
    article.save(update_fields=["doi", "doi_status", "updated_at"])
    log_action(
        AuditLog.Action.WORKFLOW,
        actor=user,
        target=f"Article {article.pk}",
        changes={"doi": article.doi, "status": "reserved"},
        request=request,
    )
    return article.doi


#: Metadata a completeness check requires before publication (SPEC §16).
REQUIRED_METADATA: list[tuple[str, str]] = [
    ("title_en", _("Title (English)")),
    ("title_uz", _("Title (Uzbek)")),
    ("title_ru", _("Title (Russian)")),
    ("abstract_en", _("Abstract (English)")),
    ("abstract_uz", _("Abstract (Uzbek)")),
    ("abstract_ru", _("Abstract (Russian)")),
    ("conflict_of_interest_statement", _("Conflict of interest statement")),
    ("ai_use_statement", _("AI use statement")),
]


def metadata_completeness(article: Article) -> list[dict[str, Any]]:
    """Return a red/green checklist of the mandatory article metadata."""
    checks: list[dict[str, Any]] = []
    for field, label in REQUIRED_METADATA:
        checks.append(
            {"label": label, "ok": bool(getattr(article, field, "")), "level": "required"}
        )

    authors = article.author_list()
    checks.append({"label": _("At least one author"), "ok": bool(authors), "level": "required"})
    checks.append(
        {
            "label": _("Every author has an affiliation with country"),
            "ok": bool(authors) and all(a.affiliation and a.country for a in authors),
            "level": "required",
        }
    )
    checks.append(
        {
            "label": _("Corresponding author with e-mail"),
            "ok": any(a.is_corresponding and a.email for a in authors),
            "level": "required",
        }
    )
    checks.append(
        {
            "label": _("ORCID iD for every author"),
            "ok": bool(authors) and all(a.orcid for a in authors),
            "level": "warning",
        }
    )
    keyword_count = article.keywords.count()
    checks.append(
        {
            "label": _("5–8 keywords"),
            "ok": settings.KEYWORDS_MIN <= keyword_count <= settings.KEYWORDS_MAX,
            "level": "required",
        }
    )
    jel_count = article.jel_codes.count()
    checks.append(
        {
            "label": _("1–5 JEL codes"),
            "ok": settings.JEL_MIN <= jel_count <= settings.JEL_MAX,
            "level": "required",
        }
    )
    checks.append({"label": _("DOI assigned"), "ok": bool(article.doi), "level": "required"})
    checks.append(
        {
            "label": _("Primary PDF galley"),
            "ok": article.primary_galley is not None,
            "level": "required",
        }
    )
    checks.append(
        {
            "label": _("At least 10 references"),
            "ok": article.references.count() >= 10,
            "level": "warning",
        }
    )
    checks.append(
        {"label": _("Licence"), "ok": article.license_id is not None, "level": "required"}
    )
    checks.append(
        {"label": _("Received date"), "ok": article.received_at is not None, "level": "required"}
    )
    checks.append(
        {"label": _("Accepted date"), "ok": article.accepted_at is not None, "level": "required"}
    )
    return checks


def completeness_blockers(article: Article) -> list[str]:
    """Labels of the failing required metadata checks."""
    return [
        str(check["label"])
        for check in metadata_completeness(article)
        if check["level"] == "required" and not check["ok"]
    ]


@transaction.atomic
def publish_online_first(article: Article, *, user=None, request=None) -> Article:
    """Publish an article ahead of its issue and register the DOI."""
    blockers = completeness_blockers(article)
    if blockers:
        raise ValidationError(_("Cannot publish: %(items)s") % {"items": ", ".join(blockers)})
    reserve_doi(article, user=user, request=request)
    article.status = Article.Status.ONLINE_FIRST
    article.published_online_at = article.published_online_at or timezone.now().date()
    article.save(update_fields=["status", "published_online_at", "doi", "doi_status", "updated_at"])

    stamp_article_pdf(article)

    submission = article.submission
    if submission is not None:
        submission.status = SubmissionStatus.PUBLISHED_ONLINE_FIRST
        submission.save(update_fields=["status", "updated_at"])

    log_action(
        AuditLog.Action.PUBLISH,
        actor=user,
        target=f"Article {article.pk}",
        changes={"mode": "online_first", "doi": article.doi},
        request=request,
    )
    invalidate_public_caches()
    _queue_deposit(article)
    return article


@transaction.atomic
def publish_issue(issue: Issue, *, user=None, request=None) -> Issue:
    """Publish an issue and everything scheduled into it."""
    articles = list(Article.objects.filter(issue=issue).with_related())
    if not articles:
        raise ValidationError(_("The issue has no articles."))

    problems: list[str] = []
    for article in articles:
        blockers = completeness_blockers(article)
        if blockers:
            problems.append(f"#{article.pk}: {', '.join(blockers)}")
    if problems:
        raise ValidationError(
            _("Some articles are incomplete: %(items)s") % {"items": "; ".join(problems)}
        )

    issue.is_published = True
    issue.published_at = issue.published_at or timezone.now().date()
    issue.is_current = True
    issue.save()

    for article in articles:
        reserve_doi(article, user=user, request=request)
        article.status = Article.Status.PUBLISHED
        article.published_at = article.published_at or issue.published_at
        article.save(update_fields=["status", "published_at", "doi", "doi_status", "updated_at"])
        stamp_article_pdf(article)
        submission = article.submission
        if submission is not None:
            submission.status = SubmissionStatus.PUBLISHED
            submission.save(update_fields=["status", "updated_at"])
            from apps.submissions.tasks import notify_published

            notify_published.delay(submission.pk)
        _queue_deposit(article)

    log_action(
        AuditLog.Action.PUBLISH,
        actor=user,
        target=f"Issue {issue.pk}",
        changes={"issue": issue.label, "articles": len(articles)},
        request=request,
    )
    invalidate_public_caches()
    return issue


def assign_to_issue(
    article: Article,
    issue: Issue,
    *,
    pages_start: str = "",
    pages_end: str = "",
    article_number: int | None = None,
    user=None,
) -> Article:
    """Schedule an article into an issue and record its pagination."""
    article.issue = issue
    article.pages_start = pages_start or article.pages_start
    article.pages_end = pages_end or article.pages_end
    if article_number is not None:
        article.article_number = article_number
    elif article.article_number is None:
        article.article_number = (
            Article.objects.filter(issue=issue).exclude(pk=article.pk).count() + 1
        )
    article.save(
        update_fields=["issue", "pages_start", "pages_end", "article_number", "updated_at"]
    )
    if article.status in {Article.Status.ONLINE_FIRST, Article.Status.PUBLISHED} and article.doi:
        # Volume/issue/pages changed: re-stamp the PDF and update the DOI record.
        stamp_article_pdf(article)
        _queue_deposit(article, update=True)
    return article


def stamp_article_pdf(article: Article) -> bool:
    """Apply the running header/footer and PDF metadata to the primary galley."""
    from apps.production.pdf_stamp import stamp_galley

    galley = article.primary_galley
    if galley is None:
        return False
    try:
        return stamp_galley(article, galley)
    except Exception:  # pragma: no cover - malformed PDFs must not block publication
        logger.exception("Could not stamp PDF for article %s", article.pk)
        return False


def _queue_deposit(article: Article, *, update: bool = False) -> None:
    """Queue a Crossref deposit for the article, tolerating broker outages."""
    from apps.crossref.tasks import deposit_article_task

    try:
        deposit_article_task.delay(article.pk, update)
    except Exception:  # pragma: no cover - broker outage
        logger.warning("Could not queue Crossref deposit for article %s", article.pk)


def invalidate_public_caches() -> None:
    """Drop cached fragments that change when content is published."""
    for key in ("home_kpis", "public_statistics", "site_settings"):
        cache.delete(key)
    for limit in (4, 5, 6, 10):
        cache.delete(f"most_read:{limit}:30")


def latest_file(submission: Submission, kind: str) -> SubmissionFile | None:
    """Most recent version of a submission file of a given kind."""
    return submission.files.filter(kind=kind).order_by("-version", "-created_at").first()
