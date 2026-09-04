#!/usr/bin/env python
"""Capture Playwright screenshots of every page into ``docs/screenshots/``.

Starts a live Django server against the development database, walks the public
site in English and Uzbek Cyrillic, signs in as each role to capture the
dashboards, and takes the responsive set at 360, 768, 1280 and 1920 pixels
(SPEC §15.13).  It also runs axe-core over the key pages and writes the
accessibility findings to ``docs/screenshots/accessibility.json``.

    python scripts/screenshots.py                 # everything
    python scripts/screenshots.py --skip-axe      # screenshots only
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import threading
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

OUT_DIR = BASE_DIR / "docs" / "screenshots"

#: Public pages captured at desktop width in English and Uzbek Cyrillic.
PUBLIC_PAGES: list[tuple[str, str]] = [
    ("01-home", "/{lang}/"),
    ("02-issue", "/{lang}/issues/{volume}/{issue}/"),
    ("03-article", "/{lang}/article/{article}/"),
    ("04-archive", "/{lang}/issues/"),
    ("05-search", "/{lang}/search/?q=customs"),
    ("06-board", "/{lang}/about/editorial-board/"),
    ("07-policy", "/{lang}/about/publication-ethics/"),
    ("08-for-authors", "/{lang}/for-authors/"),
    ("15-auth", "/{lang}/accounts/login/"),
    ("16-statistics", "/{lang}/statistics/"),
    ("19-online-first", "/{lang}/issues/online-first/"),
    ("20-jel", "/{lang}/jel/"),
    ("21-announcements", "/{lang}/announcements/"),
    ("22-contact", "/{lang}/about/contact/"),
    ("23-aims-and-scope", "/{lang}/about/aims-and-scope/"),
    ("24-peer-review", "/{lang}/about/peer-review/"),
    ("25-fees", "/{lang}/about/fees/"),
    ("26-checklist", "/{lang}/for-authors/checklist/"),
]

#: Pages captured at every breakpoint (SPEC §15.13).
RESPONSIVE_PAGES: list[tuple[str, str]] = [
    ("home", "/en/"),
    ("issue", "/en/issues/{volume}/{issue}/"),
    ("article", "/en/article/{article}/"),
    ("dashboard", "/en/dashboard/"),
]
BREAKPOINTS = [360, 768, 1280, 1920]

#: Pages checked with axe-core.
AXE_PAGES: list[tuple[str, str]] = [
    ("home", "/en/"),
    ("issue", "/en/issues/{volume}/{issue}/"),
    ("article", "/en/article/{article}/"),
    ("search", "/en/search/?q=trade"),
    ("board", "/en/about/editorial-board/"),
    ("submit", "/en/submit/"),
    ("dashboard", "/en/dashboard/"),
]

AXE_CDN = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js"


def free_port() -> int:
    """Return a free TCP port on the loopback interface."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def start_server(port: int) -> threading.Thread:
    """Run the Django development server in a daemon thread."""
    import django

    django.setup()
    from django.core.management import call_command

    def run() -> None:
        call_command(
            "runserver", f"127.0.0.1:{port}", use_reloader=False, use_threading=True, verbosity=0
        )

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    for _ in range(60):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return thread
        except OSError:
            time.sleep(0.5)
    raise RuntimeError("the development server did not start")


def context_values() -> dict[str, str]:
    """Resolve a real article and issue from the database for the URLs."""
    from apps.journal.models import Article, Issue

    article = Article.objects.public().order_by("id").first()
    issue = Issue.objects.published().select_related("volume").first()
    if article is None or issue is None:
        raise SystemExit("Run `python manage.py seed_demo` before taking screenshots.")
    return {
        "article": str(article.pk),
        "volume": str(issue.volume.number),
        "issue": str(issue.number),
    }


def login_cookie(email: str, port: int) -> dict[str, str]:
    """Create a session for ``email`` and return it as a Playwright cookie."""
    from django.conf import settings
    from django.contrib.auth import login
    from django.contrib.sessions.backends.db import SessionStore
    from django.http import HttpRequest
    from django_otp.plugins.otp_totp.models import TOTPDevice

    from apps.accounts.models import User

    user = User.objects.get(email=email)
    if user.requires_2fa:
        TOTPDevice.objects.get_or_create(
            user=user, name="screenshots", defaults={"confirmed": True}
        )
        TOTPDevice.objects.filter(user=user).update(confirmed=True)

    request = HttpRequest()
    request.session = SessionStore()
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    request.session.save()
    return {
        "name": settings.SESSION_COOKIE_NAME,
        "value": request.session.session_key,
        "domain": "127.0.0.1",
        "path": "/",
    }


def capture(page, url: str, target: Path, full: bool = True) -> None:
    """Navigate to ``url`` and write a screenshot to ``target``."""
    target.parent.mkdir(parents=True, exist_ok=True)
    page.goto(url, wait_until="networkidle", timeout=30_000)
    page.wait_for_timeout(300)
    page.screenshot(path=str(target), full_page=full)
    print(f"  {target.relative_to(BASE_DIR)}")


def run_axe(page, url: str) -> dict:
    """Run axe-core against ``url`` and return the violation summary."""
    page.goto(url, wait_until="networkidle", timeout=30_000)
    try:
        page.add_script_tag(url=AXE_CDN)
    except Exception:
        local = BASE_DIR / "static" / "js" / "axe.min.js"
        if not local.exists():
            return {"error": "axe-core unavailable (no network and no vendored copy)"}
        page.add_script_tag(path=str(local))
    result = page.evaluate("async () => await axe.run(document, {resultTypes: ['violations']})")
    return {
        "violations": [
            {
                "id": v["id"],
                "impact": v.get("impact"),
                "help": v["help"],
                "nodes": len(v["nodes"]),
            }
            for v in result.get("violations", [])
        ]
    }


def main() -> int:
    """Capture every screenshot and, unless skipped, the axe-core report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-axe", action="store_true")
    parser.add_argument("--languages", default="en,uz-cyrl")
    args = parser.parse_args()

    port = free_port()
    start_server(port)
    base = f"http://127.0.0.1:{port}"
    values = context_values()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright

    languages = [code.strip() for code in args.languages.split(",") if code.strip()]
    axe_report: dict[str, dict] = {}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()

        # --- public pages, per language -----------------------------------
        for language in languages:
            context = browser.new_context(viewport={"width": 1440, "height": 1000})
            page = context.new_page()
            print(f"public pages ({language}):")
            for name, template in PUBLIC_PAGES:
                url = base + template.format(lang=language, **values)
                capture(page, url, OUT_DIR / f"{name}-{language}.png")
            context.close()

        # --- role dashboards ----------------------------------------------
        roles = [
            ("10-dashboard-editor", "editor@algorithm-journal.uz", "/en/dashboard/"),
            (
                "10b-queue-in-review",
                "editor@algorithm-journal.uz",
                "/en/dashboard/queue/in_review/",
            ),
            ("12-dashboard-reviewer", "reviewer1@algorithm-journal.uz", "/en/review/"),
            ("13-dashboard-author", "author@algorithm-journal.uz", "/en/dashboard/"),
            ("09-submit-wizard", "author@algorithm-journal.uz", "/en/submit/"),
            ("17-production-queue", "production@algorithm-journal.uz", "/en/production/"),
        ]
        print("dashboards:")
        for name, email, path in roles:
            context = browser.new_context(viewport={"width": 1440, "height": 1000})
            context.add_cookies([login_cookie(email, port)])
            page = context.new_page()
            capture(page, base + path, OUT_DIR / f"{name}.png")
            context.close()

        # --- editor submission detail and production issue builder ---------
        from apps.journal.models import Issue
        from apps.submissions.models import Submission, SubmissionStatus

        submission = (
            Submission.objects.filter(status=SubmissionStatus.UNDER_REVIEW).first()
            or Submission.objects.exclude(status=SubmissionStatus.DRAFT).first()
        )
        draft_issue = Issue.objects.filter(is_published=False).first()
        extra = []
        if submission is not None:
            extra.append(
                (
                    "11-dashboard-submission",
                    "editor@algorithm-journal.uz",
                    f"/en/dashboard/submission/{submission.pk}/?tab=reviewers",
                )
            )
        if draft_issue is not None:
            extra.append(
                (
                    "14-production-issue-builder",
                    "production@algorithm-journal.uz",
                    f"/en/production/issue/{draft_issue.pk}/",
                )
            )
        for name, email, path in extra:
            context = browser.new_context(viewport={"width": 1440, "height": 1000})
            context.add_cookies([login_cookie(email, port)])
            page = context.new_page()
            capture(page, base + path, OUT_DIR / f"{name}.png")
            context.close()

        # --- responsive set -------------------------------------------------
        print("responsive:")
        for name, template in RESPONSIVE_PAGES:
            for width in BREAKPOINTS:
                context = browser.new_context(viewport={"width": width, "height": 900})
                if name == "dashboard":
                    context.add_cookies([login_cookie("editor@algorithm-journal.uz", port)])
                page = context.new_page()
                capture(
                    page,
                    base + template.format(**values),
                    OUT_DIR / "responsive" / f"{name}-{width}.png",
                )
                context.close()

        # --- accessibility ---------------------------------------------------
        if not args.skip_axe:
            print("axe-core:")
            for name, template in AXE_PAGES:
                context = browser.new_context(viewport={"width": 1440, "height": 1000})
                context.add_cookies([login_cookie("editor@algorithm-journal.uz", port)])
                page = context.new_page()
                axe_report[name] = run_axe(page, base + template.format(**values))
                violations = axe_report[name].get("violations", [])
                serious = [v for v in violations if v.get("impact") in {"serious", "critical"}]
                print(f"  {name}: {len(violations)} violations, {len(serious)} serious/critical")
                context.close()

            (OUT_DIR / "accessibility.json").write_text(
                json.dumps(axe_report, indent=2), encoding="utf-8"
            )

        browser.close()

    print(f"\nScreenshots written to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
