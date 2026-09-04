"""Report the metadata completeness of articles (SPEC §16)."""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand

from apps.journal.models import Article
from apps.production.services import metadata_completeness


class Command(BaseCommand):
    """``manage.py check_metadata [--status published]``."""

    help = "Print the mandatory-metadata checklist for articles."

    def add_arguments(self, parser) -> None:
        """Register the status filter."""
        parser.add_argument("--status", type=str, default="", help="Filter by article status.")
        parser.add_argument("--article", type=int, default=0, help="A single article ID.")

    def handle(self, *args: Any, **options: Any) -> None:
        """Print a red/green checklist per article and a summary."""
        queryset = Article.objects.with_related()
        if options["article"]:
            queryset = queryset.filter(pk=options["article"])
        elif options["status"]:
            queryset = queryset.filter(status=options["status"])
        else:
            queryset = queryset.public()

        incomplete = 0
        for article in queryset:
            checks = metadata_completeness(article)
            missing = [c for c in checks if not c["ok"] and c["level"] == "required"]
            warnings = [c for c in checks if not c["ok"] and c["level"] == "warning"]
            if missing:
                incomplete += 1
                self.stdout.write(self.style.ERROR(f"#{article.pk} {article.title[:60]}"))
                for check in missing:
                    self.stdout.write(f"    missing: {check['label']}")
            elif warnings:
                self.stdout.write(self.style.WARNING(f"#{article.pk} {article.title[:60]}"))
                for check in warnings:
                    self.stdout.write(f"    warning: {check['label']}")
            else:
                self.stdout.write(self.style.SUCCESS(f"#{article.pk} complete"))

        if incomplete:
            self.stdout.write(self.style.ERROR(f"{incomplete} article(s) incomplete."))
        else:
            self.stdout.write(self.style.SUCCESS("Every article passes the completeness check."))
