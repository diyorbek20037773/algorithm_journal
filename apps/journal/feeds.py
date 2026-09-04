"""RSS 2.0 and Atom feeds for the latest published articles."""

from __future__ import annotations

from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import gettext as _

from apps.core.services import get_site_settings
from apps.journal.models import Article, Section

FEED_LIMIT = 20


class LatestArticlesRSSFeed(Feed):
    """The 20 most recently published articles as RSS 2.0."""

    def title(self) -> str:
        """Feed title taken from the journal settings."""
        return get_site_settings().journal_name

    def link(self) -> str:
        """Link back to the journal home page."""
        from django.urls import reverse

        return reverse("journal:home")

    def description(self) -> str:
        """Feed description."""
        site = get_site_settings()
        return site.journal_subtitle or _("Latest articles")

    def items(self) -> list[Article]:
        """Newest publicly visible articles."""
        return list(
            Article.objects.public().with_related().order_by("-published_at", "-id")[:FEED_LIMIT]
        )

    def item_title(self, item: Article) -> str:
        """Article title."""
        return item.title

    def item_description(self, item: Article) -> str:
        """Article abstract."""
        return item.abstract_plain

    def item_link(self, item: Article) -> str:
        """Canonical article URL."""
        return item.get_absolute_url()

    def item_pubdate(self, item: Article):
        """Publication date as a datetime."""
        from datetime import datetime, time

        date = item.display_date
        return datetime.combine(date, time.min) if date else None

    def item_author_name(self, item: Article) -> str:
        """Comma-separated author names."""
        return item.authors_display()

    def item_guid(self, item: Article) -> str:
        """DOI when available, otherwise the canonical URL."""
        return item.doi_url or item.canonical_url

    def item_categories(self, item: Article) -> list[str]:
        """Keywords as feed categories."""
        return [k.name for k in item.keywords.all()]


class LatestArticlesAtomFeed(LatestArticlesRSSFeed):
    """The same content served as Atom 1.0."""

    feed_type = Atom1Feed
    subtitle = LatestArticlesRSSFeed.description


class SectionRSSFeed(LatestArticlesRSSFeed):
    """Per-section RSS feed."""

    def get_object(self, request, slug: str) -> Section:
        """Resolve the section from the URL."""
        return get_object_or_404(Section, slug=slug, is_active=True)

    def title(self, obj: Section) -> str:  # type: ignore[override]
        """Journal name plus the section name."""
        return f"{get_site_settings().journal_name} — {obj.name}"

    def link(self, obj: Section) -> str:  # type: ignore[override]
        """Section landing page."""
        return obj.get_absolute_url()

    def description(self, obj: Section) -> str:  # type: ignore[override]
        """Section description."""
        return obj.description or obj.name

    def items(self, obj: Section) -> list[Article]:  # type: ignore[override]
        """Newest articles in the section."""
        return list(
            Article.objects.public()
            .filter(section=obj)
            .with_related()
            .order_by("-published_at", "-id")[:FEED_LIMIT]
        )


class SectionAtomFeed(SectionRSSFeed):
    """Per-section Atom feed."""

    feed_type = Atom1Feed
