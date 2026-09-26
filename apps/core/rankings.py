"""The institutions shown in the Rankings section.

The list lives in ``apps/core/data/institutions.json`` rather than in the
database: it is a handful of editorial entries that change a few times a year,
it needs no workflow, and keeping it in the repository means the section works
on a fresh checkout with no fixture to load. Swap this module for a model if
the office ever needs to edit it from the admin.

Everything shipped in that file is demo content and says so; nothing here may
be presented as a real ranking (CLAUDE.md §8).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).resolve().parent / "data" / "institutions.json"


@lru_cache(maxsize=1)
def _load() -> list[dict[str, Any]]:
    """Read and cache the file; an unreadable file yields an empty section."""
    try:
        payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    entries = payload.get("institutions", [])
    return [entry for entry in entries if entry.get("id") and entry.get("name")]


def all_institutions() -> list[dict[str, Any]]:
    """Every institution, in file order."""
    return list(_load())


def featured() -> list[dict[str, Any]]:
    """The institutions the top banner rotates through."""
    return [entry for entry in _load() if entry.get("banner")]


def rail_split() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split the institutions between the left and the right rail.

    Alternating keeps both rails populated however many institutions there
    are, and keeps the same institution off both sides at once.
    """
    entries = [entry for entry in _load() if entry.get("badges")]
    return entries[0::2], entries[1::2]


def has_demo_entries() -> bool:
    """True while any entry is still the shipped placeholder."""
    return any(entry.get("demo") for entry in _load())
