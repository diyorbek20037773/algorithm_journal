"""LOCKSS manifests and issue export bundles."""

from __future__ import annotations

from django.apps import AppConfig


class PreservationConfig(AppConfig):
    """Application configuration for ``apps.preservation``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.preservation"
    verbose_name = "Preservation"
