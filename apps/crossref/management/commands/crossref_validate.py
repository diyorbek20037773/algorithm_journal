"""Validate the Crossref deposit XML of an article, an issue or everything."""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandError

from apps.crossref import xml_builder
from apps.journal.models import Article, Issue


class Command(BaseCommand):
    """``manage.py crossref_validate [--article ID | --issue ID | --all]``."""

    help = "Generate Crossref deposit XML and validate it against the schema."

    def add_arguments(self, parser) -> None:
        """Register the selection options."""
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--article", type=int, help="Validate a single article by ID.")
        group.add_argument("--issue", type=int, help="Validate every article of an issue.")
        group.add_argument("--all", action="store_true", help="Validate every public article.")
        parser.add_argument("--write", type=str, default="", help="Write the XML to this path.")

    def handle(self, *args: Any, **options: Any) -> None:
        """Build the deposit document and report validation errors."""
        articles = self._select(options)
        if not articles:
            raise CommandError("No matching articles.")

        failures = 0
        for article in articles:
            if not article.doi:
                self.stdout.write(self.style.WARNING(f"#{article.pk}: no DOI, skipped"))
                continue
            xml = xml_builder.build_deposit([article])
            errors = xml_builder.validate(xml)
            if errors:
                failures += 1
                self.stdout.write(self.style.ERROR(f"#{article.pk}: {len(errors)} problem(s)"))
                for error in errors[:10]:
                    self.stdout.write(f"    {error}")
            else:
                self.stdout.write(self.style.SUCCESS(f"#{article.pk}: valid"))
            if options["write"]:
                with open(options["write"], "wb") as handle:
                    handle.write(xml)
                self.stdout.write(f"    written to {options['write']}")

        if failures:
            raise CommandError(f"{failures} article(s) failed validation.")
        self.stdout.write(self.style.SUCCESS(f"{len(articles)} article(s) validated."))

    @staticmethod
    def _select(options: dict[str, Any]) -> list[Article]:
        """Resolve the requested articles."""
        if options["article"]:
            return list(Article.objects.with_related().filter(pk=options["article"]))
        if options["issue"]:
            issue = Issue.objects.filter(pk=options["issue"]).first()
            if issue is None:
                raise CommandError(f"Issue {options['issue']} does not exist.")
            return list(Article.objects.public().filter(issue=issue).with_related())
        return list(Article.objects.public().with_related())
