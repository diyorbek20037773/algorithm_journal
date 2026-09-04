"""Search URLs."""

from __future__ import annotations

from django.urls import path

from apps.search import views

app_name = "search"

urlpatterns = [
    path("", views.search, name="search"),
]
