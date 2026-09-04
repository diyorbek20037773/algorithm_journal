"""Unit tests for the Uzbek Latin ↔ Cyrillic transliterator (SPEC §10)."""

from __future__ import annotations

import pytest

from apps.core.translit import to_cyrillic, to_latin

# (latin, expected cyrillic)
LATIN_TO_CYRILLIC = [
    ("salom", "салом"),
    ("Salom", "Салом"),
    ("SALOM", "САЛОМ"),
    ("iqtisodiyot", "иқтисодиёт"),
    ("iqtisodiy", "иқтисодий"),
    ("tadqiqot", "тадқиқот"),
    ("tadqiqotlar", "тадқиқотлар"),
    ("sharh", "шарҳ"),
    ("sharhi", "шарҳи"),
    ("kitob", "китоб"),
    ("maqola", "мақола"),
    ("jurnal", "журнал"),
    ("bank", "банк"),
    ("moliya", "молия"),
    ("hisob", "ҳисоб"),
    ("xalqaro", "халқаро"),
    ("yangi", "янги"),
    ("yozuv", "ёзув"),
    ("yulduz", "юлдуз"),
    ("yaxshi", "яхши"),
    ("chiqish", "чиқиш"),
    ("shahar", "шаҳар"),
    ("oʻzbek", "ўзбек"),
    ("o‘zbek", "ўзбек"),
    ("o'zbek", "ўзбек"),
    ("gʻalaba", "ғалаба"),
    ("g‘alaba", "ғалаба"),
    ("Oʻzbekiston", "Ўзбекистон"),
    ("bogʻ", "боғ"),
    ("elektron", "электрон"),
    ("ekspertiza", "экспертиза"),
    ("ekonometrika", "эконометрика"),
    ("yer", "ер"),
    ("kun", "кун"),
    ("nashr", "нашр"),
    ("son", "сон"),
    ("jild", "жилд"),
    ("muallif", "муаллиф"),
    ("taqriz", "тақриз"),
    ("tahririyat", "таҳририят"),
    ("ochiq", "очиқ"),
    ("kirish", "кириш"),
    ("mualliflik", "муаллифлик"),
    ("huquq", "ҳуқуқ"),
]


@pytest.mark.parametrize(("latin", "cyrillic"), LATIN_TO_CYRILLIC)
def test_to_cyrillic(latin: str, cyrillic: str) -> None:
    """Every documented case transliterates as specified."""
    assert to_cyrillic(latin) == cyrillic


def test_apostrophe_variants_are_equivalent() -> None:
    """Every apostrophe variant produces the same Cyrillic output."""
    variants = ["oʻ", "o'", "o‘", "o’", "o`"]
    results = {to_cyrillic(v) for v in variants}
    assert results == {"ў"}


def test_word_initial_e_becomes_ae() -> None:
    """Word-initial ``e`` becomes ``э``; elsewhere it stays ``е``."""
    assert to_cyrillic("eksport") == "экспорт"
    assert to_cyrillic("kredit") == "кредит"


def test_punctuation_and_digits_pass_through() -> None:
    """Non-letters are preserved exactly."""
    assert to_cyrillic("2026-yil, 5-son.") == "2026-йил, 5-сон."


def test_empty_and_none() -> None:
    """Empty input returns an empty string."""
    assert to_cyrillic("") == ""
    assert to_cyrillic(None) == ""
    assert to_latin(None) == ""


def test_round_trip_keeps_meaning() -> None:
    """Cyrillic → Latin → Cyrillic is stable for common words."""
    for _latin, cyrillic in LATIN_TO_CYRILLIC[:20]:
        assert to_cyrillic(to_latin(cyrillic)) == cyrillic


def test_to_latin_basic() -> None:
    """Reverse transliteration handles the digraphs."""
    assert to_latin("шарҳ") == "sharh"
    assert to_latin("ўзбек") == "oʻzbek"
    assert to_latin("ғалаба") == "gʻalaba"
    assert to_latin("иқтисодиёт") == "iqtisodiyot"


def test_sentence() -> None:
    """A whole sentence transliterates cleanly."""
    latin = "Iqtisodiy tadqiqotlar sharhi — ochiq kirishli ilmiy jurnal"
    assert to_cyrillic(latin) == "Иқтисодий тадқиқотлар шарҳи — очиқ киришли илмий журнал"
