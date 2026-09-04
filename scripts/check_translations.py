#!/usr/bin/env python
"""Fail when any gettext catalogue still has untranslated or fuzzy entries.

SPEC §10 requires 100 % translated interface strings in all four languages.
Run via ``make check-translations`` or in CI.
"""

from __future__ import annotations

import sys
from pathlib import Path

import polib

BASE_DIR = Path(__file__).resolve().parent.parent
LOCALE_DIR = BASE_DIR / "locale"
REQUIRED_LOCALES = ("en", "uz", "uz_Cyrl", "ru")


def main() -> int:
    """Check every catalogue and print a per-locale report."""
    if not LOCALE_DIR.exists():
        print(f"ERROR: locale directory not found: {LOCALE_DIR}")
        return 1

    failures: list[str] = []
    for locale in REQUIRED_LOCALES:
        po_path = LOCALE_DIR / locale / "LC_MESSAGES" / "django.po"
        if not po_path.exists():
            failures.append(f"{locale}: missing catalogue {po_path}")
            continue
        catalogue = polib.pofile(str(po_path))
        untranslated = catalogue.untranslated_entries()
        fuzzy = catalogue.fuzzy_entries()
        total = len([e for e in catalogue if not e.obsolete])
        translated = len(catalogue.translated_entries())
        print(
            f"{locale:<8} {translated}/{total} translated, "
            f"{len(untranslated)} untranslated, {len(fuzzy)} fuzzy"
        )
        if untranslated:
            failures.append(
                f"{locale}: {len(untranslated)} untranslated "
                f"(first: {untranslated[0].msgid[:60]!r})"
            )
        if fuzzy:
            failures.append(f"{locale}: {len(fuzzy)} fuzzy (first: {fuzzy[0].msgid[:60]!r})")

    if failures:
        print("\nTranslation check FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("\nAll catalogues are complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
