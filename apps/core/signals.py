"""Core signal handlers: automatic Uzbek Cyrillic transliteration."""

from __future__ import annotations

import logging
from typing import Any

from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.core.models import AutoTranslitMixin
from apps.core.translit import to_cyrillic

logger = logging.getLogger(__name__)

#: modeltranslation renders the ``uz-cyrl`` language as this field suffix.
CYRILLIC_SUFFIX = "_uz_cyrl"
LATIN_SUFFIX = "_uz"


@receiver(pre_save, dispatch_uid="core_fill_uz_cyrl")
def fill_uz_cyrl(sender: type, instance: Any, **kwargs) -> None:
    """Populate empty ``*_uz_cyrl`` fields by transliterating ``*_uz``.

    Only models that opt in through
    :class:`~apps.core.models.AutoTranslitMixin` are touched.  Values written
    by a human are never overwritten; the field names that were generated are
    recorded in ``auto_translit`` so the admin can flag them for proofreading.
    """
    if not isinstance(instance, AutoTranslitMixin):
        return

    generated: dict[str, str] = {}
    existing = instance.auto_translit if isinstance(instance.auto_translit, dict) else {}

    for field in instance._meta.get_fields():
        name = getattr(field, "name", "")
        if not name.endswith(CYRILLIC_SUFFIX):
            continue
        latin_name = name[: -len(CYRILLIC_SUFFIX)] + LATIN_SUFFIX
        if not hasattr(instance, latin_name):
            continue
        latin_value = getattr(instance, latin_name, None)
        cyrillic_value = getattr(instance, name, None)
        if not latin_value:
            continue
        # Regenerate when empty, or when the Latin source changed since the
        # last machine generation.
        previously_generated_from = existing.get(name)
        if cyrillic_value and previously_generated_from != latin_value:
            continue
        try:
            converted = to_cyrillic(latin_value)
        except Exception:  # pragma: no cover - transliteration must never break saves
            logger.exception("Transliteration failed for %s.%s", sender.__name__, name)
            continue
        if converted and converted != cyrillic_value:
            setattr(instance, name, converted)
        generated[name] = latin_value

    if generated:
        merged = dict(existing)
        merged.update(generated)
        instance.auto_translit = merged
