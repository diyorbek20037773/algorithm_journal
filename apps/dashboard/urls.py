"""Dashboard URLs."""

from __future__ import annotations

from django.urls import path

from apps.dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("profile/", views.profile, name="profile"),
    path("two-factor/setup/", views.two_factor_setup, name="two_factor_setup"),
    path("reports/", views.reports, name="reports"),
    path("queue/<str:key>/", views.queue, name="queue"),
    path("submission/<int:pk>/", views.submission_detail, name="submission_detail"),
    path("submission/<int:pk>/similarity/", views.record_similarity, name="record_similarity"),
    path("submission/<int:pk>/transition/", views.run_transition, name="run_transition"),
    path("submission/<int:pk>/reviewers/", views.reviewer_finder, name="reviewer_finder"),
    path("submission/<int:pk>/invite/", views.invite_reviewer_view, name="invite_reviewer"),
    path("submission/<int:pk>/decide/", views.decide, name="decide"),
    path("submission/<int:pk>/message/", views.post_message, name="post_message"),
    path("submission/<int:pk>/note/", views.add_note, name="add_note"),
    path("assignment/<int:pk>/cancel/", views.cancel_assignment, name="cancel_assignment"),
    path("assignment/<int:pk>/remind/", views.remind_reviewer, name="remind_reviewer"),
    path("review/<int:pk>/rate/", views.rate_review, name="rate_review"),
    path("file/<int:pk>/", views.submission_file, name="submission_file"),
]
