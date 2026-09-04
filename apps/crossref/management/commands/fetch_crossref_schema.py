"""Download the Crossref 5.4.0 XSD bundle so that validation is schema-based.

The Crossref schema imports a tree of other schemas (common, funding data,
access indicators, relations, JATS and MathML).  This command follows every
``xs:import`` / ``xs:include`` recursively, stores each file under
``apps/crossref/schemas/`` by its base name and rewrites the schema locations
to those local names, so the resulting bundle validates offline.

Run it once on a machine with outbound network access; the bundle is then
committed or copied to the server.  Without it,
:func:`apps.crossref.xml_builder.validate` falls back to well-formedness plus
structural conformance checks.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from django.core.management.base import BaseCommand

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"
ROOT_URL = "https://www.crossref.org/schemas/crossref5.4.0.xsd"

LOCATION_RE = re.compile(r'schemaLocation="([^"]+)"')
MAX_FILES = 400


class Command(BaseCommand):
    """``manage.py fetch_crossref_schema [--root URL] [--max N]``."""

    help = "Download the Crossref deposit schema bundle into apps/crossref/schemas/."

    def add_arguments(self, parser) -> None:
        """Register the root URL and the file budget."""
        parser.add_argument("--root", type=str, default=ROOT_URL)
        parser.add_argument("--max", type=int, default=MAX_FILES)

    def handle(self, *args: Any, **options: Any) -> None:
        """Fetch the schema tree, rewrite locations and report the result."""
        SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
        session = requests.Session()
        session.headers["User-Agent"] = "ARER schema fetcher (+https://github.com/)"

        queue: list[str] = [options["root"]]
        seen: set[str] = set()
        failed: list[tuple[str, str]] = []
        written = 0

        while queue and written < options["max"]:
            url = queue.pop(0)
            if url in seen:
                continue
            seen.add(url)
            try:
                response = session.get(url, timeout=60)
                response.raise_for_status()
            except Exception as exc:
                failed.append((url, str(exc)[:120]))
                continue

            text = response.text
            for location in LOCATION_RE.findall(text):
                child = urljoin(url, location)
                if child not in seen:
                    queue.append(child)
            # Rewrite every reference to the local base name.
            local = LOCATION_RE.sub(
                lambda match: f'schemaLocation="{Path(match.group(1)).name}"', text
            )
            (SCHEMA_DIR / Path(url).name).write_text(local, encoding="utf-8")
            written += 1
            self.stdout.write(f"  {Path(url).name} ({len(response.content)} bytes)")

        for url, error in failed:
            self.stdout.write(self.style.WARNING(f"  failed: {url} — {error}"))

        if self._validates():
            self.stdout.write(
                self.style.SUCCESS(
                    f"Bundle of {written} file(s) is loadable; validation is now schema-based."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "The bundle could not be loaded as a schema. Validation falls back to "
                    "well-formedness plus the structural conformance checks in "
                    "apps/crossref/xml_builder.py, which is a supported configuration."
                )
            )

    def _validates(self) -> bool:
        """True when lxml can compile the downloaded root schema."""
        root = SCHEMA_DIR / "crossref5.4.0.xsd"
        if not root.exists():
            return False
        try:
            from lxml import etree

            etree.XMLSchema(etree.parse(str(root)))
            return True
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"  schema load error: {str(exc)[:200]}"))
            return False
