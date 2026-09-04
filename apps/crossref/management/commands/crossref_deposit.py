"""Build and submit a Crossref deposit."""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandError

from apps.crossref import client, services
from apps.journal.models import Article, Issue


class Command(BaseCommand):
    """``manage.py crossref_deposit --article ID | --issue ID``."""

    help = "Generate and submit Crossref deposit XML for an article or an issue."

    def add_arguments(self, parser) -> None:
        """Register the selection options."""
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--article", type=int)
        group.add_argument("--issue", type=int)
        parser.add_argument(
            "--update",
            action="store_true",
            help="Mark the deposit as a metadata update of an existing DOI.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Build and validate the batch without submitting it.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Create the batch and, unless dry-running, submit it."""
        if options["article"]:
            article = Article.objects.with_related().filter(pk=options["article"]).first()
            if article is None:
                raise CommandError(f"Article {options['article']} does not exist.")
            if not article.doi:
                raise CommandError("The article has no DOI; reserve one first.")
            targets = [article]
        else:
            issue = Issue.objects.filter(pk=options["issue"]).first()
            if issue is None:
                raise CommandError(f"Issue {options['issue']} does not exist.")
            targets = list(Article.objects.public().filter(issue=issue).with_related())
            if not targets:
                raise CommandError("The issue has no publicly visible articles.")

        batch = services.build_batch(targets, is_update=options["update"])
        self.stdout.write(f"Batch {batch.doi_batch_id} built for {len(targets)} article(s).")

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry run: not submitted."))
            return

        if not client.is_configured():
            self.stdout.write(
                self.style.WARNING(
                    "CROSSREF_USER / CROSSREF_PASSWORD are not set. The batch stays "
                    "pending and is visible in the production dashboard."
                )
            )
            return

        services.submit_batch(batch)
        self.stdout.write(self.style.SUCCESS(f"Deposit status: {batch.status}"))
