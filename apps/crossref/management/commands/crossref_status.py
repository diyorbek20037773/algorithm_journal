"""Poll Crossref for the status of open deposit batches."""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand

from apps.crossref import client, services
from apps.crossref.models import DepositBatch


class Command(BaseCommand):
    """``manage.py crossref_status [--batch DOI_BATCH_ID]``."""

    help = "Refresh the status of submitted Crossref deposit batches."

    def add_arguments(self, parser) -> None:
        """Register the optional batch filter."""
        parser.add_argument("--batch", type=str, default="", help="A single doi_batch_id.")

    def handle(self, *args: Any, **options: Any) -> None:
        """Poll each open batch and print the resulting status."""
        queryset = DepositBatch.objects.filter(
            status__in=[DepositBatch.Status.SUBMITTED, DepositBatch.Status.PENDING]
        )
        if options["batch"]:
            queryset = queryset.filter(doi_batch_id=options["batch"])

        if not client.is_configured():
            self.stdout.write(
                self.style.WARNING("Crossref credentials are not configured; nothing to poll.")
            )

        for batch in queryset:
            services.refresh_status(batch)
            self.stdout.write(f"{batch.doi_batch_id}: {batch.status}")
        self.stdout.write(self.style.SUCCESS(f"{queryset.count()} batch(es) checked."))
