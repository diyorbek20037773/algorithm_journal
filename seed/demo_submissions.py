"""Create demonstration submissions in every workflow state (SPEC §13).

The dashboards only look alive when each queue has something in it, so this
module builds: 2 drafts, 3 submitted, 2 in screening (one with a similarity
report), 4 under review with assignments in every status including overdue,
2 awaiting decision, 2 revision requested, 1 resubmitted, 2 accepted and in
production, 3 rejected and 1 withdrawn.
"""

from __future__ import annotations

import datetime as dt
import random
from typing import Any

from django.core.files.base import ContentFile
from django.utils import timezone

from apps.accounts.models import User
from apps.core.translit import to_cyrillic
from apps.journal.models import JELCode, Section
from apps.submissions.models import (
    Discussion,
    DiscussionMessage,
    EditorialDecision,
    ProductionTask,
    Review,
    ReviewAssignment,
    ReviewRound,
    RevisionRequest,
    Submission,
    SubmissionAuthor,
    SubmissionFile,
    SubmissionStatus,
)

RNG = random.Random(4771)

#: (English title, Uzbek title, Russian title, section slug, JEL codes)
TOPICS: list[tuple[str, str, str, str, list[str]]] = [
    (
        "Inflation Expectations and Central Bank Communication in an Emerging Economy",
        "Rivojlanayotgan iqtisodiyotda inflyatsiya kutilmalari va markaziy bank kommunikatsiyasi",
        "Инфляционные ожидания и коммуникация центрального банка в развивающейся экономике",
        "macroeconomics-monetary-fiscal-policy",
        ["E31", "E52", "E58"],
    ),
    (
        "Property Tax Reform and Municipal Revenue Capacity",
        "Mulk soligʻi islohoti va munitsipal daromad salohiyati",
        "Реформа налога на имущество и доходный потенциал муниципалитетов",
        "public-finance-taxation-customs",
        ["H71", "H77", "R31"],
    ),
    (
        "Export Credit Guarantees and the Entry of New Exporters",
        "Eksport kredit kafolatlari va yangi eksportchilarning bozorga kirishi",
        "Экспортные кредитные гарантии и выход новых экспортёров",
        "international-trade-integration",
        ["F14", "G28", "L26"],
    ),
    (
        "Energy Subsidy Reform and Household Welfare: A Microsimulation",
        "Energiya subsidiyalari islohoti va uy xoʻjaliklari farovonligi: mikrosimulyatsiya",
        "Реформа энергетических субсидий и благосостояние домохозяйств: микросимуляция",
        "regional-sectoral-development",
        ["Q48", "H23", "I32"],
    ),
    (
        "Vocational Training and Youth Employment: Evidence from a Randomised Programme",
        "Kasbiy taʼlim va yoshlar bandligi: tasodifiy dastur natijalari",
        "Профессиональное обучение и занятость молодёжи: данные рандомизированной программы",
        "management-entrepreneurship-labour",
        ["J24", "J64", "I25"],
    ),
    (
        "Interbank Liquidity and the Transmission of Policy Rates",
        "Banklararo likvidlik va siyosat stavkalarining uzatilishi",
        "Межбанковская ликвидность и трансмиссия ключевой ставки",
        "finance-banking-investment",
        ["G21", "E43", "E52"],
    ),
    (
        "Open Data Portals and Public Procurement Competition",
        "Ochiq maʼlumot portallari va davlat xaridlaridagi raqobat",
        "Порталы открытых данных и конкуренция в государственных закупках",
        "digital-economy-innovation",
        ["H57" , "D73", "O38"],
    ),
    (
        "Measuring Total Factor Productivity with Imperfect Deflators",
        "Nomukammal deflyatorlar bilan umumiy omil unumdorligini oʻlchash",
        "Измерение совокупной факторной производительности при несовершенных дефляторах",
        "economic-theory-methodology",
        ["C43", "D24", "O47"],
    ),
    (
        "Cross-Border E-Commerce and Small Exporter Participation",
        "Chegaralararo elektron tijorat va kichik eksportchilar ishtiroki",
        "Трансграничная электронная коммерция и участие малых экспортёров",
        "digital-economy-innovation",
        ["F14", "L81", "L26"],
    ),
    (
        "Pension Reform and Household Saving Behaviour",
        "Pensiya islohoti va uy xoʻjaliklarining jamgʻarish xulqi",
        "Пенсионная реформа и сберегательное поведение домохозяйств",
        "macroeconomics-monetary-fiscal-policy",
        ["H55", "D14", "E21"],
    ),
    (
        "Agricultural Cooperatives and Smallholder Market Access",
        "Qishloq xoʻjaligi kooperativlari va kichik fermerlarning bozorga chiqishi",
        "Сельскохозяйственные кооперативы и доступ мелких хозяйств к рынкам",
        "regional-sectoral-development",
        ["Q13", "Q12", "O13"],
    ),
    (
        "Firm Informality and the Cost of Formalisation",
        "Korxona norasmiyligi va rasmiylashtirish xarajati",
        "Неформальность фирм и издержки формализации",
        "management-entrepreneurship-labour",
        ["O17", "H26", "L26"],
    ),
    (
        "Public Debt Composition and Rollover Risk",
        "Davlat qarzi tarkibi va qayta moliyalashtirish xavfi",
        "Структура государственного долга и риск рефинансирования",
        "macroeconomics-monetary-fiscal-policy",
        ["H63", "F34", "E62"],
    ),
    (
        "Digital Skills and the Wage Premium in Services",
        "Raqamli koʻnikmalar va xizmatlar sohasidagi ish haqi ustamasi",
        "Цифровые навыки и премия к заработной плате в услугах",
        "management-entrepreneurship-labour",
        ["J31", "J24", "O33"],
    ),
    (
        "Bank Branch Closures and Local Credit Supply",
        "Bank filiallarining yopilishi va mahalliy kredit taklifi",
        "Закрытие банковских отделений и локальное предложение кредита",
        "finance-banking-investment",
        ["G21", "R11", "L26"],
    ),
    (
        "Trade Credit and Firm Liquidity during a Currency Shock",
        "Valyuta zarbasi davrida savdo krediti va korxona likvidligi",
        "Торговый кредит и ликвидность фирм во время валютного шока",
        "finance-banking-investment",
        ["G32", "F31", "L25"],
    ),
    (
        "Carbon Pricing and Industrial Competitiveness in a Small Open Economy",
        "Kichik ochiq iqtisodiyotda uglerod narxi va sanoat raqobatbardoshligi",
        "Углеродное ценообразование и промышленная конкурентоспособность в малой открытой экономике",
        "regional-sectoral-development",
        ["Q54", "Q48", "L52"],
    ),
    (
        "The Fiscal Cost of Tax Expenditures: A Systematic Assessment",
        "Soliq imtiyozlarining fiskal narxi: tizimli baholash",
        "Фискальная цена налоговых расходов: систематическая оценка",
        "public-finance-taxation-customs",
        ["H25", "H30", "H62"],
    ),
    (
        "Remittance Flows and Real Exchange Rate Appreciation",
        "Pul oʻtkazmalari oqimi va real valyuta kursining qadrlanishi",
        "Потоки денежных переводов и укрепление реального валютного курса",
        "international-trade-integration",
        ["F24", "F31", "O24"],
    ),
    (
        "Innovation Vouchers for Small Firms: Take-Up and Effects",
        "Kichik korxonalar uchun innovatsiya vaucherlari: qamrov va taʼsir",
        "Инновационные ваучеры для малых фирм: охват и эффекты",
        "digital-economy-innovation",
        ["O31", "O38", "L26"],
    ),
    (
        "Regional Price Indices and the Measurement of Real Incomes",
        "Hududiy narx indekslari va real daromadlarni oʻlchash",
        "Региональные индексы цен и измерение реальных доходов",
        "economic-theory-methodology",
        ["C43", "D31", "R11"],
    ),
    (
        "Book review: Institutions, Trade and Development in Central Asia",
        "Kitob taqrizi: Markaziy Osiyoda institutlar, savdo va rivojlanish",
        "Рецензия: институты, торговля и развитие в Центральной Азии",
        "reviews-commentary",
        ["Y30", "O53", "F15"],
    ),
]

ABSTRACT_TEMPLATE = {
    "en": (
        "This paper examines {topic_lower} using administrative and survey data covering "
        "{n} observations between 2015 and 2024. We combine a difference-in-differences "
        "design with an instrumental variable strategy to address the endogeneity of "
        "policy exposure, and we test the robustness of the estimates to alternative "
        "control groups, to functional form and to the treatment of outliers. The "
        "estimated effects are economically meaningful and statistically distinguishable "
        "from zero at conventional levels, and they are concentrated among smaller units "
        "and in regions with weaker initial institutional capacity. We also document "
        "substantial heterogeneity that averages conceal, and we show that ignoring it "
        "leads to policy conclusions that do not hold for the groups the policy is "
        "intended to help. The paper contributes to the literature by bringing "
        "disaggregated evidence to a question that has so far been studied mainly with "
        "aggregate data, and by making the identification assumptions explicit and "
        "testable. We conclude with the implications for the design of the policy "
        "instrument and with a discussion of what further data would resolve the "
        "remaining uncertainty."
    ),
    "uz": (
        "Ushbu maqolada {topic_lower} masalasi 2015–2024-yillar oraligʻidagi {n} ta "
        "kuzatuvni qamrab olgan maʼmuriy va soʻrov maʼlumotlari asosida oʻrganiladi. "
        "Siyosat taʼsirining endogenligini bartaraf etish uchun farqlar-farqi dizayni "
        "instrumental oʻzgaruvchi strategiyasi bilan birlashtiriladi hamda baholarning "
        "muqobil nazorat guruhlariga, funksional shaklga va chetlangan qiymatlarga "
        "chidamliligi tekshiriladi. Baholangan taʼsirlar iqtisodiy jihatdan sezilarli va "
        "odatdagi darajalarda statistik ahamiyatli boʻlib, kichikroq birliklarda hamda "
        "boshlangʻich institutsional salohiyati zaif hududlarda toʻplangan. Shuningdek, "
        "oʻrtacha koʻrsatkichlar yashiradigan sezilarli heterogenlik hujjatlashtiriladi va "
        "uni eʼtiborsiz qoldirish siyosat yordam berishi kerak boʻlgan guruhlar uchun "
        "amal qilmaydigan xulosalarga olib kelishi koʻrsatiladi. Maqola shu paytgacha "
        "asosan agregat maʼlumotlar bilan oʻrganilgan savolga detallashtirilgan dalil "
        "keltirish va identifikatsiya farazlarini aniq hamda tekshiriladigan qilish orqali "
        "adabiyotga hissa qoʻshadi."
    ),
    "ru": (
        "В статье исследуется {topic_lower} на административных и обследовательских данных, "
        "охватывающих {n} наблюдений за 2015–2024 годы. Мы сочетаем дизайн «разность "
        "разностей» со стратегией инструментальных переменных, чтобы учесть эндогенность "
        "подверженности политике, и проверяем устойчивость оценок к альтернативным "
        "контрольным группам, функциональной форме и обработке выбросов. Оценённые эффекты "
        "экономически значимы и статистически отличимы от нуля на общепринятых уровнях, "
        "причём они сосредоточены среди меньших единиц и в регионах со слабым исходным "
        "институциональным потенциалом. Мы также документируем существенную "
        "неоднородность, которую скрывают средние значения, и показываем, что её "
        "игнорирование ведёт к выводам, не выполняющимся для групп, которым политика "
        "призвана помочь. Статья вносит вклад в литературу, привнося дезагрегированные "
        "данные в вопрос, изучавшийся до сих пор преимущественно на агрегированных данных, "
        "и делая предпосылки идентификации явными и проверяемыми."
    ),
}

AUTHOR_POOL = [
    ("Dilnoza", "Yusupova", "Institute of Forecasting and Macroeconomic Research", "Tashkent", "UZ"),
    ("Sardor", "Rakhmonov", "Tashkent University of Information Technologies", "Tashkent", "UZ"),
    ("Aidos", "Nurgaliyev", "Graduate School of Economics", "Almaty", "KZ"),
    ("Marta", "Kowalska", "Warsaw School of Economics", "Warsaw", "PL"),
    ("Sergey", "Volkov", "Institute of Economics and Industrial Engineering", "Novosibirsk", "RU"),
    ("Gulnora", "Nazarova", "National University", "Tashkent", "UZ"),
    ("Farrukh", "Ergashev", "University of Economics and Finance", "Samarkand", "UZ"),
    ("Nilufar", "Sattorova", "Centre for Regional Studies", "Bukhara", "UZ"),
    ("Ali", "Rahmani", "University of Tehran", "Tehran", "IR"),
    ("Anna", "Fischer", "University of Vienna", "Vienna", "AT"),
]

MANUSCRIPT_TEXT = (
    "%PDF-1.4 demonstration manuscript placeholder. In a real submission this file is the "
    "anonymised manuscript uploaded by the author."
)


def _make_file(submission: Submission, kind: str, uploader: User, version: int = 1) -> SubmissionFile:
    """Attach a small placeholder file to a submission."""
    record = SubmissionFile(
        submission=submission,
        kind=kind,
        uploaded_by=uploader,
        version=version,
        mime="application/pdf",
    )
    payload = f"{MANUSCRIPT_TEXT}\nkind={kind} submission={submission.pk} v={version}".encode()
    record.file.save(f"{kind}-{submission.pk}-v{version}.pdf", ContentFile(payload), save=False)
    record.size = len(payload)
    record.save()
    return record


def _create_submission(
    *,
    topic_index: int,
    submitter: User,
    status: str,
    days_ago: int,
    editor: User | None = None,
) -> Submission:
    """Create one submission with metadata, authors and files."""
    title_en, title_uz, title_ru, section_slug, jel = TOPICS[topic_index % len(TOPICS)]
    section = Section.objects.get(slug=section_slug)
    now = timezone.now()
    submitted_at = now - dt.timedelta(days=days_ago)
    observations = f"{RNG.randint(3, 96)},{RNG.randint(100, 999)}"

    submission = Submission(
        submitter=submitter,
        section=section,
        status=status,
        article_type=Submission.ArticleType.RESEARCH,
        language="en",
        word_count=RNG.randint(5200, 9600),
        assigned_editor=editor,
        submitted_at=None if status == SubmissionStatus.DRAFT else submitted_at,
        last_activity_at=now - dt.timedelta(days=max(0, days_ago - RNG.randint(0, 8))),
        wizard_step=5,
        anonymised_file_ok=True,
        cover_letter=(
            "Dear Editors,\n\nWe are pleased to submit our manuscript for consideration. "
            "The work is original, is not under consideration elsewhere, and all authors "
            "have approved this version.\n\nYours sincerely,\nThe authors"
        ),
        author_declarations={
            "original": True,
            "not_under_consideration": True,
            "guidelines": True,
            "anonymised": True,
            "ethics": True,
            "license": True,
        },
        suggested_reviewers=["Prof. A. Nazarov, a.nazarov@example.org, National University"],
        opposed_reviewers=[],
        ai_use_statement="No generative AI tools were used in the preparation of this article.",
        funding_statement="This research received no specific grant from any funding agency.",
        conflict_of_interest_statement="The authors declare no conflict of interest.",
        data_availability_statement="Data are available from the corresponding author on request.",
    )

    titles = {"en": title_en, "uz": title_uz, "ru": title_ru, "uz-cyrl": to_cyrillic(title_uz)}
    abstracts = {
        code: ABSTRACT_TEMPLATE[code].format(
            topic_lower=title_en[0].lower() + title_en[1:] if code == "en" else title_en,
            n=observations,
        )
        for code in ("en", "uz", "ru")
    }
    abstracts["uz-cyrl"] = to_cyrillic(abstracts["uz"])
    keywords = {
        "en": ["policy evaluation", "administrative data", "identification", "heterogeneity", "emerging economies"],
        "uz": ["siyosatni baholash", "maʼmuriy maʼlumotlar", "identifikatsiya", "heterogenlik", "rivojlanayotgan iqtisodiyotlar"],
        "ru": ["оценка политики", "административные данные", "идентификация", "неоднородность", "развивающиеся экономики"],
    }
    keywords["uz-cyrl"] = [to_cyrillic(k) for k in keywords["uz"]]

    submission.title_en = title_en
    submission.title_uz = title_uz
    submission.title_ru = title_ru
    submission.title_uz_cyrl = titles["uz-cyrl"]
    submission.title = title_en
    submission.abstract_en = abstracts["en"]
    submission.abstract_uz = abstracts["uz"]
    submission.abstract_ru = abstracts["ru"]
    submission.abstract_uz_cyrl = abstracts["uz-cyrl"]
    submission.abstract = abstracts["en"]
    submission.keywords_text = ", ".join(keywords["en"])
    submission.keywords_text_uz = ", ".join(keywords["uz"])
    submission.keywords_text_ru = ", ".join(keywords["ru"])
    submission.metadata = {
        "title": titles,
        "abstract": abstracts,
        "keywords": keywords,
        "references": [],
    }
    submission.save()

    submission.jel_codes.set(JELCode.objects.filter(code__in=jel))

    chosen = RNG.sample(AUTHOR_POOL, RNG.randint(2, 3))
    for order, (given, family, affiliation, city, country) in enumerate(chosen, start=1):
        SubmissionAuthor.objects.create(
            submission=submission,
            order=order,
            given_name=given,
            family_name=family,
            email=f"{family.lower()}@example.org",
            is_corresponding=order == 1,
            orcid=f"0000-0003-{RNG.randint(1000, 9999)}-{RNG.randint(1000, 9999)}",
            affiliation=affiliation,
            city=city,
            country=country,
            credit_roles=["Conceptualization", "Formal analysis"],
        )

    if status != SubmissionStatus.DRAFT:
        _make_file(submission, SubmissionFile.Kind.MANUSCRIPT_ANON, submitter)
        _make_file(submission, SubmissionFile.Kind.TITLE_PAGE, submitter)
    else:
        _make_file(submission, SubmissionFile.Kind.MANUSCRIPT_ANON, submitter)

    _system_note(submission, f"Submission created for demonstration in state “{status}”.")
    return submission


def _system_note(submission: Submission, body: str) -> None:
    """Append a system message to the editors-only thread."""
    discussion, _created = Discussion.objects.get_or_create(
        submission=submission,
        visibility=Discussion.Visibility.EDITORS_ONLY,
        defaults={"subject": "Workflow history"},
    )
    DiscussionMessage.objects.create(discussion=discussion, body=body, is_system=True)


def _add_round(submission: Submission, number: int = 1) -> ReviewRound:
    """Open a review round on a submission."""
    submission.current_round = max(submission.current_round, number)
    submission.save(update_fields=["current_round", "updated_at"])
    round_obj, _created = ReviewRound.objects.get_or_create(
        submission=submission, number=number, defaults={"opened_at": timezone.now()}
    )
    return round_obj


def _assign(
    round_obj: ReviewRound,
    reviewer: User,
    status: str,
    *,
    editor: User,
    due_in_days: int = 21,
    with_review: bool = False,
    recommendation: str = Review.Recommendation.MINOR,
) -> ReviewAssignment:
    """Create a review assignment, optionally with a completed review."""
    now = timezone.now()
    assignment = ReviewAssignment.objects.create(
        round=round_obj,
        reviewer=reviewer,
        invited_by=editor,
        invited_at=now - dt.timedelta(days=max(1, 30 - due_in_days)),
        due_at=now + dt.timedelta(days=due_in_days),
        status=status,
        response=(
            ReviewAssignment.Response.ACCEPTED
            if status in {ReviewAssignment.Status.ACCEPTED, ReviewAssignment.Status.SUBMITTED, ReviewAssignment.Status.OVERDUE}
            else ReviewAssignment.Response.DECLINED
            if status == ReviewAssignment.Status.DECLINED
            else ReviewAssignment.Response.PENDING
        ),
        responded_at=now - dt.timedelta(days=20) if status != ReviewAssignment.Status.INVITED else None,
        completed_at=now - dt.timedelta(days=2) if status == ReviewAssignment.Status.SUBMITTED else None,
    )
    if with_review:
        Review.objects.create(
            assignment=assignment,
            recommendation=recommendation,
            scores={key: RNG.randint(3, 5) for key, _label in Review.SCORE_FIELDS},
            comments_to_authors=(
                "The paper addresses a question of clear policy relevance and the data are "
                "well suited to it. My main concern is the identification strategy in "
                "Section 3: the parallel-trends assumption is asserted rather than tested, "
                "and the pre-treatment period is short. Please add an event-study plot with "
                "at least four pre-periods and report the test of joint significance of the "
                "leads.\n\nSecond, the standard errors should be clustered at the level at "
                "which treatment varies; the current specification clusters at a finer "
                "level and almost certainly understates uncertainty.\n\nThird, the "
                "discussion overstates causality in two places (pp. 14 and 19). The "
                "language should track what the design can support.\n\nMinor points: "
                "Table 2 lacks units; three references are missing DOIs; the abstract "
                "exceeds the journal limit."
            ),
            comments_to_editor=(
                "A solid contribution once the identification concerns are addressed. "
                "I would be happy to look at a revised version."
            ),
            submitted_at=now - dt.timedelta(days=2),
            is_draft=False,
        )
    return assignment


def create_demo_submissions(stdout: Any, style: Any) -> int:
    """Create the full set of demonstration submissions and return the count."""
    if Submission.objects.exists():
        stdout.write("  submissions already present, skipping")
        return Submission.objects.count()

    author = User.objects.get(email="author@algorithm-journal.uz")
    eic = User.objects.get(email="eic@algorithm-journal.uz")
    editor = User.objects.get(email="editor@algorithm-journal.uz")
    production = User.objects.get(email="production@algorithm-journal.uz")
    reviewers = [
        User.objects.get(email="reviewer1@algorithm-journal.uz"),
        User.objects.get(email="reviewer2@algorithm-journal.uz"),
        User.objects.get(email="reviewer3@algorithm-journal.uz"),
    ]

    topic = 0
    created = 0

    def next_topic() -> int:
        nonlocal topic
        value = topic
        topic += 1
        return value

    # --- 2 drafts ----------------------------------------------------------
    for _ in range(2):
        _create_submission(
            topic_index=next_topic(), submitter=author, status=SubmissionStatus.DRAFT, days_ago=4
        )
        created += 1

    # --- 3 submitted -------------------------------------------------------
    for offset in range(3):
        _create_submission(
            topic_index=next_topic(),
            submitter=author,
            status=SubmissionStatus.SUBMITTED,
            days_ago=3 + offset,
        )
        created += 1

    # --- 2 screening (one with a similarity report) ------------------------
    for index in range(2):
        submission = _create_submission(
            topic_index=next_topic(),
            submitter=author,
            status=SubmissionStatus.SCREENING,
            days_ago=9 + index,
            editor=editor,
        )
        if index == 0:
            submission.similarity_percent = 12.4
            submission.similarity_checked_by = editor
            submission.similarity_checked_at = timezone.now() - dt.timedelta(days=1)
            submission.similarity_report.save(
                f"similarity-{submission.pk}.pdf",
                ContentFile(b"%PDF-1.4 demonstration similarity report"),
                save=False,
            )
            submission.save()
            _system_note(submission, "Similarity check recorded: 12.4 % (within the 20 % threshold).")
        created += 1

    # --- 4 under review, assignments in every status -----------------------
    review_states = [
        [ReviewAssignment.Status.INVITED, ReviewAssignment.Status.ACCEPTED],
        [ReviewAssignment.Status.ACCEPTED, ReviewAssignment.Status.DECLINED, ReviewAssignment.Status.INVITED],
        [ReviewAssignment.Status.OVERDUE, ReviewAssignment.Status.ACCEPTED],
        [ReviewAssignment.Status.SUBMITTED, ReviewAssignment.Status.ACCEPTED],
    ]
    for index, states in enumerate(review_states):
        submission = _create_submission(
            topic_index=next_topic(),
            submitter=author,
            status=SubmissionStatus.UNDER_REVIEW,
            days_ago=28 + index * 3,
            editor=editor,
        )
        submission.similarity_percent = round(RNG.uniform(5.0, 17.0), 1)
        submission.similarity_checked_by = editor
        submission.similarity_checked_at = timezone.now() - dt.timedelta(days=20)
        submission.save()
        round_obj = _add_round(submission)
        for position, state in enumerate(states):
            _assign(
                round_obj,
                reviewers[position % len(reviewers)],
                state,
                editor=editor,
                due_in_days=-3 if state == ReviewAssignment.Status.OVERDUE else 21 - index * 4,
                with_review=state == ReviewAssignment.Status.SUBMITTED,
            )
        created += 1

    # --- 2 awaiting decision ----------------------------------------------
    for index in range(2):
        submission = _create_submission(
            topic_index=next_topic(),
            submitter=author,
            status=SubmissionStatus.AWAITING_DECISION,
            days_ago=52 + index * 4,
            editor=editor,
        )
        submission.similarity_percent = 9.8
        submission.similarity_checked_by = editor
        submission.similarity_checked_at = timezone.now() - dt.timedelta(days=45)
        submission.save()
        round_obj = _add_round(submission)
        _assign(round_obj, reviewers[0], ReviewAssignment.Status.SUBMITTED, editor=editor, with_review=True,
                recommendation=Review.Recommendation.MINOR)
        _assign(round_obj, reviewers[1], ReviewAssignment.Status.SUBMITTED, editor=editor, with_review=True,
                recommendation=Review.Recommendation.MAJOR)
        _system_note(submission, "All reviews received; awaiting the editorial decision.")
        created += 1

    # --- 2 revision requested ---------------------------------------------
    for index, major in enumerate((False, True)):
        submission = _create_submission(
            topic_index=next_topic(),
            submitter=author,
            status=SubmissionStatus.REVISION_REQUESTED,
            days_ago=64 + index * 5,
            editor=editor,
        )
        submission.similarity_percent = 11.2
        submission.similarity_checked_by = editor
        submission.similarity_checked_at = timezone.now() - dt.timedelta(days=58)
        round_obj = _add_round(submission)
        _assign(round_obj, reviewers[0], ReviewAssignment.Status.SUBMITTED, editor=editor, with_review=True)
        _assign(round_obj, reviewers[2], ReviewAssignment.Status.SUBMITTED, editor=editor, with_review=True,
                recommendation=Review.Recommendation.MAJOR if major else Review.Recommendation.MINOR)
        decision = EditorialDecision.objects.create(
            submission=submission,
            round=round_obj,
            decided_by=eic,
            decision=(
                EditorialDecision.Decision.MAJOR_REVISION
                if major
                else EditorialDecision.Decision.MINOR_REVISION
            ),
            letter=(
                "Dear Author,\n\nTwo reviewers have now assessed your manuscript. Both find "
                "the question worthwhile, and both raise concerns about the identification "
                "strategy that must be addressed before the paper can be accepted. Please "
                "respond to each numbered point and supply a marked-up version alongside the "
                "clean one.\n\nYours sincerely,\nEditorial Office"
            ),
            decided_at=timezone.now() - dt.timedelta(days=6),
            emailed_at=timezone.now() - dt.timedelta(days=6),
        )
        RevisionRequest.objects.create(
            submission=submission,
            round=round_obj,
            decision=decision,
            is_major=major,
            due_at=timezone.now() + dt.timedelta(days=60 if major else 30),
        )
        submission.decision_letter = decision.letter
        submission.save()
        created += 1

    # --- 1 resubmitted -----------------------------------------------------
    submission = _create_submission(
        topic_index=next_topic(),
        submitter=author,
        status=SubmissionStatus.RESUBMITTED,
        days_ago=96,
        editor=editor,
    )
    submission.similarity_percent = 8.1
    submission.similarity_checked_by = editor
    submission.similarity_checked_at = timezone.now() - dt.timedelta(days=90)
    round_one = _add_round(submission, 1)
    _assign(round_one, reviewers[0], ReviewAssignment.Status.SUBMITTED, editor=editor, with_review=True)
    _assign(round_one, reviewers[1], ReviewAssignment.Status.SUBMITTED, editor=editor, with_review=True)
    round_one.status = ReviewRound.Status.CLOSED
    round_one.closed_at = timezone.now() - dt.timedelta(days=40)
    round_one.save()
    revision = RevisionRequest.objects.create(
        submission=submission,
        round=round_one,
        is_major=True,
        due_at=timezone.now() - dt.timedelta(days=2),
        submitted_at=timezone.now() - dt.timedelta(days=3),
        response_letter=(
            "We thank both reviewers for their careful reading. Below we respond to each "
            "point in turn and indicate where the manuscript has been changed."
        ),
    )
    _make_file(submission, SubmissionFile.Kind.REVISION, author, version=2)
    _make_file(submission, SubmissionFile.Kind.RESPONSE, author, version=2)
    submission.save()
    _system_note(submission, f"Revision received on {revision.submitted_at:%Y-%m-%d}.")
    created += 1

    # --- 2 accepted, in production ----------------------------------------
    for index, state in enumerate((SubmissionStatus.COPYEDITING, SubmissionStatus.TYPESETTING)):
        submission = _create_submission(
            topic_index=next_topic(),
            submitter=author,
            status=state,
            days_ago=120 + index * 6,
            editor=editor,
        )
        submission.similarity_percent = 7.3
        submission.similarity_checked_by = editor
        submission.similarity_checked_at = timezone.now() - dt.timedelta(days=110)
        submission.accepted_at = timezone.now() - dt.timedelta(days=20 - index * 5)
        submission.save()
        round_obj = _add_round(submission)
        _assign(round_obj, reviewers[1], ReviewAssignment.Status.SUBMITTED, editor=editor, with_review=True,
                recommendation=Review.Recommendation.ACCEPT)
        _assign(round_obj, reviewers[2], ReviewAssignment.Status.SUBMITTED, editor=editor, with_review=True,
                recommendation=Review.Recommendation.MINOR)
        EditorialDecision.objects.create(
            submission=submission,
            round=round_obj,
            decided_by=eic,
            decision=EditorialDecision.Decision.ACCEPT,
            letter="Dear Author,\n\nI am pleased to inform you that your manuscript has been accepted for publication.\n\nEditorial Office",
            decided_at=timezone.now() - dt.timedelta(days=20 - index * 5),
            emailed_at=timezone.now() - dt.timedelta(days=20 - index * 5),
        )
        for offset, stage in enumerate(ProductionTask.STAGE_ORDER):
            done = offset < (1 if state == SubmissionStatus.COPYEDITING else 3)
            ProductionTask.objects.create(
                submission=submission,
                stage=stage,
                assignee=production,
                status=ProductionTask.Status.DONE if done else ProductionTask.Status.PENDING,
                completed_at=timezone.now() - dt.timedelta(days=5) if done else None,
                due_at=timezone.now() + dt.timedelta(days=7 * (offset + 1)),
            )
        _make_file(submission, SubmissionFile.Kind.COPYEDITED, production)
        created += 1

    # --- 3 rejected --------------------------------------------------------
    for index in range(3):
        desk = index == 0
        submission = _create_submission(
            topic_index=next_topic(),
            submitter=author,
            status=SubmissionStatus.REJECTED,
            days_ago=150 + index * 11,
            editor=editor,
        )
        if not desk:
            submission.similarity_percent = 14.6
            submission.similarity_checked_by = editor
            submission.similarity_checked_at = timezone.now() - dt.timedelta(days=140)
            submission.save()
            round_obj = _add_round(submission)
            _assign(round_obj, reviewers[index % 3], ReviewAssignment.Status.SUBMITTED, editor=editor,
                    with_review=True, recommendation=Review.Recommendation.REJECT)
            _assign(round_obj, reviewers[(index + 1) % 3], ReviewAssignment.Status.SUBMITTED, editor=editor,
                    with_review=True, recommendation=Review.Recommendation.REJECT)
        EditorialDecision.objects.create(
            submission=submission,
            round=submission.latest_round,
            decided_by=eic if not desk else editor,
            decision=(
                EditorialDecision.Decision.DESK_REJECT if desk else EditorialDecision.Decision.REJECT
            ),
            letter=(
                "Dear Author,\n\nAfter an initial editorial assessment we have decided not to "
                "send your manuscript for review, because the research question falls outside "
                "the scope of the journal.\n\nEditorial Office"
                if desk
                else "Dear Author,\n\nAfter careful consideration and two independent reviews, "
                "we are unable to accept your manuscript. The reviewers' comments are "
                "included below.\n\nEditorial Office"
            ),
            decided_at=timezone.now() - dt.timedelta(days=120 - index * 10),
            emailed_at=timezone.now() - dt.timedelta(days=120 - index * 10),
        )
        created += 1

    # --- 1 withdrawn -------------------------------------------------------
    submission = _create_submission(
        topic_index=next_topic(),
        submitter=author,
        status=SubmissionStatus.WITHDRAWN,
        days_ago=175,
        editor=editor,
    )
    submission.is_withdrawn = True
    submission.withdraw_reason = (
        "The authors identified an error in the construction of the panel and will resubmit "
        "after rebuilding the dataset."
    )
    submission.save()
    _system_note(submission, "Withdrawn at the authors' request.")
    created += 1

    stdout.write(style.SUCCESS(f"  submissions in every workflow state ({created})"))
    return created
