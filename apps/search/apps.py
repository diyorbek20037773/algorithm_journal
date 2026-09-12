"""Full-text search over published content."""

from __future__ import annotations

import contextlib

from django.apps import AppConfig


class SearchConfig(AppConfig):
    """Application configuration for ``apps.search``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.search"
    verbose_name = "Search"

    def ready(self) -> None:
        """Wire the handlers that keep the stored search vector current."""
        with contextlib.suppress(ImportError):
            import apps.search.signals  # noqa: F401
