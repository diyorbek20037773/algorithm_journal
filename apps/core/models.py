"""Site-wide configuration, CMS pages, announcements and contact messages."""

from __future__ import annotations

from typing import ClassVar

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.markdown import render_markdown


class TimeStampedModel(models.Model):
    """Abstract base adding ``created_at`` / ``updated_at`` to a model."""

    created_at = models.DateTimeField(_("created at"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        abstract = True


class AutoTranslitMixin(models.Model):
    """Adds bookkeeping for machine-generated Uzbek Cyrillic field values.

    ``apps.core.signals.fill_uz_cyrl`` transliterates every empty ``*_uz_cyrl``
    field from its ``*_uz` counterpart and records the field name here, so the
    admin can show editors exactly what was machine generated.
    """

    auto_translit = models.JSONField(
        _("machine-generated fields"), default=dict, blank=True, editable=False
    )

    class Meta:
        abstract = True

    @property
    def auto_translit_fields(self) -> list[str]:
        """Names of the fields that were filled by the transliterator."""
        return sorted(self.auto_translit.keys()) if isinstance(self.auto_translit, dict) else []


class SiteSettings(TimeStampedModel, AutoTranslitMixin):
    """Singleton holding every piece of journal identity shown on the site.

    Nothing about the journal (name, ISSN, DOI prefix, publisher, contacts) may
    be hard-coded in templates — it is all read from this row.
    """

    SINGLETON_PK = 1

    journal_name = models.CharField(
        _("journal name"), max_length=255, default="ALGORITHM: Review of Economic Research"
    )
    journal_subtitle = models.CharField(_("journal subtitle"), max_length=255, blank=True)
    short_code = models.CharField(_("short code"), max_length=16, default="ARER")

    eissn = models.CharField(_("e-ISSN"), max_length=9, blank=True)
    pissn = models.CharField(_("print ISSN"), max_length=9, blank=True)
    registration_certificate_number = models.CharField(
        _("registration certificate number"), max_length=64, blank=True
    )
    registration_certificate_date = models.DateField(
        _("registration certificate date"), null=True, blank=True
    )
    registration_authority = models.CharField(
        _("registration authority"), max_length=255, blank=True
    )

    publisher_name = models.CharField(
        _("publisher"), max_length=255, default="Founder organisation (to be confirmed)"
    )
    publisher_address = models.TextField(_("publisher address"), blank=True)
    founded_year = models.PositiveIntegerField(_("founded year"), default=2026)
    doi_prefix = models.CharField(_("DOI prefix"), max_length=32, blank=True)
    frequency_text = models.CharField(
        _("publication frequency"), max_length=255, default="Monthly (12 issues per year)"
    )

    contact_email = models.EmailField(_("contact e-mail"), default="editor@localhost")
    contact_phone = models.CharField(_("contact phone"), max_length=64, blank=True)
    contact_address = models.TextField(_("contact address"), blank=True)

    editor_in_chief = models.ForeignKey(
        "journal.EditorialBoardMember",
        verbose_name=_("editor-in-chief"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    logo = models.ImageField(_("logo"), upload_to="branding/", blank=True, null=True)
    logo_dark = models.ImageField(_("logo (dark)"), upload_to="branding/", blank=True, null=True)
    favicon = models.ImageField(_("favicon"), upload_to="branding/", blank=True, null=True)

    social_links = models.JSONField(_("social links"), default=dict, blank=True)
    google_scholar_url = models.URLField(_("Google Scholar profile"), blank=True)
    crossref_member_id = models.CharField(_("Crossref member ID"), max_length=32, blank=True)

    similarity_threshold = models.PositiveSmallIntegerField(
        _("maximum similarity (%)"),
        default=20,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    announcement_bar_text = models.CharField(
        _("announcement bar text"), max_length=255, blank=True, null=True
    )
    matomo_site_id = models.CharField(_("Matomo site ID"), max_length=16, blank=True)
    indexing_badges = models.ManyToManyField(
        "core.IndexingService", verbose_name=_("indexing services"), blank=True
    )
    show_online_first = models.BooleanField(_("show Online First"), default=True)

    class Meta:
        verbose_name = _("site settings")
        verbose_name_plural = _("site settings")

    def __str__(self) -> str:
        return self.journal_name

    def save(self, *args, **kwargs):
        """Force the singleton primary key and clear the cached instance.

        Constructing a second ``SiteSettings()`` and saving it updates the one
        row instead of raising a duplicate-key error.
        """
        self.pk = self.SINGLETON_PK
        existing = SiteSettings.objects.filter(pk=self.pk).values("created_at").first()
        if self._state.adding and existing is not None:
            self._state.adding = False
            self.created_at = existing["created_at"]
            kwargs.pop("force_insert", None)
        super().save(*args, **kwargs)
        from django.core.cache import cache

        cache.delete("site_settings")

    def delete(self, *args, **kwargs):  # pragma: no cover - guarded singleton
        """Refuse deletion: the site cannot run without settings."""
        raise ValidationError(_("Site settings cannot be deleted."))

    @classmethod
    def load(cls) -> SiteSettings:
        """Return the singleton, creating it with defaults when missing."""
        obj, _created = cls.objects.get_or_create(pk=cls.SINGLETON_PK)
        return obj

    @property
    def eissn_display(self) -> str:
        """Human-readable e-ISSN, or a clear pending marker."""
        return self.eissn or str(_("pending"))

    @property
    def doi_prefix_display(self) -> str:
        """DOI prefix from the database, falling back to the environment."""
        return self.doi_prefix or settings.DOI_PREFIX

    @property
    def has_identifiers(self) -> bool:
        """True when both e-ISSN and DOI prefix are real (not placeholders)."""
        return bool(self.eissn) and self.doi_prefix_display != "10.00000"


class IndexingService(TimeStampedModel):
    """An abstracting/indexing service the journal is (or aims to be) listed in."""

    name = models.CharField(_("name"), max_length=128, unique=True)
    slug = models.SlugField(_("slug"), max_length=128, unique=True)
    logo = models.ImageField(_("logo"), upload_to="indexing/", blank=True, null=True)
    url = models.URLField(_("URL"), blank=True)
    is_active = models.BooleanField(
        _("active"), default=False, help_text=_("Only active services are displayed publicly.")
    )
    order = models.PositiveSmallIntegerField(_("order"), default=0)
    note = models.CharField(_("note"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("indexing service")
        verbose_name_plural = _("indexing services")
        ordering: ClassVar[list[str]] = ["order", "name"]

    def __str__(self) -> str:
        return self.name


class PageQuerySet(models.QuerySet):
    """Query helpers for CMS pages."""

    def published(self) -> PageQuerySet:
        """Only pages visible to the public."""
        return self.filter(is_published=True)

    def in_menu(self, group: str) -> PageQuerySet:
        """Published pages belonging to a navigation group, in menu order."""
        return self.published().filter(menu_group=group).order_by("menu_order", "title")


class Page(TimeStampedModel, AutoTranslitMixin):
    """A Markdown-authored content page (About, policies, guidelines…)."""

    class MenuGroup(models.TextChoices):
        ABOUT = "about", _("About")
        AUTHORS = "authors", _("For Authors")
        REVIEWERS = "reviewers", _("For Reviewers")
        FOOTER = "footer", _("Footer")
        NONE = "none", _("Not in menu")

    slug = models.SlugField(_("slug"), max_length=128, unique=True)
    title = models.CharField(_("title"), max_length=255)
    body = models.TextField(_("body (Markdown)"), blank=True)
    parent = models.ForeignKey(
        "self",
        verbose_name=_("parent page"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    menu_group = models.CharField(
        _("menu group"), max_length=16, choices=MenuGroup.choices, default=MenuGroup.ABOUT
    )
    menu_order = models.PositiveSmallIntegerField(_("menu order"), default=0)
    is_published = models.BooleanField(_("published"), default=True)
    seo_description = models.CharField(_("SEO description"), max_length=300, blank=True)
    needs_editorial_review = models.BooleanField(
        _("needs editorial review"),
        default=False,
        help_text=_("Machine-drafted translations are flagged for proofreading."),
    )

    objects = PageQuerySet.as_manager()

    class Meta:
        verbose_name = _("page")
        verbose_name_plural = _("pages")
        ordering: ClassVar[list[str]] = ["menu_group", "menu_order", "title"]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["menu_group", "menu_order"]),
            models.Index(fields=["is_published"]),
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        """Canonical URL of the page inside the About section."""
        return reverse("core:page", kwargs={"slug": self.slug})

    @property
    def body_html(self) -> str:
        """Sanitised HTML rendering of the Markdown body."""
        return render_markdown(self.body)


class MenuItem(TimeStampedModel):
    """A free-form navigation link that is not backed by a CMS page."""

    label = models.CharField(_("label"), max_length=128)
    url = models.CharField(_("URL"), max_length=255)
    group = models.CharField(
        _("menu group"),
        max_length=16,
        choices=Page.MenuGroup.choices,
        default=Page.MenuGroup.FOOTER,
    )
    order = models.PositiveSmallIntegerField(_("order"), default=0)
    is_active = models.BooleanField(_("active"), default=True)
    open_in_new_tab = models.BooleanField(_("open in a new tab"), default=False)

    class Meta:
        verbose_name = _("menu item")
        verbose_name_plural = _("menu items")
        ordering: ClassVar[list[str]] = ["group", "order", "label"]

    def __str__(self) -> str:
        return self.label


class AnnouncementQuerySet(models.QuerySet):
    """Query helpers for announcements."""

    def live(self) -> AnnouncementQuerySet:
        """Published announcements that have not expired."""
        now = timezone.now()
        return self.filter(published_at__lte=now).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gte=now)
        )


class Announcement(TimeStampedModel, AutoTranslitMixin):
    """News item or call for papers shown on the home page and its own list."""

    title = models.CharField(_("title"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=255, unique=True)
    body = models.TextField(_("body (Markdown)"))
    published_at = models.DateTimeField(_("published at"), default=timezone.now, db_index=True)
    expires_at = models.DateTimeField(_("expires at"), null=True, blank=True)
    is_pinned = models.BooleanField(_("pinned"), default=False)

    objects = AnnouncementQuerySet.as_manager()

    class Meta:
        verbose_name = _("announcement")
        verbose_name_plural = _("announcements")
        ordering: ClassVar[list[str]] = ["-is_pinned", "-published_at"]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["-published_at"]),
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        """Canonical URL of the announcement detail page."""
        return reverse("core:announcement_detail", kwargs={"slug": self.slug})

    @property
    def body_html(self) -> str:
        """Sanitised HTML rendering of the Markdown body."""
        return render_markdown(self.body)


class ContactMessage(TimeStampedModel):
    """A message sent through the public contact form."""

    name = models.CharField(_("name"), max_length=255)
    email = models.EmailField(_("e-mail"))
    subject = models.CharField(_("subject"), max_length=255)
    body = models.TextField(_("message"))
    ip = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    is_handled = models.BooleanField(_("handled"), default=False)
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("handled by"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="handled_contact_messages",
    )

    class Meta:
        verbose_name = _("contact message")
        verbose_name_plural = _("contact messages")
        ordering: ClassVar[list[str]] = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.subject} — {self.email}"


class EmailTemplate(TimeStampedModel, AutoTranslitMixin):
    """Editable transactional e-mail template, translated into every locale."""

    class Event(models.TextChoices):
        SIGNUP_VERIFY = "signup_verify", _("Account verification")
        SUBMISSION_RECEIVED_AUTHOR = (
            "submission_received_author",
            _("Submission received (author)"),
        )
        SUBMISSION_RECEIVED_EDITOR = (
            "submission_received_editor",
            _("Submission received (editor)"),
        )
        EDITOR_ASSIGNED = "editor_assigned", _("Editor assigned")
        REVIEWER_INVITE = "reviewer_invite", _("Reviewer invitation")
        REVIEWER_REMINDER = "reviewer_reminder", _("Reviewer reminder")
        REVIEWER_THANKS = "reviewer_thanks", _("Reviewer thanks")
        DECISION = "decision", _("Editorial decision")
        REVISION_REMINDER = "revision_reminder", _("Revision reminder")
        PROOF_REQUEST = "proof_request", _("Proof request")
        PUBLISHED = "published", _("Article published")
        DOI_REGISTERED = "doi_registered", _("DOI registered")
        CONTACT_FORM = "contact_form", _("Contact form notification")

    event = models.CharField(_("event"), max_length=64, choices=Event.choices, unique=True)
    subject = models.CharField(_("subject"), max_length=255)
    body = models.TextField(_("body (Markdown)"))
    placeholders = models.TextField(
        _("available placeholders"),
        blank=True,
        help_text=_("Documented context variables, one per line."),
    )
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        verbose_name = _("e-mail template")
        verbose_name_plural = _("e-mail templates")
        ordering: ClassVar[list[str]] = ["event"]

    def __str__(self) -> str:
        return self.get_event_display()


class AuditLog(TimeStampedModel):
    """Append-only record of security- and editorially-significant actions."""

    class Action(models.TextChoices):
        LOGIN = "login", _("Login")
        LOGIN_FAILED = "login_failed", _("Failed login")
        LOGOUT = "logout", _("Logout")
        ROLE_CHANGE = "role_change", _("Role change")
        DECISION = "decision", _("Editorial decision")
        PUBLISH = "publish", _("Publish")
        UNPUBLISH = "unpublish", _("Unpublish")
        SETTINGS_CHANGE = "settings_change", _("Settings change")
        FILE_DELETE = "file_delete", _("File deletion")
        WORKFLOW = "workflow", _("Workflow transition")
        DEPOSIT = "deposit", _("Crossref deposit")
        OVERRIDE = "override", _("Policy override")

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("actor"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_entries",
    )
    action = models.CharField(_("action"), max_length=32, choices=Action.choices, db_index=True)
    target = models.CharField(_("target"), max_length=255, blank=True)
    changes = models.JSONField(_("changes"), default=dict, blank=True)
    ip = models.GenericIPAddressField(_("IP address"), null=True, blank=True)

    class Meta:
        verbose_name = _("audit log entry")
        verbose_name_plural = _("audit log")
        ordering: ClassVar[list[str]] = ["-created_at"]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["action", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.action} {self.target}"
