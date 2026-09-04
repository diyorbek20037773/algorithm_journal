"""Admin for users and scholarly profiles."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import Profile, User


class ProfileInline(admin.StackedInline):
    """Edit the scholarly profile alongside the account."""

    model = Profile
    can_delete = False
    filter_horizontal = ("jel_codes",)
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """E-mail based user administration."""

    inlines = (ProfileInline,)
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "is_reviewer", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active", "is_reviewer", "groups")
    search_fields = ("email", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "preferred_language")}),
        (_("Editorial"), {"fields": ("is_reviewer", "must_enroll_2fa")}),
        (
            _("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined", "last_activity_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "first_name", "last_name"),
            },
        ),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Standalone profile list, useful for the reviewer pool."""

    list_display = ("user", "affiliation", "country", "orcid", "reviews_completed")
    list_filter = ("country", "orcid_verified", "accepts_review_invitations")
    search_fields = ("user__email", "user__last_name", "affiliation", "expertise", "orcid")
    filter_horizontal = ("jel_codes",)
