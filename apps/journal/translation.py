"""modeltranslation registrations for the journal app."""

from __future__ import annotations

from modeltranslation.translator import TranslationOptions, register

from apps.journal.models import (
    Article,
    Author,
    EditorialBoardMember,
    Issue,
    JELCode,
    Keyword,
    Section,
    Volume,
)


@register(Section)
class SectionTranslationOptions(TranslationOptions):
    """Section names and descriptions."""

    fields = ("name", "description")


@register(Volume)
class VolumeTranslationOptions(TranslationOptions):
    """Optional volume title."""

    fields = ("title",)


@register(Issue)
class IssueTranslationOptions(TranslationOptions):
    """Issue title and editorial note."""

    fields = ("title", "description")


@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    """Article metadata required in English, Uzbek and Russian."""

    fields = (
        "title",
        "subtitle",
        "abstract",
        "copyright_holder",
        "funding_statement",
        "conflict_of_interest_statement",
        "data_availability_statement",
        "ai_use_statement",
        "acknowledgements",
        "retraction_notice",
    )


@register(Author)
class AuthorTranslationOptions(TranslationOptions):
    """Author affiliation and biography per language."""

    fields = ("affiliation", "bio", "given_name_native", "family_name_native")


@register(Keyword)
class KeywordTranslationOptions(TranslationOptions):
    """Keyword text per language."""

    fields = ("name",)


@register(JELCode)
class JELCodeTranslationOptions(TranslationOptions):
    """JEL labels translated from the official English list."""

    fields = ("label",)


@register(EditorialBoardMember)
class EditorialBoardMemberTranslationOptions(TranslationOptions):
    """Board member descriptions per language."""

    fields = ("full_name", "degree", "academic_title", "affiliation", "bio", "expertise")
