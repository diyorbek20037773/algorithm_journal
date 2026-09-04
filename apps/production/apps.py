"""Copyediting, typesetting, galleys and issue publication."""

from __future__ import annotations

from django.apps import AppConfig


class ProductionConfig(AppConfig):
    """Application configuration for ``apps.production``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.production"
    verbose_name = "Production"
