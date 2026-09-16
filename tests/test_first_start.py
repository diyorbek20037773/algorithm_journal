"""First-start behaviour: content seeding and the optional Google sign-in."""

from __future__ import annotations

from io import StringIO

import pytest
from django.core.management import call_command

from apps.core.models import Page
from apps.journal.models import JELCode, Section

pytestmark = pytest.mark.django_db


def test_content_only_seed_creates_pages_but_no_users(django_user_model) -> None:
    """A blank database gets policy pages, sections and JEL codes — no accounts."""
    out = StringIO()
    call_command("seed_demo", "--content-only", "--if-empty", stdout=out)
    assert Page.objects.exists()
    assert Section.objects.exists()
    assert JELCode.objects.exists()
    assert not django_user_model.objects.exists()
    assert "Content seed complete" in out.getvalue()


def test_if_empty_is_a_no_op_when_pages_exist(django_user_model) -> None:
    """The entrypoint may run the seed on every start without touching content."""
    call_command("seed_demo", "--content-only", stdout=StringIO())
    page = Page.objects.first()
    page.title = "Edited by the editorial office"
    page.save(update_fields=["title"])
    out = StringIO()
    call_command("seed_demo", "--content-only", "--if-empty", stdout=out)
    page.refresh_from_db()
    assert page.title == "Edited by the editorial office"
    assert "nothing to seed" in out.getvalue()


def test_google_button_only_with_credentials(client_anon, about_pages, settings) -> None:
    """The Google button appears only once a client id and secret are configured."""
    settings.GOOGLE_CLIENT_ID = ""
    settings.GOOGLE_CLIENT_SECRET = ""
    assert "google/login" not in client_anon.get("/en/accounts/login/").content.decode()
    settings.GOOGLE_CLIENT_ID = "id"
    settings.GOOGLE_CLIENT_SECRET = "secret"
    html = client_anon.get("/en/accounts/login/").content.decode()
    assert "/accounts/google/login/" in html
    assert "Sign in with Google" in html
