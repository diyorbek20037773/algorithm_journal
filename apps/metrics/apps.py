"""Article usage statistics and editorial KPIs."""

from __future__ import annotations

import contextlib

from django.apps import AppConfig


class MetricsConfig(AppConfig):
    """Application configuration for ``apps.metrics``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.metrics"
    verbose_name = "Metrics"

    def ready(self) -> None:
        """Import signal handlers once the app registry is populated."""
        with contextlib.suppress(ImportError):
            import apps.metrics.signals  # noqa: F401
