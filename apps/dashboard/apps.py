"""Role-based editorial dashboards."""

from __future__ import annotations

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """Application configuration for ``apps.dashboard``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.dashboard"
    verbose_name = "Dashboard"
