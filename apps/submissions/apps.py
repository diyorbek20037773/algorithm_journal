"""Manuscript submission and peer-review workflow."""

from __future__ import annotations

import contextlib

from django.apps import AppConfig


class SubmissionsConfig(AppConfig):
    """Application configuration for ``apps.submissions``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.submissions"
    verbose_name = "Submissions"

    def ready(self) -> None:
        """Import signal handlers once the app registry is populated."""
        with contextlib.suppress(ImportError):
            import apps.submissions.signals  # noqa: F401
