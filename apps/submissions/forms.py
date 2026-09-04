"""Forms for the five-step submission wizard and editorial actions."""

from __future__ import annotations

from typing import Any

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.core.markdown import strip_markdown
from apps.journal.models import JELCode, Section
from apps.submissions.models import (
    EditorialDecision,
    Review,
    Submission,
    SubmissionAuthor,
    SubmissionFile,
)
from apps.submissions.services import ALLOWED_EXTENSIONS, count_words, validate_upload

TEXT_INPUT = {"class": "input"}
TEXTAREA = {"class": "textarea"}
SELECT = {"class": "select"}

#: The declarations an author must confirm in step 1.
DECLARATIONS: list[tuple[str, Any]] = [
    ("original", _("The manuscript is original and has not been published before.")),
    (
        "not_under_consideration",
        _("The manuscript is not under consideration by another journal."),
    ),
    ("guidelines", _("The manuscript follows the author guidelines and reference style.")),
    ("anonymised", _("The manuscript file contains no information identifying the authors.")),
    ("ethics", _("The research complies with the journal's publication ethics policy.")),
    ("license", _("All authors agree to publication under the CC BY 4.0 licence.")),
]


class WizardStartForm(forms.ModelForm):
    """Step 1 — section, type, language and mandatory declarations."""

    def __init__(self, *args, **kwargs):
        """Build one required checkbox per declaration."""
        super().__init__(*args, **kwargs)
        self.fields["section"].queryset = Section.objects.filter(is_active=True)
        self.fields["section"].widget.attrs.update(SELECT)
        self.fields["article_type"].widget.attrs.update(SELECT)
        self.fields["language"].widget.attrs.update(SELECT)
        self.fields["ai_use_statement"].widget.attrs.update(
            {
                **TEXTAREA,
                "rows": 4,
                "placeholder": _("Describe any use of generative AI, or write 'None'."),
            }
        )
        existing = (self.instance.author_declarations or {}) if self.instance.pk else {}
        for key, label in DECLARATIONS:
            self.fields[f"declare_{key}"] = forms.BooleanField(
                required=True, label=label, initial=existing.get(key, False)
            )

    class Meta:
        model = Submission
        fields = ("section", "article_type", "language", "ai_use_statement")
        labels = {
            "section": _("Section"),
            "article_type": _("Article type"),
            "language": _("Manuscript language"),
            "ai_use_statement": _("Declaration on the use of generative AI"),
        }

    def clean_ai_use_statement(self) -> str:
        """Require an explicit statement, even if it is 'None'."""
        value = (self.cleaned_data.get("ai_use_statement") or "").strip()
        if not value:
            raise forms.ValidationError(
                _("Please state your use of generative AI, or write 'None'.")
            )
        return value

    def save(self, commit: bool = True) -> Submission:
        """Persist the declarations as a JSON map on the submission."""
        submission = super().save(commit=False)
        submission.author_declarations = {
            key: bool(self.cleaned_data.get(f"declare_{key}")) for key, _label in DECLARATIONS
        }
        submission.anonymised_file_ok = submission.author_declarations.get("anonymised", False)
        if commit:
            submission.save()
        return submission


class FileUploadForm(forms.Form):
    """Step 2 — manuscript and supporting files."""

    manuscript = forms.FileField(
        required=False,
        label=_("Anonymised manuscript"),
        help_text=_("PDF or DOCX, at most %(size)s MB, with no author information.")
        % {"size": settings.MAX_UPLOAD_SIZE_MB},
    )
    title_page = forms.FileField(
        required=False,
        label=_("Title page"),
        help_text=_("Separate file listing all authors, affiliations and contact details."),
    )
    figures = forms.FileField(required=False, label=_("Figures and tables"))
    supplementary = forms.FileField(required=False, label=_("Data or supplementary material"))

    #: Form field name → submission file kind.
    KIND_MAP = {
        "manuscript": SubmissionFile.Kind.MANUSCRIPT_ANON,
        "title_page": SubmissionFile.Kind.TITLE_PAGE,
        "figures": SubmissionFile.Kind.FIGURES,
        "supplementary": SubmissionFile.Kind.SUPPLEMENTARY,
    }

    def clean(self) -> dict[str, Any]:
        """Validate every uploaded file against its slot's rules."""
        cleaned = super().clean()
        for field, kind in self.KIND_MAP.items():
            uploaded = cleaned.get(field)
            if uploaded:
                try:
                    validate_upload(uploaded, kind)
                except forms.ValidationError as exc:
                    self.add_error(field, exc)
        return cleaned

    def word_count(self) -> int:
        """Word count of the uploaded manuscript, when one was supplied."""
        manuscript = self.cleaned_data.get("manuscript")
        return count_words(manuscript) if manuscript else 0


class MetadataForm(forms.Form):
    """Step 3 — multilingual title, abstract, keywords and JEL codes."""

    LANGUAGES = (("en", _("English")), ("uz", _("Uzbek (Latin)")), ("ru", _("Russian")))

    jel_codes = forms.ModelMultipleChoiceField(
        queryset=JELCode.objects.none(),
        required=True,
        label=_("JEL codes"),
        widget=forms.SelectMultiple(attrs={"class": "select", "size": 10}),
        help_text=_("Select between 1 and 5 codes."),
    )
    funding_statement = forms.CharField(
        required=False, label=_("Funding"), widget=forms.Textarea(attrs={**TEXTAREA, "rows": 3})
    )
    conflict_of_interest_statement = forms.CharField(
        required=True,
        label=_("Conflict of interest"),
        initial=_("The authors declare no conflict of interest."),
        widget=forms.Textarea(attrs={**TEXTAREA, "rows": 3}),
    )
    data_availability_statement = forms.CharField(
        required=False,
        label=_("Data availability"),
        widget=forms.Textarea(attrs={**TEXTAREA, "rows": 3}),
    )
    references = forms.CharField(
        required=False,
        label=_("References"),
        help_text=_("One reference per line, APA 7th style."),
        widget=forms.Textarea(attrs={**TEXTAREA, "rows": 10}),
    )

    def __init__(self, *args, **kwargs):
        """Create title/abstract/keyword fields for each required language."""
        super().__init__(*args, **kwargs)
        self.fields["jel_codes"].queryset = JELCode.objects.filter(level=2).order_by("code")
        for code, label in self.LANGUAGES:
            self.fields[f"title_{code}"] = forms.CharField(
                label=_("Title (%(lang)s)") % {"lang": label},
                max_length=500,
                widget=forms.TextInput(attrs=TEXT_INPUT),
            )
            self.fields[f"abstract_{code}"] = forms.CharField(
                label=_("Abstract (%(lang)s)") % {"lang": label},
                widget=forms.Textarea(attrs={**TEXTAREA, "rows": 8}),
                help_text=_("Between %(min)s and %(max)s words.")
                % {"min": settings.ABSTRACT_MIN_WORDS, "max": settings.ABSTRACT_MAX_WORDS},
            )
            self.fields[f"keywords_{code}"] = forms.CharField(
                label=_("Keywords (%(lang)s)") % {"lang": label},
                widget=forms.TextInput(attrs=TEXT_INPUT),
                help_text=_("%(min)s–%(max)s keywords, comma separated.")
                % {"min": settings.KEYWORDS_MIN, "max": settings.KEYWORDS_MAX},
            )

    def clean_jel_codes(self):
        """Enforce the 1–5 JEL code policy."""
        codes = self.cleaned_data["jel_codes"]
        if not (settings.JEL_MIN <= len(codes) <= settings.JEL_MAX):
            raise forms.ValidationError(
                _("Select between %(min)s and %(max)s JEL codes.")
                % {"min": settings.JEL_MIN, "max": settings.JEL_MAX}
            )
        return codes

    def clean(self) -> dict[str, Any]:
        """Check abstract length and keyword count in every language."""
        cleaned = super().clean()
        for code, _label in self.LANGUAGES:
            abstract = cleaned.get(f"abstract_{code}")
            if abstract:
                words = len(strip_markdown(abstract).split())
                if not (settings.ABSTRACT_MIN_WORDS <= words <= settings.ABSTRACT_MAX_WORDS):
                    self.add_error(
                        f"abstract_{code}",
                        _(
                            "The abstract has %(count)s words; it must have between %(min)s and %(max)s."
                        )
                        % {
                            "count": words,
                            "min": settings.ABSTRACT_MIN_WORDS,
                            "max": settings.ABSTRACT_MAX_WORDS,
                        },
                    )
            keywords = cleaned.get(f"keywords_{code}")
            if keywords:
                count = len([k for k in keywords.split(",") if k.strip()])
                if not (settings.KEYWORDS_MIN <= count <= settings.KEYWORDS_MAX):
                    self.add_error(
                        f"keywords_{code}",
                        _("Provide between %(min)s and %(max)s keywords (you gave %(count)s).")
                        % {
                            "min": settings.KEYWORDS_MIN,
                            "max": settings.KEYWORDS_MAX,
                            "count": count,
                        },
                    )
        return cleaned


class SubmissionAuthorForm(forms.ModelForm):
    """One row of the authors formset."""

    class Meta:
        model = SubmissionAuthor
        fields = (
            "order",
            "given_name",
            "family_name",
            "email",
            "orcid",
            "affiliation",
            "city",
            "country",
            "is_corresponding",
        )
        widgets = {
            "order": forms.NumberInput(attrs={"class": "input", "min": 1}),
            "given_name": forms.TextInput(attrs=TEXT_INPUT),
            "family_name": forms.TextInput(attrs=TEXT_INPUT),
            "email": forms.EmailInput(attrs=TEXT_INPUT),
            "orcid": forms.TextInput(attrs={**TEXT_INPUT, "placeholder": "0000-0000-0000-0000"}),
            "affiliation": forms.TextInput(attrs=TEXT_INPUT),
            "city": forms.TextInput(attrs=TEXT_INPUT),
            "country": forms.Select(attrs=SELECT),
        }

    def clean_orcid(self) -> str:
        """Validate the ORCID iD checksum format."""
        import re

        value = (self.cleaned_data.get("orcid") or "").strip()
        if value and not re.fullmatch(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", value):
            raise forms.ValidationError(_("Enter an ORCID iD as 0000-0000-0000-0000."))
        return value


AuthorFormSet = forms.modelformset_factory(
    SubmissionAuthor,
    form=SubmissionAuthorForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class ReviewersForm(forms.ModelForm):
    """Step 4 — suggested/opposed reviewers and the cover letter."""

    suggested = forms.CharField(
        required=False,
        label=_("Suggested reviewers"),
        help_text=_("One per line: name, e-mail, affiliation."),
        widget=forms.Textarea(attrs={**TEXTAREA, "rows": 4}),
    )
    opposed = forms.CharField(
        required=False,
        label=_("Reviewers to exclude"),
        help_text=_("One per line, with a short reason."),
        widget=forms.Textarea(attrs={**TEXTAREA, "rows": 3}),
    )

    class Meta:
        model = Submission
        fields = ("cover_letter",)
        widgets = {"cover_letter": forms.Textarea(attrs={**TEXTAREA, "rows": 8})}
        labels = {"cover_letter": _("Cover letter")}

    def save(self, commit: bool = True) -> Submission:
        """Store the reviewer suggestions as JSON lists."""
        submission = super().save(commit=False)
        submission.suggested_reviewers = [
            line.strip() for line in self.cleaned_data["suggested"].splitlines() if line.strip()
        ]
        submission.opposed_reviewers = [
            line.strip() for line in self.cleaned_data["opposed"].splitlines() if line.strip()
        ]
        if commit:
            submission.save()
        return submission


class RevisionUploadForm(forms.Form):
    """Author upload of a revised manuscript and response letter."""

    revision = forms.FileField(label=_("Revised manuscript"))
    response = forms.FileField(required=False, label=_("Response to reviewers (file)"))
    response_letter = forms.CharField(
        required=True,
        label=_("Response to reviewers"),
        widget=forms.Textarea(attrs={**TEXTAREA, "rows": 10}),
    )

    def clean_revision(self):
        """Validate the revised manuscript upload."""
        uploaded = self.cleaned_data["revision"]
        validate_upload(uploaded, SubmissionFile.Kind.REVISION)
        return uploaded

    def clean_response(self):
        """Validate the optional response file."""
        uploaded = self.cleaned_data.get("response")
        if uploaded:
            validate_upload(uploaded, SubmissionFile.Kind.RESPONSE)
        return uploaded


class SimilarityForm(forms.ModelForm):
    """Editor records the similarity result during screening."""

    class Meta:
        model = Submission
        fields = ("similarity_percent", "similarity_report", "similarity_override_reason")
        widgets = {
            "similarity_percent": forms.NumberInput(
                attrs={"class": "input", "min": 0, "max": 100, "step": "0.1"}
            ),
            "similarity_override_reason": forms.Textarea(attrs={**TEXTAREA, "rows": 3}),
        }
        labels = {
            "similarity_percent": _("Similarity (%)"),
            "similarity_report": _("Similarity report (PDF)"),
            "similarity_override_reason": _("Justification for exceeding the threshold"),
        }

    def clean(self) -> dict[str, Any]:
        """Require a justification when the threshold is exceeded."""
        from apps.core.services import get_site_settings

        cleaned = super().clean()
        percent = cleaned.get("similarity_percent")
        threshold = get_site_settings().similarity_threshold
        if (
            percent is not None
            and percent > threshold
            and not cleaned.get("similarity_override_reason")
        ):
            self.add_error(
                "similarity_override_reason",
                _("Similarity above %(threshold)s%% requires a written justification.")
                % {"threshold": threshold},
            )
        return cleaned


class DecisionForm(forms.ModelForm):
    """Editorial decision dialog."""

    class Meta:
        model = EditorialDecision
        fields = ("decision", "letter")
        widgets = {
            "decision": forms.Select(attrs=SELECT),
            "letter": forms.Textarea(attrs={**TEXTAREA, "rows": 16}),
        }
        labels = {"decision": _("Decision"), "letter": _("Letter to the author")}


class ReviewForm(forms.ModelForm):
    """The structured reviewer form (six criteria plus comments)."""

    class Meta:
        model = Review
        fields = ("recommendation", "comments_to_authors", "comments_to_editor", "attachment")
        widgets = {
            "recommendation": forms.Select(attrs=SELECT),
            "comments_to_authors": forms.Textarea(attrs={**TEXTAREA, "rows": 12}),
            "comments_to_editor": forms.Textarea(attrs={**TEXTAREA, "rows": 6}),
        }
        labels = {
            "recommendation": _("Recommendation"),
            "comments_to_authors": _("Comments to the authors"),
            "comments_to_editor": _("Confidential comments to the editor"),
            "attachment": _("Annotated file (optional)"),
        }

    def __init__(self, *args, **kwargs):
        """Add one 1–5 score field per review criterion."""
        super().__init__(*args, **kwargs)
        existing = self.instance.scores if self.instance and self.instance.pk else {}
        for key, label in Review.SCORE_FIELDS:
            self.fields[f"score_{key}"] = forms.TypedChoiceField(
                label=label,
                choices=[(i, str(i)) for i in range(1, 6)],
                coerce=int,
                widget=forms.RadioSelect(attrs={"class": "score-radio"}),
                initial=existing.get(key),
                required=True,
            )

    def clean_comments_to_authors(self) -> str:
        """Require a substantive review."""
        value = (self.cleaned_data.get("comments_to_authors") or "").strip()
        if len(value) < 100:
            raise forms.ValidationError(
                _("Please write at least 100 characters of feedback for the authors.")
            )
        return value

    def save(self, commit: bool = True) -> Review:
        """Collect the score fields into the ``scores`` JSON map."""
        review = super().save(commit=False)
        review.scores = {
            key: self.cleaned_data.get(f"score_{key}") for key, _label in Review.SCORE_FIELDS
        }
        if commit:
            review.save()
        return review


class InviteReviewerForm(forms.Form):
    """Invite an existing user or a new person by e-mail."""

    reviewer_id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    email = forms.EmailField(
        required=False, label=_("E-mail"), widget=forms.EmailInput(attrs=TEXT_INPUT)
    )
    first_name = forms.CharField(
        required=False, label=_("Given name"), widget=forms.TextInput(attrs=TEXT_INPUT)
    )
    last_name = forms.CharField(
        required=False, label=_("Family name"), widget=forms.TextInput(attrs=TEXT_INPUT)
    )
    due_days = forms.IntegerField(
        required=False,
        initial=settings.REVIEW_DUE_DAYS,
        label=_("Days to complete"),
        widget=forms.NumberInput(attrs={"class": "input", "min": 7, "max": 90}),
    )

    def clean(self) -> dict[str, Any]:
        """Require either an existing reviewer or an e-mail address."""
        cleaned = super().clean()
        if not cleaned.get("reviewer_id") and not cleaned.get("email"):
            raise forms.ValidationError(_("Choose a reviewer or enter an e-mail address."))
        return cleaned


class WithdrawForm(forms.Form):
    """Author withdrawal request."""

    reason = forms.CharField(
        label=_("Reason for withdrawal"),
        widget=forms.Textarea(attrs={**TEXTAREA, "rows": 4}),
    )


class DiscussionMessageForm(forms.Form):
    """Post a message into a submission discussion."""

    body = forms.CharField(label=_("Message"), widget=forms.Textarea(attrs={**TEXTAREA, "rows": 4}))


#: Exposed so templates can render the allowed extensions per slot.
UPLOAD_EXTENSIONS = ALLOWED_EXTENSIONS
