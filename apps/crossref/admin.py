"""Admin for Crossref deposits."""

from __future__ import annotations

from django.contrib import admin

from apps.crossref.models import DepositBatch, DOIRegistration


@admin.register(DepositBatch)
class DepositBatchAdmin(admin.ModelAdmin):
    """Deposit batches and their Crossref responses."""

    list_display = ("doi_batch_id", "status", "is_test", "is_update", "created_at", "submitted_at")
    list_filter = ("status", "is_test", "is_update")
    search_fields = ("doi_batch_id",)
    readonly_fields = ("doi_batch_id", "response_log", "submitted_at", "resolved_at")
    filter_horizontal = ("articles",)


@admin.register(DOIRegistration)
class DOIRegistrationAdmin(admin.ModelAdmin):
    """Per-article DOI registration history."""

    list_display = ("doi", "article", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("doi",)
