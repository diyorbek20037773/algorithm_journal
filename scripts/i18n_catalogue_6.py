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
    "showing %(shown)s of %(total)s": (
        "%(total)s tadan %(shown)s tasi koʻrsatilmoqda",
        "показано %(shown)s из %(total)s",
    ),
    "Turnaround": ("Koʻrib chiqish muddati", "Сроки обработки"),
    # --- editorial reports (TZ §6.5) ---------------------------------------
    "Submissions received": ("Qabul qilingan qoʻlyozmalar", "Поступило рукописей"),
    "last 12 months": ("soʻnggi 12 oy", "за последние 12 месяцев"),
    "Rejection rate": ("Rad etish darajasi", "Доля отклонённых"),
    "%(rate)s%% desk rejected": (
        "%(rate)s%% dastlabki bosqichda rad etilgan",
        "%(rate)s%% отклонено на первичном этапе",
    ),
    "Median days a reviewer takes": (
        "Taqrizchining median muddati (kun)",
        "Медианный срок рецензента (дней)",
    ),
    "from accepting the invitation to filing": (
        "taklifni qabul qilishdan taqrizni topshirishgacha",
        "от принятия приглашения до сдачи рецензии",
    ),
    "Where the authors are": ("Mualliflar geografiyasi", "География авторов"),
    "submitting authors, last 12 months": (
        "qoʻlyozma yuborgan mualliflar, soʻnggi 12 oy",
        "авторы поданных рукописей, за последние 12 месяцев",
    ),
    "Country": ("Mamlakat", "Страна"),
    "Authors": ("Mualliflar", "Авторы"),
    # --- article full text (TZ §6.1) ---------------------------------------
    "Full text": ("Toʻliq matn", "Полный текст"),
    "Full text (HTML)": ("Toʻliq matn (HTML)", "Полный текст (HTML)"),
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
    # --- month names (see apps/core/dates.py) ------------------------------
    "January": ("Yanvar", "Январь"),
    "February": ("Fevral", "Февраль"),
    "March": ("Mart", "Март"),
    "April": ("Aprel", "Апрель"),
    "May": ("May", "Май"),
    "June": ("Iyun", "Июнь"),
    "July": ("Iyul", "Июль"),
    "August": ("Avgust", "Август"),
    "September": ("Sentabr", "Сентябрь"),
    "October": ("Oktabr", "Октябрь"),
    "November": ("Noyabr", "Ноябрь"),
    "December": ("Dekabr", "Декабрь"),
    "jan": ("yan", "янв"),
    "feb": ("fev", "фев"),
    "mar": ("mar", "мар"),
    "apr": ("apr", "апр"),
    "may": ("may", "май"),
    "jun": ("iyn", "июн"),
    "jul": ("iyl", "июл"),
    "aug": ("avg", "авг"),
    "sep": ("sen", "сен"),
    "oct": ("okt", "окт"),
    "nov": ("noy", "ноя"),
    "dec": ("dek", "дек"),
}
