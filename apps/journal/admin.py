"""Admin for published journal content."""

from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TabbedTranslationAdmin

from apps.journal.models import (
    Article,
    ArticleStatisticSnapshot,
    Author,
    EditorialBoardMember,
    Galley,
    Issue,
    JELCode,
    Keyword,
    License,
    Reference,
    Section,
    Volume,
)


class AuthorInline(admin.TabularInline):
    """Authorship rows on the article page."""

    model = Author
    extra = 0
    fields = ("order", "given_name", "family_name", "email", "orcid", "affiliation", "country", "is_corresponding")


class GalleyInline(admin.TabularInline):
    """Downloadable files attached to an article."""

    model = Galley
    extra = 0
    fields = ("label", "language", "file", "mime", "size", "is_primary", "order")


class ReferenceInline(admin.TabularInline):
    """Bibliographic references."""

    model = Reference
    extra = 0
    fields = ("order", "raw_text", "doi")


@admin.register(Section)
class SectionAdmin(TabbedTranslationAdmin):
    """Journal rubrics."""

    list_display = ("name", "slug", "order", "is_active", "is_research")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("editors",)


@admin.register(Volume)
class VolumeAdmin(TabbedTranslationAdmin):
    """Publication volumes."""

    list_display = ("number", "year", "title")


@admin.register(Issue)
class IssueAdmin(TabbedTranslationAdmin):
    """Monthly issues."""

    list_display = ("__str__", "published_at", "is_published", "is_current")
    list_filter = ("is_published", "is_current", "volume")
    date_hierarchy = "published_at"


@admin.register(Article)
class ArticleAdmin(TabbedTranslationAdmin):
    """Articles with authors, galleys and references inline."""

    list_display = ("title", "section", "issue", "status", "doi", "published_at")
    list_filter = ("status", "section", "doi_status", "article_type")
    search_fields = ("title", "abstract", "doi", "authors__family_name")
    date_hierarchy = "published_at"
    inlines = (AuthorInline, GalleyInline, ReferenceInline)
    filter_horizontal = ("keywords", "jel_codes")
    readonly_fields = ("views_count", "downloads_count", "cited_by_count", "slug")


@admin.register(Keyword)
class KeywordAdmin(TabbedTranslationAdmin):
    """Article keywords."""

    list_display = ("name", "slug")
    search_fields = ("name",)


@admin.register(JELCode)
class JELCodeAdmin(TabbedTranslationAdmin):
    """JEL classification tree."""

    list_display = ("code", "label", "level", "parent")
    list_filter = ("level",)
    search_fields = ("code", "label")


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    """Content licences."""

    list_display = ("code", "name", "is_default", "url")


@admin.register(EditorialBoardMember)
class EditorialBoardMemberAdmin(TabbedTranslationAdmin):
    """Editorial, advisory and reviewer boards."""

    list_display = ("full_name", "role", "affiliation", "country", "order", "is_active", "is_demo")
    list_filter = ("role", "is_active", "is_demo", "country")
    list_editable = ("order", "is_active")
    search_fields = ("full_name", "affiliation", "orcid")
    filter_horizontal = ("sections",)


@admin.register(ArticleStatisticSnapshot)
class ArticleStatisticSnapshotAdmin(admin.ModelAdmin):
    """Denormalised usage snapshots."""

    list_display = ("article", "views_total", "downloads_total", "computed_at")
    readonly_fields = ("article", "views_total", "downloads_total", "views_last_30d", "downloads_last_30d")
