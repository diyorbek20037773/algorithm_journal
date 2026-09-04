"""Crossref deposit bookkeeping."""

from __future__ import annotations

from typing import ClassVar

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class DepositBatch(TimeStampedModel):
    """One Crossref deposit submission and its outcome."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        SUBMITTED = "submitted", _("Submitted")
        SUCCESS = "success", _("Success")
        FAILED = "failed", _("Failed")

    doi_batch_id = models.CharField(_("batch ID"), max_length=64, unique=True)
    xml = models.FileField(_("deposit XML"), upload_to="crossref/", null=True, blank=True)
    articles = models.ManyToManyField(
        "journal.Article", verbose_name=_("articles"), related_name="deposit_batches", blank=True
    )
    status = models.CharField(
        _("status"), max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    response_log = models.TextField(_("response log"), blank=True)
    submitted_at = models.DateTimeField(_("submitted at"), null=True, blank=True)
    resolved_at = models.DateTimeField(_("resolved at"), null=True, blank=True)
    is_test = models.BooleanField(_("test deposit"), default=True)
    is_update = models.BooleanField(_("metadata update"), default=False)

    class Meta:
        verbose_name = _("deposit batch")
        verbose_name_plural = _("deposit batches")
        ordering: ClassVar[list[str]] = ["-created_at"]
        indexes: ClassVar[list[models.Index]] = [models.Index(fields=["status", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.doi_batch_id} ({self.get_status_display()})"


class DOIRegistration(TimeStampedModel):
    """History of DOI registration attempts for one article."""

    article = models.ForeignKey(
        "journal.Article",
        verbose_name=_("article"),
        on_delete=models.CASCADE,
        related_name="doi_registrations",
    )
    batch = models.ForeignKey(
        DepositBatch,
        verbose_name=_("batch"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="registrations",
    )
    doi = models.CharField(_("DOI"), max_length=128)
    status = models.CharField(_("status"), max_length=32, default="pending")
    message = models.TextField(_("message"), blank=True)

    class Meta:
        verbose_name = _("DOI registration")
        verbose_name_plural = _("DOI registrations")
        ordering: ClassVar[list[str]] = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.doi} — {self.status}"
