"""django-allauth adapters: e-mail delivery, language and ORCID handling."""

from __future__ import annotations

from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpRequest
from django.utils import translation


class AccountAdapter(DefaultAccountAdapter):
    """Send allauth e-mails through the journal's branded template layout."""

    def get_login_redirect_url(self, request: HttpRequest) -> str:
        """Send users to their role dashboard after signing in."""
        return f"/{translation.get_language() or 'en'}/dashboard/"

    def send_mail(self, template_prefix: str, email: str, context: dict[str, Any]) -> None:
        """Render allauth mails inside the shared e-mail layout."""
        context.setdefault("site_name", "ALGORITHM: Review of Economic Research")
        super().send_mail(template_prefix, email, context)

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
