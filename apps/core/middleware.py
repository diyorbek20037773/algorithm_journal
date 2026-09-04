"""Request middleware attaching journal settings to every request."""

from __future__ import annotations

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

from apps.core.services import get_site_settings


class SiteSettingsMiddleware:
    """Attach the cached :class:`~apps.core.models.SiteSettings` singleton.

    Views, templates and context processors read ``request.site_settings``
    instead of hitting the database repeatedly.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.site_settings = get_site_settings()
        return self.get_response(request)
