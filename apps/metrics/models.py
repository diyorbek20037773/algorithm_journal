"""Usage statistics: raw access events, daily aggregates and editorial KPIs."""

from __future__ import annotations

from typing import ClassVar

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class AccessEvent(models.Model):
    """A single article view or galley download.

    IP addresses are never stored: only a salted SHA-256 hash, so that the
    double-click filter and bot detection work without keeping personal data
    (SPEC §5.5, D20).
    """

    class Kind(models.TextChoices):
        VIEW = "view", _("View")
        DOWNLOAD = "download", _("Download")

    article = models.ForeignKey(
        "journal.Article",
        verbose_name=_("article"),
        on_delete=models.CASCADE,
        related_name="access_events",
    )
    kind = models.CharField(_("kind"), max_length=16, choices=Kind.choices, db_index=True)
    galley = models.ForeignKey(
        "journal.Galley",
        verbose_name=_("galley"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="access_events",
    )
    occurred_at = models.DateTimeField(_("occurred at"), default=timezone.now, db_index=True)
    ip_hash = models.CharField(_("IP hash"), max_length=64, db_index=True)
    user_agent_hash = models.CharField(_("user agent hash"), max_length=64, blank=True)
    session_key_hash = models.CharField(_("session hash"), max_length=64, blank=True)
    country = models.CharField(_("country"), max_length=2, blank=True)
    is_bot = models.BooleanField(_("bot"), default=False, db_index=True)

    class Meta:
        verbose_name = _("access event")
        verbose_name_plural = _("access events")
        ordering: ClassVar[list[str]] = ["-occurred_at"]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["article", "kind", "-occurred_at"]),
            models.Index(fields=["ip_hash", "article", "kind", "-occurred_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.kind} #{self.article_id} @ {self.occurred_at:%Y-%m-%d %H:%M}"


class DailyArticleStat(models.Model):
    """Nightly aggregate of views and downloads for one article and day."""

    article = models.ForeignKey(
        "journal.Article",
        verbose_name=_("article"),
        on_delete=models.CASCADE,
        related_name="daily_stats",
    )
    date = models.DateField(_("date"), db_index=True)
    views = models.PositiveIntegerField(_("views"), default=0)
    downloads = models.PositiveIntegerField(_("downloads"), default=0)

    class Meta:
        verbose_name = _("daily article statistic")
        verbose_name_plural = _("daily article statistics")
        ordering: ClassVar[list[str]] = ["-date"]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(fields=["article", "date"], name="unique_daily_article_stat")
        ]
        indexes: ClassVar[list[models.Index]] = [models.Index(fields=["date", "article"])]

    def __str__(self) -> str:
        return f"#{self.article_id} {self.date}: {self.views}v/{self.downloads}d"


class EditorialKPI(TimeStampedModel):
    """Monthly snapshot of editorial performance indicators."""

    month = models.DateField(_("month"), unique=True, help_text=_("First day of the month."))
    submissions_received = models.PositiveIntegerField(_("submissions received"), default=0)
    desk_rejected = models.PositiveIntegerField(_("desk rejected"), default=0)
    sent_to_review = models.PositiveIntegerField(_("sent to review"), default=0)
    accepted = models.PositiveIntegerField(_("accepted"), default=0)
    rejected = models.PositiveIntegerField(_("rejected"), default=0)
    published = models.PositiveIntegerField(_("published"), default=0)
    acceptance_rate = models.FloatField(_("acceptance rate (%)"), null=True, blank=True)
    median_days_to_first_decision = models.FloatField(
        _("median days to first decision"), null=True, blank=True
    )
    median_review_days = models.FloatField(_("median review days"), null=True, blank=True)
    active_reviewers = models.PositiveIntegerField(_("active reviewers"), default=0)
    author_countries = models.JSONField(_("author countries"), default=dict, blank=True)

    class Meta:
        verbose_name = _("editorial KPI")
        verbose_name_plural = _("editorial KPIs")
        ordering: ClassVar[list[str]] = ["-month"]

    def __str__(self) -> str:
        return f"KPI {self.month:%Y-%m}"
