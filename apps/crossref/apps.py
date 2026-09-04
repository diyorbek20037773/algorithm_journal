"""DOI deposit XML generation and Crossref communication."""

from __future__ import annotations

from django.apps import AppConfig


class CrossrefConfig(AppConfig):
    """Application configuration for ``apps.crossref``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.crossref"
    verbose_name = "Crossref"
