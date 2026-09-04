"""Forms used by the dashboard: profile editing and 2FA enrolment."""

from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import Profile, User

TEXT_INPUT = {"class": "input"}
TEXTAREA = {"class": "textarea"}
SELECT = {"class": "select"}


class UserDetailsForm(forms.ModelForm):
    """Name and interface language."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "preferred_language")
        widgets = {
            "first_name": forms.TextInput(attrs=TEXT_INPUT),
            "last_name": forms.TextInput(attrs=TEXT_INPUT),
            "preferred_language": forms.Select(attrs=SELECT),
        }
        labels = {
            "first_name": _("Given name"),
            "last_name": _("Family name"),
            "preferred_language": _("Interface language"),
        }


class ProfileForm(forms.ModelForm):
    """Scholarly identity, affiliation and reviewer expertise."""

    class Meta:
        model = Profile
        fields = (
            "orcid",
            "affiliation",
            "department",
            "city",
            "country",
            "academic_degree",
            "academic_title",
            "scopus_author_id",
            "website",
            "expertise",
            "bio",
            "accepts_review_invitations",
        )
        widgets = {
            "orcid": forms.TextInput(attrs={**TEXT_INPUT, "placeholder": "0000-0000-0000-0000"}),
            "affiliation": forms.TextInput(attrs=TEXT_INPUT),
            "department": forms.TextInput(attrs=TEXT_INPUT),
            "city": forms.TextInput(attrs=TEXT_INPUT),
            "country": forms.Select(attrs=SELECT),
            "academic_degree": forms.TextInput(attrs=TEXT_INPUT),
            "academic_title": forms.TextInput(attrs=TEXT_INPUT),
            "scopus_author_id": forms.TextInput(attrs=TEXT_INPUT),
            "website": forms.URLInput(attrs=TEXT_INPUT),
            "expertise": forms.Textarea(attrs={**TEXTAREA, "rows": 3}),
            "bio": forms.Textarea(attrs={**TEXTAREA, "rows": 5}),
        }

    def clean_orcid(self) -> str:
        """Validate the ORCID iD format."""
        import re

        value = (self.cleaned_data.get("orcid") or "").strip()
        if value and not re.fullmatch(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", value):
            raise forms.ValidationError(_("Enter an ORCID iD as 0000-0000-0000-0000."))
        return value


class TOTPSetupForm(forms.Form):
    """Confirm a TOTP device with a six-digit code."""

    token = forms.CharField(
        label=_("Six-digit code"),
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "inputmode": "numeric",
                "autocomplete": "one-time-code",
                "pattern": "[0-9]{6}",
            }
        ),
    )
