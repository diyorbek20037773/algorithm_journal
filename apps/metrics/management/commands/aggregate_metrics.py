"""Aggregate raw access events into daily statistics."""

from __future__ import annotations

import datetime as dt
from typing import Any

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.metrics import services


class Command(BaseCommand):
    """``manage.py aggregate_metrics [--days N]``."""

    help = "Fold raw access events into DailyArticleStat rows and refresh totals."

    def add_arguments(self, parser) -> None:
        """Register the look-back window."""
        parser.add_argument("--days", type=int, default=2)

    def handle(self, *args: Any, **options: Any) -> None:
        """Aggregate each day in the window and refresh denormalised totals."""
        today = timezone.localdate()
        written = 0
        for offset in range(options["days"]):
            written += services.aggregate_day(today - dt.timedelta(days=offset))
        updated = services.refresh_article_totals()
        self.stdout.write(
            self.style.SUCCESS(f"{written} article-days aggregated, {updated} totals refreshed.")
        )
