"""Manuscript submissions and the double-blind peer-review workflow."""

from __future__ import annotations

import secrets
import uuid
from datetime import timedelta
from typing import ClassVar

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from apps.core.models import TimeStampedModel


def submission_file_upload_to(instance: SubmissionFile, filename: str) -> str:
    """Store manuscript files under a UUID path, never the original name."""
    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    return f"submissions/{instance.submission_id or 'new'}/{uuid.uuid4().hex}.{suffix}"


def similarity_report_upload_to(instance: Submission, filename: str) -> str:
    """Store similarity reports under a UUID path."""
    return f"similarity/{uuid.uuid4().hex}.pdf"


def review_attachment_upload_to(instance: Review, filename: str) -> str:
    """Store reviewer attachments under a UUID path."""
    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else "pdf"
    return f"reviews/{uuid.uuid4().hex}.{suffix}"


class SubmissionStatus(models.TextChoices):
    """Finite states of the editorial workflow (SPEC §5.3)."""

    DRAFT = "draft", _("Draft")
    SUBMITTED = "submitted", _("Submitted")
    SCREENING = "screening", _("Screening")
    UNDER_REVIEW = "under_review", _("Under review")
    AWAITING_DECISION = "awaiting_decision", _("Awaiting decision")
    REVISION_REQUESTED = "revision_requested", _("Revision requested")
    RESUBMITTED = "resubmitted", _("Resubmitted")
    ACCEPTED = "accepted", _("Accepted")
    COPYEDITING = "copyediting", _("Copyediting")
    AUTHOR_PROOF = "author_proof", _("Author proof")
    TYPESETTING = "typesetting", _("Typesetting")
    READY_TO_PUBLISH = "ready_to_publish", _("Ready to publish")
    PUBLISHED_ONLINE_FIRST = "published_online_first", _("Published (Online First)")
    PUBLISHED = "published", _("Published")
    REJECTED = "rejected", _("Rejected")
    WITHDRAWN = "withdrawn", _("Withdrawn")


#: States in which an author may still withdraw the manuscript.
PRE_ACCEPT_STATES: tuple[str, ...] = (
    SubmissionStatus.DRAFT,
    SubmissionStatus.SUBMITTED,
    SubmissionStatus.SCREENING,
    SubmissionStatus.UNDER_REVIEW,
    SubmissionStatus.AWAITING_DECISION,
    SubmissionStatus.REVISION_REQUESTED,
    SubmissionStatus.RESUBMITTED,
)

#: Production stage states, in order.
PRODUCTION_STATES: tuple[str, ...] = (
    SubmissionStatus.ACCEPTED,
    SubmissionStatus.COPYEDITING,
    SubmissionStatus.AUTHOR_PROOF,
    SubmissionStatus.TYPESETTING,
    SubmissionStatus.READY_TO_PUBLISH,
)


class SubmissionQuerySet(models.QuerySet):
    """Query helpers used by the editorial dashboards."""

    def active(self) -> SubmissionQuerySet:
        """Submissions still moving through the workflow."""
        return self.exclude(
            status__in=[
                SubmissionStatus.DRAFT,
                SubmissionStatus.REJECTED,
                SubmissionStatus.WITHDRAWN,
                SubmissionStatus.PUBLISHED,
            ]
        )

    def for_editor(self, user) -> SubmissionQuerySet:
        """Submissions an editor is allowed to see."""
        from apps.accounts.models import Role

        if user.is_superuser or user.has_role(Role.EDITOR_IN_CHIEF, Role.ADMIN):
            return self.exclude(status=SubmissionStatus.DRAFT)
        return (
            self.exclude(status=SubmissionStatus.DRAFT)
            .filter(models.Q(assigned_editor=user) | models.Q(section__editors=user))
            .distinct()
        )

    def with_related(self) -> SubmissionQuerySet:
        """Prefetch related objects needed by list templates."""
        return self.select_related("section", "submitter", "assigned_editor").prefetch_related(
            "authors", "rounds"
        )


class Submission(TimeStampedModel):
    """A manuscript moving through screening, review, decision and production."""

    class ArticleType(models.TextChoices):
        RESEARCH = "research", _("Research article")
        REVIEW = "review", _("Review article")
        SHORT = "short_communication", _("Short communication")
        BOOK_REVIEW = "book_review", _("Book review")

    reference = models.CharField(
        _("submission ID"), max_length=32, unique=True, blank=True, null=True, db_index=True
    )
    article = models.OneToOneField(
        "journal.Article",
        verbose_name=_("published article"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="source_submission",
    )
    submitter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("submitter"),
        on_delete=models.PROTECT,
        related_name="submissions",
    )
    section = models.ForeignKey(
        "journal.Section",
        verbose_name=_("section"),
        on_delete=models.PROTECT,
        related_name="submissions",
    )
    article_type = models.CharField(
        _("article type"), max_length=32, choices=ArticleType.choices, default=ArticleType.RESEARCH
    )

    title = models.CharField(_("title"), max_length=500)
    abstract = models.TextField(_("abstract"), blank=True)
    keywords_text = models.CharField(
        _("keywords"), max_length=500, blank=True, help_text=_("Comma-separated, 5–8 keywords.")
    )
    jel_codes = models.ManyToManyField(
        "journal.JELCode", verbose_name=_("JEL codes"), blank=True, related_name="submissions"
    )
    language = models.CharField(
        _("manuscript language"),
        max_length=10,
        default="en",
        choices=[("en", "English"), ("uz", "Oʻzbekcha"), ("ru", "Русский")],
    )
    word_count = models.PositiveIntegerField(_("word count"), default=0)
    cover_letter = models.TextField(_("cover letter"), blank=True)

    status = models.CharField(
        _("status"),
        max_length=32,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.DRAFT,
        db_index=True,
    )
    current_round = models.PositiveSmallIntegerField(_("current round"), default=0)
    wizard_step = models.PositiveSmallIntegerField(_("wizard step"), default=1)

    assigned_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("handling editor"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="handled_submissions",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("assigned by"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="editor_assignments_made",
    )

    submitted_at = models.DateTimeField(_("submitted at"), null=True, blank=True, db_index=True)
    last_activity_at = models.DateTimeField(_("last activity"), default=timezone.now)
    accepted_at = models.DateTimeField(_("accepted at"), null=True, blank=True)

    is_withdrawn = models.BooleanField(_("withdrawn"), default=False)
    withdraw_reason = models.TextField(_("withdrawal reason"), blank=True)

    similarity_percent = models.FloatField(
        _("similarity (%)"),
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    similarity_report = models.FileField(
        _("similarity report"), upload_to=similarity_report_upload_to, null=True, blank=True
    )
    similarity_checked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("similarity checked by"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="similarity_checks",
    )
    similarity_checked_at = models.DateTimeField(_("similarity checked at"), null=True, blank=True)
    similarity_override_reason = models.TextField(
        _("similarity override justification"), blank=True
    )

    author_declarations = models.JSONField(_("author declarations"), default=dict, blank=True)
    suggested_reviewers = models.JSONField(_("suggested reviewers"), default=list, blank=True)
    opposed_reviewers = models.JSONField(_("opposed reviewers"), default=list, blank=True)
    anonymised_file_ok = models.BooleanField(_("manuscript is anonymised"), default=False)
    ai_use_statement = models.TextField(_("AI use disclosure"), blank=True)
    funding_statement = models.TextField(_("funding statement"), blank=True)
    conflict_of_interest_statement = models.TextField(
        _("conflict of interest statement"), blank=True
    )
    data_availability_statement = models.TextField(_("data availability statement"), blank=True)
    decision_letter = models.TextField(_("latest decision letter"), blank=True)

    metadata = models.JSONField(
        _("multilingual metadata"),
        default=dict,
        blank=True,
        help_text=_("Title, abstract and keywords per language, captured in the wizard."),
    )

    objects = SubmissionQuerySet.as_manager()

    class Meta:
        verbose_name = _("submission")
        verbose_name_plural = _("submissions")
        ordering: ClassVar[list[str]] = ["-last_activity_at"]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["status", "-last_activity_at"]),
            models.Index(fields=["assigned_editor", "status"]),
            models.Index(fields=["reference"]),
        ]

    def __str__(self) -> str:
        return f"{self.reference or 'DRAFT'} — {self.title[:60]}"

    def get_absolute_url(self) -> str:
        """Editorial detail page of the submission."""
        return reverse("dashboard:submission_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        """Assign a human-readable reference when the manuscript is submitted.

        Drafts keep ``NULL`` rather than an empty string so that the unique
        constraint allows any number of unsubmitted drafts.
        """
        if not self.reference and self.status != SubmissionStatus.DRAFT:
            self.reference = self.build_reference()
        if not self.reference:
            self.reference = None
        super().save(*args, **kwargs)

    def build_reference(self) -> str:
        """Generate ``ARER-<year>-<sequence>`` for this submission."""
        year = (self.submitted_at or timezone.now()).year
        prefix = f"ARER-{year}-"
        last = (
            Submission.objects.filter(reference__startswith=prefix)
            .order_by("-reference")
            .values_list("reference", flat=True)
            .first()
        )
        sequence = int(last.rsplit("-", 1)[1]) + 1 if last else 1
        return f"{prefix}{sequence:04d}"

    # --- convenience -----------------------------------------------------
    @property
    def keywords_list(self) -> list[str]:
        """Keywords as a cleaned list."""
        return [k.strip() for k in self.keywords_text.split(",") if k.strip()]

    @property
    def is_editable_by_author(self) -> bool:
        """True while the author may still change files or metadata."""
        return self.status in {SubmissionStatus.DRAFT, SubmissionStatus.REVISION_REQUESTED}

    @property
    def latest_round(self) -> ReviewRound | None:
        """Most recent review round, if any."""
        return self.rounds.order_by("-number").first()

    @property
    def similarity_ok(self) -> bool:
        """True when a similarity result exists and is within the threshold."""
        if self.similarity_percent is None:
            return False
        from apps.core.services import get_site_settings

        return self.similarity_percent <= get_site_settings().similarity_threshold

    @property
    def status_display_class(self) -> str:
        """CSS modifier used by the status chip component."""
        mapping = {
            SubmissionStatus.DRAFT: "subtle",
            SubmissionStatus.SUBMITTED: "info",
            SubmissionStatus.SCREENING: "info",
            SubmissionStatus.UNDER_REVIEW: "info",
            SubmissionStatus.AWAITING_DECISION: "warning",
            SubmissionStatus.REVISION_REQUESTED: "warning",
            SubmissionStatus.RESUBMITTED: "info",
            SubmissionStatus.ACCEPTED: "success",
            SubmissionStatus.PUBLISHED: "success",
            SubmissionStatus.PUBLISHED_ONLINE_FIRST: "success",
            SubmissionStatus.REJECTED: "danger",
            SubmissionStatus.WITHDRAWN: "danger",
        }
        return mapping.get(self.status, "info")


class SubmissionAuthor(TimeStampedModel):
    """An author declared on a submission (copied to the article on acceptance)."""

    submission = models.ForeignKey(
        Submission, verbose_name=_("submission"), on_delete=models.CASCADE, related_name="authors"
    )
    order = models.PositiveSmallIntegerField(_("order"), default=1)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("account"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="submission_authorships",
    )
    given_name = models.CharField(_("given name"), max_length=128)
    family_name = models.CharField(_("family name"), max_length=128)
    email = models.EmailField(_("e-mail"))
    is_corresponding = models.BooleanField(_("corresponding author"), default=False)
    orcid = models.CharField(_("ORCID iD"), max_length=19, blank=True)
    orcid_verified = models.BooleanField(_("ORCID verified"), default=False)
    affiliation = models.CharField(_("affiliation"), max_length=300, blank=True)
    affiliation_ror = models.CharField(_("ROR ID"), max_length=64, blank=True)
    city = models.CharField(_("city"), max_length=128, blank=True)
    country = CountryField(_("country"), blank=True)
    contribution = models.TextField(_("contribution"), blank=True)
    credit_roles = models.JSONField(_("CRediT roles"), default=list, blank=True)

    class Meta:
        verbose_name = _("submission author")
        verbose_name_plural = _("submission authors")
        ordering: ClassVar[list[str]] = ["submission", "order"]

    def __str__(self) -> str:
        return self.full_name

    @property
    def full_name(self) -> str:
        """``Given Family``."""
        return f"{self.given_name} {self.family_name}".strip()


class SubmissionFile(TimeStampedModel):
    """A file uploaded against a submission at some stage of the workflow."""

    class Kind(models.TextChoices):
        MANUSCRIPT_ANON = "manuscript_anon", _("Anonymised manuscript")
        TITLE_PAGE = "title_page", _("Title page")
        FIGURES = "figures", _("Figures and tables")
        DATA = "data", _("Data")
        SUPPLEMENTARY = "supplementary", _("Supplementary material")
        REVISION = "revision", _("Revised manuscript")
        RESPONSE = "response_to_reviewers", _("Response to reviewers")
        COPYEDITED = "copyedited", _("Copyedited manuscript")
        PROOF = "proof", _("Proof")
        FINAL = "final", _("Final version")

    #: Kinds a reviewer is allowed to download.
    REVIEWER_VISIBLE_KINDS: ClassVar[tuple[str, ...]] = (
        Kind.MANUSCRIPT_ANON,
        Kind.FIGURES,
        Kind.REVISION,
    )

    submission = models.ForeignKey(
        Submission, verbose_name=_("submission"), on_delete=models.CASCADE, related_name="files"
    )
    round = models.ForeignKey(
        "submissions.ReviewRound",
        verbose_name=_("round"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="files",
    )
    kind = models.CharField(_("kind"), max_length=32, choices=Kind.choices, db_index=True)
    file = models.FileField(_("file"), upload_to=submission_file_upload_to)
    original_name = models.CharField(_("original file name"), max_length=255, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("uploaded by"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="uploaded_submission_files",
    )
    version = models.PositiveSmallIntegerField(_("version"), default=1)
    size = models.PositiveIntegerField(_("size"), default=0)
    mime = models.CharField(_("MIME type"), max_length=128, blank=True)
    is_visible_to_reviewers = models.BooleanField(_("visible to reviewers"), default=False)

    class Meta:
        verbose_name = _("submission file")
        verbose_name_plural = _("submission files")
        ordering: ClassVar[list[str]] = ["submission", "kind", "-version"]
        indexes: ClassVar[list[models.Index]] = [models.Index(fields=["submission", "kind"])]

    def __str__(self) -> str:
        return f"{self.get_kind_display()} v{self.version}"

    def get_absolute_url(self) -> str:
        """Authenticated download route."""
        return reverse("dashboard:submission_file", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        """Default reviewer visibility from the file kind."""
        if self._state.adding:
            self.is_visible_to_reviewers = self.kind in self.REVIEWER_VISIBLE_KINDS
            if self.file and not self.size:
                self.size = getattr(self.file, "size", 0) or 0
        super().save(*args, **kwargs)


class ReviewRound(TimeStampedModel):
    """One round of peer review on a submission."""

    class Status(models.TextChoices):
        OPEN = "open", _("Open")
        CLOSED = "closed", _("Closed")

    submission = models.ForeignKey(
        Submission, verbose_name=_("submission"), on_delete=models.CASCADE, related_name="rounds"
    )
    number = models.PositiveSmallIntegerField(_("round number"), default=1)
    opened_at = models.DateTimeField(_("opened at"), default=timezone.now)
    closed_at = models.DateTimeField(_("closed at"), null=True, blank=True)
    status = models.CharField(
        _("status"), max_length=16, choices=Status.choices, default=Status.OPEN
    )

    class Meta:
        verbose_name = _("review round")
        verbose_name_plural = _("review rounds")
        ordering: ClassVar[list[str]] = ["submission", "number"]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(fields=["submission", "number"], name="unique_round_number")
        ]

    def __str__(self) -> str:
        return f"Round {self.number} of {self.submission_id}"

    @property
    def is_complete(self) -> bool:
        """True when every accepted assignment has a submitted review."""
        active = self.assignments.exclude(
            status__in=[ReviewAssignment.Status.DECLINED, ReviewAssignment.Status.CANCELLED]
        )
        return (
            active.exists()
            and not active.exclude(status=ReviewAssignment.Status.SUBMITTED).exists()
        )


class ReviewAssignment(TimeStampedModel):
    """An invitation for one reviewer to review one round."""

    class Status(models.TextChoices):
        INVITED = "invited", _("Invited")
        ACCEPTED = "accepted", _("Accepted")
        DECLINED = "declined", _("Declined")
        SUBMITTED = "submitted", _("Review submitted")
        CANCELLED = "cancelled", _("Cancelled")
        OVERDUE = "overdue", _("Overdue")

    class Response(models.TextChoices):
        PENDING = "pending", _("Pending")
        ACCEPTED = "accepted", _("Accepted")
        DECLINED = "declined", _("Declined")

    round = models.ForeignKey(
        ReviewRound, verbose_name=_("round"), on_delete=models.CASCADE, related_name="assignments"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("reviewer"),
        on_delete=models.CASCADE,
        related_name="review_assignments",
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("invited by"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="review_invitations_sent",
    )
    invited_at = models.DateTimeField(_("invited at"), default=timezone.now)
    responded_at = models.DateTimeField(_("responded at"), null=True, blank=True)
    response = models.CharField(
        _("response"), max_length=16, choices=Response.choices, default=Response.PENDING
    )
    decline_reason = models.TextField(_("decline reason"), blank=True)
    due_at = models.DateTimeField(_("due at"))
    completed_at = models.DateTimeField(_("completed at"), null=True, blank=True)
    reminders_sent = models.PositiveSmallIntegerField(_("reminders sent"), default=0)
    last_reminder_at = models.DateTimeField(_("last reminder"), null=True, blank=True)
    access_token = models.CharField(_("access token"), max_length=64, unique=True, blank=True)
    status = models.CharField(
        _("status"), max_length=16, choices=Status.choices, default=Status.INVITED, db_index=True
    )

    class Meta:
        verbose_name = _("review assignment")
        verbose_name_plural = _("review assignments")
        ordering: ClassVar[list[str]] = ["-invited_at"]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(fields=["round", "reviewer"], name="unique_reviewer_per_round")
        ]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["reviewer", "status"]),
            models.Index(fields=["status", "due_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.reviewer} → round {self.round_id}"

    def save(self, *args, **kwargs):
        """Generate a one-click access token and a default due date."""
        if not self.access_token:
            self.access_token = secrets.token_urlsafe(32)[:64]
        if not self.due_at:
            self.due_at = timezone.now() + timedelta(days=settings.REVIEW_DUE_DAYS)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Reviewer-facing page for this assignment."""
        return reverse("review:assignment_detail", kwargs={"pk": self.pk})

    @property
    def days_remaining(self) -> int:
        """Whole days left before the review is due (may be negative)."""
        return (self.due_at - timezone.now()).days

    @property
    def is_overdue(self) -> bool:
        """True when the due date passed without a submitted review."""
        return (
            self.status in {self.Status.ACCEPTED, self.Status.INVITED, self.Status.OVERDUE}
            and self.due_at < timezone.now()
        )

    @property
    def submission(self) -> Submission:
        """Shortcut to the submission being reviewed."""
        return self.round.submission


class Review(TimeStampedModel):
    """A completed structured review."""

    class Recommendation(models.TextChoices):
        ACCEPT = "accept", _("Accept")
        MINOR = "minor_revision", _("Minor revision")
        MAJOR = "major_revision", _("Major revision")
        REJECT = "reject", _("Reject")

    #: The six scored criteria of the structured review form.
    SCORE_FIELDS: ClassVar[list[tuple[str, str]]] = [
        ("originality", _("Originality and novelty")),
        ("relevance", _("Relevance to the journal's scope")),
        ("methodology", _("Methodological rigour")),
        ("results", _("Data and results")),
        ("literature", _("Coverage of the literature")),
        ("writing", _("Writing and structure")),
    ]

    assignment = models.OneToOneField(
        ReviewAssignment,
        verbose_name=_("assignment"),
        on_delete=models.CASCADE,
        related_name="review",
    )
    recommendation = models.CharField(
        _("recommendation"), max_length=16, choices=Recommendation.choices
    )
    scores = models.JSONField(_("scores"), default=dict, blank=True)
    comments_to_authors = models.TextField(_("comments to the authors"))
    comments_to_editor = models.TextField(_("confidential comments to the editor"), blank=True)
    attachment = models.FileField(
        _("annotated file"), upload_to=review_attachment_upload_to, null=True, blank=True
    )
    is_anonymised = models.BooleanField(_("attachment metadata stripped"), default=False)
    submitted_at = models.DateTimeField(_("submitted at"), null=True, blank=True)
    quality_rating = models.PositiveSmallIntegerField(
        _("review quality (1–5)"),
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    is_draft = models.BooleanField(_("draft"), default=True)

    class Meta:
        verbose_name = _("review")
        verbose_name_plural = _("reviews")
        ordering: ClassVar[list[str]] = ["-submitted_at"]

    def __str__(self) -> str:
        return f"Review for assignment {self.assignment_id}"

    @property
    def average_score(self) -> float | None:
        """Mean of the six criteria scores."""
        values = [v for v in self.scores.values() if isinstance(v, (int, float))]
        return round(sum(values) / len(values), 2) if values else None

    @property
    def score_rows(self) -> list[dict[str, object]]:
        """Score criteria with labels, for template rendering."""
        return [
            {"key": key, "label": label, "value": self.scores.get(key)}
            for key, label in self.SCORE_FIELDS
        ]


class EditorialDecision(TimeStampedModel):
    """A recorded editorial decision on one round of a submission."""

    class Decision(models.TextChoices):
        DESK_REJECT = "desk_reject", _("Desk reject")
        SEND_TO_REVIEW = "send_to_review", _("Send to review")
        ACCEPT = "accept", _("Accept")
        MINOR_REVISION = "minor_revision", _("Minor revision")
        MAJOR_REVISION = "major_revision", _("Major revision")
        REJECT = "reject", _("Reject")
        RESUBMIT = "resubmit", _("Reject with resubmission encouraged")

    submission = models.ForeignKey(
        Submission,
        verbose_name=_("submission"),
        on_delete=models.CASCADE,
        related_name="decisions",
    )
    round = models.ForeignKey(
        ReviewRound,
        verbose_name=_("round"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="decisions",
    )
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("decided by"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="decisions_made",
    )
    decision = models.CharField(_("decision"), max_length=32, choices=Decision.choices)
    letter = models.TextField(_("decision letter"), blank=True)
    decided_at = models.DateTimeField(_("decided at"), default=timezone.now, db_index=True)
    emailed_at = models.DateTimeField(_("e-mailed at"), null=True, blank=True)

    class Meta:
        verbose_name = _("editorial decision")
        verbose_name_plural = _("editorial decisions")
        ordering: ClassVar[list[str]] = ["-decided_at"]
        indexes: ClassVar[list[models.Index]] = [models.Index(fields=["submission", "-decided_at"])]

    def __str__(self) -> str:
        return f"{self.get_decision_display()} — {self.submission_id}"


class RevisionRequest(TimeStampedModel):
    """A request for the author to revise and resubmit."""

    submission = models.ForeignKey(
        Submission,
        verbose_name=_("submission"),
        on_delete=models.CASCADE,
        related_name="revision_requests",
    )
    round = models.ForeignKey(
        ReviewRound,
        verbose_name=_("round"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="revision_requests",
    )
    decision = models.ForeignKey(
        EditorialDecision,
        verbose_name=_("decision"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="revision_requests",
    )
    is_major = models.BooleanField(_("major revision"), default=False)
    due_at = models.DateTimeField(_("due at"))
    submitted_at = models.DateTimeField(_("author responded at"), null=True, blank=True)
    response_letter = models.TextField(_("response to reviewers"), blank=True)
    reminder_sent_at = models.DateTimeField(_("reminder sent"), null=True, blank=True)

    class Meta:
        verbose_name = _("revision request")
        verbose_name_plural = _("revision requests")
        ordering: ClassVar[list[str]] = ["-created_at"]

    def __str__(self) -> str:
        kind = _("major") if self.is_major else _("minor")
        return f"{kind} revision for {self.submission_id}"


class Discussion(TimeStampedModel):
    """A message thread attached to a submission."""

    class Visibility(models.TextChoices):
        AUTHOR_EDITOR = "author_editor", _("Author ↔ Editor")
        EDITOR_REVIEWER = "editor_reviewer", _("Editor ↔ Reviewer")
        EDITOR_PRODUCTION = "editor_production", _("Editor ↔ Production")
        EDITORS_ONLY = "editors_only", _("Editors only")

    submission = models.ForeignKey(
        Submission,
        verbose_name=_("submission"),
        on_delete=models.CASCADE,
        related_name="discussions",
    )
    subject = models.CharField(_("subject"), max_length=255)
    visibility = models.CharField(
        _("visibility"),
        max_length=32,
        choices=Visibility.choices,
        default=Visibility.AUTHOR_EDITOR,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("created by"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="discussions_started",
    )
    is_closed = models.BooleanField(_("closed"), default=False)

    class Meta:
        verbose_name = _("discussion")
        verbose_name_plural = _("discussions")
        ordering: ClassVar[list[str]] = ["-created_at"]

    def __str__(self) -> str:
        return self.subject


class DiscussionMessage(TimeStampedModel):
    """One message inside a discussion thread."""

    discussion = models.ForeignKey(
        Discussion, verbose_name=_("discussion"), on_delete=models.CASCADE, related_name="messages"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("author"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="discussion_messages",
    )
    body = models.TextField(_("message"))
    is_system = models.BooleanField(_("system message"), default=False)

    class Meta:
        verbose_name = _("discussion message")
        verbose_name_plural = _("discussion messages")
        ordering: ClassVar[list[str]] = ["created_at"]

    def __str__(self) -> str:
        return self.body[:60]


class EditorNote(TimeStampedModel):
    """A private note visible only to editorial staff."""

    submission = models.ForeignKey(
        Submission, verbose_name=_("submission"), on_delete=models.CASCADE, related_name="notes"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("author"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="editor_notes",
    )
    body = models.TextField(_("note"))

    class Meta:
        verbose_name = _("editor note")
        verbose_name_plural = _("editor notes")
        ordering: ClassVar[list[str]] = ["-created_at"]

    def __str__(self) -> str:
        return self.body[:60]


class ProductionTask(TimeStampedModel):
    """One stage of the production checklist for an accepted manuscript."""

    class Stage(models.TextChoices):
        COPYEDITING = "copyediting", _("Copyediting")
        AUTHOR_PROOF = "author_proof", _("Author proof")
        TYPESETTING = "typesetting", _("Typesetting")
        METADATA = "metadata", _("Metadata completion")
        DOI = "doi", _("DOI assignment")
        SCHEDULED = "scheduled", _("Scheduled to issue")

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        IN_PROGRESS = "in_progress", _("In progress")
        DONE = "done", _("Done")
        BLOCKED = "blocked", _("Blocked")

    #: Canonical order of the production stages.
    STAGE_ORDER: ClassVar[list[str]] = [
        Stage.COPYEDITING,
        Stage.AUTHOR_PROOF,
        Stage.TYPESETTING,
        Stage.METADATA,
        Stage.DOI,
        Stage.SCHEDULED,
    ]

    submission = models.ForeignKey(
        Submission,
        verbose_name=_("submission"),
        on_delete=models.CASCADE,
        related_name="production_tasks",
    )
    stage = models.CharField(_("stage"), max_length=32, choices=Stage.choices)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("assignee"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="production_tasks",
    )
    status = models.CharField(
        _("status"), max_length=16, choices=Status.choices, default=Status.PENDING
    )
    due_at = models.DateTimeField(_("due at"), null=True, blank=True)
    completed_at = models.DateTimeField(_("completed at"), null=True, blank=True)
    notes = models.TextField(_("notes"), blank=True)

    class Meta:
        verbose_name = _("production task")
        verbose_name_plural = _("production tasks")
        ordering: ClassVar[list[str]] = ["submission", "id"]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(fields=["submission", "stage"], name="unique_production_stage")
        ]

    def __str__(self) -> str:
        return f"{self.get_stage_display()} — {self.submission_id}"
