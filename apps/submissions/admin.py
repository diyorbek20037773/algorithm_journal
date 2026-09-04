"""Admin for the editorial workflow."""

from __future__ import annotations

from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from apps.submissions.models import (
    Discussion,
    DiscussionMessage,
    EditorNote,
    EditorialDecision,
    ProductionTask,
    Review,
    ReviewAssignment,
    ReviewRound,
    RevisionRequest,
    Submission,
    SubmissionAuthor,
    SubmissionFile,
)


class SubmissionAuthorInline(admin.TabularInline):
    """Authors declared on the submission."""

    model = SubmissionAuthor
    extra = 0


class SubmissionFileInline(admin.TabularInline):
    """Files uploaded against the submission."""

    model = SubmissionFile
    extra = 0
    readonly_fields = ("size", "mime")


@admin.register(Submission)
class SubmissionAdmin(TabbedTranslationAdmin):
    """Manuscripts moving through the workflow."""

    list_display = ("reference", "title", "section", "status", "assigned_editor", "submitted_at")
    list_filter = ("status", "section", "article_type")
    search_fields = ("reference", "title", "abstract", "submitter__email")
    date_hierarchy = "submitted_at"
    inlines = (SubmissionAuthorInline, SubmissionFileInline)
    filter_horizontal = ("jel_codes",)
    readonly_fields = ("reference", "submitted_at", "last_activity_at")


@admin.register(ReviewRound)
class ReviewRoundAdmin(admin.ModelAdmin):
    """Rounds of peer review."""

    list_display = ("submission", "number", "status", "opened_at", "closed_at")
    list_filter = ("status",)


@admin.register(ReviewAssignment)
class ReviewAssignmentAdmin(admin.ModelAdmin):
    """Reviewer invitations."""

    list_display = ("reviewer", "round", "status", "due_at", "completed_at", "reminders_sent")
    list_filter = ("status",)
    search_fields = ("reviewer__email",)
    readonly_fields = ("access_token",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Completed reviews."""

    list_display = ("assignment", "recommendation", "submitted_at", "quality_rating", "is_draft")
    list_filter = ("recommendation", "is_draft")


@admin.register(EditorialDecision)
class EditorialDecisionAdmin(admin.ModelAdmin):
    """Recorded decisions."""

    list_display = ("submission", "decision", "decided_by", "decided_at", "emailed_at")
    list_filter = ("decision",)
    date_hierarchy = "decided_at"


@admin.register(RevisionRequest)
class RevisionRequestAdmin(admin.ModelAdmin):
    """Revision requests and their deadlines."""

    list_display = ("submission", "is_major", "due_at", "submitted_at")
    list_filter = ("is_major",)


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    """Discussion threads."""

    list_display = ("subject", "submission", "visibility", "is_closed")
    list_filter = ("visibility", "is_closed")


@admin.register(DiscussionMessage)
class DiscussionMessageAdmin(admin.ModelAdmin):
    """Individual messages."""

    list_display = ("discussion", "author", "created_at", "is_system")
    list_filter = ("is_system",)


@admin.register(EditorNote)
class EditorNoteAdmin(admin.ModelAdmin):
    """Private editorial notes."""

    list_display = ("submission", "author", "created_at")


@admin.register(ProductionTask)
class ProductionTaskAdmin(admin.ModelAdmin):
    """Production checklist items."""

    list_display = ("submission", "stage", "status", "assignee", "due_at", "completed_at")
    list_filter = ("stage", "status")


@admin.register(SubmissionFile)
class SubmissionFileAdmin(admin.ModelAdmin):
    """All uploaded manuscript files."""

    list_display = ("submission", "kind", "version", "created_at", "is_visible_to_reviewers")
    list_filter = ("kind", "is_visible_to_reviewers")
