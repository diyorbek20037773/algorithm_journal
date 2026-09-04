"""Export a self-contained preservation bundle for one issue."""

from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.crossref import xml_builder
from apps.journal.models import Article, Issue


class Command(BaseCommand):
    """``manage.py export_issue_bundle <issue-id> [--out DIR]``.

    Produces ``exports/ARER_vol{V}_no{N}.zip`` containing, for every article:
    the published PDF, the JATS XML front matter, the Crossref deposit XML and
    a ``manifest.json`` with checksums and metadata.
    """

    help = "Create a ZIP preservation bundle for an issue (PDF + JATS + Crossref XML)."

    def add_arguments(self, parser) -> None:
        """Register the issue and output directory arguments."""
        parser.add_argument("issue_id", type=int)
        parser.add_argument("--out", type=str, default="", help="Output directory.")

    def handle(self, *args: Any, **options: Any) -> None:
        """Assemble the bundle and report the path and size."""
        issue = Issue.objects.select_related("volume").filter(pk=options["issue_id"]).first()
        if issue is None:
            raise CommandError(f"Issue {options['issue_id']} does not exist.")

        articles = list(Article.objects.public().filter(issue=issue).with_related())
        if not articles:
            raise CommandError("The issue has no publicly visible articles.")

        out_dir = Path(options["out"] or (Path(settings.BASE_DIR) / "exports"))
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / f"ARER_vol{issue.volume.number}_no{issue.number}.zip"

        manifest: dict[str, Any] = {
            "journal": "ALGORITHM: Review of Economic Research",
            "short_code": "ARER",
            "volume": issue.volume.number,
            "issue": issue.number,
            "year": issue.volume.year,
            "published_at": issue.published_at.isoformat() if issue.published_at else None,
            "generated_at": datetime.now(UTC).isoformat(),
            "articles": [],
        }

        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as bundle:
            for article in articles:
                entry: dict[str, Any] = {
                    "id": article.pk,
                    "doi": article.doi,
                    "title": article.title_en or article.title,
                    "authors": [a.citation_name for a in article.author_list()],
                    "pages": article.pages,
                    "url": article.canonical_url,
                    "files": {},
                }

                galley = article.primary_galley
                if galley is not None and galley.file:
                    galley.file.open("rb")
                    payload = galley.file.read()
                    galley.file.close()
                    name = f"pdf/arer-{article.pk}.pdf"
                    bundle.writestr(name, payload)
                    entry["files"]["pdf"] = {
                        "path": name,
                        "bytes": len(payload),
                        "sha256": hashlib.sha256(payload).hexdigest(),
                    }

                jats = self._jats(article)
                name = f"jats/arer-{article.pk}.xml"
                bundle.writestr(name, jats)
                entry["files"]["jats"] = {
                    "path": name,
                    "bytes": len(jats),
                    "sha256": hashlib.sha256(jats).hexdigest(),
                }

                deposit = xml_builder.build_deposit([article])
                name = f"crossref/arer-{article.pk}.xml"
                bundle.writestr(name, deposit)
                entry["files"]["crossref"] = {
                    "path": name,
                    "bytes": len(deposit),
                    "sha256": hashlib.sha256(deposit).hexdigest(),
                }

                manifest["articles"].append(entry)

            bundle.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

        size = target.stat().st_size
        self.stdout.write(
            self.style.SUCCESS(f"{target} — {len(articles)} article(s), {size / 1024:.0f} KB")
        )

    @staticmethod
    def _jats(article: Article) -> bytes:
        """Render the JATS front matter of one article."""
        from lxml import etree

        from apps.oai.views import _jats

        root = etree.Element("bundle")
        _jats(root, article)
        payload = root[0]
        return etree.tostring(payload, pretty_print=True, xml_declaration=True, encoding="UTF-8")
