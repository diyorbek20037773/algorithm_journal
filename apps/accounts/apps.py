"""Users, profiles, roles and two-factor authentication."""

from __future__ import annotations

import contextlib

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Application configuration for ``apps.accounts``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    verbose_name = "Accounts"

    def ready(self) -> None:
        """Import signal handlers once the app registry is populated."""
        with contextlib.suppress(ImportError):
            import apps.accounts.signals  # noqa: F401
