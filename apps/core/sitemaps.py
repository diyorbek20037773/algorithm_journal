"""XML sitemaps: index plus static, issue, article and author sections."""

from __future__ import annotations

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import index as sitemap_index_view
from django.contrib.sitemaps.views import sitemap as sitemap_view
from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from apps.core.models import Announcement, Page
from apps.journal.models import Article, Author, Issue, Section


class StaticSitemap(Sitemap):
    """Named, non-database pages of the public site."""

    changefreq = "monthly"
    priority = 0.6
    protocol = settings.SITE_PROTOCOL

    def items(self) -> list[str]:
        """URL names that always exist."""
        return [
            "journal:home",
            "journal:archive",
            "journal:online_first",
            "journal:editorial_board",
            "journal:reviewer_board",
            "journal:jel_index",
            "core:about",
            "core:for_authors",
            "core:for_reviewers",
            "core:checklist",
            "core:contact",
            "core:statistics",
            "core:announcement_list",
            "search:search",
        ]

    def location(self, item: str) -> str:
        """Resolve the URL name."""
        return reverse(item)


class PageSitemap(Sitemap):
    """CMS pages."""

    changefreq = "monthly"
    priority = 0.5
    protocol = settings.SITE_PROTOCOL

    def items(self):
        """Published CMS pages."""
        return Page.objects.published()

    def lastmod(self, obj: Page):
        """Last content change."""
        return obj.updated_at


class IssueSitemap(Sitemap):
    """Published issues."""

    changefreq = "yearly"
    priority = 0.7
    protocol = settings.SITE_PROTOCOL

    def items(self):
        """Published issues, newest first."""
        return Issue.objects.published().select_related("volume")

    def lastmod(self, obj: Issue):
        """Issue publication date."""
        return obj.updated_at


class ArticleSitemap(Sitemap):
    """Every publicly visible article."""

    changefreq = "yearly"
    priority = 0.9
    limit = 5000
    protocol = settings.SITE_PROTOCOL

    def items(self):
        """Public articles, newest first."""
        return Article.objects.public().only("id", "slug", "updated_at")

    def lastmod(self, obj: Article):
        """Last metadata change."""
        return obj.updated_at


class AuthorSitemap(Sitemap):
    """Author landing pages, de-duplicated by slug."""

    changefreq = "monthly"
    priority = 0.4
    protocol = settings.SITE_PROTOCOL

    def items(self) -> list[Author]:
        """One representative authorship row per author slug."""
        seen: dict[str, Author] = {}
        for author in Author.objects.filter(article__status__in=["published", "online_first"]):
            seen.setdefault(author.slug, author)
        return list(seen.values())

    def location(self, obj: Author) -> str:
        """Author landing page URL."""
        return obj.get_absolute_url()


class SectionSitemap(Sitemap):
    """Section landing pages."""

    changefreq = "weekly"
    priority = 0.5
    protocol = settings.SITE_PROTOCOL

    def items(self):
        """Active sections."""
        return Section.objects.filter(is_active=True)


class AnnouncementSitemap(Sitemap):
    """Announcements and calls for papers."""

    changefreq = "monthly"
    priority = 0.3
    protocol = settings.SITE_PROTOCOL

    def items(self):
        """Live announcements."""
        return Announcement.objects.live()

    def lastmod(self, obj: Announcement):
        """Last edit."""
        return obj.updated_at


SITEMAPS: dict[str, type[Sitemap]] = {
    "static": StaticSitemap,
    "pages": PageSitemap,
    "issues": IssueSitemap,
    "articles": ArticleSitemap,
    "authors": AuthorSitemap,
    "sections": SectionSitemap,
    "announcements": AnnouncementSitemap,
}


def render_sitemap_index(request: HttpRequest) -> HttpResponse:
    """Render ``/sitemap.xml`` listing every section."""
    return sitemap_index_view(request, sitemaps=SITEMAPS, sitemap_url_name="sitemap_section")


def render_sitemap_section(request: HttpRequest, section: str) -> HttpResponse:
    """Render one sitemap section such as ``/sitemap-articles.xml``."""
    return sitemap_view(request, sitemaps=SITEMAPS, section=section)
