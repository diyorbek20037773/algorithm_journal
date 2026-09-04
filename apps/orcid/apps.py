"""ORCID identifiers and OAuth glue."""

from __future__ import annotations

from django.apps import AppConfig


class OrcidConfig(AppConfig):
    """Application configuration for ``apps.orcid``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.orcid"
    label = "orcid_integration"  # allauth already claims the "orcid" app label
    verbose_name = "ORCID"
