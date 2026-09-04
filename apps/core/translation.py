"""modeltranslation registrations for the core app."""

from __future__ import annotations

from modeltranslation.translator import TranslationOptions, register

from apps.core.models import Announcement, EmailTemplate, IndexingService, MenuItem, Page, SiteSettings


@register(SiteSettings)
class SiteSettingsTranslationOptions(TranslationOptions):
    """Journal identity strings shown in every language."""

    fields = (
        "journal_name",
        "journal_subtitle",
        "registration_authority",
        "publisher_name",
        "publisher_address",
        "frequency_text",
        "contact_address",
        "announcement_bar_text",
    )


@register(Page)
class PageTranslationOptions(TranslationOptions):
    """CMS page content."""

    fields = ("title", "body", "seo_description")


@register(Announcement)
class AnnouncementTranslationOptions(TranslationOptions):
    """News and calls for papers."""

    fields = ("title", "body")


@register(MenuItem)
class MenuItemTranslationOptions(TranslationOptions):
    """Free-form navigation labels."""

    fields = ("label",)


@register(IndexingService)
class IndexingServiceTranslationOptions(TranslationOptions):
    """Indexing service note text."""

    fields = ("note",)


@register(EmailTemplate)
class EmailTemplateTranslationOptions(TranslationOptions):
    """Transactional e-mail bodies per language."""

    fields = ("subject", "body")
