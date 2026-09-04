"""Public URLs for issues, articles and browse pages."""

from __future__ import annotations

from django.urls import path

from apps.journal import views

app_name = "journal"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    # Issues -----------------------------------------------------------------
    path("issues/", views.ArchiveView.as_view(), name="archive"),
    path("issues/current/", views.current_issue, name="issue_current"),
    path("issues/online-first/", views.OnlineFirstView.as_view(), name="online_first"),
    path("issues/<int:volume>/<int:issue>/", views.IssueDetailView.as_view(), name="issue_detail"),
    # Articles ---------------------------------------------------------------
    path("article/<int:pk>/", views.ArticleDetailView.as_view(), name="article_detail"),
    path("article/<int:pk>/cite/", views.article_cite, name="article_cite"),
    path("article/<int:pk>/export/<str:fmt>/", views.article_export, name="article_export"),
    path(
        "article/<int:pk>/<slug:slug>/",
        views.ArticleDetailView.as_view(),
        name="article_detail_slug",
    ),
    # Browse -----------------------------------------------------------------
    path("authors/<slug:slug>/", views.AuthorDetailView.as_view(), name="author_detail"),
    path("keywords/<slug:slug>/", views.KeywordDetailView.as_view(), name="keyword_detail"),
    path("jel/", views.JELIndexView.as_view(), name="jel_index"),
    path("jel/<str:code>/", views.JELDetailView.as_view(), name="jel_detail"),
    path("sections/<slug:slug>/", views.SectionDetailView.as_view(), name="section_detail"),
    # Board ------------------------------------------------------------------
    path("about/editorial-board/", views.editorial_board, name="editorial_board"),
    path("about/reviewer-board/", views.reviewer_board, name="reviewer_board"),
]
