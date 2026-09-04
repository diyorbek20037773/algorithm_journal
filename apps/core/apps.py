"""Site settings, CMS pages, announcements and shared utilities."""

from __future__ import annotations

import contextlib

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Application configuration for ``apps.core``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"

    def ready(self) -> None:
        """Import signal handlers once the app registry is populated."""
        with contextlib.suppress(ImportError):
            import apps.core.signals  # noqa: F401
