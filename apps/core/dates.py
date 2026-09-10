"""Month names, re-declared so this project translates them itself.

Django ships translation catalogues for ``uz`` but not for ``uz_Cyrl``. A
Cyrillic page therefore falls back to the Latin Uzbek month names, and
``{{ issue.published_at|date:"F Y" }}`` renders "Mart 2026" in the middle of a
page that is otherwise entirely Cyrillic.

Django resolves the ``django`` message domain from ``LOCALE_PATHS`` before its
own bundled catalogues, so a msgid translated here wins. ``makemessages`` only
extracts strings it can see in this project's source, which is what this module
is for: nothing imports the names, and nothing should. The strings must stay
byte-identical to ``django.utils.dates``.

``tests/test_i18n.py`` asserts the rendered result, so a Django upgrade that
respells one of these fails the build rather than silently reverting the page
to Latin.
"""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

#: ``MONTHS`` in django.utils.dates — the ``F`` date format.
MONTH_NAMES = (
    _("January"),
    _("February"),
    _("March"),
    _("April"),
    _("May"),
    _("June"),
    _("July"),
    _("August"),
    _("September"),
    _("October"),
    _("November"),
    _("December"),
)

#: ``MONTHS_3`` in django.utils.dates — the ``M`` date format, capitalised by
#: the formatter, so the msgids really are lower case.
MONTH_ABBREVIATIONS = (
    _("jan"),
    _("feb"),
    _("mar"),
    _("apr"),
    _("may"),
    _("jun"),
    _("jul"),
    _("aug"),
    _("sep"),
    _("oct"),
    _("nov"),
    _("dec"),
)
