"""django-allauth adapters: e-mail delivery, language and ORCID handling."""

from __future__ import annotations

from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpRequest
from django.utils import translation
from django.utils.translation import gettext as _


class AccountAdapter(DefaultAccountAdapter):
    """Send allauth e-mails through the journal's branded template layout."""

    def get_login_redirect_url(self, request: HttpRequest) -> str:
        """Send users to their role dashboard after signing in."""
        return f"/{translation.get_language() or 'en'}/dashboard/"

    def get_signup_redirect_url(self, request: HttpRequest) -> str:
        """Keep a new author in the language they signed up in.

        allauth falls back to the unprefixed ``LOGIN_REDIRECT_URL``, which the
        locale middleware then resolved from the browser — an author signing up
        on ``/uz/`` landed on ``/en/dashboard/``.
        """
        return self.get_login_redirect_url(request)

    def send_mail(self, template_prefix: str, email: str, context: dict[str, Any]) -> None:
        """Send the account mails through the journal's branded HTML layout.

        allauth's stock messages are plain text signed "Hello from example.com".
        The confirmation and password-reset mails — the two every author sees —
        are rendered here through :func:`send_templated_email` instead, in the
        recipient's interface language; anything else falls back to allauth.
        """
        from apps.core.services import get_site_settings, send_templated_email

        site = get_site_settings()
        context.setdefault("site_name", site.journal_name)
        user = context.get("user")
        language = getattr(user, "preferred_language", None) or translation.get_language() or "en"
        activate_url = context.get("activate_url")
        reset_url = context.get("password_reset_url")

        with translation.override(language):
            if template_prefix.startswith("account/email/email_confirmation") and activate_url:
                subject = _("Confirm your e-mail address — %(site)s") % {"site": site.journal_name}
                body = _(
                    "Thank you for registering with %(site)s.\n\n"
                    "Please confirm your e-mail address by opening this link:\n\n"
                    "%(url)s\n\n"
                    "The link is valid for three days. If you did not create an account, "
                    "you can ignore this message."
                ) % {"site": site.journal_name, "url": activate_url}
                event = "email_confirm"
            elif template_prefix.startswith("account/email/password_reset_key") and reset_url:
                subject = _("Reset your password — %(site)s") % {"site": site.journal_name}
                body = _(
                    "Someone asked to reset the password for your %(site)s account.\n\n"
                    "Choose a new password here:\n\n"
                    "%(url)s\n\n"
                    "If this was not you, no action is needed — your password stays as it is."
                ) % {"site": site.journal_name, "url": reset_url}
                event = "password_reset"
            else:
                super().send_mail(template_prefix, email, context)
                return

        send_templated_email(
            event,
            to=[email],
            context={"site": site.journal_name, "url": activate_url or reset_url},
            language=language,
            fallback_subject=subject,
            fallback_body=body,
        )

    def save_user(self, request: HttpRequest, user, form, commit: bool = True):
        """Persist the preferred interface language chosen at signup."""
        user = super().save_user(request, user, form, commit=False)
        user.preferred_language = translation.get_language() or "en"
        if commit:
            user.save()
        return user


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Store the authenticated ORCID iD on the user's profile."""

    def save_user(self, request: HttpRequest, sociallogin, form=None):
        """Create the user and copy the verified ORCID iD into the profile."""
        user = super().save_user(request, sociallogin, form)
        self._store_orcid(user, sociallogin)
        return user

    def pre_social_login(self, request: HttpRequest, sociallogin) -> None:
        """Refresh the ORCID iD on every subsequent ORCID login."""
        if sociallogin.is_existing and sociallogin.user_id:
            self._store_orcid(sociallogin.user, sociallogin)

    @staticmethod
    def _store_orcid(user, sociallogin) -> None:
        """Copy the ORCID identifier from the social account onto the profile."""
        if sociallogin.account.provider != "orcid":
            return
        orcid = sociallogin.account.uid
        if not orcid:
            return
        from apps.accounts.models import Profile

        profile, _created = Profile.objects.get_or_create(user=user)
        profile.orcid = orcid
        profile.orcid_verified = True
        profile.save(update_fields=["orcid", "orcid_verified", "updated_at"])
