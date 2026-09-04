"""OAI-PMH endpoint URL."""

from __future__ import annotations

from django.urls import path

from apps.oai import views

urlpatterns = [
    path("", views.endpoint, name="oai_endpoint"),
]
