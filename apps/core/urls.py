"""URLs for CMS pages, the author/reviewer hubs, contact and statistics."""

from __future__ import annotations

from django.urls import path

from apps.core import views, views_pages

app_name = "core"

urlpatterns = [
    # About group — explicit routes are declared before the catch-all slug.
    path("about/", views_pages.about, name="about"),
    path(
        "about/aims-and-scope/",
        views_pages.named_page,
        {"slug": "aims-and-scope"},
        name="aims_and_scope",
    ),
    path("about/peer-review/", views_pages.named_page, {"slug": "peer-review"}, name="peer_review"),
    path(
        "about/publication-ethics/",
        views_pages.named_page,
        {"slug": "publication-ethics"},
        name="publication_ethics",
    ),
    path("about/open-access/", views_pages.named_page, {"slug": "open-access"}, name="open_access"),
    path("about/fees/", views_pages.named_page, {"slug": "fees"}, name="fees"),
    path("about/archiving/", views_pages.named_page, {"slug": "archiving"}, name="archiving"),
    path("about/indexing/", views_pages.indexing, name="indexing"),
    path("about/ai-policy/", views_pages.named_page, {"slug": "ai-policy"}, name="ai_policy"),
    path("about/privacy/", views_pages.named_page, {"slug": "privacy"}, name="privacy"),
    path("about/contact/", views_pages.contact, name="contact"),
    path("about/<slug:slug>/", views.page_detail, name="page"),
    # Author and reviewer hubs
    path("for-authors/", views_pages.for_authors, name="for_authors"),
    path(
        "for-authors/guidelines/",
        views_pages.named_page,
        {"slug": "author-guidelines"},
        name="author_guidelines",
    ),
    path("for-authors/checklist/", views_pages.checklist, name="checklist"),
    path("for-authors/template/", views_pages.templates_download, name="templates"),
    path("for-reviewers/", views_pages.for_reviewers, name="for_reviewers"),
    # Announcements and statistics
    path("announcements/", views.announcement_list, name="announcement_list"),
    path("announcements/<slug:slug>/", views.announcement_detail, name="announcement_detail"),
    path("statistics/", views_pages.statistics, name="statistics"),
]
