"""Public URLs for issues, articles and browse pages."""

from __future__ import annotations

from django.urls import path

from apps.core.caching import cache_public_page
from apps.journal import views

#: Reader-facing pages are identical for every anonymous visitor.
cached = cache_public_page()

app_name = "journal"

urlpatterns = [
    path("", cached(views.HomeView.as_view()), name="home"),
    # Issues -----------------------------------------------------------------
    path("issues/", cached(views.ArchiveView.as_view()), name="archive"),
    path("issues/current/", views.current_issue, name="issue_current"),
    path("issues/online-first/", cached(views.OnlineFirstView.as_view()), name="online_first"),
    path(
        "issues/<int:volume>/<int:issue>/",
        cached(views.IssueDetailView.as_view()),
        name="issue_detail",
    ),
    # Articles ---------------------------------------------------------------
    path("article/<int:pk>/", cached(views.ArticleDetailView.as_view()), name="article_detail"),
    path("article/<int:pk>/cite/", views.article_cite, name="article_cite"),
    path("article/<int:pk>/view/", views.article_view_beacon, name="article_view_beacon"),
    path("article/<int:pk>/export/<str:fmt>/", views.article_export, name="article_export"),
    path(
        "article/<int:pk>/<slug:slug>/",
        cached(views.ArticleDetailView.as_view()),
        name="article_detail_slug",
    ),
    # Browse -----------------------------------------------------------------
    path("authors/<slug:slug>/", cached(views.AuthorDetailView.as_view()), name="author_detail"),
    path("keywords/<slug:slug>/", cached(views.KeywordDetailView.as_view()), name="keyword_detail"),
    path("jel/", cached(views.JELIndexView.as_view()), name="jel_index"),
    path("jel/<str:code>/", cached(views.JELDetailView.as_view()), name="jel_detail"),
    path("sections/<slug:slug>/", cached(views.SectionDetailView.as_view()), name="section_detail"),
    # Board ------------------------------------------------------------------
    path("about/editorial-board/", cached(views.editorial_board), name="editorial_board"),
    path("about/reviewer-board/", cached(views.reviewer_board), name="reviewer_board"),
]
