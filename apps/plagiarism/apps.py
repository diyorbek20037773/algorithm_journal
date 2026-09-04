"""Similarity-check providers."""

from __future__ import annotations

from django.apps import AppConfig


class PlagiarismConfig(AppConfig):
    """Application configuration for ``apps.plagiarism``."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.plagiarism"
    verbose_name = "Plagiarism"
