"""modeltranslation registrations for the submissions app."""

from __future__ import annotations

from modeltranslation.translator import TranslationOptions, register

from apps.submissions.models import Submission


@register(Submission)
class SubmissionTranslationOptions(TranslationOptions):
    """Manuscript metadata captured in English, Uzbek and Russian."""

    fields = ("title", "abstract", "keywords_text")
