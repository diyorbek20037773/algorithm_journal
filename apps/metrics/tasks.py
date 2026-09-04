"""Celery tasks aggregating usage statistics and editorial KPIs."""

from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.metrics import services
from apps.metrics.models import AccessEvent, EditorialKPI

logger = logging.getLogger(__name__)

RAW_EVENT_RETENTION_DAYS = 90


@shared_task(name="apps.metrics.tasks.aggregate_daily_stats")
def aggregate_daily_stats(days_back: int = 2) -> str:
    """Fold recent raw events into daily statistics and refresh totals."""
    today = timezone.now().date()
    written = 0
    for offset in range(days_back):
        written += services.aggregate_day(today - timedelta(days=offset))
    services.refresh_article_totals()
    return f"{written} article-days aggregated"


@shared_task(name="apps.metrics.tasks.prune_access_events")
def prune_access_events(days: int = RAW_EVENT_RETENTION_DAYS) -> str:
    """Delete raw access events older than the retention window."""
    cutoff = timezone.now() - timedelta(days=days)
    deleted, _details = AccessEvent.objects.filter(occurred_at__lt=cutoff).delete()
    return f"{deleted} events pruned"


@shared_task(name="apps.metrics.tasks.snapshot_editorial_kpi")
def snapshot_editorial_kpi() -> str:
    """Store a KPI snapshot for the current month."""
    from apps.journal.models import Article, Author
    from apps.submissions.models import EditorialDecision, ReviewAssignment, Submission

    month = timezone.now().date().replace(day=1)
    next_month = services._shift_month(month, 1)

    submissions = Submission.objects.filter(
        submitted_at__date__gte=month, submitted_at__date__lt=next_month
    )
    decisions = EditorialDecision.objects.filter(
        decided_at__date__gte=month, decided_at__date__lt=next_month
    )
    accepted = decisions.filter(decision=EditorialDecision.Decision.ACCEPT).count()
    rejected = decisions.filter(
        decision__in=[EditorialDecision.Decision.REJECT, EditorialDecision.Decision.DESK_REJECT]
    ).count()
    window = services.compute_kpi_window()

    countries: dict[str, int] = {}
    for author in Author.objects.filter(article__in=Article.objects.public()):
        if author.country:
            countries[author.country.code] = countries.get(author.country.code, 0) + 1

    EditorialKPI.objects.update_or_create(
        month=month,
        defaults={
            "submissions_received": submissions.count(),
            "desk_rejected": decisions.filter(
                decision=EditorialDecision.Decision.DESK_REJECT
            ).count(),
            "sent_to_review": decisions.filter(
                decision=EditorialDecision.Decision.SEND_TO_REVIEW
            ).count(),
            "accepted": accepted,
            "rejected": rejected,
            "published": Article.objects.filter(
                published_at__gte=month, published_at__lt=next_month
            ).count(),
            "acceptance_rate": window["acceptance_rate"],
            "median_days_to_first_decision": window["median_days_to_first_decision"],
            "median_review_days": services.median_review_days(),
            "active_reviewers": ReviewAssignment.objects.filter(
                completed_at__gte=timezone.now() - timedelta(days=365)
            )
            .values("reviewer")
            .distinct()
            .count(),
            "author_countries": countries,
        },
    )
    return f"KPI snapshot for {month:%Y-%m}"
