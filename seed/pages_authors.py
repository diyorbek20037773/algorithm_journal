"""Author hub, guidelines, checklist, templates and reviewer guidelines."""

from __future__ import annotations

from typing import Any

AUTHOR_PAGES: list[dict[str, Any]] = [
    {
        "slug": "for-authors",
        "menu_group": "authors",
        "order": 1,
        "title": {"en": "For Authors", "uz": "Mualliflar uchun", "ru": "Авторам"},
        "seo": {
            "en": "Everything you need to prepare and submit a manuscript: scope, guidelines, checklist, submission and what happens next.",
            "uz": "Qoʻlyozmani tayyorlash va yuborish uchun kerak boʻlgan hamma narsa: yoʻnalish, yoʻriqnoma, tekshiruv roʻyxati, yuborish va keyingi bosqichlar.",
            "ru": "Всё необходимое для подготовки и подачи рукописи: тематика, руководство, чек-лист, подача и что происходит дальше.",
        },
        "body": {
            "en": """Publishing with us costs nothing, takes five steps to submit, and normally
produces a first decision within eight weeks. This page is the map; the detailed rules are
in the [Author Guidelines](/en/for-authors/guidelines/).

## Frequently asked questions

**In which language should I write?**
English, Uzbek or Russian. Whatever the language of the article, the title, abstract and
keywords must be supplied in English, Uzbek and Russian; the Uzbek Cyrillic version is
generated automatically and can be corrected. English-language articles reach the widest
readership and are what indexing databases assess.

**How long should the article be?**
A research article is 4,000–10,000 words including everything except the reference list.
A short communication is 2,000–4,000 words. Review articles may be longer by arrangement
with the editor.

**Do I need to anonymise my manuscript?**
Yes. The manuscript file must contain no author names, affiliations, acknowledgements,
funding details or self-identifying phrases such as "as we showed in our earlier work
(Author, 2023)". All identifying information goes on the separate title page. Remember to
clear the document properties in Word or LibreOffice as well.

**Can I suggest reviewers?**
Yes, and it helps — but the editor is never bound by your suggestions and always adds at
least one independent reviewer. You may also name people who should not review your work,
with a short reason.

**What happens after I submit?**
You receive a reference number of the form `ARER-2026-0001` and can follow every step in
your dashboard. Screening takes up to seven days, review 21 days, and the first decision
normally arrives within eight weeks.

**Will I have to pay anything?**
No. See [Article Processing Charges](/en/about/fees/).

**Can I publish before the issue appears?**
Yes. Accepted articles are published **Online First** with a DOI as soon as production
finishes, and are fully citable from that moment. Volume, issue and page numbers are added
later without changing the DOI.

**Can I withdraw my manuscript?**
Yes, at any point before acceptance, from your dashboard, stating a reason. Please do not
withdraw simply because review is taking a few days longer than expected — write to the
editor instead.

## After publication

You may deposit any version of the article in any repository with no embargo, translate
it, reuse it in teaching, and include it in your thesis — you keep the copyright. Please
cite the published version by DOI so that citations accumulate against the record.""",
            "uz": """Bizda chop etish bepul, yuborish besh bosqichdan iborat va birinchi qaror odatda
sakkiz hafta ichida bildiriladi. Bu sahifa — yoʻl xaritasi; batafsil qoidalar
[Mualliflar uchun yoʻriqnoma](/uz/for-authors/guidelines/) sahifasida.

## Koʻp beriladigan savollar

**Qaysi tilda yozish kerak?**
Ingliz, oʻzbek yoki rus tilida. Maqola tilidan qatʼi nazar, sarlavha, annotatsiya va
kalit soʻzlar ingliz, oʻzbek va rus tillarida taqdim etilishi shart; oʻzbek kirill
varianti avtomatik yaratiladi va tuzatilishi mumkin. Ingliz tilidagi maqolalar eng keng
auditoriyaga yetadi va indeksatsiya bazalari aynan ularni baholaydi.

**Maqola qanchalik uzun boʻlishi kerak?**
Ilmiy maqola — adabiyotlar roʻyxatidan tashqari 4 000–10 000 soʻz. Qisqa maʼlumot —
2 000–4 000 soʻz. Sharh maqolalari muharrir bilan kelishilgan holda uzunroq boʻlishi
mumkin.

**Qoʻlyozmani anonimlashtirish kerakmi?**
Ha. Qoʻlyozma faylida mualliflar ismi, ish joyi, minnatdorchilik, moliyalashtirish
maʼlumotlari va «avvalgi ishimizda koʻrsatganimizdek (Muallif, 2023)» kabi oʻzini
oshkor qiluvchi iboralar boʻlmasligi kerak. Barcha identifikatsiya maʼlumotlari alohida
sarlavha sahifasida keltiriladi. Word yoki LibreOffice hujjat xossalarini ham tozalashni
unutmang.

**Taqrizchi tavsiya qila olamanmi?**
Ha, bu foydali — lekin muharrir sizning tavsiyangiz bilan bogʻlanib qolmaydi va har doim
kamida bitta mustaqil taqrizchi qoʻshadi. Ishingizni taqriz qilmasligi kerak boʻlgan
shaxslarni ham qisqa izoh bilan koʻrsatishingiz mumkin.

**Yuborgandan keyin nima boʻladi?**
Siz `ARER-2026-0001` koʻrinishidagi raqam olasiz va har bir bosqichni boshqaruv panelida
kuzatasiz. Dastlabki koʻrik yetti kungacha, taqriz 21 kun, birinchi qaror odatda sakkiz
hafta ichida keladi.

**Biror toʻlov qilishim kerakmi?**
Yoʻq. [Maqolani qayta ishlash toʻlovlari](/uz/about/fees/) sahifasiga qarang.

**Son chiqmasidan oldin chop eta olamanmi?**
Ha. Qabul qilingan maqolalar nashrga tayyorlash tugagach **Online First** sifatida DOI
bilan chop etiladi va shu lahzadan iqtibos qilinadi. Jild, son va sahifa raqamlari
keyinroq, DOI oʻzgarmagan holda qoʻshiladi.

**Qoʻlyozmani qaytarib ola olamanmi?**
Ha, qabul qilinishidan oldingi istalgan vaqtda boshqaruv panelidan, sababini koʻrsatib.
Taqriz kutilganidan bir necha kun uzoqroq davom etayotgani uchun qaytarib olmang — avval
muharrirga yozing.

## Chop etilgandan keyin

Maqolaning istalgan variantini istalgan repozitoriyga embargosiz joylashtirishingiz,
tarjima qilishingiz, oʻqitishda foydalanishingiz va dissertatsiyangizga kiritishingiz
mumkin — mualliflik huquqi sizda qoladi. Iqtiboslar yozuvga jamlanishi uchun chop etilgan
variantni DOI orqali iqtibos qiling.""",
            "ru": """Публикация у нас бесплатна, подача занимает пять шагов, а первое решение обычно
приходит в течение восьми недель. Эта страница — карта; подробные правила — в
[Руководстве для авторов](/ru/for-authors/guidelines/).

## Частые вопросы

**На каком языке писать?**
На английском, узбекском или русском. Независимо от языка статьи название, аннотация и
ключевые слова должны быть представлены на английском, узбекском и русском; узбекская
кириллическая версия создаётся автоматически и может быть исправлена. Англоязычные статьи
охватывают самую широкую аудиторию, и именно их оценивают базы индексации.

**Каким должен быть объём?**
Научная статья — 4 000–10 000 слов без списка литературы. Краткое сообщение —
2 000–4 000 слов. Обзорные статьи по согласованию с редактором могут быть больше.

**Нужно ли обезличивать рукопись?**
Да. Файл рукописи не должен содержать имён авторов, мест работы, благодарностей, сведений
о финансировании и самоидентифицирующих фраз вроде «как мы показали в предыдущей работе
(Автор, 2023)». Все идентифицирующие сведения указываются на отдельном титульном листе.
Не забудьте очистить свойства документа в Word или LibreOffice.

**Могу ли я предложить рецензентов?**
Да, и это помогает — но редактор не связан вашими предложениями и всегда добавляет как
минимум одного независимого рецензента. Вы также можете указать тех, кто не должен
рецензировать вашу работу, с кратким обоснованием.

**Что происходит после подачи?**
Вы получаете номер вида `ARER-2026-0001` и можете следить за каждым шагом в личном
кабинете. Отбор занимает до семи дней, рецензирование — 21 день, первое решение обычно
приходит в течение восьми недель.

**Придётся ли платить?**
Нет. См. [Плата за публикацию](/ru/about/fees/).

**Можно ли опубликоваться до выхода выпуска?**
Да. Принятые статьи публикуются как **Online First** с DOI сразу после завершения
подготовки и с этого момента полностью цитируемы. Том, выпуск и страницы добавляются
позже без изменения DOI.

**Можно ли отозвать рукопись?**
Да, в любой момент до принятия — из личного кабинета, с указанием причины. Не отзывайте
рукопись только потому, что рецензирование идёт на несколько дней дольше ожидаемого —
сначала напишите редактору.

## После публикации

Вы можете разместить любую версию статьи в любом репозитории без эмбарго, перевести её,
использовать в преподавании и включить в диссертацию — авторское право остаётся у вас.
Цитируйте опубликованную версию по DOI, чтобы цитирования накапливались на записи.""",
        },
    },
    {
        "slug": "author-guidelines",
        "menu_group": "authors",
        "order": 2,
        "title": {
            "en": "Author Guidelines",
            "uz": "Mualliflar uchun yoʻriqnoma",
            "ru": "Руководство для авторов",
        },
        "seo": {
            "en": "Article types, structure, trilingual abstracts, keywords, JEL codes, APA 7 references, figures, anonymisation and submission steps.",
            "uz": "Maqola turlari, tuzilishi, uch tilli annotatsiya, kalit soʻzlar, JEL kodlari, APA 7 adabiyotlar, rasmlar, anonimlashtirish va yuborish bosqichlari.",
            "ru": "Типы статей, структура, трёхъязычные аннотации, ключевые слова, коды JEL, ссылки APA 7, рисунки, обезличивание и порядок подачи.",
        },
        "body": {
            "en": """Read these guidelines before you prepare your manuscript. Submissions that do not
follow them are returned without review, which costs everyone time.

## Article types

| Type | Length (excluding references) | Abstract | Notes |
|---|---|---|---|
| Research article | 4,000–10,000 words | 150–250 words | the standard format; IMRaD structure |
| Review article | 6,000–12,000 words | 150–250 words | systematic or critical review; state the search strategy |
| Short communication | 2,000–4,000 words | 100–150 words | a single, well-defined result |
| Book review | 1,000–2,000 words | none | commissioned or proposed to the editor |

## Structure

Research articles follow **IMRaD**:

1. **Introduction** — the research question, why it matters, what is new here, and how the
   paper is organised.
2. **Literature review** — what is already known, and the specific gap this paper fills.
   Cite international literature, not only regional sources.
3. **Methodology** — data sources, sample, variables, model specification, identification
   strategy, software. Enough detail for the work to be reproduced.
4. **Results** — findings with tables and figures; report estimates with standard errors,
   sample sizes and diagnostic tests.
5. **Discussion** — interpretation, comparison with earlier findings, mechanisms,
   limitations. Do not overstate causality.
6. **Conclusion** — answers to the research question, policy implications where warranted,
   and directions for further work.

Then, in order: acknowledgements, funding statement, conflict-of-interest statement, data
availability statement, AI use statement, references, appendices.

## Trilingual metadata

Title, abstract and keywords are mandatory in **English, Uzbek (Latin) and Russian**. The
Uzbek Cyrillic version is generated by transliteration in the submission system and may be
edited. The abstract must be 150–250 words, must be a single paragraph without citations
or abbreviations, and must state the purpose, the data and method, the main result and the
conclusion. Provide **5–8 keywords** per language, not repeating words from the title where
avoidable.

## JEL codes

Choose **1–5** codes from the [JEL classification](/en/jel/). Put the most specific
applicable code first. Codes are used for browsing, for reviewer matching and by indexing
services.

## References

Use **APA 7th edition**. Every in-text citation must have a reference entry and every
reference must be cited. Include a **DOI** as `https://doi.org/10.xxxx/yyyy` wherever one
exists. A research article normally has at least 25 references, of which a substantial part
should be from the last five years and from international journals.

Non-Latin sources must be given in Latin transliteration, followed by an English
translation of the title in square brackets and the language in parentheses:

> Karimov, A. A. (2023). Raqamli iqtisodiyot va mehnat bozori [The digital economy and the
> labour market]. *Iqtisodiyot va Taʼlim*, 24(3), 45–58. (in Uzbek)

## Figures and tables

Number figures and tables consecutively and refer to each in the text. Give every table a
caption above it and every figure a caption below it, both self-explanatory. Do not use
colour as the only way of distinguishing series. Supply figures at a minimum of 300 dpi, or
as vector files. State units and the source of every table and figure. Do not paste images
of tables — tables must be real, selectable text.

## Units, numbers and language

Use SI units. Use a full stop as the decimal separator in English text. Report currency
amounts with the currency and, where relevant, the exchange rate and date used. Define
every abbreviation at first use. Write in the third person or the first person plural,
consistently; avoid rhetorical questions and unsupported adjectives.

## Anonymisation checklist

Before uploading the manuscript file:

* remove author names, affiliations, e-mail addresses and ORCID iDs;
* remove acknowledgements and funding details (they go on the title page);
* replace self-citations in the text with "Author (year)" where they would identify you;
* remove the name of your institution from data descriptions where it is not essential;
* clear the document properties (File → Properties in Word; File → Properties in
  LibreOffice);
* check headers, footers and file name for identifying information.

## Submission steps

1. **Start** — section, article type, language, mandatory declarations, AI use statement.
2. **Files** — anonymised manuscript (required), title page (required), figures, data.
3. **Metadata** — trilingual title, abstract and keywords; JEL codes; authors with
   affiliations, countries and ORCID iDs; statements.
4. **Reviewers and cover letter** — optional suggestions, optional exclusions, cover letter.
5. **Review and submit** — check the summary and confirm.

Your work is saved after every step; you may leave and return at any time. On submission you
receive a reference number and a confirmation e-mail.

## What happens next

Screening within seven days, review by at least two reviewers over 21 days, first decision
normally within eight weeks. Minor revisions are due in 30 days, major revisions in 60 days.
See [Peer Review Process](/en/about/peer-review/).""",
            "uz": """Qoʻlyozmani tayyorlashdan oldin ushbu yoʻriqnomani oʻqing. Unga rioya
qilmagan qoʻlyozmalar taqrizsiz qaytariladi, bu esa hammaning vaqtini oladi.

## Maqola turlari

| Turi | Hajmi (adabiyotlarsiz) | Annotatsiya | Izoh |
|---|---|---|---|
| Ilmiy maqola | 4 000–10 000 soʻz | 150–250 soʻz | standart format; IMRaD tuzilishi |
| Sharh maqolasi | 6 000–12 000 soʻz | 150–250 soʻz | tizimli yoki tanqidiy sharh; qidiruv strategiyasini koʻrsating |
| Qisqa maʼlumot | 2 000–4 000 soʻz | 100–150 soʻz | bitta aniq natija |
| Kitob taqrizi | 1 000–2 000 soʻz | talab etilmaydi | buyurtma boʻyicha yoki muharrirga taklif qilinadi |

## Tuzilish

Ilmiy maqolalar **IMRaD** tuzilishiga amal qiladi:

1. **Kirish** — tadqiqot savoli, uning ahamiyati, ishning yangiligi va maqola tuzilishi.
2. **Adabiyotlar sharhi** — nima maʼlum va ushbu maqola qaysi boʻshliqni toʻldiradi. Faqat
   mintaqaviy emas, xalqaro adabiyotni ham iqtibos qiling.
3. **Metodologiya** — maʼlumot manbalari, tanlanma, oʻzgaruvchilar, model spetsifikatsiyasi,
   identifikatsiya strategiyasi, dasturiy taʼminot. Ishni takrorlash mumkin boʻladigan
   darajada batafsil.
4. **Natijalar** — jadval va rasmlar bilan; baholarni standart xatolar, tanlanma hajmi va
   diagnostik testlar bilan keltiring.
5. **Muhokama** — talqin, avvalgi natijalar bilan taqqoslash, mexanizmlar, cheklovlar.
   Sababiy bogʻliqlikni oshirib yubormang.
6. **Xulosa** — tadqiqot savoliga javob, asoslangan boʻlsa siyosiy tavsiyalar va keyingi
   ish yoʻnalishlari.

Soʻngra tartib bilan: minnatdorchilik, moliyalashtirish bayonoti, manfaatlar toʻqnashuvi
bayonoti, maʼlumot mavjudligi bayonoti, SI dan foydalanish bayonoti, adabiyotlar, ilovalar.

## Uch tilli metamaʼlumotlar

Sarlavha, annotatsiya va kalit soʻzlar **ingliz, oʻzbek (lotin) va rus** tillarida
majburiy. Oʻzbek kirill varianti yuborish tizimida transliteratsiya orqali yaratiladi va
tahrirlanishi mumkin. Annotatsiya 150–250 soʻz, iqtibos va qisqartmalarsiz bitta xatboshi
boʻlishi hamda maqsad, maʼlumot va usul, asosiy natija va xulosani ifodalashi kerak. Har
bir tilda **5–8 kalit soʻz** bering, imkon qadar sarlavhadagi soʻzlarni takrorlamang.

## JEL kodlari

[JEL tasnifi](/uz/jel/) dan **1–5 ta** kod tanlang. Eng aniq mos keladigan kodni birinchi
qoʻying. Kodlar koʻrib chiqish, taqrizchi tanlash va indeksatsiya xizmatlari uchun
ishlatiladi.

## Adabiyotlar

**APA 7-nashri** talablariga amal qiling. Matndagi har bir iqtibosning roʻyxatda yozuvi
boʻlishi va har bir manba matnda iqtibos qilinishi shart. Mavjud boʻlsa **DOI** ni
`https://doi.org/10.xxxx/yyyy` koʻrinishida keltiring. Ilmiy maqolada odatda kamida 25 ta
manba boʻladi, ularning sezilarli qismi soʻnggi besh yilga va xalqaro jurnallarga tegishli
boʻlishi lozim.

Lotin boʻlmagan manbalar lotin transliteratsiyasida keltiriladi, soʻngra kvadrat qavsda
sarlavhaning inglizcha tarjimasi va qavsda til koʻrsatiladi:

> Karimov, A. A. (2023). Raqamli iqtisodiyot va mehnat bozori [The digital economy and the
> labour market]. *Iqtisodiyot va Taʼlim*, 24(3), 45–58. (in Uzbek)

## Rasm va jadvallar

Rasm va jadvallarni ketma-ket raqamlang va har biriga matnda murojaat qiling. Har bir
jadvalga ustida, har bir rasmga ostida oʻzini oʻzi tushuntiradigan izoh bering. Qatorlarni
ajratishning yagona usuli sifatida rangdan foydalanmang. Rasmlarni kamida 300 dpi yoki
vektor formatida bering. Har bir jadval va rasm uchun oʻlchov birligi va manbani
koʻrsating. Jadval tasvirini joylashtirmang — jadvallar tanlanadigan haqiqiy matn boʻlishi
kerak.

## Oʻlchov birliklari, sonlar va til

SI birliklaridan foydalaning. Valyuta miqdorini valyuta bilan, tegishli boʻlsa kurs va
sanani koʻrsatib keltiring. Har bir qisqartmani birinchi ishlatishda izohlang. Uchinchi
shaxsda yoki birinchi shaxs koʻplikda izchil yozing; ritorik savollar va asossiz
sifatlardan qoching.

## Anonimlashtirish roʻyxati

Qoʻlyozma faylini yuklashdan oldin:

* mualliflar ismi, ish joyi, elektron pochta va ORCID identifikatorlarini olib tashlang;
* minnatdorchilik va moliyalashtirish maʼlumotlarini olib tashlang (ular sarlavha
  sahifasiga kiradi);
* sizni oshkor qiladigan oʻz-oʻzini iqtiboslarni matnda «Muallif (yil)» bilan almashtiring;
* zarur boʻlmagan joyda maʼlumot tavsifidan muassasangiz nomini olib tashlang;
* hujjat xossalarini tozalang (Word: Fayl → Xossalar; LibreOffice: Fayl → Xossalar);
* kolontitullar va fayl nomida identifikatsiya maʼlumoti yoʻqligini tekshiring.

## Yuborish bosqichlari

1. **Boshlash** — boʻlim, maqola turi, til, majburiy deklaratsiyalar, SI bayonoti.
2. **Fayllar** — anonimlashtirilgan qoʻlyozma (majburiy), sarlavha sahifasi (majburiy),
   rasmlar, maʼlumotlar.
3. **Metamaʼlumotlar** — uch tilli sarlavha, annotatsiya va kalit soʻzlar; JEL kodlari;
   ish joyi, mamlakat va ORCID bilan mualliflar; bayonotlar.
4. **Taqrizchilar va muqova xati** — ixtiyoriy tavsiyalar, istisnolar, muqova xati.
5. **Koʻrib chiqish va yuborish** — xulosani tekshirib tasdiqlang.

Ishingiz har bosqichdan keyin saqlanadi; istalgan vaqtda qaytishingiz mumkin. Yuborilgach
raqam va tasdiq xati olasiz.

## Keyin nima boʻladi

Yetti kun ichida dastlabki koʻrik, kamida ikki taqrizchi tomonidan 21 kunlik taqriz, odatda
sakkiz hafta ichida birinchi qaror. Kichik qayta ishlash 30 kun, katta qayta ishlash 60 kun
muddatda. [Taqriz jarayoni](/uz/about/peer-review/) sahifasiga qarang.""",
            "ru": """Прочитайте это руководство до подготовки рукописи. Рукописи, не отвечающие
требованиям, возвращаются без рецензирования, что отнимает время у всех.

## Типы статей

| Тип | Объём (без списка литературы) | Аннотация | Примечание |
|---|---|---|---|
| Научная статья | 4 000–10 000 слов | 150–250 слов | стандартный формат; структура IMRaD |
| Обзорная статья | 6 000–12 000 слов | 150–250 слов | систематический или критический обзор; укажите стратегию поиска |
| Краткое сообщение | 2 000–4 000 слов | 100–150 слов | один чётко определённый результат |
| Рецензия на книгу | 1 000–2 000 слов | не требуется | по заказу или по предложению редактору |

## Структура

Научные статьи строятся по **IMRaD**:

1. **Введение** — исследовательский вопрос, его значимость, новизна работы и структура
   статьи.
2. **Обзор литературы** — что уже известно и какой пробел заполняет статья. Цитируйте
   международную литературу, а не только региональные источники.
3. **Методология** — источники данных, выборка, переменные, спецификация модели, стратегия
   идентификации, программное обеспечение. Достаточно подробно для воспроизведения.
4. **Результаты** — с таблицами и рисунками; приводите оценки со стандартными ошибками,
   размерами выборки и диагностическими тестами.
5. **Обсуждение** — интерпретация, сопоставление с прежними результатами, механизмы,
   ограничения. Не преувеличивайте причинность.
6. **Заключение** — ответы на исследовательский вопрос, обоснованные рекомендации и
   направления дальнейшей работы.

Далее по порядку: благодарности, сведения о финансировании, заявление о конфликте
интересов, заявление о доступности данных, заявление об использовании ИИ, список
литературы, приложения.

## Трёхъязычные метаданные

Название, аннотация и ключевые слова обязательны на **английском, узбекском (латиница) и
русском** языках. Узбекская кириллическая версия создаётся транслитерацией в системе подачи
и может быть отредактирована. Аннотация — 150–250 слов, один абзац без цитат и сокращений,
с указанием цели, данных и метода, основного результата и вывода. Приведите **5–8 ключевых
слов** на каждом языке, по возможности не повторяя слова из названия.

## Коды JEL

Выберите **1–5** кодов из [классификации JEL](/ru/jel/). Наиболее конкретный код ставьте
первым. Коды используются для навигации, подбора рецензентов и службами индексации.

## Список литературы

Используйте **APA 7-е издание**. Каждой внутритекстовой ссылке должна соответствовать
запись в списке, и каждая запись должна цитироваться. Указывайте **DOI** в виде
`https://doi.org/10.xxxx/yyyy` везде, где он есть. В научной статье обычно не менее 25
источников, значительная часть которых — за последние пять лет и из международных журналов.

Источники не на латинице приводятся в латинской транслитерации, затем в квадратных скобках
английский перевод названия и в круглых — язык:

> Karimov, A. A. (2023). Raqamli iqtisodiyot va mehnat bozori [The digital economy and the
> labour market]. *Iqtisodiyot va Taʼlim*, 24(3), 45–58. (in Uzbek)

## Рисунки и таблицы

Нумеруйте рисунки и таблицы последовательно и ссылайтесь на каждый в тексте. Подпись к
таблице размещается сверху, к рисунку — снизу; обе должны быть самодостаточными. Не
используйте цвет как единственный способ различения рядов. Рисунки — не менее 300 dpi или
в векторном формате. Указывайте единицы измерения и источник для каждой таблицы и рисунка.
Не вставляйте изображения таблиц — таблицы должны быть настоящим выделяемым текстом.

## Единицы, числа и язык

Используйте единицы СИ. Денежные суммы приводите с указанием валюты и, при необходимости,
курса и даты. Расшифровывайте каждое сокращение при первом употреблении. Пишите
последовательно от третьего лица или от первого лица множественного числа; избегайте
риторических вопросов и неподкреплённых эпитетов.

## Чек-лист обезличивания

Перед загрузкой файла рукописи:

* удалите имена авторов, места работы, адреса электронной почты и ORCID;
* удалите благодарности и сведения о финансировании (они идут на титульный лист);
* замените самоцитирования в тексте на «Автор (год)» там, где они вас выдают;
* уберите название вашей организации из описания данных, где оно не существенно;
* очистите свойства документа (Word: Файл → Свойства; LibreOffice: Файл → Свойства);
* проверьте колонтитулы и имя файла на наличие идентифицирующих сведений.

## Порядок подачи

1. **Начало** — рубрика, тип статьи, язык, обязательные заявления, заявление об ИИ.
2. **Файлы** — обезличенная рукопись (обязательно), титульный лист (обязательно), рисунки,
   данные.
3. **Метаданные** — трёхъязычные название, аннотация и ключевые слова; коды JEL; авторы с
   местами работы, странами и ORCID; заявления.
4. **Рецензенты и сопроводительное письмо** — необязательные предложения и исключения,
   письмо.
5. **Проверка и отправка** — проверьте сводку и подтвердите.

Работа сохраняется после каждого шага; вы можете вернуться в любое время. После отправки вы
получите номер и письмо-подтверждение.

## Что дальше

Отбор в течение семи дней, рецензирование не менее чем двумя рецензентами за 21 день,
первое решение обычно в течение восьми недель. Малая доработка — 30 дней, существенная —
60 дней. См. [Процесс рецензирования](/ru/about/peer-review/).""",
        },
    },
    {
        "slug": "submission-checklist",
        "menu_group": "authors",
        "order": 3,
        "title": {
            "en": "Pre-submission Checklist",
            "uz": "Yuborishdan oldingi tekshiruv roʻyxati",
            "ru": "Чек-лист перед подачей",
        },
        "seo": {
            "en": "Twelve checks to complete before opening the submission wizard.",
            "uz": "Yuborish sehrgarini ochishdan oldin bajarish kerak boʻlgan oʻn ikki tekshiruv.",
            "ru": "Двенадцать проверок, которые нужно выполнить до открытия мастера подачи.",
        },
        "body": {
            "en": """Tick every item above before you open the submission wizard. Nothing you tick is
sent to the server — the list is for you.

## Why we ask

Roughly one submission in three is returned at screening for something on this list, most
often an abstract of the wrong length, missing Russian or Uzbek metadata, references that
are not in APA 7, or a manuscript that still contains the authors' names. Each return costs
the author a week and the editorial office an hour.

## Files you will need

* **Anonymised manuscript** — PDF or DOCX, up to 20 MB, with no identifying information.
* **Title page** — a separate file with the full title in three languages, all authors in
  order, affiliations with city and country, ORCID iDs, the corresponding author's e-mail,
  acknowledgements, funding, and the conflict-of-interest statement.
* **Figures** — if they are not embedded at sufficient resolution in the manuscript.
* **Data and supplementary material** — optional, but strongly encouraged.

## Information you will need to type

The trilingual title, abstract and keywords; JEL codes; each author's full details; the
funding, conflict-of-interest, data availability and AI use statements; and the reference
list.""",
            "uz": """Yuborish sehrgarini ochishdan oldin yuqoridagi har bir bandni belgilang.
Belgilaganlaringiz serverga yuborilmaydi — roʻyxat siz uchun.

## Nega soʻraymiz

Har uch qoʻlyozmadan taxminan bittasi ushbu roʻyxatdagi biror sabab tufayli dastlabki
koʻrikda qaytariladi: koʻpincha annotatsiya hajmi notoʻgʻri, ruscha yoki oʻzbekcha
metamaʼlumotlar yoʻq, adabiyotlar APA 7 da emas yoki qoʻlyozmada hali ham mualliflar ismi
bor. Har bir qaytarish muallifning bir haftasini, tahririyatning bir soatini oladi.

## Kerak boʻladigan fayllar

* **Anonimlashtirilgan qoʻlyozma** — PDF yoki DOCX, 20 MB gacha, identifikatsiya
  maʼlumotlarisiz.
* **Sarlavha sahifasi** — uch tilda toʻliq sarlavha, tartib boʻyicha barcha mualliflar,
  shahar va mamlakat bilan ish joylari, ORCID identifikatorlari, masʼul muallif elektron
  pochtasi, minnatdorchilik, moliyalashtirish va manfaatlar toʻqnashuvi bayonoti boʻlgan
  alohida fayl.
* **Rasmlar** — qoʻlyozmada yetarli sifatda joylashtirilmagan boʻlsa.
* **Maʼlumotlar va qoʻshimcha materiallar** — ixtiyoriy, lekin qatʼiy tavsiya etiladi.

## Kiritish kerak boʻlgan maʼlumotlar

Uch tilli sarlavha, annotatsiya va kalit soʻzlar; JEL kodlari; har bir muallifning toʻliq
maʼlumotlari; moliyalashtirish, manfaatlar toʻqnashuvi, maʼlumot mavjudligi va SI dan
foydalanish bayonotlari; adabiyotlar roʻyxati.""",
            "ru": """Отметьте каждый пункт выше до открытия мастера подачи. Отмеченное не
передаётся на сервер — список нужен вам.

## Зачем мы просим

Примерно каждая третья рукопись возвращается на этапе отбора из-за пунктов этого списка:
чаще всего это аннотация неверного объёма, отсутствие русских или узбекских метаданных,
список литературы не по APA 7 либо рукопись, в которой остались имена авторов. Каждый
возврат стоит автору недели, а редакции — часа работы.

## Какие файлы понадобятся

* **Обезличенная рукопись** — PDF или DOCX до 20 МБ без идентифицирующих сведений.
* **Титульный лист** — отдельный файл с полным названием на трёх языках, всеми авторами по
  порядку, местами работы с городом и страной, идентификаторами ORCID, адресом
  корреспондирующего автора, благодарностями, финансированием и заявлением о конфликте
  интересов.
* **Рисунки** — если они не встроены в рукопись в достаточном разрешении.
* **Данные и дополнительные материалы** — необязательно, но настоятельно рекомендуется.

## Какие сведения нужно будет ввести

Трёхъязычные название, аннотация и ключевые слова; коды JEL; полные данные каждого автора;
заявления о финансировании, конфликте интересов, доступности данных и использовании ИИ;
список литературы.""",
        },
    },
    {
        "slug": "manuscript-template",
        "menu_group": "authors",
        "order": 4,
        "title": {
            "en": "Manuscript Templates",
            "uz": "Qoʻlyozma shablonlari",
            "ru": "Шаблоны рукописи",
        },
        "seo": {
            "en": "Download the DOCX and LaTeX manuscript templates, the title page template and the cover letter template.",
            "uz": "DOCX va LaTeX qoʻlyozma shablonlari, sarlavha sahifasi va muqova xati shablonlarini yuklab oling.",
            "ru": "Скачайте шаблоны рукописи в DOCX и LaTeX, шаблон титульного листа и сопроводительного письма.",
        },
        "body": {
            "en": """Using the templates is not compulsory, but it removes most of the reasons a
manuscript is returned at screening: they already contain the required section headings,
the trilingual abstract block, the statement block and correctly formatted reference
examples.

## How to use the manuscript template

1. Open the DOCX (or the `.tex` file) and save it under your own file name.
2. Replace the placeholder text section by section, keeping the headings.
3. Keep the abstract between 150 and 250 words — the template shows the word count.
4. Fill the trilingual block: English, Uzbek (Latin), Russian. Leave the Uzbek Cyrillic
   field empty; the submission system generates it.
5. Do **not** put author names anywhere in this file. They go on the title page template.
6. Before uploading, clear the document properties and check the anonymisation list in the
   [Author Guidelines](/en/for-authors/guidelines/).

## LaTeX

The `.tex` template uses only standard packages (`amsmath`, `booktabs`, `graphicx`,
`natbib` with an APA style). Compile with pdfLaTeX or XeLaTeX; XeLaTeX is recommended if
your text contains Uzbek Latin characters `oʻ` and `gʻ` or Cyrillic. Submit the compiled
PDF, not the source; the source may be requested at the production stage.""",
            "uz": """Shablonlardan foydalanish majburiy emas, ammo u qoʻlyozma dastlabki koʻrikda
qaytarilishining aksariyat sabablarini bartaraf etadi: shablonlarda talab qilingan boʻlim
sarlavhalari, uch tilli annotatsiya bloki, bayonotlar bloki va toʻgʻri formatlangan
adabiyot namunalari mavjud.

## Qoʻlyozma shablonidan qanday foydalanish kerak

1. DOCX (yoki `.tex`) faylni oching va oʻz nomingiz bilan saqlang.
2. Sarlavhalarni saqlagan holda oʻrnini bosuvchi matnni boʻlimma-boʻlim almashtiring.
3. Annotatsiyani 150–250 soʻz oraligʻida saqlang — shablon soʻz sonini koʻrsatadi.
4. Uch tilli blokni toʻldiring: ingliz, oʻzbek (lotin), rus. Oʻzbek kirill maydonini boʻsh
   qoldiring; uni yuborish tizimi yaratadi.
5. Bu faylning hech joyiga mualliflar ismini **yozmang**. Ular sarlavha sahifasi
   shabloniga kiradi.
6. Yuklashdan oldin hujjat xossalarini tozalang va
   [Mualliflar uchun yoʻriqnoma](/uz/for-authors/guidelines/) dagi anonimlashtirish
   roʻyxatini tekshiring.

## LaTeX

`.tex` shabloni faqat standart paketlardan foydalanadi (`amsmath`, `booktabs`, `graphicx`,
APA uslubidagi `natbib`). pdfLaTeX yoki XeLaTeX bilan kompilyatsiya qiling; matningizda
oʻzbek lotin belgilari `oʻ` va `gʻ` yoki kirill boʻlsa, XeLaTeX tavsiya etiladi. Manba
emas, kompilyatsiya qilingan PDF ni yuboring; manba nashrga tayyorlash bosqichida
soʻralishi mumkin.""",
            "ru": """Использование шаблонов не обязательно, но снимает большинство причин возврата
рукописи на этапе отбора: в них уже есть требуемые заголовки разделов, блок трёхъязычной
аннотации, блок заявлений и корректно оформленные примеры ссылок.

## Как пользоваться шаблоном рукописи

1. Откройте DOCX (или файл `.tex`) и сохраните под своим именем.
2. Заменяйте текст-заполнитель раздел за разделом, сохраняя заголовки.
3. Держите аннотацию в пределах 150–250 слов — шаблон показывает счётчик слов.
4. Заполните трёхъязычный блок: английский, узбекский (латиница), русский. Поле узбекской
   кириллицы оставьте пустым; система подачи заполнит его сама.
5. **Не** указывайте имена авторов нигде в этом файле. Они помещаются в шаблон титульного
   листа.
6. Перед загрузкой очистите свойства документа и сверьтесь со списком обезличивания в
   [Руководстве для авторов](/ru/for-authors/guidelines/).

## LaTeX

Шаблон `.tex` использует только стандартные пакеты (`amsmath`, `booktabs`, `graphicx`,
`natbib` со стилем APA). Компилируйте pdfLaTeX или XeLaTeX; XeLaTeX рекомендуется, если в
тексте есть узбекские латинские знаки `oʻ` и `gʻ` или кириллица. Подавайте
скомпилированный PDF, а не исходник; исходник может быть запрошен на этапе подготовки к
публикации.""",
        },
    },
    {
        "slug": "reviewer-guidelines",
        "menu_group": "reviewers",
        "order": 1,
        "title": {
            "en": "Reviewer Guidelines",
            "uz": "Taqrizchilar uchun yoʻriqnoma",
            "ru": "Руководство для рецензентов",
        },
        "seo": {
            "en": "How to review for the journal: what we ask, how the form works, confidentiality, timing, ethics and recognition.",
            "uz": "Jurnal uchun qanday taqriz yozish kerak: nima soʻraymiz, shakl qanday ishlaydi, maxfiylik, muddat, etika va eʼtirof.",
            "ru": "Как рецензировать для журнала: что мы просим, как устроена форма, конфиденциальность, сроки, этика и признание.",
        },
        "body": {
            "en": """Thank you for reviewing. A good review helps the editor decide and helps the
authors write a better paper, whatever the decision.

## Before you accept

Accept only if you have the subject and methodological expertise the manuscript requires,
can complete the review within **21 days**, and have no conflict of interest. Decline —
promptly, so we can invite someone else — if you have co-authored with an author in the past
three years, work at the same institution, have a financial or personal interest in the
outcome, or for any other reason cannot judge the work impartially. Declining is normal and
is never held against you; a late review is far more costly than a decline.

You are welcome to suggest an alternative reviewer when you decline.

## What we ask you to assess

The form scores six criteria from 1 (poor) to 5 (excellent):

1. **Originality and novelty** — does the paper add something that is not already known?
2. **Relevance to the journal's scope** — is this economics research of international
   interest?
3. **Methodological rigour** — are the data, the model and the identification strategy
   appropriate, and are the assumptions stated?
4. **Data and results** — are the results correctly derived, adequately reported and
   robust?
5. **Coverage of the literature** — is the relevant international literature engaged with?
6. **Writing and structure** — is the argument clear and the structure appropriate?

Then you write comments to the authors and, if you wish, confidential comments to the
editor, and give a recommendation: **accept**, **minor revision**, **major revision** or
**reject**.

## Writing useful comments

* Start with two or three sentences summarising what the paper does, so the authors can see
  whether you understood it as they intended.
* Separate **major** points (which affect the validity of the conclusions) from **minor**
  points (typos, wording, formatting). Number them; authors respond point by point.
* Be specific: "the standard errors in Table 3 should be clustered at the firm level,
  because treatment varies at that level" is useful; "the econometrics is weak" is not.
* Say what would convince you. If you recommend rejection, explain what is not fixable by
  revision.
* Criticise the work, never the authors. Do not speculate about who the authors are, and
  do not let a guess about nationality, institution or seniority affect your assessment.
* If you suspect plagiarism, data fabrication or duplicate publication, do not accuse the
  authors in the comments — tell the editor confidentially in the editor-only field.
* Do not require the authors to cite your own work unless it is genuinely essential.

## Confidentiality and AI

A manuscript under review is a confidential document. Do not share it, discuss it with
identifiable third parties, cite it, or use its results before publication. If you would
like a junior colleague to co-review, ask the editor first and name them; they will be
credited. **Do not upload the manuscript, or any part of it, to any generative-AI
service** — see the [AI Policy](/en/about/ai-policy/). The review must be your own
assessment.

## Timing and reminders

Reviews are due 21 days after you accept. The system reminds you three days before the
deadline, on the day, and seven days after. If you need more time, tell the editor — an
extension is usually easy to arrange, silence is not.

## After the review

You will be told the decision and can read the other reviews for the same manuscript in
your dashboard. Editors rate the usefulness of each review from 1 to 5; the rating is
private and is used only to choose reviewers well.

## Recognition

Reviewers can download a certificate of review at any time from the reviewer dashboard, and
the journal publishes an annual acknowledgement listing everyone who reviewed during the
year (with their consent).""",
            "uz": """Taqriz uchun rahmat. Yaxshi taqriz muharrirga qaror qabul qilishda va
mualliflarga — qaror qanday boʻlishidan qatʼi nazar — yaxshiroq maqola yozishda yordam
beradi.

## Qabul qilishdan oldin

Faqat qoʻlyozma talab qiladigan mavzu va metodologik bilimga ega boʻlsangiz, taqrizni
**21 kun** ichida tugatа olsangiz va manfaatlar toʻqnashuvi boʻlmasa qabul qiling. Agar
soʻnggi uch yilda muallif bilan hammuallif boʻlgan, bir muassasada ishlaydigan, natijadan
moliyaviy yoki shaxsiy manfaatdor boʻlsangiz yoki boshqa sababga koʻra xolis baho bera
olmasangiz — tezda rad eting, shunda biz boshqa kishini taklif qila olamiz. Rad etish
odatiy hol va sizga hech qachon salbiy taʼsir qilmaydi; kechikkan taqriz rad etishdan
ancha qimmatga tushadi.

Rad etishda muqobil taqrizchi tavsiya qilishingiz mumkin.

## Nimani baholashni soʻraymiz

Shakl olti mezonni 1 (yomon) dan 5 (aʼlo) gacha baholaydi:

1. **Originallik va yangilik** — maqola allaqachon maʼlum boʻlmagan nimadir qoʻshadimi?
2. **Jurnal yoʻnalishiga muvofiqlik** — bu xalqaro qiziqish uygʻotadigan iqtisodiy
   tadqiqotmi?
3. **Metodologik puxtalik** — maʼlumot, model va identifikatsiya strategiyasi mosmi,
   farazlar koʻrsatilganmi?
4. **Maʼlumot va natijalar** — natijalar toʻgʻri olinganmi, yetarli darajada
   keltirilganmi va barqarormi?
5. **Adabiyot qamrovi** — tegishli xalqaro adabiyot bilan ishlanganmi?
6. **Yozilish va tuzilish** — dalil aniqmi va tuzilish mosmi?

Soʻngra mualliflarga izohlar va istasangiz muharrirga maxfiy izohlar yozasiz hamda tavsiya
berasiz: **qabul qilish**, **kichik qayta ishlash**, **katta qayta ishlash** yoki
**rad etish**.

## Foydali izohlar yozish

* Maqola nima qilganini ikki-uch gapda umumlashtirib boshlang — shunda mualliflar sizni
  toʻgʻri tushunganingizni koʻradi.
* **Asosiy** fikrlarni (xulosalar asosliligiga taʼsir qiladiganlar) **kichik** fikrlardan
  (imlo, ifoda, formatlash) ajrating. Ularni raqamlang; mualliflar band-band javob
  beradi.
* Aniq boʻling: «3-jadvaldagi standart xatolar firma darajasida klasterlanishi kerak,
  chunki taʼsir shu darajada oʻzgaradi» — foydali; «ekonometrikasi zaif» — emas.
* Sizni nima ishontirishini ayting. Rad etishni tavsiya qilsangiz, nimani qayta ishlash
  bilan tuzatib boʻlmasligini tushuntiring.
* Ishni tanqid qiling, mualliflarni emas. Mualliflar kimligini taxmin qilmang va millat,
  muassasa yoki lavozim haqidagi taxmin bahoyingizga taʼsir qilmasin.
* Plagiat, maʼlumot toʻqib chiqarish yoki takroriy nashrga shubha qilsangiz, izohlarda
  mualliflarni aybламang — muharrirga faqat unga koʻrinadigan maydonda maxfiy ayting.
* Haqiqatan zarur boʻlmasa, mualliflardan oʻz ishlaringizni iqtibos qilishni talab
  qilmang.

## Maxfiylik va SI

Taqrizdagi qoʻlyozma maxfiy hujjatdir. Uni ulashmang, aniqlanadigan uchinchi shaxslar
bilan muhokama qilmang, iqtibos qilmang va chop etilishidan oldin natijalaridan
foydalanmang. Yosh hamkasbingiz bilan birga taqriz qilmoqchi boʻlsangiz, avval muharrirdan
soʻrang va ismini ayting; u eʼtirof etiladi. **Qoʻlyozmani yoki uning biror qismini hech
qanday generativ SI xizmatiga yuklamang** — [SI siyosati](/uz/about/ai-policy/) ga qarang.
Taqriz sizning oʻz bahoyingiz boʻlishi kerak.

## Muddat va eslatmalar

Taqriz qabul qilganingizdan 21 kun keyin topshiriladi. Tizim muddatdan uch kun oldin,
muddat kunida va yetti kundan keyin eslatma yuboradi. Qoʻshimcha vaqt kerak boʻlsa,
muharrirga ayting — muddatni uzaytirish odatda oson, sukut saqlash esa emas.

## Taqrizdan keyin

Sizga qaror haqida xabar beriladi va boshqaruv panelida shu qoʻlyozmaga oid boshqa
taqrizlarni oʻqiy olasiz. Muharrirlar har bir taqrizning foydaliligini 1 dan 5 gacha
baholaydi; baho maxfiy va faqat taqrizchilarni yaxshi tanlash uchun ishlatiladi.

## Eʼtirof

Taqrizchilar istalgan vaqtda boshqaruv panelidan taqriz sertifikatini yuklab olishi
mumkin, jurnal esa yil davomida taqriz qilgan barchani (roziligi bilan) sanab oʻtadigan
yillik minnatdorchilik eʼlon qiladi.""",
            "ru": """Спасибо за рецензирование. Хорошая рецензия помогает редактору принять решение,
а авторам — написать лучшую статью, каким бы ни было решение.

## Прежде чем согласиться

Соглашайтесь, только если обладаете предметной и методологической экспертизой, требуемой
рукописью, можете завершить рецензию в течение **21 дня** и не имеете конфликта интересов.
Откажитесь — быстро, чтобы мы могли пригласить другого, — если за последние три года были
соавтором автора, работаете в той же организации, имеете финансовый или личный интерес в
результате либо по иной причине не можете судить беспристрастно. Отказ — нормальная
ситуация, он никогда не ставится в упрёк; опоздавшая рецензия обходится куда дороже отказа.

При отказе вы можете предложить другого рецензента.

## Что мы просим оценить

Форма оценивает шесть критериев от 1 (плохо) до 5 (отлично):

1. **Оригинальность и новизна** — добавляет ли работа то, что ещё не известно?
2. **Соответствие тематике журнала** — это ли экономическое исследование международного
   интереса?
3. **Методологическая строгость** — адекватны ли данные, модель и стратегия идентификации,
   сформулированы ли допущения?
4. **Данные и результаты** — корректно ли получены результаты, достаточно ли они изложены и
   устойчивы?
5. **Охват литературы** — задействована ли релевантная международная литература?
6. **Изложение и структура** — ясна ли аргументация и уместна ли структура?

Затем вы пишете комментарии авторам и, при желании, конфиденциальные комментарии редактору
и даёте рекомендацию: **принять**, **малая доработка**, **существенная доработка** или
**отклонить**.

## Как писать полезные комментарии

* Начните с двух-трёх предложений, резюмирующих, что делает статья, — так авторы увидят,
  поняли ли вы её так, как они задумывали.
* Отделяйте **существенные** замечания (влияющие на достоверность выводов) от
  **второстепенных** (опечатки, формулировки, оформление). Нумеруйте их; авторы отвечают
  по пунктам.
* Будьте конкретны: «стандартные ошибки в таблице 3 следует кластеризовать на уровне фирмы,
  поскольку воздействие варьируется на этом уровне» — полезно; «эконометрика слабая» — нет.
* Скажите, что вас убедило бы. Если рекомендуете отклонить, объясните, что нельзя исправить
  доработкой.
* Критикуйте работу, а не авторов. Не гадайте, кто авторы, и не позволяйте догадкам о
  гражданстве, организации или статусе влиять на оценку.
* Если подозреваете плагиат, фабрикацию данных или дублирующую публикацию, не обвиняйте
  авторов в комментариях — сообщите редактору конфиденциально в поле только для редактора.
* Не требуйте цитировать ваши собственные работы, если это не действительно необходимо.

## Конфиденциальность и ИИ

Рукопись на рецензии — конфиденциальный документ. Не передавайте её, не обсуждайте с
идентифицируемыми третьими лицами, не цитируйте и не используйте её результаты до
публикации. Если хотите привлечь младшего коллегу к соавторству рецензии, сначала спросите
редактора и назовите его; он будет отмечен. **Не загружайте рукопись или её части в
какие-либо сервисы генеративного ИИ** — см. [Политику в отношении ИИ](/ru/about/ai-policy/).
Рецензия должна быть вашей собственной оценкой.

## Сроки и напоминания

Рецензия должна быть представлена через 21 день после согласия. Система напоминает за три
дня до срока, в день срока и через семь дней. Если нужно больше времени, скажите редактору —
продление обычно легко согласовать, молчание — нет.

## После рецензии

Вам сообщат решение, и в личном кабинете вы сможете прочитать другие рецензии на ту же
рукопись. Редакторы оценивают полезность каждой рецензии от 1 до 5; оценка непубличная и
используется только для правильного подбора рецензентов.

## Признание

Рецензенты в любой момент могут скачать сертификат из кабинета рецензента, а журнал
ежегодно публикует благодарность со списком всех, кто рецензировал в течение года (с их
согласия).""",
        },
    },
]
