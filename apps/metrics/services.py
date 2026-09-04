"""Recording, filtering and aggregating usage statistics."""

from __future__ import annotations

import hashlib
import re
import statistics
from datetime import date, timedelta
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, F, Q, Sum
from django.http import HttpRequest
from django.utils import timezone

from apps.journal.models import Article, Galley
from apps.metrics.models import AccessEvent, DailyArticleStat, EditorialKPI

#: Subset of the COUNTER robots list plus common crawlers and libraries.
BOT_PATTERN = re.compile(
    r"(bot|crawler|spider|slurp|curl|wget|python-requests|httpclient|libwww|java/|scrapy|"
    r"headlesschrome|phantomjs|facebookexternalhit|semrush|ahrefs|mj12|dotbot|bingpreview|"
    r"yandex|baidu|duckduck|archive\.org_bot|ia_archiver|feedfetcher|monitoring|uptime|"
    r"pingdom|lighthouse|gtmetrix|playwright)",
    re.IGNORECASE,
)

#: Two accesses from the same reader within this window count once.
DOUBLE_CLICK_WINDOW = timedelta(seconds=30)


def hash_value(value: str) -> str:
    """Salted SHA-256 hash — the only form in which identifiers are stored."""
    salt = settings.IP_HASH_SALT
    return hashlib.sha256(f"{salt}:{value}".encode()).hexdigest()


def is_bot(user_agent: str) -> bool:
    """True when the user agent looks like a robot (COUNTER-style filter)."""
    if not user_agent:
        return True
    return bool(BOT_PATTERN.search(user_agent))


def record_access(
    request: HttpRequest,
    article: Article,
    *,
    kind: str = "view",
    galley: Galley | None = None,
) -> AccessEvent | None:
    """Record a view or download, applying bot and double-click filtering.

    Returns the created event, or ``None`` when the access was filtered out.
    Staff traffic is never counted.
    """
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated and user.is_editorial_staff:
        return None

    user_agent = request.META.get("HTTP_USER_AGENT", "")
    bot = is_bot(user_agent)

    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    ip = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR", "")
    ip_hash = hash_value(ip or "unknown")

    if not bot:
        cutoff = timezone.now() - DOUBLE_CLICK_WINDOW
        duplicate = AccessEvent.objects.filter(
            article=article, kind=kind, ip_hash=ip_hash, occurred_at__gte=cutoff
        ).exists()
        if duplicate:
            return None

    event = AccessEvent.objects.create(
        article=article,
        kind=kind,
        galley=galley,
        ip_hash=ip_hash,
        user_agent_hash=hash_value(user_agent)[:64] if user_agent else "",
        session_key_hash=hash_value(request.session.session_key or "")[:64]
        if getattr(request, "session", None) and request.session.session_key
        else "",
        country=_country_for(ip),
        is_bot=bot,
    )

    if not bot:
        field = "views_count" if kind == "view" else "downloads_count"
        Article.objects.filter(pk=article.pk).update(**{field: F(field) + 1})

    return event


def _country_for(ip: str) -> str:
    """Resolve an IP to a country code when a GeoIP database is configured."""
    if not ip:
        return ""
    try:  # pragma: no cover - optional dependency and data file
        from django.contrib.gis.geoip2 import GeoIP2

        return GeoIP2().country_code(ip) or ""
    except Exception:
        return ""


def most_read(limit: int = 5, days: int = 30) -> list[Article]:
    """Most-viewed public articles over the last ``days`` days."""
    cache_key = f"most_read:{limit}:{days}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    since = timezone.now().date() - timedelta(days=days)
    rows = (
        DailyArticleStat.objects.filter(date__gte=since)
        .values("article")
        .annotate(total=Sum("views"))
        .order_by("-total")[: limit * 3]
    )
    ids = [r["article"] for r in rows]
    articles = {a.pk: a for a in Article.objects.public().filter(pk__in=ids).with_related()}
    ordered = [articles[i] for i in ids if i in articles][:limit]
    if not ordered:
        ordered = list(Article.objects.public().with_related().order_by("-views_count")[:limit])
    cache.set(cache_key, ordered, 600)
    return ordered


def home_kpis() -> dict[str, Any] | None:
    """Headline KPIs for the home page, or ``None`` when data is too thin.

    SPEC §6.1: only render when at least ten editorial decisions exist.
    """
    from apps.submissions.models import EditorialDecision

    cached = cache.get("home_kpis")
    if cached is not None:
        return cached or None

    decisions = EditorialDecision.objects.count()
    if decisions < 10:
        cache.set("home_kpis", {}, 300)
        return None

    kpi = EditorialKPI.objects.order_by("-month").first()
    result: dict[str, Any] = {
        "acceptance_rate": kpi.acceptance_rate if kpi else None,
        "median_days_to_first_decision": kpi.median_days_to_first_decision if kpi else None,
    }
    if result["acceptance_rate"] is None and result["median_days_to_first_decision"] is None:
        computed = compute_kpi_window()
        result.update(computed)
    cache.set("home_kpis", result, 600)
    return result


def compute_kpi_window(months: int = 12) -> dict[str, Any]:
    """Compute acceptance rate and decision speed over a rolling window."""
    from apps.submissions.models import EditorialDecision, Submission

    since = timezone.now() - timedelta(days=30 * months)
    decisions = EditorialDecision.objects.filter(decided_at__gte=since)
    accepted = decisions.filter(decision=EditorialDecision.Decision.ACCEPT).count()
    rejected = decisions.filter(
        decision__in=[EditorialDecision.Decision.REJECT, EditorialDecision.Decision.DESK_REJECT]
    ).count()
    total = accepted + rejected
    acceptance_rate = round(accepted / total * 100, 1) if total else None

    durations: list[float] = []
    for submission in Submission.objects.filter(submitted_at__gte=since).prefetch_related(
        "decisions"
    ):
        first = submission.decisions.order_by("decided_at").first()
        if first and submission.submitted_at:
            durations.append((first.decided_at - submission.submitted_at).days)
    median_days = round(statistics.median(durations), 1) if durations else None

    return {"acceptance_rate": acceptance_rate, "median_days_to_first_decision": median_days}


def public_statistics() -> dict[str, Any]:
    """Data for the public ``/statistics/`` page (SPEC §6.9)."""
    from apps.journal.models import Author
    from apps.submissions.models import ReviewAssignment

    cached = cache.get("public_statistics")
    if cached is not None:
        return cached

    articles = Article.objects.public()
    article_count = articles.count()
    author_rows = Author.objects.filter(article__in=articles)
    countries = sorted(
        {a.country.name for a in author_rows.select_related() if a.country},
    )
    author_names = {(a.given_name.lower(), a.family_name.lower()) for a in author_rows}

    since_year = timezone.now().date() - timedelta(days=365)
    downloads_last_year = (
        DailyArticleStat.objects.filter(date__gte=since_year).aggregate(total=Sum("downloads"))[
            "total"
        ]
        or 0
    )
    reviewers_active = (
        ReviewAssignment.objects.filter(completed_at__gte=timezone.now() - timedelta(days=365))
        .values("reviewer")
        .distinct()
        .count()
    )

    window = compute_kpi_window()
    monthly = monthly_series()

    stats = {
        "articles_published": article_count,
        "authors": len(author_names),
        "countries": countries,
        "country_count": len(countries),
        "acceptance_rate": window["acceptance_rate"],
        "median_days_to_first_decision": window["median_days_to_first_decision"],
        "median_review_days": median_review_days(),
        "reviewers_active": reviewers_active,
        "downloads_last_year": downloads_last_year,
        "monthly": monthly,
        "has_data": article_count > 0,
    }
    cache.set("public_statistics", stats, 900)
    return stats


def median_review_days() -> float | None:
    """Median number of days reviewers take to return a completed review."""
    from apps.submissions.models import ReviewAssignment

    values = [
        (a.completed_at - a.invited_at).days
        for a in ReviewAssignment.objects.filter(completed_at__isnull=False).only(
            "completed_at", "invited_at"
        )
        if a.invited_at and a.completed_at
    ]
    return round(statistics.median(values), 1) if values else None


def monthly_series(months: int = 12) -> list[dict[str, Any]]:
    """Submissions and acceptances per month for the statistics bar chart."""
    from apps.submissions.models import EditorialDecision, Submission

    today = timezone.now().date().replace(day=1)
    series: list[dict[str, Any]] = []
    for offset in range(months - 1, -1, -1):
        month = _shift_month(today, -offset)
        next_month = _shift_month(month, 1)
        submissions = Submission.objects.filter(
            submitted_at__date__gte=month, submitted_at__date__lt=next_month
        ).count()
        accepted = EditorialDecision.objects.filter(
            decided_at__date__gte=month,
            decided_at__date__lt=next_month,
            decision=EditorialDecision.Decision.ACCEPT,
        ).count()
        series.append({"month": month, "submissions": submissions, "accepted": accepted})
    return _with_chart_geometry(series)


def _with_chart_geometry(series: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Add SVG coordinates so the statistics bar chart needs no JavaScript.

    The chart canvas is 720x240 with the baseline at y=200 and the axis at
    x=40; each month occupies a 55-pixel column with two 18-pixel bars.
    """
    peak = max([max(p["submissions"], p["accepted"]) for p in series] or [0]) or 1
    for index, point in enumerate(series):
        left = 52 + index * 55
        point["x_submissions"] = left
        point["x_accepted"] = left + 20
        point["x_label"] = left + 19
        point["h_submissions"] = round(point["submissions"] / peak * 170)
        point["h_accepted"] = round(point["accepted"] / peak * 170)
        point["y_submissions"] = 200 - point["h_submissions"]
        point["y_accepted"] = 200 - point["h_accepted"]
    return series


def _shift_month(value: date, delta: int) -> date:
    """Return ``value`` shifted by ``delta`` months, on the first of the month."""
    total = value.year * 12 + (value.month - 1) + delta
    return date(total // 12, total % 12 + 1, 1)


def aggregate_day(target: date) -> int:
    """Fold raw events of one day into :class:`DailyArticleStat` rows."""
    rows = (
        AccessEvent.objects.filter(occurred_at__date=target, is_bot=False)
        .values("article")
        .annotate(
            views=Count("id", filter=Q(kind=AccessEvent.Kind.VIEW)),
            downloads=Count("id", filter=Q(kind=AccessEvent.Kind.DOWNLOAD)),
        )
    )
    written = 0
    for row in rows:
        DailyArticleStat.objects.update_or_create(
            article_id=row["article"],
            date=target,
            defaults={"views": row["views"], "downloads": row["downloads"]},
        )
        written += 1
    return written


def refresh_article_totals() -> int:
    """Recompute denormalised totals on every article from daily statistics."""
    updated = 0
    aggregates = DailyArticleStat.objects.values("article").annotate(
        views=Sum("views"), downloads=Sum("downloads")
    )
    for row in aggregates:
        Article.objects.filter(pk=row["article"]).update(
            views_count=row["views"] or 0, downloads_count=row["downloads"] or 0
        )
        updated += 1
    return updated
