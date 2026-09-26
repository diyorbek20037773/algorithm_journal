"""Regressions found by the end-to-end editorial run of 2026-09-25.

A real manuscript was taken through the site in the Uzbek interface — sign-up,
the five-step wizard, screening, two reviews, acceptance, production and
Online First. Each test below pins one defect that run exposed.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from django.core import mail
from django.core.cache import cache
from django.test import Client
from django.utils import translation

from apps.accounts.models import Role
from apps.citations.services import render_citation
from apps.core.markdown import markdown_to_text
from apps.core.services import send_templated_email
from apps.journal.models import Article
from apps.production import services as production
from apps.submissions.models import SubmissionStatus
from apps.submissions.services import find_reviewers
from apps.submissions.views import _save_metadata
from apps.submissions.workflow import TRANSITIONS

pytestmark = pytest.mark.django_db


def _metadata_form(jel_codes) -> SimpleNamespace:
    """A stand-in for a valid step-3 form."""
    return SimpleNamespace(
        cleaned_data={
            "title_en": "Customs services and cross-border tourism",
            "title_uz": "Bojxona xizmatlari va chegaralararo turizm",
            "title_ru": "Таможенные услуги и трансграничный туризм",
            "abstract_en": "English abstract.",
            "abstract_uz": "Oʻzbekcha annotatsiya.",
            "abstract_ru": "Русская аннотация.",
            "keywords_en": "tourism, customs",
            "keywords_uz": "turizm, bojxona",
            "keywords_ru": "туризм, таможня",
            "jel_codes": jel_codes,
            "references": "",
        }
    )


def test_wizard_keeps_the_uzbek_title_when_the_author_works_in_uzbek(submission, jel_codes) -> None:
    """Saving step 3 in the Uzbek interface must not write English over Uzbek."""
    with translation.override("uz"):
        _save_metadata(submission, _metadata_form(jel_codes[:1]))
    submission.refresh_from_db()
    assert submission.title_uz == "Bojxona xizmatlari va chegaralararo turizm"
    assert submission.abstract_uz == "Oʻzbekcha annotatsiya."
    assert submission.title_en == "Customs services and cross-border tourism"


def test_article_keeps_every_translation_whatever_the_editor_language(
    submission, author_user, site_settings, license_cc_by
) -> None:
    """Creating the article in the Uzbek interface keeps the Uzbek title and keywords."""
    submission.status = SubmissionStatus.ACCEPTED
    submission.save()
    with translation.override("uz"):
        article = production.create_article_from_submission(submission)
    article.refresh_from_db()
    assert article.title_uz == "Banklararo likvidlik"
    assert article.title_en == "Interbank Liquidity and Policy Rate Transmission"
    keyword = article.keywords.get(name_en="liquidity")
    assert keyword.name_uz == "likvidlik"


def test_production_page_cannot_publish_around_the_checks(
    submission, production_user, site_settings, license_cc_by
) -> None:
    """The bare publish transitions are neither offered nor accepted.

    They marked the manuscript published while its article stayed a draft
    with no DOI and no PDF.
    """
    submission.status = SubmissionStatus.READY_TO_PUBLISH
    submission.save()
    client = Client()
    client.force_login(production_user)

    page = client.get(f"/en/production/submission/{submission.pk}/")
    assert page.status_code == 200
    names = {t.name for t in page.context["transitions"]}
    assert "publish_online_first" not in names
    assert "publish" not in names

    client.post(
        f"/en/production/submission/{submission.pk}/advance/",
        {"transition": "publish_online_first"},
    )
    submission.refresh_from_db()
    assert submission.status == SubmissionStatus.READY_TO_PUBLISH


def test_reviewer_pool_is_not_emptied_by_jel_codes(submission, reviewers) -> None:
    """Reviewers without a matching JEL code are still offered, ranked lower."""
    found = find_reviewers(jel_codes=["F1", "Z3"], exclude_users=[submission.submitter_id])
    assert {row["user"] for row in found} == set(reviewers)


def test_workflow_labels_follow_the_active_language() -> None:
    """Transition labels are translated at display time, not at import."""
    with translation.override("uz"):
        assert str(TRANSITIONS["desk_reject"].label) != "Desk reject"


def test_email_text_part_keeps_links_and_entities() -> None:
    """Text-only mail clients still get the accept link, without HTML entities."""
    text = markdown_to_text(
        "Section: Public Finance, Taxation & Customs.\n\n"
        "[Accept the invitation](https://example.org/accept/?a=1&b=2)"
    )
    assert "Taxation & Customs" in text
    assert "Accept the invitation: https://example.org/accept/?a=1&b=2" in text
    assert "\n\n" in text


def test_email_context_is_resolved_in_the_recipient_language(site_settings) -> None:
    """Callable context values are evaluated in the recipient's language."""
    send_templated_email(
        "test_event",
        to=["someone@example.org"],
        context={"lang": translation.get_language},
        language="ru",
        fallback_subject="Language {lang}",
        fallback_body="Body {lang}",
    )
    assert mail.outbox[-1].subject == "Language ru"


def test_console_badge_shows_the_most_senior_role(eic_user, groups) -> None:
    """An editor-in-chief who also authored a paper is badged EIC, not author."""
    eic_user.groups.add(groups[Role.AUTHOR])
    with translation.override("en"):
        assert eic_user.role_labels[0] == "Editor-in-Chief"


def test_signup_keeps_the_interface_language(site_settings) -> None:
    """A new author signing up on /uz/ lands on the Uzbek dashboard."""
    cache.clear()  # allauth's sign-up rate limit is kept in the cache
    client = Client()
    response = client.post(
        "/uz/accounts/signup/",
        {
            "email": "new.author@example.org",
            "password1": "Algorithm2026!x",
            "password2": "Algorithm2026!x",
        },
    )
    assert response.status_code == 302
    assert response["Location"].startswith("/uz/")


def test_apa_citation_is_spaced(article, site_settings) -> None:
    """The APA fallback separates year, title and journal."""
    text = render_citation(article, "apa")
    assert f"). {article.title_en}. " in text


def test_gost_and_vancouver_author_lists_are_clean(article, site_settings) -> None:
    """No "M.." double stops and no " , " separators."""
    for style in ("gost", "vancouver", "mla", "chicago"):
        text = render_citation(article, style)
        assert ".." not in text.replace("...", "")
        assert " , " not in text


def test_doi_suffix_uses_the_journal_short_code(article, site_settings) -> None:
    """The DOI suffix follows the journal's short code, not a hard-coded name."""
    article.doi = ""
    article.save()
    doi = production.reserve_doi(article)
    assert f"/{site_settings.short_code.lower()}." in doi
    assert Article.objects.get(pk=article.pk).doi == doi


# --- 2026-09-26: Railway-style run (no Redis) through the real UI -------------


def test_keywords_accept_semicolons_and_new_lines() -> None:
    """Authors paste keyword lines separated by semicolons; count them correctly."""
    from apps.submissions.services import normalise_keywords

    assert normalise_keywords("digital payments; saving;  financial   inclusion") == [
        "digital payments",
        "saving",
        "financial inclusion",
    ]
    assert normalise_keywords("a, b\nc;") == ["a", "b", "c"]


def test_first_author_row_is_prefilled_from_the_account(author_user, section) -> None:
    """Step 3 of a fresh submission starts with the submitter as first author."""
    from apps.submissions.models import Submission

    author_user.first_name, author_user.last_name = "Bekzod", "Toshmatov"
    author_user.save()
    draft = Submission.objects.create(submitter=author_user, section=section, wizard_step=3)
    client = Client()
    client.force_login(author_user)
    html = client.get(f"/en/submit/{draft.pk}/step-3/").content.decode()
    assert 'name="authors-0-given_name" value="Bekzod"' in html
    assert 'name="authors-0-family_name" value="Toshmatov"' in html
