"""Four-language coverage of the public site (SPEC §15.2, §15.3)."""

from __future__ import annotations

import pytest
from django.utils import translation

pytestmark = pytest.mark.django_db

LANGUAGES = ["en", "uz", "uz-cyrl", "ru"]

#: The 22 mandatory pages from the client's terms of reference (SPEC §15.3).
MANDATORY_PATHS = [
    "/{lang}/",
    "/{lang}/about/",
    "/{lang}/about/aims-and-scope/",
    "/{lang}/about/editorial-board/",
    "/{lang}/about/reviewer-board/",
    "/{lang}/about/peer-review/",
    "/{lang}/about/publication-ethics/",
    "/{lang}/about/ai-policy/",
    "/{lang}/for-authors/guidelines/",
    "/{lang}/for-authors/checklist/",
    "/{lang}/submit/",
    "/{lang}/for-reviewers/",
    "/{lang}/about/open-access/",
    "/{lang}/about/fees/",
    "/{lang}/about/archiving/",
    "/{lang}/about/indexing/",
    "/{lang}/issues/",
    "/{lang}/issues/online-first/",
    "/{lang}/search/",
    "/{lang}/statistics/",
    "/{lang}/announcements/",
    "/{lang}/about/contact/",
    "/{lang}/about/privacy/",
]


@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize("path", MANDATORY_PATHS)
def test_every_mandatory_page_responds(
    client_anon, about_pages, article, site_settings, language, path
) -> None:
    """All 22 mandatory pages respond in all four languages."""
    response = client_anon.get(path.format(lang=language))
    assert response.status_code in (200, 302), path.format(lang=language)


@pytest.mark.parametrize("language", LANGUAGES)
def test_pages_are_not_empty(client_anon, about_pages, article, site_settings, language) -> None:
    """Every mandatory page carries substantive content, not just chrome."""
    for path in MANDATORY_PATHS:
        url = path.format(lang=language)
        response = client_anon.get(url)
        if response.status_code != 200:
            continue
        body = response.content.decode()
        assert len(body) > 3000, f"{url} looks empty ({len(body)} bytes)"


def test_root_redirects_to_a_language(client_anon, about_pages, site_settings) -> None:
    """The unprefixed root redirects into a language prefix."""
    response = client_anon.get("/")
    assert response.status_code == 302
    assert any(response.headers["Location"].startswith(f"/{lang}/") for lang in LANGUAGES)


def test_language_prefixes_are_the_only_switch(client_anon, about_pages, site_settings) -> None:
    """Query-string language switching is not used (SPEC §8 forbids it)."""
    html = client_anon.get("/en/").content.decode()
    assert "?lang=" not in html


def test_uz_cyrl_locale_is_registered() -> None:
    """Django knows the uz-cyrl locale (SPEC §10)."""
    from django.conf.locale import LANG_INFO

    assert "uz-cyrl" in LANG_INFO
    assert LANG_INFO["uz-cyrl"]["name_local"] == "Ўзбекча"
    assert LANG_INFO["uz-cyrl"]["bidi"] is False


def test_settings_list_four_languages(settings) -> None:
    """LANGUAGES contains exactly the four configured locales."""
    codes = [code for code, _name in settings.LANGUAGES]
    assert codes == ["en", "uz", "uz-cyrl", "ru"]


def test_modeltranslation_uses_the_same_codes(settings) -> None:
    """modeltranslation is configured with the hyphenated codes."""
    assert settings.MODELTRANSLATION_LANGUAGES == ("en", "uz", "uz-cyrl", "ru")


def test_translated_content_differs_between_languages(
    client_anon, article, about_pages, site_settings
) -> None:
    """The article page shows the Russian title when Russian is requested."""
    russian = client_anon.get(f"/ru/article/{article.pk}/").content.decode()
    assert article.title_ru in russian


def test_language_switcher_is_present_on_every_page(
    client_anon, about_pages, site_settings
) -> None:
    """All four languages are offered in the switcher."""
    html = client_anon.get("/en/about/").content.decode()
    for language in LANGUAGES:
        assert f'hreflang="{language}"' in html


def test_module_level_lists_are_translated_per_request(
    client_anon, about_pages, site_settings
) -> None:
    """Constants built at import time must still translate for the reader.

    The pre-submission checklist and the production completeness labels are
    module-level lists. Built with eager ``gettext`` they are evaluated once,
    at import, when no request language is active — every reader then gets
    English no matter which locale they asked for, and no page-level test that
    only counts HTTP 200 will notice.
    """
    from apps.core.views_pages import CHECKLIST_ITEMS
    from apps.production.services import REQUIRED_METADATA

    response = client_anon.get("/ru/for-authors/checklist/")
    assert response.status_code == 200
    russian = response.content.decode()
    assert "Рукопись оригинальна" in russian
    assert "The manuscript is original" not in russian

    with translation.override("ru"):
        assert str(CHECKLIST_ITEMS[0]).startswith("Рукопись")
        assert str(dict(REQUIRED_METADATA)["title_en"]) == "Название (английский)"
    with translation.override("uz"):
        assert str(dict(REQUIRED_METADATA)["title_en"]) == "Sarlavha (inglizcha)"


def test_month_names_are_cyrillic_on_cyrillic_pages(client_anon, article, site_settings) -> None:
    """A date on a Cyrillic page must not borrow the Latin Uzbek month name.

    Django ships a catalogue for ``uz`` but none for ``uz_Cyrl``, so without
    the msgids re-declared in ``apps/core/dates.py`` the ``F`` date format
    falls through to Latin and renders "Mart 2026" in the middle of an
    otherwise Cyrillic page.
    """
    from django.utils import dateformat

    published = article.display_date
    with translation.override("uz-cyrl"):
        rendered = dateformat.format(published, "F Y")
    assert rendered.split()[0].isalpha()
    assert not rendered.isascii(), f"month name is still Latin: {rendered}"

    with translation.override("uz"):
        latin = dateformat.format(published, "F Y")
    assert latin.isascii()
