"""Load the JEL classification tree from ``seed/jel.json``."""

from __future__ import annotations

import json
from pathlib import Path

SEED_PATH = Path(__file__).resolve().parent / "jel.json"


def load_jel(path: Path | None = None) -> int:
    """Create or update every JEL code and link it to its parent.

    Returns the number of codes in the tree.  Safe to run repeatedly.
    """
    from apps.journal.models import JELCode

    payload = json.loads((path or SEED_PATH).read_text(encoding="utf-8"))

    # First pass: create every node without parents so links always resolve.
    for row in payload:
        code, created = JELCode.objects.get_or_create(code=row["code"])
        code.level = row["level"]
        code.label_en = row["en"]
        code.label_uz = row["uz"]
        code.label_ru = row["ru"]
        code.label = row["en"]
        code.save()

    # Second pass: attach parents.
    lookup = {c.code: c for c in JELCode.objects.all()}
    for row in payload:
        parent_code = row.get("parent")
        if not parent_code:
            continue
        child = lookup.get(row["code"])
        parent = lookup.get(parent_code)
        if child is not None and parent is not None and child.parent_id != parent.pk:
            child.parent = parent
            child.save(update_fields=["parent", "updated_at"])

    return len(payload)
