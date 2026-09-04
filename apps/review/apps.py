"""Reviewer-facing views and forms."""

from __future__ import annotations

from django.apps import AppConfig


class ReviewConfig(AppConfig):
    """Application configuration for ``apps.review``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.review"
    verbose_name = "Review"
