"""Read-only public JSON API."""

from __future__ import annotations

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Application configuration for ``apps.api``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.api"
    verbose_name = "API"
