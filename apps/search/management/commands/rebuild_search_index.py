"""Recompute the stored search vector for every article."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.search.indexing import rebuild_all


class Command(BaseCommand):
    """``manage.py rebuild_search_index`` — rebuild ``Article.search_vector``.

    Needed after a bulk import, after changing what the document contains, or
    whenever search results look stale. Normal edits keep the vector current
    through signals, so this is a repair tool, not a scheduled job.
    """

    help = "Recompute the full-text search document for every article."

    def handle(self, *args, **options) -> None:
        count = rebuild_all()
        self.stdout.write(self.style.SUCCESS(f"Rebuilt the search index for {count} articles."))
