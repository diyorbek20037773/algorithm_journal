"""Force TOTP enrolment for editorial staff before they reach any dashboard."""

from __future__ import annotations

from collections.abc import Callable

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _

#: URL name prefixes that stay reachable while enrolment is pending.
EXEMPT_PREFIXES: tuple[str, ...] = (
    "/accounts/",
    "/static/",
    "/media/",
    "/healthz/",
    "/i18n/",
    "/oai/",
    "/api/",
)

EXEMPT_SUFFIXES: tuple[str, ...] = (
    "/dashboard/two-factor/setup/",
    "/dashboard/two-factor/verify/",
    "/dashboard/two-factor/recovery/",
)


class StaffTwoFactorMiddleware:
    """Redirect staff without a confirmed TOTP device to the enrolment page.

    SPEC §11 requires two-factor authentication for editor, EIC, production and
    admin roles.  Readers and authors are never affected.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not getattr(settings, "STAFF_2FA_REQUIRED", True):
            return self.get_response(request)

        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return self.get_response(request)

        path = request.path
        if any(path.startswith(p) or f"/{p.lstrip('/')}" in path for p in EXEMPT_PREFIXES):
            return self.get_response(request)
        if any(path.endswith(s) for s in EXEMPT_SUFFIXES):
            return self.get_response(request)

        if user.requires_2fa and not user.has_verified_totp:
            messages.warning(
                request,
                _(
                    "Two-factor authentication is mandatory for editorial accounts. "
                    "Please set it up to continue."
                ),
            )
            return redirect(reverse("dashboard:two_factor_setup"))

        return self.get_response(request)
