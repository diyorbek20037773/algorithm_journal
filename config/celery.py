"""Celery application for background and scheduled editorial jobs."""

from __future__ import annotations

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("arer")
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


@app.task(bind=True, ignore_result=True)
def debug_task(self) -> str:
    """Trivial task used to verify that the worker is reachable."""
    return f"celery ok: {self.request.id}"
