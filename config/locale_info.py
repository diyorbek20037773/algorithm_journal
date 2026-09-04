"""Register the ``uz-cyrl`` locale with Django.

Django ships no metadata for Uzbek written in the Cyrillic script, so
``django.conf.locale.LANG_INFO`` is extended here before the settings module
builds ``LANGUAGES``.  Importing this module is idempotent.
"""

from __future__ import annotations

from django.conf import locale as django_locale


def register_uz_cyrl() -> None:
    """Add ``uz-cyrl`` / ``uz_Cyrl`` entries to Django's ``LANG_INFO`` table."""
    lang_info = django_locale.LANG_INFO
    lang_info.setdefault(
        "uz-cyrl",
        {
            "bidi": False,
            "code": "uz-cyrl",
            "name": "Uzbek (Cyrillic)",
            "name_local": "Ўзбекча",
        },
    )
    # Django normalises locale directory names to ``uz_Cyrl``; make both known.
    lang_info.setdefault(
        "uz_Cyrl",
        {
            "bidi": False,
            "code": "uz-cyrl",
            "name": "Uzbek (Cyrillic)",
            "name_local": "Ўзбекча",
        },
    )


register_uz_cyrl()
