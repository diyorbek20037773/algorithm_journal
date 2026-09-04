"""Custom user, profile and role helpers for the editorial system."""

from __future__ import annotations

from typing import ClassVar

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from apps.core.models import TimeStampedModel


class Role(models.TextChoices):
    """Django group names used as editorial roles (SPEC §3)."""

    AUTHOR = "author", _("Author")
    REVIEWER = "reviewer", _("Reviewer")
    SECTION_EDITOR = "section_editor", _("Section editor")
    EDITOR_IN_CHIEF = "editor_in_chief", _("Editor-in-Chief")
    PRODUCTION_EDITOR = "production_editor", _("Production editor")
    ADMIN = "admin", _("Administrator")


#: Roles for which TOTP two-factor authentication is mandatory.
STAFF_ROLES: tuple[str, ...] = (
    Role.SECTION_EDITOR,
    Role.EDITOR_IN_CHIEF,
    Role.PRODUCTION_EDITOR,
    Role.ADMIN,
)


class UserManager(BaseUserManager):
    """Manager for the e-mail-as-username custom user."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra):
        if not email:
            raise ValueError("Users must have an e-mail address")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra):
        """Create a regular user identified by e-mail."""
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email: str, password: str | None = None, **extra):
        """Create a Django superuser (technical administrator)."""
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("is_active", True)
        if extra.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self._create_user(email, password, **extra)


class User(AbstractUser):
    """A platform account.  The e-mail address is the login identifier."""

    username = None  # type: ignore[assignment]
    email = models.EmailField(_("e-mail address"), unique=True, db_index=True)
    first_name = models.CharField(_("given name"), max_length=150, blank=True)
    last_name = models.CharField(_("family name"), max_length=150, blank=True)
    preferred_language = models.CharField(
        _("preferred language"),
        max_length=10,
        default="en",
        choices=[("en", "English"), ("uz", "Oʻzbekcha"), ("uz-cyrl", "Ўзбекча"), ("ru", "Русский")],
    )
    is_reviewer = models.BooleanField(
        _("available as reviewer"),
        default=False,
        help_text=_("Flagged by an editor; controls appearance in the reviewer finder."),
    )
    must_enroll_2fa = models.BooleanField(
        _("must enrol in 2FA"),
        default=False,
        help_text=_("Set for staff accounts created by seeding or by an administrator."),
    )
    last_activity_at = models.DateTimeField(_("last activity"), null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering: ClassVar[list[str]] = ["last_name", "first_name", "email"]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_reviewer"]),
        ]

    def __str__(self) -> str:
        return self.get_full_name() or self.email

    def get_full_name(self) -> str:
        """Full name, falling back to the e-mail local part."""
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.email.split("@")[0]

    def get_short_name(self) -> str:
        """Given name, or the e-mail local part."""
        return self.first_name or self.email.split("@")[0]

    def get_absolute_url(self) -> str:
        """Link to the user's dashboard profile page."""
        return reverse("dashboard:profile")

    # --- role helpers ---------------------------------------------------
    @property
    def role_names(self) -> set[str]:
        """Set of group names the user belongs to."""
        return {g.name for g in self.groups.all()}

    def has_role(self, *roles: str) -> bool:
        """True when the user belongs to any of ``roles`` (superuser: always)."""
        if self.is_superuser:
            return True
        return bool(self.role_names & set(roles))

    @property
    def is_editorial_staff(self) -> bool:
        """True for section editors, EIC, production editors and admins."""
        return self.is_superuser or bool(self.role_names & set(STAFF_ROLES))

    @property
    def requires_2fa(self) -> bool:
        """True when policy demands a confirmed TOTP device for this account."""
        return self.is_editorial_staff or self.is_staff

    @property
    def has_verified_totp(self) -> bool:
        """True when at least one confirmed TOTP device exists."""
        from django_otp.plugins.otp_totp.models import TOTPDevice

        return TOTPDevice.objects.filter(user=self, confirmed=True).exists()

    def touch_activity(self) -> None:
        """Record that the user did something (cheap, unsaved fields only)."""
        User.objects.filter(pk=self.pk).update(last_activity_at=timezone.now())


class Profile(TimeStampedModel):
    """Scholarly identity attached to every account."""

    user = models.OneToOneField(
        User, verbose_name=_("user"), on_delete=models.CASCADE, related_name="profile"
    )
    orcid = models.CharField(_("ORCID iD"), max_length=19, blank=True, db_index=True)
    orcid_verified = models.BooleanField(_("ORCID verified"), default=False)
    affiliation = models.CharField(_("affiliation"), max_length=255, blank=True)
    department = models.CharField(_("department"), max_length=255, blank=True)
    city = models.CharField(_("city"), max_length=128, blank=True)
    country = CountryField(_("country"), blank=True)
    academic_degree = models.CharField(_("academic degree"), max_length=128, blank=True)
    academic_title = models.CharField(_("academic title"), max_length=128, blank=True)
    bio = models.TextField(_("biography"), blank=True)
    website = models.URLField(_("website"), blank=True)
    scopus_author_id = models.CharField(_("Scopus Author ID"), max_length=32, blank=True)
    expertise = models.TextField(
        _("areas of expertise"),
        blank=True,
        help_text=_("Comma-separated keywords used by the reviewer finder."),
    )
    jel_codes = models.ManyToManyField(
        "journal.JELCode", verbose_name=_("JEL codes"), blank=True, related_name="profiles"
    )
    reviews_completed = models.PositiveIntegerField(_("reviews completed"), default=0)
    reviews_declined = models.PositiveIntegerField(_("reviews declined"), default=0)
    average_review_days = models.FloatField(_("average review days"), null=True, blank=True)
    average_quality_rating = models.FloatField(_("average quality rating"), null=True, blank=True)
    accepts_review_invitations = models.BooleanField(
        _("accepts review invitations"), default=True
    )

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")
        ordering: ClassVar[list[str]] = ["user__last_name", "user__first_name"]

    def __str__(self) -> str:
        return f"Profile of {self.user}"

    def get_absolute_url(self) -> str:
        """Link to the dashboard profile editor."""
        return reverse("dashboard:profile")

    @property
    def orcid_url(self) -> str:
        """Public ORCID record URL, or an empty string."""
        return f"https://orcid.org/{self.orcid}" if self.orcid else ""

    @property
    def expertise_list(self) -> list[str]:
        """Expertise keywords as a cleaned list."""
        return [part.strip() for part in self.expertise.split(",") if part.strip()]
