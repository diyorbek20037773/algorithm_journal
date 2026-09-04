"""Pluggable similarity-check providers (SPEC §5.6)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class NotConfigured(RuntimeError):
    """Raised when a provider is selected but its credentials are missing."""


@dataclass
class PlagiarismResult:
    """Outcome of a similarity check."""

    percent: float
    report_url: str = ""
    external_id: str = ""
    checked_at: datetime | None = None

    def __post_init__(self) -> None:
        """Default the timestamp to now."""
        if self.checked_at is None:
            self.checked_at = timezone.now()


@runtime_checkable
class PlagiarismProvider(Protocol):
    """Interface every similarity-check backend implements."""

    slug: str

    def submit(self, submission, file) -> str:
        """Send a manuscript for checking and return an external identifier."""
        ...

    def fetch_result(self, external_id: str) -> PlagiarismResult | None:
        """Retrieve a finished result, or ``None`` while it is still running."""
        ...


class ManualProvider:
    """Default provider: an editor uploads the report and enters the percentage.

    ``submit`` is a no-op; the editor's dashboard form writes
    ``similarity_percent`` and ``similarity_report`` directly on the submission.
    """

    slug = "manual"
    label = _("Manual (editor uploads report)")

    def submit(self, submission, file) -> str:
        """Return a synthetic identifier; no external system is contacted."""
        return f"manual:{submission.pk}"

    def fetch_result(self, external_id: str) -> PlagiarismResult | None:
        """Read the percentage an editor already recorded on the submission."""
        from apps.submissions.models import Submission

        try:
            pk = int(external_id.split(":", 1)[1])
        except (IndexError, ValueError):
            return None
        submission = Submission.objects.filter(pk=pk).first()
        if submission is None or submission.similarity_percent is None:
            return None
        return PlagiarismResult(
            percent=submission.similarity_percent,
            report_url=submission.similarity_report.url if submission.similarity_report else "",
            external_id=external_id,
            checked_at=submission.similarity_checked_at,
        )


class IThenticateProvider:
    """Structure of an iThenticate v2 client — inactive without credentials.

    The class is complete enough to show exactly which endpoints would be
    called, but it never contacts the network unless ``ITHENTICATE_URL`` and
    ``ITHENTICATE_API_KEY`` are both configured (SPEC §18: live calls are out
    of scope for v1).
    """

    slug = "ithenticate"
    label = _("iThenticate (Crossref Similarity Check)")

    def __init__(self) -> None:
        """Capture the configuration and refuse to run when it is missing."""
        self.base_url = settings.ITHENTICATE_URL.rstrip("/")
        self.api_key = settings.ITHENTICATE_API_KEY
        if not self.base_url or not self.api_key:
            raise NotConfigured(
                "ITHENTICATE_URL and ITHENTICATE_API_KEY must be set to use this provider."
            )

    @property
    def _headers(self) -> dict[str, str]:
        """Authorisation headers for the v2 API."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-Turnitin-Integration-Name": "ARER",
            "X-Turnitin-Integration-Version": "1.0",
        }

    def submit(self, submission, file) -> str:  # pragma: no cover - needs credentials
        """Create a submission and upload the manuscript for checking."""
        import requests

        response = requests.post(
            f"{self.base_url}/api/v1/submissions",
            headers=self._headers,
            json={
                "owner": submission.submitter.email,
                "title": submission.title[:200],
                "submitter": submission.submitter.email,
            },
            timeout=30,
        )
        response.raise_for_status()
        external_id = response.json()["id"]
        file.seek(0)
        upload = requests.put(
            f"{self.base_url}/api/v1/submissions/{external_id}/original",
            headers={**self._headers, "Content-Type": "binary/octet-stream"},
            data=file.read(),
            timeout=120,
        )
        upload.raise_for_status()
        return external_id

    def fetch_result(self, external_id: str) -> PlagiarismResult | None:  # pragma: no cover
        """Poll the similarity report for a finished score."""
        import requests

        response = requests.get(
            f"{self.base_url}/api/v1/submissions/{external_id}/similarity",
            headers=self._headers,
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") != "COMPLETE":
            return None
        return PlagiarismResult(
            percent=float(payload["overall_match_percentage"]),
            report_url=payload.get("viewer_url", ""),
            external_id=external_id,
        )


PROVIDERS: dict[str, type] = {
    ManualProvider.slug: ManualProvider,
    IThenticateProvider.slug: IThenticateProvider,
}


def get_provider(slug: str | None = None) -> PlagiarismProvider:
    """Instantiate the configured provider, falling back to the manual one."""
    slug = slug or settings.PLAGIARISM_PROVIDER
    provider_class = PROVIDERS.get(slug, ManualProvider)
    try:
        return provider_class()
    except NotConfigured:
        logger.warning("Provider %s is not configured; falling back to manual.", slug)
        return ManualProvider()
