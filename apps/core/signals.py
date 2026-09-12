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


# --- public page cache ------------------------------------------------------
# Anything an editor changes through the admin that appears on a public page
# must invalidate the whole-page cache, or the change waits up to two minutes
# to show — long enough for an editor to conclude the save failed.


def _invalidate_public_pages(**kwargs: Any) -> None:
    from apps.core.caching import bump_public_cache_generation

    bump_public_cache_generation()


def _connect_cache_invalidation() -> None:
    from django.db.models.signals import post_delete, post_save

    from apps.core.models import Announcement, IndexingService, Page, SiteSettings
    from apps.journal.models import Article, EditorialBoardMember, Issue, Section, Volume

    for model in (
        Announcement,
        IndexingService,
        Page,
        SiteSettings,
        Article,
        EditorialBoardMember,
        Issue,
        Section,
        Volume,
    ):
        post_save.connect(
            _invalidate_public_pages,
            sender=model,
            weak=False,
            dispatch_uid=f"public_cache_save_{model.__name__}",
        )
        post_delete.connect(
            _invalidate_public_pages,
            sender=model,
            weak=False,
            dispatch_uid=f"public_cache_delete_{model.__name__}",
        )


_connect_cache_invalidation()
