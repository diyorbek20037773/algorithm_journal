"""Submission wizard and author action URLs."""

from __future__ import annotations

from django.urls import path

from apps.submissions import views

app_name = "submissions"

urlpatterns = [
    path("", views.wizard_start, name="wizard_start"),
    path("new/", views.wizard_step1, name="wizard_new"),
    path("<int:pk>/step-1/", views.wizard_step1, name="wizard_step1"),
    path("<int:pk>/step-2/", views.wizard_step2, name="wizard_step2"),
    path("<int:pk>/step-3/", views.wizard_step3, name="wizard_step3"),
    path("<int:pk>/step-4/", views.wizard_step4, name="wizard_step4"),
    path("<int:pk>/step-5/", views.wizard_step5, name="wizard_step5"),
    path("<int:pk>/revision/", views.upload_revision, name="upload_revision"),
    path("<int:pk>/withdraw/", views.withdraw, name="withdraw"),
    path("file/<int:pk>/delete/", views.delete_file, name="delete_file"),
]
