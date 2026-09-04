"""Crossref deposit orchestration."""

from __future__ import annotations

import logging

from django.core.files.base import ContentFile
from django.utils import timezone

from apps.core.models import AuditLog
from apps.core.services import log_action
from apps.crossref import client, xml_builder
from apps.crossref.models import DepositBatch, DOIRegistration
from apps.journal.models import Article, Issue

logger = logging.getLogger(__name__)


def build_batch(articles: list[Article], *, is_update: bool = False) -> DepositBatch:
    """Generate deposit XML for ``articles`` and store it as a batch record."""
    from django.conf import settings

    doi_batch_id = xml_builder.batch_id()
    xml_bytes = xml_builder.build_deposit(articles, doi_batch_id=doi_batch_id)
    errors = xml_builder.validate(xml_bytes)
    batch = DepositBatch.objects.create(
        doi_batch_id=doi_batch_id,
        status=DepositBatch.Status.PENDING,
        is_test=settings.CROSSREF_TEST,
        is_update=is_update,
        response_log="\n".join(errors) if errors else "XML validated successfully.",
    )
    batch.xml.save(f"{doi_batch_id}.xml", ContentFile(xml_bytes), save=True)
    batch.articles.set(articles)
    for article in articles:
        DOIRegistration.objects.create(
            article=article, batch=batch, doi=article.doi, status="pending"
        )
    if errors:
        logger.warning("Crossref XML for batch %s has %s issues", doi_batch_id, len(errors))
    return batch


def submit_batch(batch: DepositBatch, *, user=None) -> DepositBatch:
    """POST a prepared batch to Crossref and record the outcome."""
    batch.xml.open("rb")
    payload = batch.xml.read()
    batch.xml.close()
    try:
        success, response = client.deposit(payload, filename=f"{batch.doi_batch_id}.xml")
    except client.CrossrefNotConfigured as exc:
        batch.response_log = (
            f"{batch.response_log}\n\nDeposit not attempted: {exc}".strip()
        )
        batch.save(update_fields=["response_log", "updated_at"])
        return batch

    batch.submitted_at = timezone.now()
    batch.response_log = f"{batch.response_log}\n\n{response}".strip()
    batch.status = DepositBatch.Status.SUBMITTED if success else DepositBatch.Status.FAILED
    batch.save(update_fields=["submitted_at", "response_log", "status", "updated_at"])

    new_status = Article.DOIStatus.REGISTERED if success else Article.DOIStatus.FAILED
    if batch.is_update and success:
        new_status = Article.DOIStatus.UPDATED
    batch.articles.update(doi_status=new_status)
    batch.registrations.update(status="submitted" if success else "failed")

    log_action(
        AuditLog.Action.DEPOSIT,
        actor=user,
        target=f"DepositBatch {batch.doi_batch_id}",
        changes={"status": batch.status, "articles": batch.articles.count()},
    )
    return batch


def deposit_article(article: Article, *, is_update: bool = False, user=None) -> DepositBatch:
    """Build and submit a deposit for a single article."""
    batch = build_batch([article], is_update=is_update)
    return submit_batch(batch, user=user)


def deposit_issue(issue: Issue, *, user=None) -> DepositBatch:
    """Build and submit a deposit for every published article in an issue."""
    articles = list(Article.objects.filter(issue=issue).public().with_related())
    if not articles:
        raise ValueError("The issue has no publicly visible articles.")
    batch = build_batch(articles)
    return submit_batch(batch, user=user)


def refresh_status(batch: DepositBatch) -> DepositBatch:
    """Poll Crossref for the outcome of a submitted batch."""
    if batch.status not in {DepositBatch.Status.SUBMITTED, DepositBatch.Status.PENDING}:
        return batch
    try:
        status, body = client.submission_status(batch.doi_batch_id)
    except client.CrossrefNotConfigured:
        return batch
    batch.response_log = f"{batch.response_log}\n\n--- poll ---\n{body}".strip()
    if status == "success":
        batch.status = DepositBatch.Status.SUCCESS
        batch.resolved_at = timezone.now()
        batch.articles.update(
            doi_status=Article.DOIStatus.UPDATED if batch.is_update else Article.DOIStatus.REGISTERED
        )
        batch.registrations.update(status="registered")
    elif status == "failed":
        batch.status = DepositBatch.Status.FAILED
        batch.resolved_at = timezone.now()
        batch.articles.update(doi_status=Article.DOIStatus.FAILED)
        batch.registrations.update(status="failed")
    batch.save(update_fields=["status", "resolved_at", "response_log", "updated_at"])
    return batch
