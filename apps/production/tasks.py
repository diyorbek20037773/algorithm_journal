"""Celery tasks for production: building the issue PDF."""

from __future__ import annotations

from celery import shared_task


@shared_task(name="apps.production.tasks.build_issue_print", time_limit=60 * 30)
def build_issue_print_task(issue_id: int) -> str:
    """Build the issue PDF and every offprint of ``issue_id``."""
    from apps.production.issue_print import run_build

    return run_build(issue_id)
