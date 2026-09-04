"""Usage statistics: bot filtering, double-click filtering and aggregation."""

from __future__ import annotations

import datetime as dt

import pytest
from django.test import RequestFactory
from django.utils import timezone

from apps.metrics import services
from apps.metrics.models import AccessEvent, DailyArticleStat

pytestmark = pytest.mark.django_db


def _request(user_agent: str = "Mozilla/5.0 (Reader)", ip: str = "203.0.113.5"):
    """Build a bare request with a session for the metrics recorder."""
    factory = RequestFactory()
    request = factory.get("/", HTTP_USER_AGENT=user_agent, REMOTE_ADDR=ip)
    request.user = None

    class _Session:
        session_key = "abc123"

    request.session = _Session()
    return request


def test_ip_is_never_stored_in_the_clear(article, site_settings) -> None:
    """Only a salted hash of the IP address is persisted (SPEC §5.5, D20)."""
    event = services.record_access(_request(), article, kind="view")
    assert event is not None
    assert "203.0.113.5" not in event.ip_hash
    assert len(event.ip_hash) == 64


@pytest.mark.parametrize(
    "agent",
    [
        "Googlebot/2.1",
        "python-requests/2.31",
        "AhrefsBot",
        "curl/8.0",
        "Mozilla/5.0 (compatible; bingbot/2.0)",
    ],
)
def test_bot_user_agents_are_flagged(article, site_settings, agent) -> None:
    """Crawlers are recorded but excluded from the counters."""
    event = services.record_access(_request(agent), article, kind="view")
    assert event.is_bot
    article.refresh_from_db()
    assert article.views_count == 0


def test_double_click_within_thirty_seconds_counts_once(article, site_settings) -> None:
    """A second identical access inside the window is discarded."""
    assert services.record_access(_request(), article, kind="view") is not None
    assert services.record_access(_request(), article, kind="view") is None
    article.refresh_from_db()
    assert article.views_count == 1


def test_different_ip_counts_separately(article, site_settings) -> None:
    """Two readers are counted twice."""
    services.record_access(_request(ip="203.0.113.5"), article, kind="view")
    services.record_access(_request(ip="198.51.100.9"), article, kind="view")
    article.refresh_from_db()
    assert article.views_count == 2


def test_aggregation_writes_daily_rows(article, site_settings) -> None:
    """Raw events fold into a DailyArticleStat row."""
    services.record_access(_request(ip="203.0.113.1"), article, kind="view")
    services.record_access(_request(ip="203.0.113.2"), article, kind="download")
    written = services.aggregate_day(timezone.localdate())
    assert written == 1
    row = DailyArticleStat.objects.get(article=article, date=timezone.localdate())
    assert row.views == 1
    assert row.downloads == 1


def test_refresh_totals_from_daily_rows(article, site_settings) -> None:
    """Denormalised totals are recomputed from the daily table."""
    today = timezone.localdate()
    DailyArticleStat.objects.create(article=article, date=today, views=10, downloads=4)
    DailyArticleStat.objects.create(
        article=article, date=today - dt.timedelta(days=1), views=6, downloads=2
    )
    services.refresh_article_totals()
    article.refresh_from_db()
    assert article.views_count == 16
    assert article.downloads_count == 6


def test_prune_removes_old_events(article, site_settings) -> None:
    """Raw events older than the retention window are deleted."""
    from apps.metrics.tasks import prune_access_events

    old = AccessEvent.objects.create(article=article, kind=AccessEvent.Kind.VIEW, ip_hash="x" * 64)
    AccessEvent.objects.filter(pk=old.pk).update(
        occurred_at=timezone.now() - dt.timedelta(days=200)
    )
    prune_access_events()
    assert not AccessEvent.objects.filter(pk=old.pk).exists()


def test_home_kpis_hidden_until_ten_decisions(article, site_settings) -> None:
    """Headline KPIs stay hidden while the record is thin (SPEC §6.1)."""
    from django.core.cache import cache

    cache.clear()
    assert services.home_kpis() is None


def test_public_statistics_shape(article, site_settings) -> None:
    """The statistics page data has every documented key."""
    from django.core.cache import cache

    cache.clear()
    stats = services.public_statistics()
    for key in (
        "articles_published",
        "authors",
        "countries",
        "acceptance_rate",
        "median_days_to_first_decision",
        "reviewers_active",
        "downloads_last_year",
        "monthly",
    ):
        assert key in stats
    assert stats["articles_published"] == 1
    assert "Uzbekistan" in stats["countries"]


def test_monthly_series_has_chart_geometry(article, site_settings) -> None:
    """Each month carries the SVG coordinates the template needs."""
    series = services.monthly_series(6)
    assert len(series) == 6
    for point in series:
        for key in ("x_submissions", "y_submissions", "h_submissions", "x_label"):
            assert key in point
