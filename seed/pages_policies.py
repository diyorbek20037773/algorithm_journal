"""Policy and About pages, written for the ``about`` navigation group.

Each entry has ``title``, ``body`` (Markdown) and ``seo`` in English, Uzbek
Latin and Russian.  The Uzbek Cyrillic version is generated automatically.
"""

from __future__ import annotations

from typing import Any

POLICY_PAGES: list[dict[str, Any]] = [
    # ------------------------------------------------------------------ about
    {
        "slug": "about",
        "menu_group": "about",
        "order": 1,
        "title": {
            "en": "About the Journal",
            "uz": "Jurnal haqida",
            "ru": "О журнале",
        },
        "seo": {
            "en": "ALGORITHM: Review of Economic Research is an open-access, double-blind peer-reviewed monthly journal of economics.",
            "uz": "«ALGORITM» — iqtisodiy tadqiqotlar sharhi: ochiq kirishli, ikki tomonlama yashirin taqrizdan oʻtadigan oylik iqtisodiy jurnal.",
            "ru": "«АЛГОРИТМ» — обзор экономических исследований: ежемесячный экономический журнал открытого доступа с двойным слепым рецензированием.",
        },
        "body": {
            "en": """**ALGORITHM: Review of Economic Research** is an international, peer-reviewed,
open-access scholarly journal publishing original research in economics. The journal
appears monthly and accepts submissions in English, Uzbek and Russian.

## What we publish

We publish empirical and theoretical work that is methodologically sound, clearly
written and relevant beyond a single national context. Studies of Uzbekistan, Central
Asia and other emerging economies are especially welcome when the questions they ask
and the methods they use are of international interest. See
[Aims & Scope](/en/about/aims-and-scope/) for the full description of the sections.

## How we work

Every manuscript is screened by an editor for scope, structure and similarity, and is
then sent to at least two independent reviewers under a **double-blind** procedure:
reviewers do not know who the authors are, and authors do not know who the reviewers
are. Our target is a first decision within eight weeks of submission. The
[Peer Review Process](/en/about/peer-review/) page describes each step and its typical
duration.

## Open access without charges

The journal is **diamond open access**. Authors pay nothing — no article processing
charge, no submission fee, no page or colour charges — and readers pay nothing.
Articles are published under a [Creative Commons Attribution 4.0 licence](/en/about/open-access/)
and authors retain copyright.

## Identity and infrastructure

Every article receives a DOI registered with Crossref, carries structured metadata for
Google Scholar and Schema.org, and is exposed through an OAI-PMH endpoint for
harvesting. Author identity is recorded with ORCID. Long-term preservation follows the
[Archiving Policy](/en/about/archiving/).

## Editorial office

The editorial office answers author and reviewer enquiries within three working days.
Contact details are on the [Contact](/en/about/contact/) page. Complaints and appeals
follow the procedure set out in the
[Publication Ethics](/en/about/publication-ethics/) statement.""",
            "uz": """**«ALGORITM» — iqtisodiy tadqiqotlar sharhi** — iqtisodiyot sohasidagi original
tadqiqotlarni chop etuvchi xalqaro, taqrizdan oʻtkaziladigan, ochiq kirishli ilmiy
jurnal. Jurnal har oyda chiqadi va ingliz, oʻzbek hamda rus tillaridagi maqolalarni
qabul qiladi.

## Nimalarni chop etamiz

Metodologik jihatdan puxta, aniq yozilgan va bitta mamlakat doirasidan tashqarida ham
ahamiyatga ega boʻlgan empirik va nazariy ishlarni chop etamiz. Oʻzbekiston, Markaziy
Osiyo va boshqa rivojlanayotgan iqtisodiyotlarga oid tadqiqotlar, agar ular qoʻygan
savollar va qoʻllagan usullar xalqaro qiziqish uygʻotsa, ayniqsa qadrlanadi.
Boʻlimlarning toʻliq tavsifi [Maqsad va yoʻnalishlar](/uz/about/aims-and-scope/)
sahifasida keltirilgan.

## Qanday ishlaymiz

Har bir qoʻlyozma muharrir tomonidan mavzuga mosligi, tuzilishi va oʻxshashlik darajasi
boʻyicha koʻrib chiqiladi, soʻngra kamida ikki mustaqil taqrizchiga **ikki tomonlama
yashirin** tartibda yuboriladi: taqrizchilar mualliflarni, mualliflar esa
taqrizchilarni bilmaydi. Maqsadimiz — qoʻlyozma yuborilgandan keyin sakkiz hafta
ichida birinchi qarorni bildirish. Har bir bosqich va uning odatdagi muddati
[Taqriz jarayoni](/uz/about/peer-review/) sahifasida tavsiflangan.

## Toʻlovsiz ochiq kirish

Jurnal **diamond open access** tamoyilida ishlaydi. Mualliflar hech qanday toʻlov
qilmaydi — maqolani qayta ishlash toʻlovi, yuborish toʻlovi, sahifa yoki rangli chop
etish toʻlovi yoʻq — oʻquvchilar ham toʻlamaydi. Maqolalar
[Creative Commons Attribution 4.0 litsenziyasi](/uz/about/open-access/) ostida chop
etiladi, mualliflik huquqi esa muallifda qoladi.

## Identifikatorlar va infratuzilma

Har bir maqola Crossref tizimida roʻyxatdan oʻtgan DOI oladi, Google Scholar va
Schema.org uchun tuzilmali metamaʼlumotlarga ega boʻladi hamda OAI-PMH interfeysi
orqali yigʻib olish uchun ochiq boʻladi. Muallif identifikatori ORCID orqali qayd
etiladi. Uzoq muddatli saqlash [Arxivlash siyosati](/uz/about/archiving/) asosida
amalga oshiriladi.

## Tahririyat

Tahririyat mualliflar va taqrizchilarning murojaatlariga uch ish kuni ichida javob
beradi. Aloqa maʼlumotlari [Bogʻlanish](/uz/about/contact/) sahifasida. Shikoyat va
apellyatsiyalar [Nashr etikasi](/uz/about/publication-ethics/) bayonotidagi tartibda
koʻrib chiqiladi.""",
            "ru": """**«АЛГОРИТМ» — обзор экономических исследований** — международный
рецензируемый научный журнал открытого доступа, публикующий оригинальные исследования
по экономике. Журнал выходит ежемесячно и принимает рукописи на английском, узбекском
и русском языках.

## Что мы публикуем

Мы публикуем эмпирические и теоретические работы, методологически корректные, ясно
написанные и значимые за пределами одной страны. Исследования Узбекистана, Центральной
Азии и других развивающихся экономик особенно приветствуются, если поставленные вопросы
и применённые методы представляют международный интерес. Полное описание рубрик — на
странице [Цели и тематика](/ru/about/aims-and-scope/).

## Как мы работаем

Каждая рукопись проходит редакционный отбор по соответствию тематике, структуре и
уровню заимствований, после чего направляется не менее чем двум независимым
рецензентам по **двойной слепой** процедуре: рецензенты не знают авторов, авторы не
знают рецензентов. Наша цель — первое решение в течение восьми недель с момента
подачи. Каждый этап и его типичная продолжительность описаны на странице
[Процесс рецензирования](/ru/about/peer-review/).

## Открытый доступ без оплаты

Журнал работает по модели **diamond open access**. Авторы не платят ничего — нет платы
за обработку статьи, за подачу, за страницы или цветную печать; читатели также не
платят. Статьи публикуются под
[лицензией Creative Commons Attribution 4.0](/ru/about/open-access/), авторское право
остаётся у авторов.

## Идентификаторы и инфраструктура

Каждая статья получает DOI, зарегистрированный в Crossref, снабжается структурированными
метаданными для Google Scholar и Schema.org и доступна для сбора через интерфейс
OAI-PMH. Идентификация авторов ведётся через ORCID. Долгосрочное хранение описано в
[Политике архивирования](/ru/about/archiving/).

## Редакция

Редакция отвечает на обращения авторов и рецензентов в течение трёх рабочих дней.
Контакты — на странице [Контакты](/ru/about/contact/). Жалобы и апелляции
рассматриваются в порядке, изложенном в
[Заявлении об издательской этике](/ru/about/publication-ethics/).""",
        },
    },
    # -------------------------------------------------------- aims and scope
    {
        "slug": "aims-and-scope",
        "menu_group": "about",
        "order": 2,
        "title": {"en": "Aims & Scope", "uz": "Maqsad va yoʻnalishlar", "ru": "Цели и тематика"},
        "seo": {
            "en": "The journal publishes rigorous empirical and theoretical economics with international relevance, including research on Uzbekistan and Central Asia.",
            "uz": "Jurnal xalqaro ahamiyatga ega puxta empirik va nazariy iqtisodiy tadqiqotlarni, jumladan Oʻzbekiston va Markaziy Osiyoga oid ishlarni chop etadi.",
            "ru": "Журнал публикует строгие эмпирические и теоретические исследования по экономике, имеющие международное значение, включая работы по Узбекистану и Центральной Азии.",
        },
        "body": {
            "en": """The journal exists to raise the visibility and the methodological standard of
economic research produced in and about emerging economies, and to make that research
freely available to the international scholarly community.

We publish original studies that make a defensible contribution to economic knowledge:
work that states a clear research question, situates it in the international literature,
uses data and methods appropriate to the question, reports results transparently
(including negative or inconclusive ones), and draws conclusions the evidence supports.
We do not privilege any particular school of thought or any particular method:
econometric, experimental, computational, historical and carefully argued theoretical
work are all in scope.

Research on **Uzbekistan, Central Asia and other emerging and transition economies** is
explicitly welcome. Such papers must, however, be written for an international readership:
the question must be motivated by the wider literature, the institutional context must be
explained to a reader who does not know it, and the findings must be interpreted in terms
that travel beyond the country studied.

## Sections

1. **Economic Theory & Methodology** — microeconomic and macroeconomic theory,
   econometric methodology, philosophy and history of economics.
2. **Macroeconomics, Monetary & Fiscal Policy** — growth, inflation, business cycles,
   monetary and exchange-rate policy, fiscal rules, debt sustainability.
3. **Public Finance, Taxation & Customs** — tax design and administration, public
   expenditure, intergovernmental finance, customs and trade facilitation.
4. **International Trade & Economic Integration** — trade flows and policy, regional
   integration, global value chains, foreign direct investment.
5. **Finance, Banking & Investment** — financial markets and intermediaries, banking
   regulation, corporate finance, financial inclusion, capital markets.
6. **Digital Economy, Innovation & Data-Driven Analysis** — digitalisation of firms and
   government, e-commerce, platform economics, innovation systems, applications of
   machine learning to economic questions.
7. **Regional, Sectoral & Development Economics** — regional disparities, agriculture,
   energy, transport, poverty and inequality, development programme evaluation.
8. **Management, Entrepreneurship & Labour Economics** — firm performance and strategy,
   entrepreneurship, human capital, labour markets, migration.

A ninth, non-research section — **Reviews & Commentary** — carries review articles,
book reviews and invited commentary. Contributions to it are edited but are not counted
as original research articles.

## What is out of scope

* Purely descriptive reports without a research question or an identification strategy.
* Policy advocacy that is not supported by evidence presented in the paper.
* Work in adjacent disciplines (law, political science, pedagogy, information technology)
  with no substantive economic analysis.
* Manuscripts that duplicate work already published elsewhere, in any language.
* Student coursework, project reports and consultancy deliverables in their original form.

If you are unsure whether your manuscript is in scope, write to the editorial office
with the title and abstract before submitting; we answer within three working days.""",
            "uz": """Jurnalning maqsadi — rivojlanayotgan iqtisodiyotlarda va ular haqida yaratilgan
iqtisodiy tadqiqotlarning koʻrinuvchanligi va metodologik darajasini oshirish hamda bu
tadqiqotlarni xalqaro ilmiy hamjamiyat uchun bepul ochiq qilish.

Biz iqtisodiy bilimga asosli hissa qoʻshadigan original tadqiqotlarni chop etamiz: aniq
tadqiqot savoli qoʻyilgan, xalqaro adabiyot kontekstida joylashtirilgan, savolga mos
maʼlumot va usullar qoʻllanilgan, natijalari shaffof (jumladan salbiy yoki noaniq
natijalar ham) keltirilgan va xulosalari dalillar bilan asoslangan ishlar. Biz biror
maktab yoki usulga ustunlik bermaymiz: ekonometrik, eksperimental, hisoblash, tarixiy
va puxta asoslangan nazariy ishlar bir xilda koʻrib chiqiladi.

**Oʻzbekiston, Markaziy Osiyo va boshqa rivojlanayotgan hamda oʻtish davridagi
iqtisodiyotlar** boʻyicha tadqiqotlar alohida qoʻllab-quvvatlanadi. Ammo bunday
maqolalar xalqaro oʻquvchi uchun yozilishi kerak: savol keng adabiyot bilan
asoslanishi, institutsional kontekst uni bilmaydigan oʻquvchiga tushuntirilishi va
natijalar oʻrganilgan mamlakat doirasidan tashqarida ham maʼnoli boʻlishi lozim.

## Boʻlimlar

1. **Iqtisodiy nazariya va metodologiya** — mikro va makroiqtisodiy nazariya,
   ekonometrik metodologiya, iqtisodiyot falsafasi va tarixi.
2. **Makroiqtisodiyot, pul-kredit va fiskal siyosat** — oʻsish, inflyatsiya, biznes
   sikllari, pul va valyuta siyosati, fiskal qoidalar, qarz barqarorligi.
3. **Davlat moliyasi, soliqlar va bojxona** — soliq tizimi va maʼmuriyati, davlat
   xarajatlari, byudjetlararo munosabatlar, bojxona va savdoni soddalashtirish.
4. **Xalqaro savdo va iqtisodiy integratsiya** — savdo oqimlari va siyosati, mintaqaviy
   integratsiya, global qiymat zanjirlari, toʻgʻridan-toʻgʻri xorijiy investitsiyalar.
5. **Moliya, bank ishi va investitsiyalar** — moliya bozorlari va vositachilari, bank
   tartibga solish, korporativ moliya, moliyaviy qamrov, kapital bozorlari.
6. **Raqamli iqtisodiyot, innovatsiya va maʼlumotlarga asoslangan tahlil** —
   korxonalar va davlat boshqaruvining raqamlashuvi, elektron tijorat, platforma
   iqtisodiyoti, innovatsion tizimlar, mashinali oʻqitishning iqtisodiy masalalarga
   qoʻllanishi.
7. **Hududiy, tarmoq va rivojlanish iqtisodiyoti** — hududiy tafovutlar, qishloq
   xoʻjaligi, energetika, transport, qashshoqlik va tengsizlik, rivojlanish
   dasturlarini baholash.
8. **Menejment, tadbirkorlik va mehnat iqtisodiyoti** — korxona samaradorligi va
   strategiyasi, tadbirkorlik, inson kapitali, mehnat bozorlari, migratsiya.

Toʻqqizinchi, ilmiy tadqiqot boʻlmagan boʻlim — **Sharhlar va mulohazalar** — sharh
maqolalari, kitob taqrizlari va taklif etilgan mulohazalarni chop etadi. Ularga
tahririy ishlov beriladi, lekin original ilmiy maqola sifatida hisoblanmaydi.

## Yoʻnalishga kirmaydigan ishlar

* Tadqiqot savoli yoki identifikatsiya strategiyasisiz sof tavsifiy hisobotlar.
* Maqolada keltirilgan dalillar bilan asoslanmagan siyosiy targʻibot.
* Iqtisodiy tahlilsiz qoʻshni sohalardagi (huquq, siyosatshunoslik, pedagogika,
  axborot texnologiyalari) ishlar.
* Boshqa joyda, istalgan tilda allaqachon chop etilgan ishning takrori.
* Talaba kurs ishlari, loyiha hisobotlari va konsalting hujjatlari asl holida.

Agar qoʻlyozmangiz yoʻnalishga mosligiga ishonchingiz komil boʻlmasa, yuborishdan oldin
sarlavha va annotatsiyani tahririyatga yuboring; biz uch ish kuni ichida javob
beramiz.""",
            "ru": """Цель журнала — повысить видимость и методологический уровень экономических
исследований, выполненных в развивающихся экономиках и о них, и сделать эти
исследования свободно доступными международному научному сообществу.

Мы публикуем оригинальные работы, вносящие обоснованный вклад в экономическое знание:
работы с ясно поставленным исследовательским вопросом, помещённым в контекст
международной литературы, с данными и методами, адекватными вопросу, с прозрачным
изложением результатов (включая отрицательные и неопределённые) и с выводами, которые
подтверждаются доказательствами. Мы не отдаём предпочтения какой-либо школе или методу:
эконометрические, экспериментальные, вычислительные, исторические и строго
аргументированные теоретические работы рассматриваются на равных.

Исследования по **Узбекистану, Центральной Азии и другим развивающимся и переходным
экономикам** особо приветствуются. Однако такие статьи должны быть написаны для
международного читателя: вопрос должен быть мотивирован широкой литературой,
институциональный контекст — объяснён читателю, который с ним не знаком, а результаты —
интерпретированы так, чтобы они имели значение за пределами изучаемой страны.

## Рубрики

1. **Экономическая теория и методология** — микро- и макроэкономическая теория,
   эконометрическая методология, философия и история экономической науки.
2. **Макроэкономика, денежно-кредитная и фискальная политика** — рост, инфляция,
   деловые циклы, денежная и курсовая политика, фискальные правила, устойчивость долга.
3. **Государственные финансы, налоги и таможня** — устройство и администрирование
   налогов, государственные расходы, межбюджетные отношения, таможня и упрощение
   торговых процедур.
4. **Международная торговля и экономическая интеграция** — торговые потоки и политика,
   региональная интеграция, глобальные цепочки создания стоимости, прямые иностранные
   инвестиции.
5. **Финансы, банковское дело и инвестиции** — финансовые рынки и посредники,
   банковское регулирование, корпоративные финансы, финансовая доступность, рынки
   капитала.
6. **Цифровая экономика, инновации и анализ данных** — цифровизация компаний и
   государственного управления, электронная коммерция, экономика платформ, инновационные
   системы, применение машинного обучения к экономическим задачам.
7. **Региональная, отраслевая экономика и экономика развития** — региональные различия,
   сельское хозяйство, энергетика, транспорт, бедность и неравенство, оценка программ
   развития.
8. **Менеджмент, предпринимательство и экономика труда** — результативность и стратегия
   фирмы, предпринимательство, человеческий капитал, рынки труда, миграция.

Девятая, ненаучная рубрика — **Обзоры и комментарии** — содержит обзорные статьи,
рецензии на книги и приглашённые комментарии. Они проходят редакционную подготовку, но
не считаются оригинальными научными статьями.

## Что вне тематики

* Чисто описательные отчёты без исследовательского вопроса и стратегии идентификации.
* Политическая адвокация, не подкреплённая приведёнными в статье доказательствами.
* Работы смежных дисциплин (право, политология, педагогика, информационные технологии)
  без содержательного экономического анализа.
* Рукописи, дублирующие уже опубликованные работы на любом языке.
* Студенческие курсовые, проектные отчёты и консалтинговые документы в исходном виде.

Если вы не уверены, соответствует ли рукопись тематике, напишите в редакцию название и
аннотацию до подачи; мы ответим в течение трёх рабочих дней.""",
        },
    },
    # ----------------------------------------------------------- peer review
    {
        "slug": "peer-review",
        "menu_group": "about",
        "order": 3,
        "title": {"en": "Peer Review Process", "uz": "Taqriz jarayoni", "ru": "Процесс рецензирования"},
        "seo": {
            "en": "Double-blind peer review with at least two reviewers, screening within 7 days and a first decision within 8 weeks.",
            "uz": "Kamida ikki taqrizchi ishtirokidagi ikki tomonlama yashirin taqriz; dastlabki koʻrik 7 kun, birinchi qaror 8 hafta ichida.",
            "ru": "Двойное слепое рецензирование не менее чем двумя рецензентами: отбор — 7 дней, первое решение — 8 недель.",
        },
        "body": {
            "en": """All research articles published by the journal are peer reviewed under a
**double-blind** procedure. Reviewers are not told who the authors are; authors are never
told who the reviewers are. Editorial material (editorials, book reviews and invited
commentary) is reviewed by the editors and is labelled as such on the article page.

## The steps and how long they take

| # | Step | Who | Typical duration |
|---|---|---|---|
| 1 | Technical check and editorial screening | Managing editor, section editor | ≤ 7 days |
| 2 | Similarity check | Editorial office | included in step 1 |
| 3 | Reviewer invitation and acceptance | Section editor | 3–10 days |
| 4 | Review | 2 or more reviewers | 21 days |
| 5 | Recommendation and decision | Section editor, Editor-in-Chief | 7 days |
| **—** | **Submission to first decision** | | **≤ 8 weeks** |
| 6 | Revision (minor / major) | Authors | 30 / 60 days |
| 7 | Re-review, if required | Original reviewers where possible | 14 days |
| 8 | Production: copyediting, proof, typesetting | Production editor, authors | 2–4 weeks |
| 9 | Online First publication with DOI | Production editor | 1–3 days after acceptance of the proof |

## Screening

The editor checks that the manuscript is within scope, is structured as required, has
complete trilingual metadata, is properly anonymised, and passes the similarity check.
A manuscript may be **desk rejected** at this stage — most often for being out of scope,
for lacking a research question, or for a similarity level above our threshold. A desk
rejection is communicated with a short reason within seven days, so that authors lose no
time.

## Choosing reviewers

Reviewers are selected for subject expertise, methodological competence and absence of
conflict of interest. Suggested reviewers proposed by the authors may be used, but never
exclusively, and the editor always adds at least one reviewer of their own choosing.
A reviewer must decline if they have co-authored with an author in the last three years,
share an institution with them, have a financial interest in the outcome, or feel unable
to be impartial for any other reason.

## What reviewers are asked

Reviewers complete a structured form scoring the manuscript from 1 to 5 on originality,
relevance to scope, methodological rigour, data and results, coverage of the literature,
and writing and structure, and then write free-text comments to the authors and, if they
wish, confidential comments to the editor. They finish with a recommendation: accept,
minor revision, major revision, or reject. Full guidance is on the
[Reviewer Guidelines](/en/for-reviewers/) page.

## Decisions

The section editor makes a recommendation; the Editor-in-Chief takes the final decision.
Possible decisions are **accept**, **minor revision**, **major revision**, **reject**,
and **reject with resubmission encouraged**. A decision letter always includes the
reviewers' comments to the authors. Where two reviewers disagree substantially, a third
reviewer is invited before a decision is taken.

## Appeals

An author who believes a decision rests on a factual error or on a demonstrable
misunderstanding may appeal once, in writing, to the Editor-in-Chief within 30 days,
stating specifically what was misunderstood. Appeals are answered within 30 days. The
decision on an appeal is final. Appealing does not entitle the author to a new round of
review, and a manuscript under appeal must not be submitted elsewhere.

## Confidentiality

A submitted manuscript is a confidential document. Reviewers and editors must not share
it, cite it, or use its content before publication, and must not upload it to any
generative-AI service — see the [AI Policy](/en/about/ai-policy/).""",
            "uz": """Jurnalda chop etiladigan barcha ilmiy maqolalar **ikki tomonlama yashirin**
tartibda taqrizdan oʻtkaziladi. Taqrizchilarga mualliflar kim ekani aytilmaydi;
mualliflarga esa taqrizchilar hech qachon oshkor qilinmaydi. Tahririy materiallar
(bosh maqola, kitob taqrizlari, taklif etilgan mulohazalar) muharrirlar tomonidan koʻrib
chiqiladi va maqola sahifasida shunday belgilanadi.

## Bosqichlar va muddatlar

| # | Bosqich | Kim bajaradi | Odatdagi muddat |
|---|---|---|---|
| 1 | Texnik va tahririy koʻrik | Masʼul kotib, boʻlim muharriri | ≤ 7 kun |
| 2 | Oʻxshashlikni tekshirish | Tahririyat | 1-bosqich ichida |
| 3 | Taqrizchini taklif qilish va roziligi | Boʻlim muharriri | 3–10 kun |
| 4 | Taqriz | 2 yoki undan ortiq taqrizchi | 21 kun |
| 5 | Tavsiya va qaror | Boʻlim muharriri, Bosh muharrir | 7 kun |
| **—** | **Yuborishdan birinchi qarorgacha** | | **≤ 8 hafta** |
| 6 | Qayta ishlash (kichik / katta) | Mualliflar | 30 / 60 kun |
| 7 | Zarur boʻlsa qayta taqriz | Imkon qadar oʻsha taqrizchilar | 14 kun |
| 8 | Nashrga tayyorlash: tahrir, korrektura, sahifalash | Nashr muharriri, mualliflar | 2–4 hafta |
| 9 | DOI bilan Online First eʼloni | Nashr muharriri | korrektura tasdiqlangach 1–3 kun |

## Dastlabki koʻrik

Muharrir qoʻlyozmaning yoʻnalishga mosligini, talab qilingan tuzilishga egaligini,
uch tilli metamaʼlumotlarning toʻliqligini, anonimlashtirilganini va oʻxshashlik
tekshiruvidan oʻtganini tekshiradi. Shu bosqichda qoʻlyozma **muharrir tomonidan rad
etilishi** mumkin — koʻpincha yoʻnalishga mos emasligi, tadqiqot savoli yoʻqligi yoki
oʻxshashlik darajasi belgilangan chegaradan yuqoriligi sababli. Bunday rad etish qisqa
izoh bilan yetti kun ichida bildiriladi, shunda muallif vaqt yoʻqotmaydi.

## Taqrizchilarni tanlash

Taqrizchilar mavzu boʻyicha bilimi, metodologik salohiyati va manfaatlar toʻqnashuvi
yoʻqligi asosida tanlanadi. Mualliflar tavsiya etgan taqrizchilardan foydalanish mumkin,
lekin faqat ulardan emas: muharrir har doim oʻzi tanlagan kamida bitta taqrizchini
qoʻshadi. Taqrizchi soʻnggi uch yilda muallif bilan hammuallif boʻlgan, u bilan bir
muassasada ishlaydigan, natijadan moliyaviy manfaatdor yoki boshqa sababga koʻra
xolis boʻla olmasa, taklifni rad etishi shart.

## Taqrizchidan nima soʻraladi

Taqrizchi tuzilmali shaklni toʻldiradi: originallik, yoʻnalishga muvofiqlik, metodologik
puxtalik, maʼlumot va natijalar, adabiyot qamrovi hamda yozilish va tuzilish boʻyicha
1 dan 5 gacha baho qoʻyadi, soʻng mualliflarga erkin matnli izohlar va istasa muharrirga
maxfiy izohlar yozadi. Yakunda tavsiya beradi: qabul qilish, kichik qayta ishlash, katta
qayta ishlash yoki rad etish. Toʻliq yoʻriqnoma
[Taqrizchilar uchun](/uz/for-reviewers/) sahifasida.

## Qarorlar

Boʻlim muharriri tavsiya beradi; yakuniy qarorni Bosh muharrir qabul qiladi. Mumkin
boʻlgan qarorlar: **qabul qilish**, **kichik qayta ishlash**, **katta qayta ishlash**,
**rad etish** va **qayta yuborish tavsiyasi bilan rad etish**. Qaror xatiga har doim
taqrizchilarning mualliflarga yozgan izohlari ilova qilinadi. Ikki taqrizchi jiddiy
darajada kelishmasa, qaror qabul qilishdan oldin uchinchi taqrizchi taklif etiladi.

## Apellyatsiya

Qaror faktik xato yoki isbotlanadigan notoʻgʻri tushunishga asoslangan deb hisoblagan
muallif 30 kun ichida Bosh muharrirga bir marta yozma apellyatsiya bera oladi va nima
notoʻgʻri tushunilganini aniq koʻrsatishi kerak. Apellyatsiyaga 30 kun ichida javob
beriladi. Apellyatsiya boʻyicha qaror yakuniy hisoblanadi. Apellyatsiya yangi taqriz
bosqichiga huquq bermaydi va koʻrib chiqilayotgan qoʻlyozma boshqa jurnalga yuborilmasligi
kerak.

## Maxfiylik

Yuborilgan qoʻlyozma maxfiy hujjatdir. Taqrizchilar va muharrirlar uni chop etilishidan
oldin boshqalarga bermasligi, iqtibos keltirmasligi va mazmunidan foydalanmasligi, hech
qanday generativ sunʼiy intellekt xizmatiga yuklamasligi shart —
[SI siyosati](/uz/about/ai-policy/) ga qarang.""",
            "ru": """Все научные статьи журнала проходят рецензирование по **двойной слепой**
процедуре. Рецензентам не сообщают, кто авторы; авторам никогда не сообщают, кто
рецензенты. Редакционные материалы (редакционные статьи, рецензии на книги, приглашённые
комментарии) рассматриваются редакторами и помечаются на странице статьи.

## Этапы и сроки

| № | Этап | Кто выполняет | Типичный срок |
|---|---|---|---|
| 1 | Техническая и редакционная проверка | Ответственный секретарь, редактор рубрики | ≤ 7 дней |
| 2 | Проверка на заимствования | Редакция | в рамках этапа 1 |
| 3 | Приглашение рецензента и согласие | Редактор рубрики | 3–10 дней |
| 4 | Рецензирование | 2 и более рецензентов | 21 день |
| 5 | Рекомендация и решение | Редактор рубрики, главный редактор | 7 дней |
| **—** | **От подачи до первого решения** | | **≤ 8 недель** |
| 6 | Доработка (малая / существенная) | Авторы | 30 / 60 дней |
| 7 | Повторное рецензирование при необходимости | По возможности те же рецензенты | 14 дней |
| 8 | Подготовка: редактирование, корректура, вёрстка | Выпускающий редактор, авторы | 2–4 недели |
| 9 | Публикация Online First с DOI | Выпускающий редактор | 1–3 дня после утверждения корректуры |

## Редакционный отбор

Редактор проверяет соответствие тематике, требуемую структуру, полноту трёхъязычных
метаданных, анонимизацию файла и результат проверки на заимствования. На этом этапе
рукопись может быть **отклонена редактором** — чаще всего из-за несоответствия тематике,
отсутствия исследовательского вопроса или превышения порога заимствований. Такое решение
сообщается с кратким обоснованием в течение семи дней, чтобы автор не терял время.

## Выбор рецензентов

Рецензенты подбираются по предметной экспертизе, методологической компетентности и
отсутствию конфликта интересов. Предложенные авторами рецензенты могут привлекаться, но
никогда исключительно: редактор всегда добавляет как минимум одного рецензента по
собственному выбору. Рецензент обязан отказаться, если за последние три года был
соавтором автора, работает в той же организации, имеет финансовый интерес в результате
или по иной причине не может быть беспристрастным.

## О чём спрашивают рецензента

Рецензент заполняет структурированную форму, оценивая рукопись по шкале от 1 до 5 по
оригинальности, соответствию тематике, методологической строгости, данным и результатам,
охвату литературы, а также изложению и структуре, затем пишет комментарии авторам и, при
желании, конфиденциальные комментарии редактору. В завершение даётся рекомендация:
принять, малая доработка, существенная доработка или отклонить. Полное руководство — на
странице [Для рецензентов](/ru/for-reviewers/).

## Решения

Редактор рубрики даёт рекомендацию; окончательное решение принимает главный редактор.
Возможные решения: **принять**, **малая доработка**, **существенная доработка**,
**отклонить**, **отклонить с предложением повторной подачи**. К письму с решением всегда
прилагаются комментарии рецензентов авторам. При существенном расхождении двух
рецензентов до принятия решения привлекается третий.

## Апелляции

Автор, считающий, что решение основано на фактической ошибке или доказуемом
недопонимании, может однократно подать письменную апелляцию главному редактору в течение
30 дней, конкретно указав, что было понято неверно. Ответ даётся в течение 30 дней.
Решение по апелляции окончательно. Апелляция не даёт права на новый раунд рецензирования,
а рукопись, находящаяся на апелляции, не должна подаваться в другие журналы.

## Конфиденциальность

Поданная рукопись — конфиденциальный документ. Рецензенты и редакторы не вправе
передавать её, цитировать или использовать её содержание до публикации и не должны
загружать её в какие-либо сервисы генеративного ИИ — см.
[Политику в отношении ИИ](/ru/about/ai-policy/).""",
        },
    },
]
