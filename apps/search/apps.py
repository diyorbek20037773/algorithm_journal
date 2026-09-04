"""Full-text search over published content."""

from __future__ import annotations

from django.apps import AppConfig


class SearchConfig(AppConfig):
    """Application configuration for ``apps.search``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.search"
    verbose_name = "Search"
