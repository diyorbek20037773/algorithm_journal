"""Uzbek (Latin) and Russian translations — part 6: the editorial dashboard.

Strings introduced when the dashboard was rebuilt around elapsed time rather
than bare counts.  As in the earlier parts, each entry maps an English
``msgid`` to ``(uzbek_latin, russian)``; the Uzbek Cyrillic catalogue is
generated from the Uzbek Latin values by ``apps.core.translit`` (SPEC §10).
"""

from __future__ import annotations

PART_6: dict[str, tuple[str, str]] = {
    # --- attention list ----------------------------------------------------
    "Needs attention": ("Eʼtibor talab qiladi", "Требует внимания"),
    "%(counter)s item": ("%(counter)s ta element", "%(counter)s элемент"),
    "%(counter)s items": ("%(counter)s ta element", "%(counter)s элементов"),
    "Nothing is overdue. Every manuscript is inside its target.": (
        "Muddati oʻtgan ish yoʻq. Har bir qoʻlyozma belgilangan muddat ichida.",
        "Просроченных работ нет. Каждая рукопись укладывается в срок.",
    ),
    "Review overdue": ("Taqriz muddati oʻtdi", "Рецензия просрочена"),
    "Send reminder": ("Eslatma yuborish", "Отправить напоминание"),
    "Invitation unanswered": ("Taklifga javob yoʻq", "На приглашение нет ответа"),
    "Find another reviewer": ("Boshqa taqrizchi topish", "Найти другого рецензента"),
    "Awaiting your decision": ("Sizning qaroringiz kutilmoqda", "Ожидает вашего решения"),
    "Not yet screened": ("Hali koʻrikdan oʻtmagan", "Ещё не прошла первичную проверку"),
    "No activity": ("Harakat yoʻq", "Нет активности"),
    # --- queues and turnaround --------------------------------------------
    "oldest waiting %(days)s days": (
        "eng eskisi %(days)s kundan beri kutmoqda",
        "самая старая ждёт %(days)s дней",
    ),
    "empty": ("boʻsh", "пусто"),
    "Turnaround": ("Koʻrib chiqish muddati", "Сроки обработки"),
    "target ≤ %(days)s days": ("maqsad ≤ %(days)s kun", "цель ≤ %(days)s дней"),
    "share of decided manuscripts accepted": (
        "qaror qabul qilingan qoʻlyozmalardan qabul qilinganlari ulushi",
        "доля принятых среди рукописей с решением",
    ),
    "Your manuscripts need you": (
        "Qoʻlyozmalaringiz sizni kutmoqda",
        "Ваши рукописи ждут вас",
    ),
    # --- indexing page -----------------------------------------------------
    "We do not display impact-factor style badges from unverified providers.": (
        "Biz tasdiqlanmagan provayderlarning taʼsir omili koʻrinishidagi belgilarini koʻrsatmaymiz.",
        "Мы не размещаем значки импакт-фактора от непроверенных поставщиков.",
    ),
}
