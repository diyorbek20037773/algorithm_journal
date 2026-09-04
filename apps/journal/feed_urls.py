"""RSS and Atom feed URLs."""

from __future__ import annotations

from django.urls import path

from apps.journal.feeds import (
    LatestArticlesAtomFeed,
    LatestArticlesRSSFeed,
    SectionAtomFeed,
    SectionRSSFeed,
)

urlpatterns = [
    path("", LatestArticlesRSSFeed(), name="feed_rss_default"),
    path("rss/", LatestArticlesRSSFeed(), name="feed_rss"),
    path("atom/", LatestArticlesAtomFeed(), name="feed_atom"),
    path("section/<slug:slug>/rss/", SectionRSSFeed(), name="feed_section_rss"),
    path("section/<slug:slug>/atom/", SectionAtomFeed(), name="feed_section_atom"),
]
