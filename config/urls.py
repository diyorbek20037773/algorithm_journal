"""Root URL configuration.

Public pages live under ``i18n_patterns`` (``/en/``, ``/uz/``, ``/uz-cyrl/``,
``/ru/``).  Machine endpoints (OAI-PMH, API, sitemaps, feeds, PDF galleys)
are deliberately language-neutral so that harvesters and Google Scholar get
one stable URL per resource.
"""

from __future__ import annotations

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from apps.core import views as core_views

handler400 = "apps.core.views.bad_request"
handler403 = "apps.core.views.permission_denied"
handler404 = "apps.core.views.page_not_found"
handler500 = "apps.core.views.server_error"

# --- language-neutral endpoints ------------------------------------------
urlpatterns = [
    path("healthz/", core_views.healthz, name="healthz"),
    path("robots.txt", core_views.robots_txt, name="robots"),
    path("sitemap.xml", core_views.sitemap_index, name="sitemap_index"),
    path("sitemap-<str:section>.xml", core_views.sitemap_section, name="sitemap_section"),
    path("feed/", include("apps.journal.feed_urls")),
    path("article/", include("apps.journal.file_urls")),
    path("oai/", include("apps.oai.urls")),
    path("api/v1/", include("apps.api.urls")),
    path("lockss/", include("apps.preservation.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
]

# --- localised public site ------------------------------------------------
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("submit/", include("apps.submissions.urls")),
    path("review/", include("apps.review.urls")),
    path("production/", include("apps.production.urls")),
    path("search/", include("apps.search.urls")),
    path("", include("apps.journal.urls")),
    path("", include("apps.core.urls")),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")

# Convenience aliases used by tests and templates.
urlpatterns += [
    path(
        ".well-known/security.txt",
        TemplateView.as_view(template_name="security.txt", content_type="text/plain"),
        name="security_txt",
    ),
]
