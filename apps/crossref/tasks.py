"""Celery tasks for Crossref deposits and cited-by counts."""

from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from apps.crossref import client, services
from apps.crossref.models import DepositBatch
from apps.journal.models import Article

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="apps.crossref.tasks.deposit_article_task",
    autoretry_for=(Exception,),
    retry_backoff=60,
    retry_kwargs={"max_retries": 5},
)
def deposit_article_task(self, article_id: int, is_update: bool = False) -> str:
    """Build and submit a Crossref deposit for one article."""
    article = Article.objects.with_related().filter(pk=article_id).first()
    if article is None or not article.doi:
        return "skipped: no article or DOI"
    batch = services.deposit_article(article, is_update=is_update)
    return f"{batch.doi_batch_id}: {batch.status}"


@shared_task(name="apps.crossref.tasks.deposit_issue_task")
def deposit_issue_task(issue_id: int) -> str:
    """Deposit every article of one issue."""
    from apps.journal.models import Issue

    issue = Issue.objects.filter(pk=issue_id).first()
    if issue is None:
        return "skipped: no issue"
    batch = services.deposit_issue(issue)
    return f"{batch.doi_batch_id}: {batch.status}"


@shared_task(name="apps.crossref.tasks.poll_deposit_status_task")
def poll_deposit_status_task() -> str:
    """Refresh the status of every batch that is still open."""
    batches = DepositBatch.objects.filter(
        status__in=[DepositBatch.Status.SUBMITTED, DepositBatch.Status.PENDING]
    )
    checked = 0
    for batch in batches:
        services.refresh_status(batch)
        checked += 1
    return f"{checked} batches polled"


@shared_task(name="apps.crossref.tasks.fetch_cited_by_task")
def fetch_cited_by_task() -> str:
    """Update the Crossref cited-by count of every article with a DOI."""
    updated = 0
    for article in Article.objects.public().exclude(doi="").only("id", "doi"):
        count = client.cited_by_count(article.doi)
        if count is None:
            continue
        Article.objects.filter(pk=article.pk).update(
            cited_by_count=count, cited_by_updated_at=timezone.now()
        )
        updated += 1
    return f"{updated} articles updated"
