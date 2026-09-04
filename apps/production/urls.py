"""Production dashboard URLs."""

from __future__ import annotations

from django.urls import path

from apps.production import views

app_name = "production"

urlpatterns = [
    path("", views.queue, name="queue"),
    path("submission/<int:pk>/", views.submission_production, name="submission"),
    path("submission/<int:pk>/advance/", views.advance_stage, name="advance"),
    path("submission/<int:pk>/upload/", views.upload_production_file, name="upload_file"),
    path("task/<int:pk>/complete/", views.complete_task, name="complete_task"),
    path("article/<int:pk>/", views.article_production, name="article"),
    path("article/<int:pk>/galley/", views.upload_galley, name="upload_galley"),
    path("article/<int:pk>/doi/", views.assign_doi, name="assign_doi"),
    path("article/<int:pk>/online-first/", views.publish_online_first, name="publish_online_first"),
    path("article/<int:pk>/schedule/", views.schedule_to_issue, name="schedule"),
    path("issue/new/", views.create_issue, name="create_issue"),
    path("issue/<int:pk>/", views.issue_builder, name="issue_builder"),
    path("issue/<int:pk>/reorder/", views.reorder_issue, name="reorder_issue"),
    path("issue/<int:pk>/publish/", views.publish_issue, name="publish_issue"),
]
