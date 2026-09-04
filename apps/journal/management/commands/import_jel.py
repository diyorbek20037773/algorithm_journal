"""Import the complete official JEL classification from a CSV export."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from apps.journal.models import JELCode


class Command(BaseCommand):
    """``manage.py import_jel <file.csv>``.

    The AEA publishes the classification as a CSV with ``code`` and
    ``description`` columns.  Existing codes are updated, new ones created, and
    the parent links are rebuilt.  Uzbek and Russian labels of codes already in
    the database are preserved.
    """

    help = "Import the official JEL classification from an AEA CSV export."

    def add_arguments(self, parser) -> None:
        """Register the file argument."""
        parser.add_argument("path", type=str, help="Path to the JEL CSV file.")
        parser.add_argument(
            "--code-column", type=str, default="code", help="Name of the code column."
        )
        parser.add_argument(
            "--label-column", type=str, default="description", help="Name of the label column."
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Read the CSV, upsert every code and relink parents."""
        path = Path(options["path"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        created = updated = 0
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if options["code_column"] not in (reader.fieldnames or []):
                raise CommandError(
                    f"Column '{options['code_column']}' not found. "
                    f"Columns present: {', '.join(reader.fieldnames or [])}"
                )
            for row in reader:
                code = (row[options["code_column"]] or "").strip().upper()
                label = (row.get(options["label_column"]) or "").strip()
                if not code or len(code) > 8:
                    continue
                obj, was_created = JELCode.objects.get_or_create(code=code)
                obj.level = min(len(code), 3)
                obj.label_en = label or obj.label_en
                obj.label = obj.label_en
                obj.save()
                created += int(was_created)
                updated += int(not was_created)

        lookup = {c.code: c for c in JELCode.objects.all()}
        relinked = 0
        for code_obj in lookup.values():
            parent_code = code_obj.code[:-1] if len(code_obj.code) > 1 else None
            parent = lookup.get(parent_code) if parent_code else None
            if parent is not None and code_obj.parent_id != parent.pk:
                code_obj.parent = parent
                code_obj.save(update_fields=["parent", "updated_at"])
                relinked += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"JEL import finished: {created} created, {updated} updated, {relinked} relinked. "
                "Uzbek and Russian labels of existing codes were preserved; translate any new "
                "codes in the admin."
            )
        )
