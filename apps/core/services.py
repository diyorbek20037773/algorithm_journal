"""Shared services: cached settings access, e-mail sending, audit logging."""

from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.db import OperationalError, ProgrammingError
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils import translation

from apps.core.markdown import render_markdown, strip_markdown
from apps.core.models import AuditLog, EmailTemplate, SiteSettings

logger = logging.getLogger(__name__)

SETTINGS_CACHE_KEY = "site_settings"
SETTINGS_CACHE_TTL = 300


def get_site_settings() -> SiteSettings:
    """Return the journal settings singleton, cached for five minutes.

    Falls back to an unsaved instance when the database is not migrated yet so
    that ``manage.py`` commands and health checks never crash.
    """
    cached = cache.get(SETTINGS_CACHE_KEY)
    if cached is not None:
        return cached
    try:
        obj = SiteSettings.load()
    except (OperationalError, ProgrammingError):  # pragma: no cover - pre-migrate
        return SiteSettings()
    cache.set(SETTINGS_CACHE_KEY, obj, SETTINGS_CACHE_TTL)
    return obj


def client_ip(request: HttpRequest | None) -> str | None:
    """Best-effort client IP behind a reverse proxy."""
    if request is None:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_action(
    action: str,
    *,
    actor: Any = None,
    target: str = "",
    changes: dict[str, Any] | None = None,
    request: HttpRequest | None = None,
) -> AuditLog:
    """Append an entry to the audit log.

    Every editorial decision, publication and settings change must call this.
    """
    if actor is None and request is not None:
        user = getattr(request, "user", None)
        actor = user if user is not None and user.is_authenticated else None
    return AuditLog.objects.create(
        actor=actor,
        action=action,
        target=target[:255],
        changes=changes or {},
        ip=client_ip(request),
    )


def absolute_url(path: str) -> str:
    """Turn a root-relative path into an absolute URL using ``SITE_URL``."""
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{settings.SITE_URL.rstrip('/')}/{path.lstrip('/')}"


def send_templated_email(
    event: str,
    *,
    to: list[str],
    context: dict[str, Any],
    language: str = "en",
    fallback_subject: str = "",
    fallback_body: str = "",
    attachments: list[tuple[str, bytes, str]] | None = None,
) -> int:
    """Render and send a transactional e-mail for ``event``.

    The body is taken from the editable :class:`EmailTemplate` for the event in
    the recipient's language, rendered as Markdown into the shared HTML e-mail
    layout.  When no template row exists the supplied fallbacks are used, so
    notifications never silently disappear.
    """
    if not to:
        return 0

    subject = fallback_subject
    body_md = fallback_body
    with translation.override(language):
        try:
            template = EmailTemplate.objects.filter(event=event, is_active=True).first()
        except (OperationalError, ProgrammingError):  # pragma: no cover - pre-migrate
            template = None
        if template is not None:
            subject = template.subject or fallback_subject
            body_md = template.body or fallback_body

        rendered_subject = _merge(subject, context)
        rendered_body = _merge(body_md, context)
        site = get_site_settings()
        html = render_to_string(
            "emails/base_email.html",
            {
                "subject": rendered_subject,
                "body_html": render_markdown(rendered_body),
                "site_settings": site,
                "site_url": settings.SITE_URL,
                **context,
            },
        )
        text = strip_markdown(rendered_body)

    message = EmailMultiAlternatives(
        subject=rendered_subject,
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to,
    )
    message.attach_alternative(html, "text/html")
    for name, content, mime in attachments or []:
        message.attach(name, content, mime)
    try:
        return message.send(fail_silently=False)
    except Exception:  # pragma: no cover - network/SMTP failures must not break flows
        logger.exception("Failed to send %s e-mail to %s", event, to)
        return 0


def _merge(template_text: str, context: dict[str, Any]) -> str:
    """Substitute ``{placeholder}`` tokens, leaving unknown ones untouched."""
    if not template_text:
        return ""
    out = template_text
    for key, value in context.items():
        out = out.replace("{" + key + "}", str(value))
    return out
