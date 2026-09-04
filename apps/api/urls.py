"""Read-only public API URLs."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.api import views

app_name = "api"

router = DefaultRouter()
router.register("articles", views.ArticleViewSet, basename="article")
router.register("issues", views.IssueViewSet, basename="issue")
router.register("sections", views.SectionViewSet, basename="section")

urlpatterns = [
    path("", views.api_root, name="root"),
    path("search/", views.search, name="search"),
    path("doaj-export/", views.doaj_export, name="doaj_export"),
    path("", include(router.urls)),
]
