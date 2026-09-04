"""Admin for usage statistics."""

from __future__ import annotations

from django.contrib import admin

from apps.metrics.models import AccessEvent, DailyArticleStat, EditorialKPI


@admin.register(AccessEvent)
class AccessEventAdmin(admin.ModelAdmin):
    """Raw, anonymised access events."""

    list_display = ("article", "kind", "occurred_at", "is_bot", "country")
    list_filter = ("kind", "is_bot")
    date_hierarchy = "occurred_at"
    readonly_fields = ("ip_hash", "user_agent_hash", "session_key_hash")


@admin.register(DailyArticleStat)
class DailyArticleStatAdmin(admin.ModelAdmin):
    """Nightly aggregates."""

    list_display = ("article", "date", "views", "downloads")
    date_hierarchy = "date"


@admin.register(EditorialKPI)
class EditorialKPIAdmin(admin.ModelAdmin):
    """Monthly editorial indicators."""

    list_display = (
        "month", "submissions_received", "accepted", "rejected",
        "acceptance_rate", "median_days_to_first_decision",
    )
    date_hierarchy = "month"
