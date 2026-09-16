"""The account pages and mails carry the journal's own layout, not allauth's stock one."""

from __future__ import annotations

import re

import pytest
from django.core import mail

pytestmark = pytest.mark.django_db


def test_signup_sends_a_branded_confirmation_mail(
    client_anon, about_pages, site_settings, settings
) -> None:
    """With mandatory verification, registering sends one branded HTML mail."""
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    response = client_anon.post(
        "/en/accounts/signup/",
        {
            "email": "new.author@example.org",
            "password1": "Correct-Horse-Battery-9",
            "password2": "Correct-Horse-Battery-9",
        },
        follow=True,
    )
    assert response.status_code == 200
    html = response.content.decode()
    assert "Check your inbox" in html  # our verification_sent.html, not allauth's
    assert 'class="card"' in html
    assert len(mail.outbox) == 1
    message = mail.outbox[0]
    assert site_settings.journal_name in message.subject
    assert "Hello from" not in message.body
    assert re.search(r"/accounts/confirm-email/[^/\s]+/", message.body)
    assert message.alternatives and "text/html" in message.alternatives[0][1]
    assert site_settings.journal_name in message.alternatives[0][0]


def test_password_reset_pages_are_styled(client_anon, about_pages, author_user) -> None:
    """Every step of the reset flow renders inside the styled card."""
    response = client_anon.post(
        "/en/accounts/password/reset/", {"email": author_user.email}, follow=True
    )
    assert response.status_code == 200
    assert "Check your inbox" in response.content.decode()
    assert len(mail.outbox) == 1
    assert "Reset your password" in mail.outbox[0].subject
    link = re.search(r"https?://\S+/accounts/password/reset/key/\S+", mail.outbox[0].body)
    assert link
    path = re.sub(r"^https?://[^/]+", "", link.group(0))
    page = client_anon.get(path, follow=True)
    assert page.status_code == 200
    assert "Choose a new password" in page.content.decode()


def test_signup_without_verification_signs_the_user_in(client_anon, about_pages) -> None:
    """By default (D42) a new account is active at once and no mail is sent."""
    response = client_anon.post(
        "/en/accounts/signup/",
        {
            "email": "quick.author@example.org",
            "password1": "Correct-Horse-Battery-9",
            "password2": "Correct-Horse-Battery-9",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert response.wsgi_request.user.is_authenticated
    assert mail.outbox == []
