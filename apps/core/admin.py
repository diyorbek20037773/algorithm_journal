"""Django admin registrations for core models."""

from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TabbedTranslationAdmin

from apps.core.models import (
    Announcement,
    AuditLog,
    ContactMessage,
    EmailTemplate,
    IndexingService,
    MenuItem,
    Page,
    SiteSettings,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(TabbedTranslationAdmin):
    """Singleton editor for the journal's identity and policies."""

    fieldsets = (
        (_("Identity"), {"fields": ("journal_name", "journal_subtitle", "short_code", "founded_year")}),
        (_("Identifiers"), {
            "fields": (
                "eissn", "pissn", "doi_prefix", "crossref_member_id",
                "registration_certificate_number", "registration_certificate_date",
                "registration_authority",
            )
        }),
        (_("Publisher"), {"fields": ("publisher_name", "publisher_address", "frequency_text")}),
        (_("Contact"), {"fields": ("contact_email", "contact_phone", "contact_address", "editor_in_chief")}),
        (_("Branding"), {"fields": ("logo", "logo_dark", "favicon", "social_links")}),
        (_("Policies"), {"fields": ("similarity_threshold", "show_online_first", "announcement_bar_text")}),
        (_("Integrations"), {"fields": ("google_scholar_url", "matomo_site_id", "indexing_badges")}),
    )
    filter_horizontal = ("indexing_badges",)

    def has_add_permission(self, request) -> bool:
        """Only one settings row may exist."""
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None) -> bool:
        """The settings row can never be deleted."""
        return False


@admin.register(Page)
class PageAdmin(TabbedTranslationAdmin):
    """Markdown CMS pages with a per-language editor."""

    list_display = ("title", "slug", "menu_group", "menu_order", "is_published", "needs_editorial_review")
    list_filter = ("menu_group", "is_published", "needs_editorial_review")
    search_fields = ("title", "slug", "body")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("menu_order", "is_published")


@admin.register(Announcement)
class AnnouncementAdmin(TabbedTranslationAdmin):
    """News items and calls for papers."""

    list_display = ("title", "published_at", "expires_at", "is_pinned")
    list_filter = ("is_pinned",)
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"


@admin.register(IndexingService)
class IndexingServiceAdmin(TabbedTranslationAdmin):
    """Abstracting and indexing services shown on the site."""

    list_display = ("name", "is_active", "order", "url")
    list_editable = ("is_active", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(MenuItem)
class MenuItemAdmin(TabbedTranslationAdmin):
    """Free-form navigation links."""

    list_display = ("label", "group", "order", "is_active", "url")
    list_editable = ("order", "is_active")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Read-only inbox of contact form messages."""

    list_display = ("subject", "name", "email", "created_at", "is_handled")
    list_filter = ("is_handled",)
    search_fields = ("name", "email", "subject", "body")
    readonly_fields = ("name", "email", "subject", "body", "ip", "created_at")


@admin.register(EmailTemplate)
class EmailTemplateAdmin(TabbedTranslationAdmin):
    """Editable transactional e-mail templates."""

    list_display = ("event", "subject", "is_active")
    list_filter = ("is_active",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Append-only audit trail."""

    list_display = ("created_at", "action", "actor", "target", "ip")
    list_filter = ("action", "created_at")
    search_fields = ("target", "actor__email")
    date_hierarchy = "created_at"
    readonly_fields = ("actor", "action", "target", "changes", "ip", "created_at", "updated_at")

    def has_add_permission(self, request) -> bool:
        """Entries are written by the application only."""
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """The audit log is immutable."""
        return False
