"""CSL citation rendering and bibliographic exports."""

from __future__ import annotations

from django.apps import AppConfig


class CitationsConfig(AppConfig):
    """Application configuration for ``apps.citations``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.citations"
    verbose_name = "Citations"
