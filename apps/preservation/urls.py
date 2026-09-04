"""LOCKSS manifest URLs."""

from __future__ import annotations

from django.urls import path

from apps.preservation import views

urlpatterns = [
    path("", views.manifest_index, name="lockss_index"),
    path("<int:volume>/", views.manifest_volume, name="lockss_volume"),
]
