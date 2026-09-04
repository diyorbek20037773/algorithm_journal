"""Reviewer-facing URLs."""

from __future__ import annotations

from django.urls import path

from apps.review import views

app_name = "review"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("assignment/<int:pk>/", views.assignment_detail, name="assignment_detail"),
    path("assignment/<int:pk>/form/", views.review_form, name="review_form"),
    path("assignment/<int:pk>/respond/", views.respond_dashboard, name="respond_dashboard"),
    path("file/<int:pk>/", views.download_file, name="download_file"),
    path("certificate/", views.certificate, name="certificate"),
    path("invitation/<str:token>/<str:answer>/", views.respond, name="respond"),
]
