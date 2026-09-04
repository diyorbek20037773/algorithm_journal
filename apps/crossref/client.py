"""HTTPS client for depositing metadata with Crossref and reading its API."""

from __future__ import annotations

import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TIMEOUT = 60


class CrossrefNotConfigured(RuntimeError):
    """Raised when deposit credentials are missing."""


def deposit_url() -> str:
    """Test or production deposit endpoint, depending on ``CROSSREF_TEST``."""
    return (
        settings.CROSSREF_DEPOSIT_URL
        if settings.CROSSREF_TEST
        else settings.CROSSREF_DEPOSIT_URL_PROD
    )


def is_configured() -> bool:
    """True when a deposit could actually be attempted."""
    return bool(settings.CROSSREF_USER and settings.CROSSREF_PASSWORD)


def deposit(xml_bytes: bytes, *, filename: str = "deposit.xml") -> tuple[bool, str]:
    """POST a deposit document; returns ``(success, response_text)``.

    Raises :class:`CrossrefNotConfigured` when credentials are absent so the
    caller can leave the batch in ``pending`` with a clear dashboard message.
    """
    if not is_configured():
        raise CrossrefNotConfigured(
            "CROSSREF_USER and CROSSREF_PASSWORD are not set; the deposit stays pending."
        )
    response = requests.post(
        deposit_url(),
        data={
            "operation": "doMDUpload",
            "login_id": settings.CROSSREF_USER,
            "login_passwd": settings.CROSSREF_PASSWORD,
        },
        files={"fname": (filename, xml_bytes, "text/xml")},
        timeout=TIMEOUT,
        headers={"User-Agent": user_agent()},
    )
    text = response.text or ""
    success = response.status_code == 200 and "SUCCESS" in text.upper()
    logger.info("Crossref deposit %s: HTTP %s", filename, response.status_code)
    return success, text[:8000]


def submission_status(doi_batch_id: str) -> tuple[str, str]:
    """Query the deposit status of a batch; returns ``(status, raw_body)``."""
    if not is_configured():
        raise CrossrefNotConfigured("Crossref credentials are not configured.")
    host = "test.crossref.org" if settings.CROSSREF_TEST else "doi.crossref.org"
    response = requests.get(
        f"https://{host}/servlet/submissionDownload",
        params={
            "usr": settings.CROSSREF_USER,
            "pwd": settings.CROSSREF_PASSWORD,
            "doi_batch_id": doi_batch_id,
            "type": "result",
        },
        timeout=TIMEOUT,
        headers={"User-Agent": user_agent()},
    )
    body = response.text or ""
    upper = body.upper()
    if 'STATUS="COMPLETED"' in upper.replace(" ", "") or "SUCCESS" in upper:
        status = "success"
    elif "FAILURE" in upper or "ERROR" in upper:
        status = "failed"
    else:
        status = "submitted"
    return status, body[:8000]


def user_agent() -> str:
    """Polite user agent required by the Crossref REST API."""
    return f"ARER/1.0 (https://{settings.SITE_DOMAIN}; mailto:{settings.CROSSREF_POLITE_MAILTO})"


def cited_by_count(doi: str) -> int | None:
    """Fetch ``is-referenced-by-count`` for a DOI from the Crossref REST API."""
    try:
        response = requests.get(
            f"https://api.crossref.org/works/{doi}",
            timeout=30,
            headers={"User-Agent": user_agent()},
        )
        if response.status_code != 200:
            return None
        payload: dict[str, Any] = response.json()
        return int(payload.get("message", {}).get("is-referenced-by-count", 0))
    except Exception:  # pragma: no cover - network failures are expected offline
        logger.info("Could not fetch cited-by count for %s", doi)
        return None
