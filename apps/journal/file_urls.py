"""Language-neutral galley download URLs (stable for Google Scholar)."""

from __future__ import annotations

from django.urls import path

from apps.journal import file_views

urlpatterns = [
    path("<int:pk>/pdf/", file_views.article_pdf, name="article_pdf"),
    path("<int:pk>/galley/<int:galley_id>/", file_views.galley_download, name="galley_download"),
]
