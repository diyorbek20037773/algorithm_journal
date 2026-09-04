"""Sections, licences, indexing services, e-mail templates and the demo board."""

from __future__ import annotations

from typing import Any

from seed.pages_authors import AUTHOR_PAGES
from seed.pages_ethics import ETHICS_PAGES
from seed.pages_policies import POLICY_PAGES

#: Every CMS page the journal ships with.
PAGES: list[dict[str, Any]] = POLICY_PAGES + ETHICS_PAGES + AUTHOR_PAGES

# ---------------------------------------------------------------------------
# Sections (SPEC §5.2)
# ---------------------------------------------------------------------------
SECTIONS: list[dict[str, Any]] = [
    {
        "slug": "economic-theory-methodology",
        "order": 1,
        "is_research": True,
        "jel": ["A", "B", "C", "D"],
        "name": {
            "en": "Economic Theory & Methodology",
            "uz": "Iqtisodiy nazariya va metodologiya",
            "ru": "Экономическая теория и методология",
        },
        "description": {
            "en": "Microeconomic and macroeconomic theory, econometric methodology, and the history and philosophy of economics.",
            "uz": "Mikro va makroiqtisodiy nazariya, ekonometrik metodologiya, iqtisodiyot tarixi va falsafasi.",
            "ru": "Микро- и макроэкономическая теория, эконометрическая методология, история и философия экономической науки.",
        },
    },
    {
        "slug": "macroeconomics-monetary-fiscal-policy",
        "order": 2,
        "is_research": True,
        "jel": ["E", "F4"],
        "name": {
            "en": "Macroeconomics, Monetary & Fiscal Policy",
            "uz": "Makroiqtisodiyot, pul-kredit va fiskal siyosat",
            "ru": "Макроэкономика, денежно-кредитная и фискальная политика",
        },
        "description": {
            "en": "Growth, inflation, business cycles, monetary and exchange-rate policy, fiscal rules and debt sustainability.",
            "uz": "Oʻsish, inflyatsiya, biznes sikllari, pul va valyuta siyosati, fiskal qoidalar va qarz barqarorligi.",
            "ru": "Рост, инфляция, деловые циклы, денежная и курсовая политика, фискальные правила и устойчивость долга.",
        },
    },
    {
        "slug": "public-finance-taxation-customs",
        "order": 3,
        "is_research": True,
        "jel": ["H", "K34"],
        "name": {
            "en": "Public Finance, Taxation & Customs",
            "uz": "Davlat moliyasi, soliqlar va bojxona",
            "ru": "Государственные финансы, налоги и таможня",
        },
        "description": {
            "en": "Tax design and administration, public expenditure, intergovernmental finance, customs procedures and trade facilitation.",
            "uz": "Soliq tizimi va maʼmuriyati, davlat xarajatlari, byudjetlararo munosabatlar, bojxona tartiblari va savdoni soddalashtirish.",
            "ru": "Устройство и администрирование налогов, государственные расходы, межбюджетные отношения, таможенные процедуры и упрощение торговли.",
        },
    },
    {
        "slug": "international-trade-integration",
        "order": 4,
        "is_research": True,
        "jel": ["F1", "F2", "F3"],
        "name": {
            "en": "International Trade & Economic Integration",
            "uz": "Xalqaro savdo va iqtisodiy integratsiya",
            "ru": "Международная торговля и экономическая интеграция",
        },
        "description": {
            "en": "Trade flows and policy, regional integration, global value chains and foreign direct investment.",
            "uz": "Savdo oqimlari va siyosati, mintaqaviy integratsiya, global qiymat zanjirlari va toʻgʻridan-toʻgʻri xorijiy investitsiyalar.",
            "ru": "Торговые потоки и политика, региональная интеграция, глобальные цепочки создания стоимости и прямые иностранные инвестиции.",
        },
    },
    {
        "slug": "finance-banking-investment",
        "order": 5,
        "is_research": True,
        "jel": ["G"],
        "name": {
            "en": "Finance, Banking & Investment",
            "uz": "Moliya, bank ishi va investitsiyalar",
            "ru": "Финансы, банковское дело и инвестиции",
        },
        "description": {
            "en": "Financial markets and intermediaries, banking regulation, corporate finance, financial inclusion and capital markets.",
            "uz": "Moliya bozorlari va vositachilari, bank tartibga solish, korporativ moliya, moliyaviy qamrov va kapital bozorlari.",
            "ru": "Финансовые рынки и посредники, банковское регулирование, корпоративные финансы, финансовая доступность и рынки капитала.",
        },
    },
    {
        "slug": "digital-economy-innovation",
        "order": 6,
        "is_research": True,
        "jel": ["O3", "L86", "C8"],
        "name": {
            "en": "Digital Economy, Innovation & Data-Driven Analysis",
            "uz": "Raqamli iqtisodiyot, innovatsiya va maʼlumotlarga asoslangan tahlil",
            "ru": "Цифровая экономика, инновации и анализ данных",
        },
        "description": {
            "en": "Digitalisation of firms and government, e-commerce, platform economics, innovation systems and machine learning applied to economic questions.",
            "uz": "Korxonalar va davlat boshqaruvining raqamlashuvi, elektron tijorat, platforma iqtisodiyoti, innovatsion tizimlar va mashinali oʻqitishning iqtisodiy masalalarga qoʻllanishi.",
            "ru": "Цифровизация компаний и государства, электронная коммерция, экономика платформ, инновационные системы и применение машинного обучения к экономическим задачам.",
        },
    },
    {
        "slug": "regional-sectoral-development",
        "order": 7,
        "is_research": True,
        "jel": ["O1", "Q", "R"],
        "name": {
            "en": "Regional, Sectoral & Development Economics",
            "uz": "Hududiy, tarmoq va rivojlanish iqtisodiyoti",
            "ru": "Региональная, отраслевая экономика и экономика развития",
        },
        "description": {
            "en": "Regional disparities, agriculture, energy, transport, poverty and inequality, and the evaluation of development programmes.",
            "uz": "Hududiy tafovutlar, qishloq xoʻjaligi, energetika, transport, qashshoqlik va tengsizlik hamda rivojlanish dasturlarini baholash.",
            "ru": "Региональные различия, сельское хозяйство, энергетика, транспорт, бедность и неравенство, оценка программ развития.",
        },
    },
    {
        "slug": "management-entrepreneurship-labour",
        "order": 8,
        "is_research": True,
        "jel": ["M", "J", "L26"],
        "name": {
            "en": "Management, Entrepreneurship & Labour Economics",
            "uz": "Menejment, tadbirkorlik va mehnat iqtisodiyoti",
            "ru": "Менеджмент, предпринимательство и экономика труда",
        },
        "description": {
            "en": "Firm performance and strategy, entrepreneurship, human capital, labour markets and migration.",
            "uz": "Korxona samaradorligi va strategiyasi, tadbirkorlik, inson kapitali, mehnat bozorlari va migratsiya.",
            "ru": "Результативность и стратегия фирмы, предпринимательство, человеческий капитал, рынки труда и миграция.",
        },
    },
    {
        "slug": "reviews-commentary",
        "order": 9,
        "is_research": False,
        "jel": ["Y3", "A1"],
        "name": {
            "en": "Reviews & Commentary",
            "uz": "Sharhlar va mulohazalar",
            "ru": "Обзоры и комментарии",
        },
        "description": {
            "en": "Review articles, book reviews and invited commentary. Edited but not counted as original research.",
            "uz": "Sharh maqolalari, kitob taqrizlari va taklif etilgan mulohazalar. Tahrirlanadi, ammo original tadqiqot sifatida hisoblanmaydi.",
            "ru": "Обзорные статьи, рецензии на книги и приглашённые комментарии. Проходят редактуру, но не считаются оригинальными исследованиями.",
        },
    },
]

# ---------------------------------------------------------------------------
# Licences
# ---------------------------------------------------------------------------
LICENSES: list[dict[str, Any]] = [
    {
        "code": "CC-BY-4.0",
        "name": "Creative Commons Attribution 4.0 International",
        "url": "https://creativecommons.org/licenses/by/4.0/",
        "is_default": True,
    },
    {
        "code": "CC-BY-SA-4.0",
        "name": "Creative Commons Attribution-ShareAlike 4.0 International",
        "url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "is_default": False,
    },
]

# ---------------------------------------------------------------------------
# Indexing services — only real ones are seeded active
# ---------------------------------------------------------------------------
INDEXING_SERVICES: list[dict[str, Any]] = [
    {
        "slug": "crossref",
        "name": "Crossref",
        "url": "https://www.crossref.org/",
        "is_active": True,
        "order": 1,
        "note": {
            "en": "DOI registration and reference linking for every published article.",
            "uz": "Har bir chop etilgan maqola uchun DOI roʻyxatga olish va havolalarni bogʻlash.",
            "ru": "Регистрация DOI и связывание ссылок для каждой опубликованной статьи.",
        },
    },
    {
        "slug": "google-scholar",
        "name": "Google Scholar",
        "url": "https://scholar.google.com/",
        "is_active": True,
        "order": 2,
        "note": {
            "en": "Full-text indexing through Highwire Press metadata and crawlable PDFs.",
            "uz": "Highwire Press metamaʼlumotlari va indekslanadigan PDF orqali toʻliq matn indeksatsiyasi.",
            "ru": "Полнотекстовая индексация через метаданные Highwire Press и индексируемые PDF.",
        },
    },
    {
        "slug": "orcid",
        "name": "ORCID",
        "url": "https://orcid.org/",
        "is_active": True,
        "order": 3,
        "note": {
            "en": "Authenticated author identifiers, deposited with Crossref.",
            "uz": "Tasdiqlangan muallif identifikatorlari, Crossref ga yuboriladi.",
            "ru": "Подтверждённые идентификаторы авторов, передаваемые в Crossref.",
        },
    },
    {
        "slug": "doaj",
        "name": "DOAJ",
        "url": "https://doaj.org/",
        "is_active": False,
        "order": 4,
        "note": {
            "en": "Application planned after twelve months of continuous publication.",
            "uz": "Ariza uzluksiz nashrning oʻn ikki oyidan keyin rejalashtirilgan.",
            "ru": "Заявка планируется после двенадцати месяцев непрерывного выпуска.",
        },
    },
    {
        "slug": "scopus",
        "name": "Scopus",
        "url": "https://www.scopus.com/",
        "is_active": False,
        "order": 5,
        "note": {
            "en": "CSAB application planned after twenty-four months of publication.",
            "uz": "CSAB arizasi nashrning yigirma toʻrt oyidan keyin rejalashtirilgan.",
            "ru": "Заявка в CSAB планируется после двадцати четырёх месяцев выпуска.",
        },
    },
    {
        "slug": "clockss",
        "name": "CLOCKSS",
        "url": "https://clockss.org/",
        "is_active": False,
        "order": 6,
        "note": {
            "en": "Digital preservation; LOCKSS manifests are already published.",
            "uz": "Raqamli saqlash; LOCKSS manifestlari allaqachon eʼlon qilingan.",
            "ru": "Цифровое хранение; манифесты LOCKSS уже опубликованы.",
        },
    },
]

# ---------------------------------------------------------------------------
# E-mail templates
# ---------------------------------------------------------------------------
EMAIL_TEMPLATES: list[dict[str, Any]] = [
    {
        "event": "submission_received_author",
        "placeholders": "reference\ntitle\njournal\nsection\ndashboard_url",
        "subject": {
            "en": "Your submission {reference} has been received",
            "uz": "{reference} raqamli qoʻlyozmangiz qabul qilindi",
            "ru": "Ваша рукопись {reference} получена",
        },
        "body": {
            "en": "Dear author,\n\nThank you for submitting **{title}** to {journal}.\n\nYour submission reference is **{reference}**. Please quote it in any correspondence.\n\nAn editor will screen the manuscript within seven days and, if it goes forward, invite at least two reviewers. You can follow every step in your dashboard:\n\n{dashboard_url}\n\nEditorial Office",
            "uz": "Hurmatli muallif,\n\n**{title}** qoʻlyozmasini {journal} ga yuborganingiz uchun rahmat.\n\nQoʻlyozmangiz raqami — **{reference}**. Yozishmalarda shu raqamni koʻrsating.\n\nMuharrir qoʻlyozmani yetti kun ichida koʻrib chiqadi va davom etsa, kamida ikki taqrizchini taklif qiladi. Har bir bosqichni boshqaruv panelida kuzatishingiz mumkin:\n\n{dashboard_url}\n\nTahririyat",
            "ru": "Уважаемый автор,\n\nблагодарим за отправку рукописи **{title}** в {journal}.\n\nНомер вашей рукописи — **{reference}**. Указывайте его в переписке.\n\nРедактор проведёт отбор в течение семи дней и, если работа пойдёт дальше, пригласит не менее двух рецензентов. Следить за каждым шагом можно в личном кабинете:\n\n{dashboard_url}\n\nРедакция",
        },
    },
    {
        "event": "submission_received_editor",
        "placeholders": "reference\ntitle\nsection\ndetail_url",
        "subject": {
            "en": "New submission {reference} in {section}",
            "uz": "{section} boʻlimiga yangi qoʻlyozma {reference}",
            "ru": "Новая рукопись {reference} в рубрике {section}",
        },
        "body": {
            "en": "A new manuscript has been submitted.\n\n**{title}**\nReference: {reference}\nSection: {section}\n\nOpen it here: {detail_url}\n\nPlease complete the screening within seven days.",
            "uz": "Yangi qoʻlyozma yuborildi.\n\n**{title}**\nRaqam: {reference}\nBoʻlim: {section}\n\nBu yerda oching: {detail_url}\n\nDastlabki koʻrikni yetti kun ichida yakunlang.",
            "ru": "Поступила новая рукопись.\n\n**{title}**\nНомер: {reference}\nРубрика: {section}\n\nОткрыть: {detail_url}\n\nПожалуйста, завершите отбор в течение семи дней.",
        },
    },
    {
        "event": "editor_assigned",
        "placeholders": "reference\ntitle\ndetail_url",
        "subject": {
            "en": "You are the handling editor for {reference}",
            "uz": "{reference} boʻyicha masʼul muharrir sizsiz",
            "ru": "Вы — ответственный редактор рукописи {reference}",
        },
        "body": {
            "en": "You have been assigned as handling editor for **{title}** ({reference}).\n\nOpen it here: {detail_url}",
            "uz": "Siz **{title}** ({reference}) qoʻlyozmasi boʻyicha masʼul muharrir etib tayinlandingiz.\n\nBu yerda oching: {detail_url}",
            "ru": "Вы назначены ответственным редактором рукописи **{title}** ({reference}).\n\nОткрыть: {detail_url}",
        },
    },
    {
        "event": "reviewer_invite",
        "placeholders": "title\nabstract\nsection\ndue_date\naccept_url\ndecline_url\njournal",
        "subject": {
            "en": "Invitation to review for {journal}",
            "uz": "{journal} uchun taqriz yozishga taklif",
            "ru": "Приглашение рецензировать для {journal}",
        },
        "body": {
            "en": "Dear colleague,\n\nWe would be grateful if you would review the following manuscript for {journal} (section: {section}).\n\n**{title}**\n\n{abstract}\n\nThe review would be due by **{due_date}** — 21 days from acceptance. The review is double-blind: the manuscript contains no information identifying the authors, and your identity is never disclosed to them.\n\n[Accept the invitation]({accept_url})  ·  [Decline]({decline_url})\n\nIf you cannot review, a prompt decline helps us greatly, and a suggestion of another reviewer helps even more.\n\nEditorial Office",
            "uz": "Hurmatli hamkasb,\n\n{journal} uchun quyidagi qoʻlyozmaga taqriz yozsangiz, minnatdor boʻlardik (boʻlim: {section}).\n\n**{title}**\n\n{abstract}\n\nTaqriz **{due_date}** gacha — qabul qilingandan 21 kun ichida topshiriladi. Taqriz ikki tomonlama yashirin: qoʻlyozmada mualliflarni aniqlovchi maʼlumot yoʻq, sizning shaxsingiz esa ularga hech qachon oshkor qilinmaydi.\n\n[Taklifni qabul qilish]({accept_url})  ·  [Rad etish]({decline_url})\n\nAgar taqriz qila olmasangiz, tezda rad etishingiz bizga juda yordam beradi, boshqa taqrizchi tavsiya qilsangiz esa undan ham koʻproq.\n\nTahririyat",
            "ru": "Уважаемый коллега,\n\nбудем признательны, если вы отрецензируете следующую рукопись для {journal} (рубрика: {section}).\n\n**{title}**\n\n{abstract}\n\nСрок рецензии — до **{due_date}**, 21 день с момента согласия. Рецензирование двойное слепое: рукопись не содержит сведений об авторах, а ваша личность им никогда не раскрывается.\n\n[Принять приглашение]({accept_url})  ·  [Отклонить]({decline_url})\n\nЕсли вы не можете рецензировать, быстрый отказ очень нам поможет, а предложение другого рецензента — ещё больше.\n\nРедакция",
        },
    },
    {
        "event": "reviewer_reminder",
        "placeholders": "title\ndue_date\nreview_url\nkind",
        "subject": {
            "en": "Reminder: your review is due on {due_date}",
            "uz": "Eslatma: taqrizingiz {due_date} gacha topshirilishi kerak",
            "ru": "Напоминание: рецензия должна быть представлена до {due_date}",
        },
        "body": {
            "en": "This is a friendly reminder that your review of **{title}** is due on {due_date}.\n\nOpen the review form: {review_url}\n\nIf you need more time, reply to this message and we will extend the deadline.",
            "uz": "**{title}** boʻyicha taqrizingiz {due_date} gacha topshirilishi kerakligini eslatamiz.\n\nTaqriz shaklini oching: {review_url}\n\nQoʻshimcha vaqt kerak boʻlsa, ushbu xatga javob bering — muddatni uzaytiramiz.",
            "ru": "Напоминаем, что ваша рецензия на **{title}** должна быть представлена до {due_date}.\n\nОткрыть форму рецензии: {review_url}\n\nЕсли нужно больше времени, ответьте на это письмо — мы продлим срок.",
        },
    },
    {
        "event": "reviewer_thanks",
        "placeholders": "title\ncertificate_url",
        "subject": {
            "en": "Thank you for your review",
            "uz": "Taqrizingiz uchun rahmat",
            "ru": "Благодарим за рецензию",
        },
        "body": {
            "en": "Thank you for reviewing **{title}**. Your assessment has reached the editor and will inform the decision.\n\nYou can download a certificate of review at any time:\n\n{certificate_url}",
            "uz": "**{title}** ga taqriz yozganingiz uchun rahmat. Bahoyingiz muharrirga yetib bordi va qaror qabul qilishda hisobga olinadi.\n\nTaqriz sertifikatini istalgan vaqtda yuklab olishingiz mumkin:\n\n{certificate_url}",
            "ru": "Благодарим за рецензию на **{title}**. Ваша оценка передана редактору и будет учтена при принятии решения.\n\nСертификат рецензента можно скачать в любое время:\n\n{certificate_url}",
        },
    },
    {
        "event": "decision",
        "placeholders": "reference\ntitle\ndecision\nletter\ndashboard_url",
        "subject": {
            "en": "Decision on {reference}: {decision}",
            "uz": "{reference} boʻyicha qaror: {decision}",
            "ru": "Решение по рукописи {reference}: {decision}",
        },
        "body": {
            "en": "{letter}\n\n---\n\nYou can see the full record of this manuscript in your dashboard: {dashboard_url}",
            "uz": "{letter}\n\n---\n\nUshbu qoʻlyozmaning toʻliq yozuvini boshqaruv panelida koʻrishingiz mumkin: {dashboard_url}",
            "ru": "{letter}\n\n---\n\nПолную историю рукописи можно посмотреть в личном кабинете: {dashboard_url}",
        },
    },
    {
        "event": "revision_reminder",
        "placeholders": "reference\ntitle\ndue_date\ndashboard_url",
        "subject": {
            "en": "Revision of {reference} is due on {due_date}",
            "uz": "{reference} qayta ishlangan varianti {due_date} gacha topshirilishi kerak",
            "ru": "Доработка рукописи {reference} должна быть представлена до {due_date}",
        },
        "body": {
            "en": "Your revised version of **{title}** ({reference}) is due on {due_date}.\n\nUpload it here: {dashboard_url}\n\nIf you need more time, write to the editorial office before the deadline.",
            "uz": "**{title}** ({reference}) qayta ishlangan varianti {due_date} gacha topshirilishi kerak.\n\nBu yerga yuklang: {dashboard_url}\n\nQoʻshimcha vaqt kerak boʻlsa, muddatdan oldin tahririyatga yozing.",
            "ru": "Доработанная версия рукописи **{title}** ({reference}) должна быть представлена до {due_date}.\n\nЗагрузите её здесь: {dashboard_url}\n\nЕсли нужно больше времени, напишите в редакцию до истечения срока.",
        },
    },
    {
        "event": "proof_request",
        "placeholders": "reference\ntitle\ndashboard_url\ndeadline",
        "subject": {
            "en": "Proof of {reference} is ready for your approval",
            "uz": "{reference} korrekturasi tasdiqlashingiz uchun tayyor",
            "ru": "Корректура рукописи {reference} готова к утверждению",
        },
        "body": {
            "en": "The typeset proof of **{title}** ({reference}) is ready.\n\nPlease check it carefully — this is the last opportunity to correct errors — and approve it by **{deadline}**:\n\n{dashboard_url}\n\nOnly typographical and factual corrections can be made at this stage.",
            "uz": "**{title}** ({reference}) sahifalangan korrekturasi tayyor.\n\nUni diqqat bilan tekshiring — bu xatolarni tuzatishning oxirgi imkoniyati — va **{deadline}** gacha tasdiqlang:\n\n{dashboard_url}\n\nBu bosqichda faqat imlo va faktik tuzatishlar kiritiladi.",
            "ru": "Свёрстанная корректура рукописи **{title}** ({reference}) готова.\n\nВнимательно проверьте её — это последняя возможность исправить ошибки — и утвердите до **{deadline}**:\n\n{dashboard_url}\n\nНа этом этапе возможны только типографские и фактические исправления.",
        },
    },
    {
        "event": "published",
        "placeholders": "title\ndoi\nurl",
        "subject": {
            "en": "Your article is published",
            "uz": "Maqolangiz chop etildi",
            "ru": "Ваша статья опубликована",
        },
        "body": {
            "en": "Your article **{title}** is now published and freely available.\n\nDOI: {doi}\nURL: {url}\n\nYou keep the copyright and may deposit any version in any repository with no embargo. Please cite the published version by its DOI.\n\nCongratulations, and thank you for publishing with us.",
            "uz": "**{title}** maqolangiz chop etildi va erkin foydalanish uchun ochiq.\n\nDOI: {doi}\nURL: {url}\n\nMualliflik huquqi sizda qoladi va istalgan variantni istalgan repozitoriyga embargosiz joylashtirishingiz mumkin. Chop etilgan variantni DOI orqali iqtibos qiling.\n\nTabriklaymiz va biz bilan nashr etganingiz uchun rahmat.",
            "ru": "Ваша статья **{title}** опубликована и находится в свободном доступе.\n\nDOI: {doi}\nURL: {url}\n\nАвторское право остаётся у вас, любую версию можно разместить в любом репозитории без эмбарго. Цитируйте опубликованную версию по DOI.\n\nПоздравляем и благодарим за публикацию у нас.",
        },
    },
    {
        "event": "doi_registered",
        "placeholders": "title\ndoi",
        "subject": {
            "en": "DOI registered for your article",
            "uz": "Maqolangiz uchun DOI roʻyxatga olindi",
            "ru": "Для вашей статьи зарегистрирован DOI",
        },
        "body": {
            "en": "The DOI **{doi}** has been registered with Crossref for your article **{title}**. It may take a few hours to resolve.",
            "uz": "**{title}** maqolangiz uchun **{doi}** DOI Crossref da roʻyxatdan oʻtkazildi. U ishlashi uchun bir necha soat kerak boʻlishi mumkin.",
            "ru": "Для вашей статьи **{title}** в Crossref зарегистрирован DOI **{doi}**. Разрешение ссылки может занять несколько часов.",
        },
    },
    {
        "event": "signup_verify",
        "placeholders": "reset_url",
        "subject": {
            "en": "Activate your account",
            "uz": "Hisobingizni faollashtiring",
            "ru": "Активируйте вашу учётную запись",
        },
        "body": {
            "en": "An account has been created for you in the editorial system.\n\nSet your password here: {reset_url}\n\nIf you were not expecting this message, you can ignore it.",
            "uz": "Tahririy tizimda siz uchun hisob yaratildi.\n\nParolni bu yerda oʻrnating: {reset_url}\n\nAgar bu xatni kutmagan boʻlsangiz, eʼtiborsiz qoldiring.",
            "ru": "Для вас создана учётная запись в редакционной системе.\n\nЗадайте пароль здесь: {reset_url}\n\nЕсли вы не ожидали этого письма, просто проигнорируйте его.",
        },
    },
    {
        "event": "contact_form",
        "placeholders": "name\nemail\nsubject\nmessage",
        "subject": {
            "en": "[Contact] {subject}",
            "uz": "[Murojaat] {subject}",
            "ru": "[Обращение] {subject}",
        },
        "body": {
            "en": "**From:** {name} <{email}>\n\n**Subject:** {subject}\n\n{message}",
            "uz": "**Kimdan:** {name} <{email}>\n\n**Mavzu:** {subject}\n\n{message}",
            "ru": "**От:** {name} <{email}>\n\n**Тема:** {subject}\n\n{message}",
        },
    },
]

# ---------------------------------------------------------------------------
# Demonstration editorial board — every entry is marked DEMO and must be replaced
# ---------------------------------------------------------------------------
BOARD: list[dict[str, Any]] = [
    {
        "role": "editor_in_chief",
        "name": "DEMO — replace: Prof. Nodira Rakhimova",
        "degree": {
            "en": "Doctor of Economics (DSc)",
            "uz": "Iqtisodiyot fanlari doktori (DSc)",
            "ru": "Доктор экономических наук (DSc)",
        },
        "title": {"en": "Professor", "uz": "Professor", "ru": "Профессор"},
        "affiliation": {
            "en": "Institute of Economic Research, Tashkent",
            "uz": "Iqtisodiy tadqiqotlar instituti, Toshkent",
            "ru": "Институт экономических исследований, Ташкент",
        },
        "country": "UZ",
        "orcid": "0000-0002-0000-0001",
        "email": "eic@algorithm-journal.uz",
        "expertise": {
            "en": "Macroeconomic policy, structural reform, transition economies",
            "uz": "Makroiqtisodiy siyosat, tarkibiy islohotlar, oʻtish iqtisodiyoti",
            "ru": "Макроэкономическая политика, структурные реформы, переходные экономики",
        },
        "order": 1,
    },
    {
        "role": "deputy_editor",
        "name": "DEMO — replace: Prof. Timur Abdullayev",
        "degree": {
            "en": "Doctor of Economics (DSc)",
            "uz": "Iqtisodiyot fanlari doktori (DSc)",
            "ru": "Доктор экономических наук (DSc)",
        },
        "title": {"en": "Professor", "uz": "Professor", "ru": "Профессор"},
        "affiliation": {
            "en": "University of Economics and Finance, Samarkand",
            "uz": "Iqtisodiyot va moliya universiteti, Samarqand",
            "ru": "Университет экономики и финансов, Самарканд",
        },
        "country": "UZ",
        "orcid": "0000-0002-0000-0002",
        "expertise": {
            "en": "Public finance, taxation, fiscal decentralisation",
            "uz": "Davlat moliyasi, soliqlar, fiskal markazsizlashtirish",
            "ru": "Государственные финансы, налоги, фискальная децентрализация",
        },
        "order": 2,
    },
    {
        "role": "deputy_editor",
        "name": "DEMO — replace: Prof. Elena Sokolova",
        "degree": {
            "en": "Doctor of Economics (DSc)",
            "uz": "Iqtisodiyot fanlari doktori (DSc)",
            "ru": "Доктор экономических наук (DSc)",
        },
        "title": {"en": "Professor", "uz": "Professor", "ru": "Профессор"},
        "affiliation": {
            "en": "Graduate School of Economics, Almaty",
            "uz": "Iqtisodiyot oliy maktabi, Almati",
            "ru": "Высшая школа экономики, Алматы",
        },
        "country": "KZ",
        "orcid": "0000-0002-0000-0003",
        "expertise": {
            "en": "International trade, regional integration, gravity models",
            "uz": "Xalqaro savdo, mintaqaviy integratsiya, gravitatsion modellar",
            "ru": "Международная торговля, региональная интеграция, гравитационные модели",
        },
        "order": 3,
    },
    {
        "role": "managing_editor",
        "name": "DEMO — replace: Dr Kamola Yusupova",
        "degree": {
            "en": "PhD in Economics",
            "uz": "Iqtisodiyot boʻyicha falsafa doktori (PhD)",
            "ru": "PhD по экономике",
        },
        "title": {"en": "Associate Professor", "uz": "Dotsent", "ru": "Доцент"},
        "affiliation": {
            "en": "Institute of Economic Research, Tashkent",
            "uz": "Iqtisodiy tadqiqotlar instituti, Toshkent",
            "ru": "Институт экономических исследований, Ташкент",
        },
        "country": "UZ",
        "orcid": "0000-0002-0000-0004",
        "email": "editor@algorithm-journal.uz",
        "expertise": {
            "en": "Editorial management, research methodology",
            "uz": "Tahririy boshqaruv, tadqiqot metodologiyasi",
            "ru": "Редакционное управление, методология исследований",
        },
        "order": 4,
    },
    {
        "role": "section_editor",
        "name": "DEMO — replace: Dr Aziz Karimov",
        "degree": {
            "en": "PhD in Economics",
            "uz": "Iqtisodiyot boʻyicha falsafa doktori (PhD)",
            "ru": "PhD по экономике",
        },
        "title": {"en": "Associate Professor", "uz": "Dotsent", "ru": "Доцент"},
        "affiliation": {
            "en": "Banking and Finance Academy, Tashkent",
            "uz": "Bank-moliya akademiyasi, Toshkent",
            "ru": "Банковско-финансовая академия, Ташкент",
        },
        "country": "UZ",
        "orcid": "0000-0002-0000-0005",
        "expertise": {
            "en": "Banking regulation, financial inclusion, credit markets",
            "uz": "Bank tartibga solish, moliyaviy qamrov, kredit bozorlari",
            "ru": "Банковское регулирование, финансовая доступность, кредитные рынки",
        },
        "order": 5,
        "sections": ["finance-banking-investment"],
    },
    {
        "role": "section_editor",
        "name": "DEMO — replace: Dr Marta Kowalska",
        "degree": {
            "en": "PhD in Economics",
            "uz": "Iqtisodiyot boʻyicha falsafa doktori (PhD)",
            "ru": "PhD по экономике",
        },
        "title": {"en": "Senior Lecturer", "uz": "Katta oʻqituvchi", "ru": "Старший преподаватель"},
        "affiliation": {
            "en": "Warsaw School of Economics",
            "uz": "Varshava iqtisodiyot maktabi",
            "ru": "Варшавская школа экономики",
        },
        "country": "PL",
        "orcid": "0000-0002-0000-0006",
        "expertise": {
            "en": "Digital economy, platform markets, applied microeconometrics",
            "uz": "Raqamli iqtisodiyot, platforma bozorlari, amaliy mikroekonometrika",
            "ru": "Цифровая экономика, платформенные рынки, прикладная микроэконометрика",
        },
        "order": 6,
        "sections": ["digital-economy-innovation"],
    },
    {
        "role": "board_member",
        "name": "DEMO — replace: Prof. Rashid Alimov",
        "degree": {
            "en": "Doctor of Economics (DSc)",
            "uz": "Iqtisodiyot fanlari doktori (DSc)",
            "ru": "Доктор экономических наук (DSc)",
        },
        "title": {"en": "Professor", "uz": "Professor", "ru": "Профессор"},
        "affiliation": {
            "en": "National University, Tashkent",
            "uz": "Milliy universitet, Toshkent",
            "ru": "Национальный университет, Ташкент",
        },
        "country": "UZ",
        "orcid": "0000-0002-0000-0007",
        "expertise": {
            "en": "Labour economics, migration, human capital",
            "uz": "Mehnat iqtisodiyoti, migratsiya, inson kapitali",
            "ru": "Экономика труда, миграция, человеческий капитал",
        },
        "order": 7,
    },
    {
        "role": "board_member",
        "name": "DEMO — replace: Dr Ayşe Demir",
        "degree": {
            "en": "PhD in Economics",
            "uz": "Iqtisodiyot boʻyicha falsafa doktori (PhD)",
            "ru": "PhD по экономике",
        },
        "title": {"en": "Associate Professor", "uz": "Dotsent", "ru": "Доцент"},
        "affiliation": {
            "en": "Middle East Technical University, Ankara",
            "uz": "Yaqin Sharq texnika universiteti, Anqara",
            "ru": "Ближневосточный технический университет, Анкара",
        },
        "country": "TR",
        "orcid": "0000-0002-0000-0008",
        "expertise": {
            "en": "Monetary policy, inflation dynamics, emerging markets",
            "uz": "Pul-kredit siyosati, inflyatsiya dinamikasi, rivojlanayotgan bozorlar",
            "ru": "Денежно-кредитная политика, динамика инфляции, развивающиеся рынки",
        },
        "order": 8,
    },
    {
        "role": "board_member",
        "name": "DEMO — replace: Dr Bekzod Toshmatov",
        "degree": {
            "en": "PhD in Economics",
            "uz": "Iqtisodiyot boʻyicha falsafa doktori (PhD)",
            "ru": "PhD по экономике",
        },
        "title": {
            "en": "Senior Researcher",
            "uz": "Katta ilmiy xodim",
            "ru": "Старший научный сотрудник",
        },
        "affiliation": {
            "en": "Centre for Regional Studies, Bukhara",
            "uz": "Hududiy tadqiqotlar markazi, Buxoro",
            "ru": "Центр региональных исследований, Бухара",
        },
        "country": "UZ",
        "orcid": "0000-0002-0000-0009",
        "expertise": {
            "en": "Regional development, agriculture, water economics",
            "uz": "Hududiy rivojlanish, qishloq xoʻjaligi, suv iqtisodiyoti",
            "ru": "Региональное развитие, сельское хозяйство, экономика водных ресурсов",
        },
        "order": 9,
    },
    {
        "role": "advisory",
        "name": "DEMO — replace: Prof. Michael Brennan",
        "degree": {
            "en": "PhD in Economics",
            "uz": "Iqtisodiyot boʻyicha falsafa doktori (PhD)",
            "ru": "PhD по экономике",
        },
        "title": {
            "en": "Professor Emeritus",
            "uz": "Faxriy professor",
            "ru": "Заслуженный профессор",
        },
        "affiliation": {
            "en": "University of Manchester",
            "uz": "Manchester universiteti",
            "ru": "Манчестерский университет",
        },
        "country": "GB",
        "orcid": "0000-0002-0000-0010",
        "expertise": {
            "en": "Development economics, programme evaluation",
            "uz": "Rivojlanish iqtisodiyoti, dasturlarni baholash",
            "ru": "Экономика развития, оценка программ",
        },
        "order": 10,
    },
    {
        "role": "advisory",
        "name": "DEMO — replace: Prof. Hiroshi Tanaka",
        "degree": {
            "en": "Doctor of Economics",
            "uz": "Iqtisodiyot fanlari doktori",
            "ru": "Доктор экономических наук",
        },
        "title": {"en": "Professor", "uz": "Professor", "ru": "Профессор"},
        "affiliation": {
            "en": "Hitotsubashi University, Tokyo",
            "uz": "Hitotsubashi universiteti, Tokio",
            "ru": "Университет Хитоцубаси, Токио",
        },
        "country": "JP",
        "orcid": "0000-0002-0000-0011",
        "expertise": {
            "en": "Trade policy, global value chains, industrial organisation",
            "uz": "Savdo siyosati, global qiymat zanjirlari, tarmoq iqtisodiyoti",
            "ru": "Торговая политика, глобальные цепочки создания стоимости, отраслевая организация",
        },
        "order": 11,
    },
    {
        "role": "reviewer_board",
        "name": "DEMO — replace: Dr Zarina Ismailova",
        "degree": {
            "en": "PhD in Economics",
            "uz": "Iqtisodiyot boʻyicha falsafa doktori (PhD)",
            "ru": "PhD по экономике",
        },
        "title": {"en": "Associate Professor", "uz": "Dotsent", "ru": "Доцент"},
        "affiliation": {
            "en": "Institute of Forecasting and Macroeconomic Research, Tashkent",
            "uz": "Prognozlashtirish va makroiqtisodiy tadqiqotlar instituti, Toshkent",
            "ru": "Институт прогнозирования и макроэкономических исследований, Ташкент",
        },
        "country": "UZ",
        "orcid": "0000-0002-0000-0012",
        "expertise": {
            "en": "Applied econometrics, panel data, firm-level analysis",
            "uz": "Amaliy ekonometrika, panel maʼlumotlar, korxona darajasidagi tahlil",
            "ru": "Прикладная эконометрика, панельные данные, анализ на уровне фирм",
        },
        "order": 12,
    },
]

#: Announcements shipped with the demo content.
ANNOUNCEMENTS: list[dict[str, Any]] = [
    {
        "slug": "call-for-papers-vol-1-no-5",
        "days_ago": 5,
        "is_pinned": True,
        "title": {
            "en": "Call for papers: Vol. 1, No. 5 — Digital public finance",
            "uz": "Maqolalar uchun chaqiruv: 1-jild, 5-son — Raqamli davlat moliyasi",
            "ru": "Приём статей: том 1, № 5 — Цифровые государственные финансы",
        },
        "body": {
            "en": "We invite submissions for a themed section of **Vol. 1, No. 5** on *digital public finance*: e-invoicing and VAT compliance, digital tax administration, public expenditure transparency platforms, and the measurement of their effects on revenue and on firms.\n\nWe are particularly interested in work using firm-level or transaction-level administrative data with a credible identification strategy.\n\n**Deadline for submissions: 15 March 2026.** Submit through the normal [submission system](/en/submit/) and mention the themed section in your cover letter. All submissions are peer reviewed to the usual standard; there are no fees.",
            "uz": "**1-jild, 5-son**ning *raqamli davlat moliyasi* mavzusidagi maxsus boʻlimi uchun maqolalar qabul qilamiz: elektron hisob-fakturalar va QQS boʻyicha rioya, raqamli soliq maʼmuriyati, davlat xarajatlari shaffofligi platformalari hamda ularning daromadlar va korxonalarga taʼsirini oʻlchash.\n\nAyniqsa korxona yoki tranzaksiya darajasidagi maʼmuriy maʼlumotlardan ishonchli identifikatsiya strategiyasi bilan foydalanadigan ishlar qiziqtiradi.\n\n**Qabul muddati: 2026-yil 15-mart.** Odatdagi [yuborish tizimi](/uz/submit/) orqali yuboring va muqova xatida maxsus boʻlimni koʻrsating. Barcha maqolalar odatdagi standartda taqrizdan oʻtadi; toʻlov yoʻq.",
            "ru": "Приглашаем присылать статьи в тематический раздел **тома 1, № 5** по теме *цифровые государственные финансы*: электронные счета-фактуры и соблюдение НДС, цифровое налоговое администрирование, платформы прозрачности государственных расходов и измерение их влияния на доходы бюджета и на фирмы.\n\nОсобый интерес представляют работы на административных данных уровня фирм или транзакций с убедительной стратегией идентификации.\n\n**Срок подачи: 15 марта 2026 года.** Подавайте через обычную [систему подачи](/ru/submit/) и укажите тематический раздел в сопроводительном письме. Все рукописи проходят рецензирование по обычным правилам; плата не взимается.",
        },
    },
    {
        "slug": "reviewer-acknowledgement-2026",
        "days_ago": 20,
        "is_pinned": False,
        "title": {
            "en": "Thank you to our reviewers",
            "uz": "Taqrizchilarimizga minnatdorchilik",
            "ru": "Благодарность нашим рецензентам",
        },
        "body": {
            "en": "Peer review is unpaid, invisible and indispensable. We thank everyone who reviewed for the journal this year: the median review was returned in 19 days, and 84 % of invitations were answered within three days.\n\nReviewers can download a certificate from the reviewer dashboard at any time. A full acknowledgement list, naming everyone who consented to be named, is published with the December issue.",
            "uz": "Taqriz — haq toʻlanmaydigan, koʻrinmas, ammo almashtirib boʻlmaydigan mehnat. Bu yil jurnal uchun taqriz yozgan barchaga rahmat aytamiz: taqrizning median muddati 19 kunni tashkil etdi, takliflarning 84 % iga uch kun ichida javob berildi.\n\nTaqrizchilar sertifikatni istalgan vaqtda boshqaruv panelidan yuklab olishi mumkin. Ismini eʼlon qilishga rozilik bergan barchaning toʻliq roʻyxati dekabr soni bilan birga chop etiladi.",
            "ru": "Рецензирование — неоплачиваемый, невидимый и незаменимый труд. Благодарим всех, кто рецензировал для журнала в этом году: медианный срок рецензии составил 19 дней, на 84 % приглашений ответили в течение трёх дней.\n\nРецензенты могут в любой момент скачать сертификат в личном кабинете. Полный список тех, кто согласился быть названным, публикуется вместе с декабрьским выпуском.",
        },
    },
    {
        "slug": "crossref-membership-and-dois",
        "days_ago": 45,
        "is_pinned": False,
        "title": {
            "en": "Every article now has a Crossref DOI",
            "uz": "Endi har bir maqola Crossref DOI ga ega",
            "ru": "Теперь у каждой статьи есть DOI в Crossref",
        },
        "body": {
            "en": "Metadata for every published article — including author ORCID iDs, abstracts in three languages, licence information and the full reference list — is now deposited with Crossref, so citations are linked and the articles are discoverable through Crossref's API.\n\nThe journal's metadata is also available through our own [OAI-PMH endpoint](/oai/?verb=Identify) and [JSON API](/api/v1/). Applications to DOAJ and, later, to Scopus follow the schedule set out on the [Indexing](/en/about/indexing/) page.",
            "uz": "Endi har bir chop etilgan maqolaning metamaʼlumotlari — mualliflarning ORCID identifikatorlari, uch tildagi annotatsiyalar, litsenziya maʼlumotlari va toʻliq adabiyotlar roʻyxati — Crossref ga yuboriladi, shu sababli iqtiboslar bogʻlanadi va maqolalar Crossref API orqali topiladi.\n\nJurnal metamaʼlumotlari bizning [OAI-PMH interfeysimiz](/oai/?verb=Identify) va [JSON API](/api/v1/) orqali ham mavjud. DOAJ va keyinchalik Scopus ga arizalar [Indeksatsiya](/uz/about/indexing/) sahifasidagi jadval boʻyicha topshiriladi.",
            "ru": "Метаданные каждой опубликованной статьи — включая идентификаторы ORCID авторов, аннотации на трёх языках, сведения о лицензии и полный список литературы — теперь передаются в Crossref, поэтому цитирования связываются, а статьи обнаруживаются через API Crossref.\n\nМетаданные журнала также доступны через наш [интерфейс OAI-PMH](/oai/?verb=Identify) и [JSON API](/api/v1/). Заявки в DOAJ и затем в Scopus подаются по графику, изложенному на странице [Индексация](/ru/about/indexing/).",
        },
    },
]
