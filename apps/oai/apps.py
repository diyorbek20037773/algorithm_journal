"""OAI-PMH 2.0 metadata harvesting endpoint."""

from __future__ import annotations

from django.apps import AppConfig


class OaiConfig(AppConfig):
    """Application configuration for ``apps.oai``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.oai"
    verbose_name = "OAI-PMH"
