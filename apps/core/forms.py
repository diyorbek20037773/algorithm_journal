"""Public forms owned by the core app."""

from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.models import ContactMessage


class ContactForm(forms.ModelForm):
    """Contact form with a honeypot field instead of an external captcha."""

    website = forms.CharField(
        required=False,
        label=_("Leave this field empty"),
        widget=forms.TextInput(attrs={"autocomplete": "off", "tabindex": "-1"}),
    )

    class Meta:
        model = ContactMessage
        fields = ("name", "email", "subject", "body")
        widgets = {
            "name": forms.TextInput(attrs={"class": "input", "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"class": "input", "autocomplete": "email"}),
            "subject": forms.TextInput(attrs={"class": "input"}),
            "body": forms.Textarea(attrs={"class": "textarea", "rows": 7}),
        }
        labels = {
            "name": _("Your name"),
            "email": _("E-mail address"),
            "subject": _("Subject"),
            "body": _("Message"),
        }

    def clean_website(self) -> str:
        """Reject submissions that filled the hidden honeypot field."""
        value = self.cleaned_data.get("website", "")
        if value:
            raise forms.ValidationError(_("Spam detected."))
        return value

    def clean_body(self) -> str:
        """Require a message of reasonable length."""
        body = (self.cleaned_data.get("body") or "").strip()
        if len(body) < 20:
            raise forms.ValidationError(_("Please write at least 20 characters."))
        return body
