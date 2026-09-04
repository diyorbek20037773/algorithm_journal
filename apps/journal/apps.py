"""Volumes, issues, articles, authors and the editorial board."""

from __future__ import annotations

import contextlib

from django.apps import AppConfig


class JournalConfig(AppConfig):
    """Application configuration for ``apps.journal``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.journal"
    verbose_name = "Journal"

    def ready(self) -> None:
        """Import signal handlers once the app registry is populated."""
        with contextlib.suppress(ImportError):
            import apps.journal.signals  # noqa: F401
