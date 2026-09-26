"""Celery application for background and scheduled editorial jobs."""

from __future__ import annotations

import logging
import os
from typing import Any

from celery import Celery, Task
from celery.schedules import crontab
from celery.signals import worker_process_init

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

logger = logging.getLogger(__name__)


def _is_broker_outage(exc: BaseException) -> bool:
    """True for the errors an unreachable broker or result backend raises."""
    from kombu.exceptions import OperationalError

    try:
        import redis.exceptions as rexc

        redis_errors: tuple[type[BaseException], ...] = (rexc.ConnectionError, rexc.TimeoutError)
    except ImportError:  # pragma: no cover - redis is always installed
        redis_errors = ()
    return isinstance(exc, (OperationalError, OSError, *redis_errors))


class ResilientTask(Task):
    """Task whose ``delay()`` runs in-process when the broker is unreachable.

    Editorial actions (submit, invite a reviewer, record a decision) queue an
    e-mail. A broker outage or a deploy without Redis must not turn those
    actions into a server error: the work is done in the request instead, and
    the outage is logged.
    """

    def apply_async(self, args: Any = None, kwargs: Any = None, **options: Any):
        try:
            return super().apply_async(args, kwargs, **options)
        except Exception as exc:
            if not _is_broker_outage(exc):
                raise
            logger.error("Broker unavailable (%s); running %s in-process", exc, self.name)
            return self.apply(args, kwargs, throw=False)


app = Celery("arer", task_cls=ResilientTask)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "aggregate-daily-article-stats": {
        "task": "apps.metrics.tasks.aggregate_daily_stats",
        "schedule": crontab(hour=1, minute=15),
    },
    "prune-access-events": {
        "task": "apps.metrics.tasks.prune_access_events",
        "schedule": crontab(hour=1, minute=45),
    },
    "snapshot-editorial-kpi": {
        "task": "apps.metrics.tasks.snapshot_editorial_kpi",
        "schedule": crontab(hour=2, minute=0),
    },
    "poll-crossref-deposit-status": {
        "task": "apps.crossref.tasks.poll_deposit_status_task",
        "schedule": crontab(minute="*/30"),
    },
    "fetch-crossref-cited-by": {
        "task": "apps.crossref.tasks.fetch_cited_by_task",
        "schedule": crontab(hour=3, minute=30),
    },
    "send-review-reminders": {
        "task": "apps.submissions.tasks.send_review_reminders",
        "schedule": crontab(hour=7, minute=0),
    },
    "flag-overdue-reviews": {
        "task": "apps.submissions.tasks.flag_overdue_reviews",
        "schedule": crontab(hour=7, minute=30),
    },
    "send-revision-reminders": {
        "task": "apps.submissions.tasks.send_revision_reminders",
        "schedule": crontab(hour=8, minute=0),
    },
}


@worker_process_init.connect(weak=False)
def _init_worker_tracing(**kwargs) -> None:
    """Trace tasks in each forked worker process (no-op without an OTLP endpoint)."""
    from apps.core.observability import init_tracing

    init_tracing("worker")


@app.task(bind=True, ignore_result=True)
def debug_task(self) -> str:
    """Trivial task used to verify that the worker is reachable."""
    return f"celery ok: {self.request.id}"
