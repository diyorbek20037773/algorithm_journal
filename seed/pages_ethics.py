"""Publication ethics, AI policy, open access, fees, archiving, indexing, privacy."""

from __future__ import annotations

from typing import Any

ETHICS_PAGES: list[dict[str, Any]] = [
    {
        "slug": "publication-ethics",
        "menu_group": "about",
        "order": 4,
        "title": {
            "en": "Publication Ethics and Malpractice Statement",
            "uz": "Nashr etikasi va suiisteʼmolning oldini olish bayonoti",
            "ru": "Издательская этика и заявление о недобросовестной практике",
        },
        "seo": {
            "en": "COPE-based duties of editors, reviewers and authors, plagiarism policy, corrections and retractions, complaints and appeals.",
            "uz": "COPE asosidagi muharrir, taqrizchi va muallif majburiyatlari, plagiat siyosati, tuzatish va chaqirib olish, shikoyatlar.",
            "ru": "Обязанности редакторов, рецензентов и авторов по COPE, политика в отношении плагиата, исправления и отзывы, жалобы.",
        },
        "body": {
            "en": """This statement follows the **COPE Core Practices** of the Committee on
Publication Ethics. It binds everyone involved in publishing with the journal: editors,
reviewers, authors, and the publisher.

## Duties of editors

Editors decide which manuscripts are published on the basis of scholarly merit alone,
without regard to the authors' nationality, institution, gender, ethnicity, religion,
seniority or political views. They keep every submitted manuscript confidential, disclose
and step aside from any manuscript in which they have a competing interest, and never use
unpublished material from a submission in their own research. Editors act on credible
allegations of misconduct whenever they arise, including after publication, and they
document each decision in the editorial system's audit log.

## Duties of reviewers

Reviewers help the editor decide and help the authors improve the paper. A reviewer who
feels unqualified, who cannot complete the review in time, or who has a competing interest
must decline promptly. Reviews must be objective, argued and free of personal criticism.
Reviewers must treat the manuscript as confidential: it may not be shown to anyone, cited,
used, or uploaded to any third-party service, including generative-AI tools. A reviewer
who notices substantial overlap with published work must tell the editor.

## Duties of authors

Authors must present their work honestly and completely. Specifically:

* the manuscript must be original and must not be under consideration elsewhere;
* data and methods must be described so that the work can be assessed and, in principle,
  reproduced; data and code should be available on reasonable request;
* every source used must be cited, in any language; verbatim text must be quoted and
  attributed;
* fabrication, falsification and manipulation of data or images are serious misconduct;
* funding and any competing interests must be disclosed;
* errors discovered after submission or after publication must be reported to the editor
  immediately.

## Authorship and contributions

Authorship is limited to those who made a substantial contribution to the conception or
design of the work, or to the acquisition, analysis or interpretation of the data; who
drafted or critically revised the manuscript; who approved the version submitted; and who
agree to be accountable for the work. Everyone who meets these criteria must be listed;
no one who does not meet them may be listed. Contributions are recorded using the
**CRediT** taxonomy. Gift, guest and ghost authorship are misconduct. Changes to the
author list after submission require the written agreement of every author.

## Plagiarism and similarity

Every submission is checked for textual similarity. Our threshold is **20 % overall
similarity excluding the reference list and correctly attributed quotations**. There is
**zero tolerance** for unattributed copying, however small, and for self-plagiarism
presented as new work. A manuscript above the threshold is returned or rejected; an
editor-in-chief may override the threshold only with a written justification recorded in
the system.

## Duplicate and redundant publication

Submitting the same work to more than one journal at the same time, or republishing work
already published in any language without a clear cross-reference and the permission of
the original publisher, is unacceptable. Prior publication as a working paper, a preprint,
a conference abstract, or a thesis chapter is acceptable and must be disclosed in the cover
letter.

## Corrections, retractions and expressions of concern

* A **correction** is issued for an error that affects the record but not the conclusions.
* A **retraction** is issued, following COPE retraction guidelines, when findings are
  unreliable through error or misconduct, when the work is plagiarised or previously
  published, when authorship is disputed and unresolved, or when the peer review was
  compromised.
* An **expression of concern** is published where an investigation is inconclusive or
  unresolved.

Retracted articles stay online with the original content, watermarked and clearly labelled
"Retracted", with the notice linked from the article page. The DOI is never withdrawn.

## Complaints and appeals

Complaints about editorial decisions, process or conduct should be sent to the editorial
office; if the complaint concerns the Editor-in-Chief, it should be addressed to the
publisher. All complaints are acknowledged within five working days and answered within
30 days. The appeals procedure for editorial decisions is described on the
[Peer Review Process](/en/about/peer-review/) page.

## Post-publication discussion

Readers may send substantiated comments on published articles to the editorial office.
Comments raising a matter of scholarly substance are forwarded to the authors for a
response, and both may be published as a comment and reply.""",
            "uz": """Ushbu bayonot Nashr etikasi qoʻmitasining (COPE) **asosiy amaliyotlariga**
asoslanadi. U jurnal bilan bogʻliq barcha ishtirokchilar uchun majburiy: muharrirlar,
taqrizchilar, mualliflar va nashriyot.

## Muharrirlarning majburiyatlari

Muharrirlar qaysi qoʻlyozma chop etilishini faqat ilmiy qiymat asosida hal qiladi;
muallifning millati, muassasasi, jinsi, etnik kelib chiqishi, dini, lavozimi yoki siyosiy
qarashlari hisobga olinmaydi. Ular har bir qoʻlyozmani maxfiy saqlaydi, manfaatlar
toʻqnashuvi boʻlgan qoʻlyozmadan chetlashadi va yuborilgan chop etilmagan materialdan
oʻz tadqiqotida foydalanmaydi. Muharrirlar suiisteʼmol haqidagi asosli daʼvolar boʻyicha,
jumladan chop etilgandan keyin ham, chora koʻradi va har bir qarorni tizim audit
jurnalida qayd etadi.

## Taqrizchilarning majburiyatlari

Taqrizchi muharrirga qaror qabul qilishda va muallifga maqolani yaxshilashda yordam
beradi. Oʻzini malakasiz deb bilgan, muddatida ulgurmaydigan yoki manfaatlar toʻqnashuvi
boʻlgan taqrizchi taklifni darhol rad etishi kerak. Taqriz xolis, asoslangan va shaxsiy
tanqiddan xoli boʻlishi lozim. Qoʻlyozma maxfiy: uni hech kimga koʻrsatish, iqtibos
keltirish, foydalanish yoki uchinchi tomon xizmatlariga, jumladan generativ SI
vositalariga yuklash mumkin emas. Chop etilgan ish bilan jiddiy oʻxshashlikni sezgan
taqrizchi muharrirga xabar berishi shart.

## Mualliflarning majburiyatlari

Mualliflar oʻz ishini halol va toʻliq taqdim etishi kerak. Xususan:

* qoʻlyozma original boʻlishi va boshqa joyda koʻrib chiqilmayotgan boʻlishi kerak;
* maʼlumot va usullar ishni baholash hamda tamoyilan takrorlash mumkin boʻladigan darajada
  tavsiflanishi lozim; maʼlumot va kod asosli soʻrov boʻyicha taqdim etilishi kerak;
* foydalanilgan har bir manba, qaysi tilda boʻlishidan qatʼi nazar, iqtibos qilinishi
  shart; soʻzma-soʻz matn qoʻshtirnoqqa olinib manba koʻrsatilishi kerak;
* maʼlumot yoki tasvirlarni toʻqib chiqarish, soxtalashtirish va manipulyatsiya qilish
  ogʻir suiisteʼmoldir;
* moliyalashtirish va har qanday manfaatlar toʻqnashuvi oshkor qilinishi shart;
* yuborilgandan yoki chop etilgandan keyin aniqlangan xatolar darhol muharrirga
  bildirilishi kerak.

## Mualliflik va hissa

Mualliflik quyidagi shartlarni bajargan shaxslar bilan cheklanadi: ishning gʻoyasi yoki
dizayniga, yoxud maʼlumot toʻplash, tahlil qilish va talqin etishga sezilarli hissa
qoʻshgan; qoʻlyozmani yozgan yoki tanqidiy qayta ishlagan; yuborilgan variantni
maʼqullagan; ish uchun javobgarlikni zimmasiga olgan. Ushbu mezonlarga javob beradigan
har bir kishi roʻyxatga kiritilishi, javob bermaydigan hech kim kiritilmasligi shart.
Hissalar **CRediT** taksonomiyasi orqali qayd etiladi. Sovgʻa, mehmon va soya mualliflik
suiisteʼmol hisoblanadi. Yuborilgandan keyin mualliflar roʻyxatini oʻzgartirish barcha
mualliflarning yozma roziligini talab qiladi.

## Plagiat va oʻxshashlik

Har bir qoʻlyozma matn oʻxshashligi boʻyicha tekshiriladi. Chegaramiz — **adabiyotlar
roʻyxati va toʻgʻri koʻrsatilgan iqtiboslardan tashqari 20 % umumiy oʻxshashlik**.
Manbasi koʻrsatilmagan koʻchirmaga, hajmidan qatʼi nazar, va yangi ish sifatida taqdim
etilgan oʻz-oʻzidan plagiatga **mutlaqo yoʻl qoʻyilmaydi**. Chegaradan yuqori qoʻlyozma
qaytariladi yoki rad etiladi; bosh muharrir chegarani faqat tizimda qayd etilgan yozma
asos bilan bekor qilishi mumkin.

## Takroriy va ortiqcha nashr

Bir ishni bir vaqtda bir nechta jurnalga yuborish yoki istalgan tilda allaqachon chop
etilgan ishni aniq havolasiz va dastlabki nashriyot ruxsatisiz qayta chop etish qabul
qilinmaydi. Ishchi maqola, preprint, konferensiya tezisi yoki dissertatsiya bobi sifatida
oldin eʼlon qilinishi mumkin va bu haqda muqova xatida xabar berilishi kerak.

## Tuzatishlar, chaqirib olish va xavotir bayonoti

* **Tuzatish** — yozuvga taʼsir qiladigan, ammo xulosalarni oʻzgartirmaydigan xato uchun.
* **Chaqirib olish** COPE yoʻriqnomasiga muvofiq chiqariladi: natijalar xato yoki
  suiisteʼmol tufayli ishonchsiz boʻlsa, ish plagiat yoki avval chop etilgan boʻlsa,
  mualliflik bahsi hal boʻlmasa yoki taqriz jarayoni buzilgan boʻlsa.
* **Xavotir bayonoti** tekshiruv natijasi noaniq yoki tugallanmagan hollarda eʼlon
  qilinadi.

Chaqirib olingan maqolalar asl mazmuni bilan saytda qoladi, «Chaqirib olingan» deb aniq
belgilanadi va sahifasidan bildirishnomaga havola beriladi. DOI hech qachon bekor
qilinmaydi.

## Shikoyat va apellyatsiyalar

Tahririy qarorlar, jarayon yoki xatti-harakatlar boʻyicha shikoyatlar tahririyatga
yuboriladi; shikoyat Bosh muharrirga tegishli boʻlsa, u nashriyot nomiga yoziladi.
Barcha shikoyatlar besh ish kuni ichida qabul qilinganligi tasdiqlanadi va 30 kun ichida
javob beriladi. Tahririy qarorlar boʻyicha apellyatsiya tartibi
[Taqriz jarayoni](/uz/about/peer-review/) sahifasida.

## Nashrdan keyingi muhokama

Oʻquvchilar chop etilgan maqolalar boʻyicha asoslangan izohlarni tahririyatga yuborishi
mumkin. Ilmiy mohiyatga daxldor izohlar mualliflarga javob uchun yuboriladi va ikkalasi
izoh va javob sifatida chop etilishi mumkin.""",
            "ru": """Настоящее заявление основано на **Core Practices** Комитета по издательской
этике (COPE) и обязательно для всех участников издательского процесса: редакторов,
рецензентов, авторов и издателя.

## Обязанности редакторов

Редакторы принимают решение о публикации исключительно на основании научной ценности, без
учёта гражданства, места работы, пола, этнической принадлежности, вероисповедания,
должности или политических взглядов авторов. Они сохраняют конфиденциальность каждой
рукописи, раскрывают конфликт интересов и устраняются от работы с такой рукописью, не
используют неопубликованные материалы поданных работ в собственных исследованиях.
Редакторы реагируют на обоснованные заявления о нарушениях, в том числе после публикации,
и фиксируют каждое решение в журнале аудита редакционной системы.

## Обязанности рецензентов

Рецензент помогает редактору принять решение, а авторам — улучшить работу. Рецензент,
считающий себя недостаточно компетентным, не успевающий в срок или имеющий конфликт
интересов, обязан незамедлительно отказаться. Рецензия должна быть объективной,
аргументированной и свободной от личной критики. Рукопись конфиденциальна: её нельзя
показывать, цитировать, использовать или загружать в сторонние сервисы, включая
инструменты генеративного ИИ. Заметив существенное совпадение с опубликованной работой,
рецензент обязан сообщить редактору.

## Обязанности авторов

Авторы обязаны представлять работу честно и полно. В частности:

* рукопись должна быть оригинальной и не рассматриваться другими изданиями;
* данные и методы должны быть описаны так, чтобы работу можно было оценить и в принципе
  воспроизвести; данные и код предоставляются по обоснованному запросу;
* каждый использованный источник должен быть процитирован на любом языке; дословный текст
  оформляется как цитата с указанием источника;
* фабрикация, фальсификация и манипулирование данными или изображениями — грубое
  нарушение;
* источники финансирования и любые конфликты интересов подлежат раскрытию;
* об ошибках, обнаруженных после подачи или после публикации, необходимо немедленно
  сообщить редактору.

## Авторство и вклад

Авторство ограничивается теми, кто внёс существенный вклад в замысел или дизайн работы
либо в сбор, анализ или интерпретацию данных; кто написал или критически переработал
рукопись; кто одобрил поданную версию; и кто готов нести ответственность за работу. Все,
кто отвечает этим критериям, должны быть указаны; никто, кто им не отвечает, указан быть
не может. Вклад фиксируется по таксономии **CRediT**. Подарочное, гостевое и теневое
авторство — нарушение. Изменение состава авторов после подачи требует письменного
согласия всех авторов.

## Плагиат и заимствования

Каждая рукопись проверяется на текстовые заимствования. Наш порог — **20 % общего
совпадения без учёта списка литературы и корректно оформленных цитат**. Действует
**нулевая терпимость** к неатрибутированному копированию любого объёма и к
самоплагиату, представленному как новая работа. Рукопись выше порога возвращается или
отклоняется; главный редактор вправе превысить порог только с письменным обоснованием,
зафиксированным в системе.

## Дублирующие и избыточные публикации

Подача одной работы одновременно в несколько журналов, а также повторная публикация уже
изданной на любом языке работы без ясной ссылки и разрешения первого издателя
недопустимы. Предварительная публикация в виде рабочего доклада, препринта, тезисов
конференции или главы диссертации допустима и должна быть раскрыта в сопроводительном
письме.

## Исправления, отзывы и выражения обеспокоенности

* **Исправление** выпускается при ошибке, затрагивающей запись, но не выводы.
* **Отзыв (retraction)** выпускается по руководству COPE, если результаты недостоверны
  вследствие ошибки или нарушения, если работа является плагиатом или ранее
  опубликована, если спор об авторстве не разрешён или если рецензирование было
  скомпрометировано.
* **Выражение обеспокоенности** публикуется, когда расследование не завершено или
  неопределённо.

Отозванные статьи остаются в сети с исходным содержанием, с ясной пометкой «Отозвана» и
ссылкой на уведомление со страницы статьи. DOI никогда не аннулируется.

## Жалобы и апелляции

Жалобы на редакционные решения, процесс или поведение направляются в редакцию; если
жалоба касается главного редактора — издателю. Получение всех жалоб подтверждается в
течение пяти рабочих дней, ответ даётся в течение 30 дней. Порядок апелляции на
редакционные решения описан на странице
[Процесс рецензирования](/ru/about/peer-review/).

## Обсуждение после публикации

Читатели могут направлять в редакцию обоснованные комментарии к опубликованным статьям.
Комментарии, затрагивающие научную суть, передаются авторам для ответа, и оба текста
могут быть опубликованы как комментарий и ответ.""",
        },
    },
    {
        "slug": "ai-policy",
        "menu_group": "about",
        "order": 5,
        "title": {
            "en": "Policy on Generative AI",
            "uz": "Generativ sunʼiy intellekt boʻyicha siyosat",
            "ru": "Политика в отношении генеративного ИИ",
        },
        "seo": {
            "en": "AI tools cannot be authors; any use in writing or analysis must be disclosed; reviewers must not upload manuscripts to AI services.",
            "uz": "SI vositalari muallif boʻla olmaydi; yozish yoki tahlilda foydalanish oshkor qilinishi shart; taqrizchilar qoʻlyozmani SI xizmatlariga yuklamasligi kerak.",
            "ru": "ИИ не может быть автором; любое использование при написании или анализе подлежит раскрытию; рецензентам запрещено загружать рукописи в ИИ-сервисы.",
        },
        "body": {
            "en": """Generative artificial intelligence is now part of many research workflows. The
journal neither forbids it nor treats it as neutral: it requires that its use be
disclosed, and it holds human authors fully responsible for everything they submit.

## AI systems cannot be authors

A large language model, chatbot or other AI system cannot be listed as an author or
co-author. Authorship requires accountability for the work, agreement to be answerable for
its accuracy and integrity, and the ability to approve the final version — none of which
an AI system can provide.

## Authors must disclose use

Every submission carries a mandatory **AI use statement**. If no generative tools were
used, write "No generative AI tools were used in the preparation of this article." If they
were used, state plainly which tool, which version if known, and for what: language
editing, translation, code generation, literature search, data cleaning, image generation,
or anything else. A typical disclosure reads:

> The authors used a large language model to improve the readability of the English text
> in sections 2 and 4. The authors reviewed and edited the output and take full
> responsibility for the content of the article.

Disclosure of language editing does not affect the editorial decision. Failure to disclose
does: it is treated as a breach of research integrity.

## Where authors remain responsible

Authors are fully responsible for the accuracy of every statement, every citation and
every number in the manuscript, whether or not a tool helped produce it. In particular:

* references invented or altered by a model ("hallucinated citations") are a serious
  integrity problem — check every reference against the original source;
* AI-generated text describing results the authors did not obtain is fabrication;
* AI-generated or AI-modified figures and images that alter research data are not
  permitted; purely illustrative AI images must be labelled as such in the caption.

## Reviewers and editors

Reviewers and editors **must not upload a submitted manuscript, or any part of it, to a
generative-AI service**. Manuscripts are confidential documents, and most public AI
services retain and may reuse the text supplied to them. A review must be the reviewer's
own assessment; AI may not be used to write it. Editors may use AI tools only for
administrative language support in correspondence, never for evaluating a manuscript and
never with confidential content.

## Editorial use of AI in production

The journal itself uses machine assistance for one clearly bounded task: generating the
Uzbek Cyrillic version of Uzbek Latin metadata by deterministic transliteration. Such
fields are flagged in the editorial system and proofread by the editorial office.""",
            "uz": """Generativ sunʼiy intellekt bugungi kunda koʻplab tadqiqot jarayonlarining bir
qismidir. Jurnal uni taqiqlamaydi, ammo neytral deb ham hisoblamaydi: undan foydalanish
oshkor qilinishini talab qiladi va yuborilgan hamma narsa uchun toʻliq javobgarlikni
inson mualliflar zimmasiga yuklaydi.

## SI tizimlari muallif boʻla olmaydi

Katta til modeli, chatbot yoki boshqa SI tizimi muallif yoki hammuallif sifatida
koʻrsatilishi mumkin emas. Mualliflik ish uchun javobgarlikni, uning aniqligi va
yaxlitligi uchun javob berish roziligini hamda yakuniy variantni maʼqullash imkoniyatini
talab qiladi — bularning hech birini SI tizimi taʼminlay olmaydi.

## Mualliflar foydalanishni oshkor qilishi shart

Har bir qoʻlyozmada majburiy **SI dan foydalanish bayonoti** boʻladi. Agar generativ
vositalar ishlatilmagan boʻlsa: «Ushbu maqolani tayyorlashda generativ sunʼiy intellekt
vositalari ishlatilmagan» deb yoziladi. Ishlatilgan boʻlsa, qaysi vosita, maʼlum boʻlsa
versiyasi va nima uchun ishlatilgani aniq koʻrsatiladi: til tahriri, tarjima, kod
yaratish, adabiyot qidiruvi, maʼlumotlarni tozalash, tasvir yaratish yoki boshqa maqsad.
Odatiy bayonot quyidagicha:

> Mualliflar 2 va 4-boʻlimlardagi inglizcha matnning oʻqilishini yaxshilash uchun katta
> til modelidan foydalangan. Mualliflar natijani koʻrib chiqib tahrirlagan va maqola
> mazmuni uchun toʻliq javobgarlikni oʻz zimmasiga oladi.

Til tahririni oshkor qilish tahririy qarorga taʼsir qilmaydi. Oshkor qilmaslik esa taʼsir
qiladi: bu ilmiy halollikning buzilishi sifatida baholanadi.

## Mualliflarning javobgarligi

Mualliflar qoʻlyozmadagi har bir gap, har bir iqtibos va har bir raqamning aniqligi uchun
toʻliq javobgar, vosita yordam bergan yoki bermaganidan qatʼi nazar. Xususan:

* model toʻqib chiqargan yoki oʻzgartirgan manbalar («gallyutsinatsiyali iqtiboslar»)
  jiddiy muammo — har bir manbani asl nusxa bilan solishtiring;
* mualliflar olmagan natijalarni tasvirlovchi SI matni — soxtalashtirishdir;
* tadqiqot maʼlumotlarini oʻzgartiradigan SI tomonidan yaratilgan yoki oʻzgartirilgan
  rasmlar taqiqlanadi; faqat illyustrativ SI tasvirlari izohda shunday belgilanishi shart.

## Taqrizchilar va muharrirlar

Taqrizchilar va muharrirlar **yuborilgan qoʻlyozmani yoki uning biror qismini generativ
SI xizmatiga yuklamasligi shart**. Qoʻlyozmalar maxfiy hujjat, koʻpchilik ommaviy SI
xizmatlari esa yuborilgan matnni saqlaydi va qayta ishlatishi mumkin. Taqriz
taqrizchining oʻz bahosi boʻlishi kerak; uni yozish uchun SI ishlatilmaydi. Muharrirlar
SI vositalaridan faqat yozishmalarda maʼmuriy til yordami sifatida foydalanishi mumkin,
qoʻlyozmani baholash uchun va maxfiy mazmun bilan hech qachon emas.

## Nashrda SI dan tahririy foydalanish

Jurnalning oʻzi mashina yordamidan bitta aniq chegaralangan vazifa uchun foydalanadi:
oʻzbek lotin metamaʼlumotlaridan determinlashgan transliteratsiya orqali kirill
variantini yaratish. Bunday maydonlar tahririy tizimda belgilanadi va tahririyat
tomonidan tekshiriladi.""",
            "ru": """Генеративный искусственный интеллект стал частью многих исследовательских
процессов. Журнал его не запрещает, но и не считает нейтральным: он требует раскрытия
факта использования и возлагает полную ответственность за поданный материал на авторов —
людей.

## ИИ-системы не могут быть авторами

Большая языковая модель, чат-бот или иная ИИ-система не может быть указана автором или
соавтором. Авторство предполагает ответственность за работу, готовность отвечать за её
точность и целостность и способность утвердить окончательную версию — ничего из этого
ИИ-система обеспечить не может.

## Авторы обязаны раскрывать использование

Каждая рукопись содержит обязательное **заявление об использовании ИИ**. Если
генеративные инструменты не применялись, пишется: «При подготовке настоящей статьи
инструменты генеративного искусственного интеллекта не использовались». Если применялись,
прямо указывается инструмент, его версия (если известна) и цель: языковое редактирование,
перевод, генерация кода, поиск литературы, очистка данных, генерация изображений или иное.
Типичное раскрытие:

> Авторы использовали большую языковую модель для улучшения читаемости английского текста
> в разделах 2 и 4. Авторы проверили и отредактировали результат и несут полную
> ответственность за содержание статьи.

Раскрытие языкового редактирования не влияет на редакционное решение. Нераскрытие —
влияет: оно рассматривается как нарушение научной добросовестности.

## Ответственность авторов

Авторы полностью отвечают за точность каждого утверждения, каждой ссылки и каждого числа
в рукописи независимо от того, помогал ли инструмент. В частности:

* выдуманные или изменённые моделью источники («галлюцинированные цитаты») — серьёзное
  нарушение; сверяйте каждую ссылку с оригиналом;
* текст, сгенерированный ИИ и описывающий результаты, которых авторы не получали, —
  фабрикация;
* созданные или изменённые ИИ изображения, искажающие исследовательские данные, не
  допускаются; чисто иллюстративные ИИ-изображения должны быть помечены в подписи.

## Рецензенты и редакторы

Рецензентам и редакторам **запрещено загружать поданную рукопись или её части в сервисы
генеративного ИИ**. Рукопись — конфиденциальный документ, а большинство публичных
ИИ-сервисов сохраняют и могут повторно использовать переданный текст. Рецензия должна
быть собственной оценкой рецензента; ИИ не может использоваться для её написания.
Редакторы вправе применять ИИ только как административную языковую помощь в переписке,
никогда — для оценки рукописи и никогда — с конфиденциальным содержанием.

## Редакционное использование ИИ

Сам журнал использует машинную помощь для одной чётко ограниченной задачи: генерации
узбекской кириллической версии метаданных из узбекской латиницы посредством
детерминированной транслитерации. Такие поля помечаются в редакционной системе и
вычитываются редакцией.""",
        },
    },
    {
        "slug": "open-access",
        "menu_group": "about",
        "order": 6,
        "title": {
            "en": "Open Access, Licence and Copyright",
            "uz": "Ochiq kirish, litsenziya va mualliflik huquqi",
            "ru": "Открытый доступ, лицензия и авторское право",
        },
        "seo": {
            "en": "All articles are published under CC BY 4.0; authors retain copyright; self-archiving of any version is allowed with no embargo.",
            "uz": "Barcha maqolalar CC BY 4.0 ostida chop etiladi; mualliflik huquqi muallifda; har qanday variantni embargosiz arxivlash mumkin.",
            "ru": "Все статьи публикуются под CC BY 4.0; авторское право остаётся у авторов; самоархивирование любой версии разрешено без эмбарго.",
        },
        "body": {
            "en": """The journal is **fully open access**. Every article is free to read, download,
copy, print, distribute, translate, text- and data-mine, and build upon from the moment it
is published. There is no subscription, no registration requirement, and no embargo of any
kind.

## Licence

All articles are published under the **Creative Commons Attribution 4.0 International
licence (CC BY 4.0)**. Anyone may share and adapt the material for any purpose, including
commercially, provided they give appropriate credit, link to the licence, and indicate if
changes were made. The machine-readable licence is embedded in every article's metadata and
deposited with Crossref.

## Copyright

**Authors retain copyright in their work.** Submitting to the journal does not transfer
copyright; authors grant the journal a non-exclusive right to publish and archive the
article. Because authors keep copyright, they may reuse their own work — in a thesis, a
book chapter, teaching material or a later paper — without asking permission, citing the
original publication.

## Self-archiving

Authors may deposit **any version** of the article — submitted manuscript, accepted
manuscript, or the published version of record — in any repository, on a personal or
institutional website, or on a preprint server, at any time, with **no embargo**. We ask
only that the deposited copy links to the published version by DOI.

## Reuse by third parties

Under CC BY 4.0 you may:

* reproduce figures, tables and text with attribution, without asking us;
* translate an article into another language and publish the translation, stating that it
  is a translation and citing the original;
* include articles in course packs, anthologies and commercial products;
* run automated text and data mining over the full text — the PDF is machine readable and
  a text-mining URL is registered with Crossref for every article.

Attribution should give the authors, the article title, the journal name, the year, and
the DOI.

## No charges

There are no article processing charges, submission fees, page charges, colour charges or
any other author-facing costs — see [Article Processing Charges](/en/about/fees/). The
journal is financed by its founding organisation.""",
            "uz": """Jurnal **toʻliq ochiq kirishli**. Har bir maqolani chop etilgan lahzadan
boshlab bepul oʻqish, yuklab olish, nusxalash, chop etish, tarqatish, tarjima qilish,
matn va maʼlumot qidiruvidan oʻtkazish hamda uning asosida yangi ishlar yaratish mumkin.
Obuna, roʻyxatdan oʻtish talabi va hech qanday embargo yoʻq.

## Litsenziya

Barcha maqolalar **Creative Commons Attribution 4.0 International litsenziyasi (CC BY
4.0)** ostida chop etiladi. Har kim materialni istalgan maqsadda, jumladan tijorat
maqsadida ham ulashishi va moslashtirishi mumkin, agar tegishli tarzda manbani koʻrsatsa,
litsenziyaga havola bersa va oʻzgarishlar kiritilganini bildirsa. Mashina oʻqiy oladigan
litsenziya har bir maqola metamaʼlumotlariga joylanadi va Crossref ga yuboriladi.

## Mualliflik huquqi

**Mualliflik huquqi mualliflarda qoladi.** Jurnalga yuborish mualliflik huquqini
oʻtkazmaydi; mualliflar jurnalga maqolani chop etish va arxivlash boʻyicha noeksklyuziv
huquq beradi. Mualliflik huquqi saqlangani uchun mualliflar oʻz ishidan — dissertatsiyada,
kitob bobida, oʻquv materialida yoki keyingi maqolada — ruxsat soʻramasdan, dastlabki
nashrga iqtibos berib foydalanishi mumkin.

## Oʻz-oʻzini arxivlash

Mualliflar maqolaning **istalgan variantini** — yuborilgan qoʻlyozma, qabul qilingan
qoʻlyozma yoki chop etilgan yakuniy variantni — istalgan repozitoriyga, shaxsiy yoki
muassasa saytiga, preprint serveriga istalgan vaqtda, **embargosiz** joylashtirishi
mumkin. Yagona iltimosimiz — joylashtirilgan nusxada DOI orqali chop etilgan variantga
havola boʻlsin.

## Uchinchi tomonlar tomonidan qayta foydalanish

CC BY 4.0 doirasida siz:

* rasm, jadval va matnlarni manba koʻrsatib, bizdan soʻramasdan qayta chop etishingiz;
* maqolani boshqa tilga tarjima qilib, tarjima ekanini koʻrsatgan va aslini iqtibos
  qilgan holda chop etishingiz;
* maqolalarni oʻquv toʻplamlari, antologiyalar va tijorat mahsulotlariga kiritishingiz;
* toʻliq matn boʻyicha avtomatik matn va maʼlumot qidiruvini oʻtkazishingiz mumkin —
  PDF mashina oʻqiy oladigan va har bir maqola uchun Crossref da text-mining havolasi
  roʻyxatdan oʻtkaziladi.

Manba koʻrsatishda mualliflar, maqola sarlavhasi, jurnal nomi, yil va DOI keltiriladi.

## Toʻlovlar yoʻq

Maqolani qayta ishlash toʻlovi, yuborish toʻlovi, sahifa yoki rangli chop etish toʻlovi
va boshqa hech qanday muallif toʻlovi yoʻq —
[Maqolani qayta ishlash toʻlovlari](/uz/about/fees/) sahifasiga qarang. Jurnal muassis
tashkilot tomonidan moliyalashtiriladi.""",
            "ru": """Журнал имеет **полностью открытый доступ**. Каждую статью можно бесплатно
читать, скачивать, копировать, печатать, распространять, переводить, обрабатывать
методами text and data mining и использовать как основу для новых работ с момента
публикации. Подписки, обязательной регистрации и какого-либо эмбарго нет.

## Лицензия

Все статьи публикуются под лицензией **Creative Commons Attribution 4.0 International
(CC BY 4.0)**. Любой может распространять и адаптировать материал в любых целях, включая
коммерческие, при условии указания авторства, ссылки на лицензию и обозначения внесённых
изменений. Машиночитаемая лицензия включена в метаданные каждой статьи и передаётся в
Crossref.

## Авторское право

**Авторское право остаётся у авторов.** Подача в журнал не передаёт авторских прав; авторы
предоставляют журналу неисключительное право на публикацию и архивирование статьи.
Поскольку права сохраняются за авторами, они могут повторно использовать собственную
работу — в диссертации, главе книги, учебных материалах или последующей статье — без
запроса разрешения, ссылаясь на первую публикацию.

## Самоархивирование

Авторы вправе размещать **любую версию** статьи — поданную рукопись, принятую рукопись
или опубликованную версию — в любом репозитории, на личном или институциональном сайте,
на сервере препринтов, в любое время и **без эмбарго**. Единственная просьба — чтобы
размещённая копия ссылалась на опубликованную версию по DOI.

## Повторное использование третьими лицами

В рамках CC BY 4.0 вы можете:

* воспроизводить рисунки, таблицы и текст с указанием источника, не спрашивая нас;
* перевести статью на другой язык и опубликовать перевод, указав, что это перевод, и
  сославшись на оригинал;
* включать статьи в учебные сборники, антологии и коммерческие продукты;
* выполнять автоматическую обработку полного текста — PDF машиночитаем, а для каждой
  статьи в Crossref зарегистрирован URL для text mining.

При указании источника приводятся авторы, название статьи, название журнала, год и DOI.

## Отсутствие платы

Нет платы за обработку статьи, за подачу, за страницы, за цветную печать и любых иных
расходов для авторов — см. [Плата за публикацию](/ru/about/fees/). Журнал финансируется
организацией-учредителем.""",
        },
    },
    {
        "slug": "fees",
        "menu_group": "about",
        "order": 7,
        "title": {
            "en": "Article Processing Charges",
            "uz": "Maqolani qayta ishlash toʻlovlari",
            "ru": "Плата за публикацию",
        },
        "seo": {
            "en": "No article processing charges, no submission fees, no page charges. Publication is free for authors and free for readers.",
            "uz": "Maqolani qayta ishlash toʻlovi yoʻq, yuborish toʻlovi yoʻq, sahifa toʻlovi yoʻq. Nashr mualliflar va oʻquvchilar uchun bepul.",
            "ru": "Нет платы за обработку статьи, за подачу и за страницы. Публикация бесплатна для авторов и для читателей.",
        },
        "body": {
            "en": """## There are no fees

**The journal charges authors nothing, at any stage.**

| Charge | Amount |
|---|---|
| Article processing charge (APC) | **none** |
| Submission fee | **none** |
| Page charge | **none** |
| Colour figure charge | **none** |
| Supplementary material charge | **none** |
| Fee to make an article open access | **none** — every article is open access |
| Fee for readers (subscription, pay-per-view) | **none** |

This is the model usually called **diamond open access**: free for authors and free for
readers. The costs of running the journal — editorial work, peer review management, DOI
registration, hosting and preservation — are met by the founding organisation.

## No payment is ever requested

The journal will **never** ask an author to pay, to buy a certificate, to purchase a
printed copy as a condition of publication, or to transfer money to a personal account.
If you receive such a request in the journal's name, it is fraudulent: forward it to the
editorial office and do not respond to it.

## What is also free

* Registration and use of the submission system.
* DOI registration for every published article.
* Reviewer certificates.
* Long-term preservation and permanent public access.

## Waivers

Because there are no charges, no waiver policy is needed. This is a deliberate choice: no
author should be prevented from publishing sound research by an inability to pay.""",
            "uz": """## Hech qanday toʻlov yoʻq

**Jurnal mualliflardan hech qanday bosqichda toʻlov olmaydi.**

| Toʻlov turi | Miqdori |
|---|---|
| Maqolani qayta ishlash toʻlovi (APC) | **yoʻq** |
| Yuborish toʻlovi | **yoʻq** |
| Sahifa toʻlovi | **yoʻq** |
| Rangli rasm toʻlovi | **yoʻq** |
| Qoʻshimcha material toʻlovi | **yoʻq** |
| Maqolani ochiq kirishli qilish toʻlovi | **yoʻq** — barcha maqolalar ochiq |
| Oʻquvchilar uchun toʻlov (obuna, koʻrish uchun toʻlov) | **yoʻq** |

Bu model odatda **diamond open access** deb ataladi: mualliflar uchun ham, oʻquvchilar
uchun ham bepul. Jurnalni yuritish xarajatlari — tahririy ish, taqriz jarayonini
boshqarish, DOI roʻyxatga olish, xosting va saqlash — muassis tashkilot tomonidan
qoplanadi.

## Toʻlov hech qachon soʻralmaydi

Jurnal **hech qachon** muallifdan pul toʻlashni, sertifikat sotib olishni, chop etish
sharti sifatida bosma nusxa xarid qilishni yoki shaxsiy hisobga pul oʻtkazishni
soʻramaydi. Jurnal nomidan bunday soʻrov kelsa, u firibgarlikdir: uni tahririyatga
yuboring va javob bermang.

## Yana nimalar bepul

* Yuborish tizimida roʻyxatdan oʻtish va undan foydalanish.
* Har bir chop etilgan maqola uchun DOI roʻyxatga olish.
* Taqrizchi sertifikatlari.
* Uzoq muddatli saqlash va doimiy ochiq kirish.

## Imtiyozlar

Toʻlovlar boʻlmagani uchun imtiyoz siyosati talab qilinmaydi. Bu ongli tanlov: hech bir
muallif toʻlov imkoni yoʻqligi sababli puxta tadqiqotini chop eta olmay qolmasligi
kerak.""",
            "ru": """## Плата отсутствует

**Журнал не взимает с авторов никакой платы ни на одном этапе.**

| Вид платы | Размер |
|---|---|
| Плата за обработку статьи (APC) | **нет** |
| Плата за подачу | **нет** |
| Постраничная плата | **нет** |
| Плата за цветные иллюстрации | **нет** |
| Плата за дополнительные материалы | **нет** |
| Плата за открытый доступ к статье | **нет** — все статьи в открытом доступе |
| Плата для читателей (подписка, оплата за просмотр) | **нет** |

Эта модель обычно называется **diamond open access**: бесплатно для авторов и бесплатно
для читателей. Расходы на работу журнала — редакционная работа, организация
рецензирования, регистрация DOI, хостинг и хранение — покрывает организация-учредитель.

## Оплата никогда не запрашивается

Журнал **никогда** не просит автора внести плату, купить сертификат, приобрести печатный
экземпляр как условие публикации или перевести деньги на личный счёт. Если вы получили
такое требование от имени журнала, это мошенничество: перешлите его в редакцию и не
отвечайте на него.

## Что ещё бесплатно

* Регистрация и работа в системе подачи рукописей.
* Регистрация DOI для каждой опубликованной статьи.
* Сертификаты рецензентов.
* Долгосрочное хранение и постоянный открытый доступ.

## Льготы

Поскольку платы нет, политика льгот не требуется. Это сознательный выбор: ни один автор
не должен лишаться возможности опубликовать качественное исследование из-за
невозможности заплатить.""",
        },
    },
    {
        "slug": "archiving",
        "menu_group": "about",
        "order": 8,
        "title": {
            "en": "Archiving and Preservation Policy",
            "uz": "Arxivlash va saqlash siyosati",
            "ru": "Политика архивирования и хранения",
        },
        "seo": {
            "en": "Digital preservation through CLOCKSS/Portico, LOCKSS manifests, per-issue export bundles, DOI persistence and self-archiving.",
            "uz": "CLOCKSS/Portico, LOCKSS manifestlari, son boʻyicha eksport toʻplamlari, DOI barqarorligi va oʻz-oʻzini arxivlash orqali raqamli saqlash.",
            "ru": "Цифровое хранение через CLOCKSS/Portico, манифесты LOCKSS, экспортные пакеты по выпускам, устойчивость DOI и самоархивирование.",
        },
        "body": {
            "en": """Long-term availability is part of what makes a journal citable. The journal
preserves its content through several independent mechanisms so that it survives the
failure of any one of them, including the failure of the journal itself.

## Preservation networks

The journal is prepared for deposit in a distributed preservation network and names
**CLOCKSS** and **Portico** as its intended archives; the publisher completes the
membership formalities as part of bringing the journal into full production. The technical
requirements are already met:

* a **LOCKSS permission manifest** at [`/lockss/`](/lockss/) and one manifest per volume,
  carrying the standard permission statement that authorises harvesting;
* stable, predictable URLs for every article landing page and PDF;
* complete, harvestable metadata through OAI-PMH.

## What is preserved

For each issue the journal can produce a self-contained export bundle
(`ARER_vol{V}_no{N}.zip`) containing, for every article: the published PDF, the JATS XML
front matter, the Crossref deposit XML, and a `manifest.json` listing checksums and
metadata. Bundles are generated by the production dashboard and by the management command
`manage.py export_issue_bundle <issue-id>`, and are stored with the nightly backups.

## Identifiers

Every article receives a **DOI registered with Crossref**. DOIs are permanent: they are
never reassigned, never deleted, and continue to resolve for retracted and withdrawn
articles. The DOI suffix is issue-independent (`arer.{year}.{article-id}`), so an article
published as Online First keeps the same DOI when it is later assigned to an issue.

## Web archiving

The journal's `robots.txt` permits crawling by all agents, and complete XML sitemaps are
published, so that the Internet Archive and national web archives can capture the site.
Article PDFs are text-based, not scanned images, so archived copies remain searchable.

## Self-archiving by authors

Because authors retain copyright under CC BY 4.0, they may deposit any version of their
article in institutional or subject repositories with no embargo. This is encouraged: it
adds another independent copy of the scholarly record.

## Journal cessation

Should the journal cease to publish, its complete content will be transferred to the
preservation networks named above and, in addition, deposited in an open repository so
that the record remains publicly accessible with its DOIs resolving.

## Backups

The production installation takes nightly database and media backups with a 30-day
retention window and copies them to off-site storage in an encrypted form. Restores are
tested; the procedure is documented in `docs/BACKUP_RESTORE.md`. Backups are an
operational safeguard and are not a substitute for the preservation arrangements above.""",
            "uz": """Uzoq muddatli mavjudlik jurnalning iqtibos qilinadigan boʻlishining bir
qismidir. Jurnal oʻz kontentini bir nechta mustaqil mexanizm orqali saqlaydi — shunda
ulardan birortasi, hattoki jurnalning oʻzi ishdan chiqsa ham, kontent saqlanib qoladi.

## Saqlash tarmoqlari

Jurnal taqsimlangan saqlash tarmogʻiga joylashtirishga tayyor va **CLOCKSS** hamda
**Portico** ni moʻljallangan arxivlar sifatida koʻrsatadi; nashriyot aʼzolik
rasmiyatchiliklarini jurnalni toʻliq ishlab chiqarishga olib chiqish doirasida
yakunlaydi. Texnik talablar allaqachon bajarilgan:

* [`/lockss/`](/lockss/) manzilidagi **LOCKSS ruxsat manifesti** va har bir jild uchun
  alohida manifest, yigʻib olishga ruxsat beruvchi standart bayonot bilan;
* har bir maqola sahifasi va PDF uchun barqaror, oldindan bilinadigan URL manzillar;
* OAI-PMH orqali toʻliq, yigʻib olinadigan metamaʼlumotlar.

## Nima saqlanadi

Har bir son uchun jurnal mustaqil eksport toʻplamini (`ARER_vol{V}_no{N}.zip`) yarata
oladi; unda har bir maqola boʻyicha: chop etilgan PDF, JATS XML metamaʼlumoti, Crossref
uchun XML va nazorat summalari hamda metamaʼlumotlarni oʻz ichiga olgan `manifest.json`
boʻladi. Toʻplamlar nashr boshqaruv panelidan va `manage.py export_issue_bundle <son-id>`
buyrugʻi orqali yaratiladi hamda tungi zaxira nusxalari bilan birga saqlanadi.

## Identifikatorlar

Har bir maqola **Crossref da roʻyxatdan oʻtgan DOI** oladi. DOI doimiy: u qayta
tayinlanmaydi, oʻchirilmaydi va chaqirib olingan hamda qaytarib olingan maqolalar uchun
ham ishlashda davom etadi. DOI suffiksi songa bogʻliq emas (`arer.{yil}.{maqola-id}`),
shuning uchun Online First sifatida chop etilgan maqola keyinchalik songa kiritilganda
ham oʻsha DOI ni saqlab qoladi.

## Veb-arxivlash

Jurnalning `robots.txt` fayli barcha agentlarga indekslashga ruxsat beradi va toʻliq XML
sayt xaritalari eʼlon qilinadi — shunda Internet Archive va milliy veb-arxivlar saytni
qamrab olishi mumkin. Maqola PDF fayllari skanerlangan tasvir emas, matnli, shuning uchun
arxiv nusxalarida qidiruv ishlaydi.

## Mualliflar tomonidan oʻz-oʻzini arxivlash

CC BY 4.0 boʻyicha mualliflik huquqi mualliflarda qolgani uchun ular maqolaning istalgan
variantini muassasa yoki soha repozitoriylariga embargosiz joylashtirishi mumkin. Bu
ragʻbatlantiriladi: bu ilmiy yozuvning yana bir mustaqil nusxasini yaratadi.

## Jurnal faoliyati toʻxtaganda

Agar jurnal nashrni toʻxtatsa, uning butun kontenti yuqorida koʻrsatilgan saqlash
tarmoqlariga oʻtkaziladi va qoʻshimcha ravishda ochiq repozitoriyga joylashtiriladi —
shunda yozuv ommaga ochiq qoladi va DOI lar ishlashda davom etadi.

## Zaxira nusxalar

Ishlab chiqarish oʻrnatmasi har kecha maʼlumotlar bazasi va media fayllarning zaxira
nusxasini oladi, ularni 30 kun saqlaydi va shifrlangan holda tashqi omborga koʻchiradi.
Tiklash sinovdan oʻtkaziladi; tartib `docs/BACKUP_RESTORE.md` da tavsiflangan. Zaxira
nusxalar operatsion himoya vositasi boʻlib, yuqoridagi saqlash tadbirlarini
almashtirmaydi.""",
            "ru": """Долгосрочная доступность — часть того, что делает журнал цитируемым. Журнал
сохраняет своё содержание с помощью нескольких независимых механизмов, чтобы оно
пережило отказ любого из них, включая прекращение работы самого журнала.

## Сети хранения

Журнал подготовлен к депонированию в распределённой сети хранения и указывает **CLOCKSS**
и **Portico** как предполагаемые архивы; издатель завершает формальности членства в рамках
вывода журнала в полноценную эксплуатацию. Технические требования уже выполнены:

* **манифест разрешения LOCKSS** по адресу [`/lockss/`](/lockss/) и отдельный манифест для
  каждого тома со стандартным разрешительным заявлением;
* устойчивые предсказуемые URL для каждой страницы статьи и PDF;
* полные, доступные для сбора метаданные через OAI-PMH.

## Что сохраняется

Для каждого выпуска журнал формирует автономный экспортный пакет
(`ARER_vol{V}_no{N}.zip`), содержащий для каждой статьи: опубликованный PDF, JATS XML,
XML депозита Crossref и `manifest.json` с контрольными суммами и метаданными. Пакеты
создаются из панели выпуска и командой `manage.py export_issue_bundle <id-выпуска>` и
хранятся вместе с ночными резервными копиями.

## Идентификаторы

Каждая статья получает **DOI, зарегистрированный в Crossref**. DOI постоянен: он не
переназначается, не удаляется и продолжает разрешаться для отозванных и изъятых статей.
Суффикс DOI не зависит от выпуска (`arer.{год}.{id-статьи}`), поэтому статья,
опубликованная как Online First, сохраняет тот же DOI после включения в выпуск.

## Веб-архивирование

Файл `robots.txt` разрешает обход всем агентам, публикуются полные XML-карты сайта,
чтобы Internet Archive и национальные веб-архивы могли захватить сайт. PDF статей —
текстовые, а не сканированные изображения, поэтому в архивных копиях работает поиск.

## Самоархивирование авторами

Поскольку по CC BY 4.0 авторское право остаётся у авторов, они могут размещать любую
версию статьи в институциональных и тематических репозиториях без эмбарго. Мы это
поощряем: так появляется ещё одна независимая копия научной записи.

## Прекращение выпуска журнала

Если журнал прекратит выпуск, всё его содержание будет передано в указанные сети хранения
и дополнительно депонировано в открытом репозитории, чтобы запись оставалась публично
доступной, а DOI продолжали разрешаться.

## Резервное копирование

Производственная установка выполняет ежедневное резервное копирование базы данных и
медиафайлов с хранением 30 дней и копирует их в зашифрованном виде во внешнее хранилище.
Восстановление тестируется; процедура описана в `docs/BACKUP_RESTORE.md`. Резервные копии —
эксплуатационная мера и не заменяют описанных выше мер долговременного хранения.""",
        },
    },
    {
        "slug": "indexing",
        "menu_group": "about",
        "order": 9,
        "title": {
            "en": "Indexing and Abstracting",
            "uz": "Indeksatsiya va referatlash",
            "ru": "Индексация и реферирование",
        },
        "seo": {
            "en": "Services the journal is currently listed in, the applications planned, and why we display no impact-factor badges.",
            "uz": "Jurnal hozirda roʻyxatdan oʻtgan xizmatlar, rejalashtirilgan arizalar va nega impakt-faktor nishonlarini koʻrsatmasligimiz.",
            "ru": "Сервисы, в которых журнал уже представлен, планируемые заявки и почему мы не показываем значки импакт-фактора.",
        },
        "body": {
            "en": """We list only the services in which the journal is **actually** indexed. Nothing
on this site displays a metric or a badge we cannot substantiate.

## Currently

The list below is maintained by the editorial office and is updated as soon as an
application succeeds. The services shown on the home page are exactly those marked active
here.

## Applications planned

Most reputable databases require a publication history before they will consider an
application. Our sequence is:

| When | Database | Requirement we are meeting |
|---|---|---|
| From issue 1 | Crossref | membership and DOI registration for every article |
| From issue 1 | Google Scholar | Highwire `citation_*` metadata, crawlable PDFs, sitemaps |
| From issue 1 | ORCID | authenticated author identifiers |
| After 12 months | **DOAJ** | one year of continuous publication, ≥ 5 research articles, complete policies |
| After 24 months | Scopus (CSAB) | at least two years of publication, international board and authorship, English abstracts and references, citation record |
| As available | national and subject databases | as their criteria require |

## Why we display no impact-factor badges

The journal deliberately shows **no** "impact factor", "SJIF", "Global Impact Factor",
"ICV" or similar badge from unverified providers. Such metrics are sold rather than earned
and are treated by DOAJ, Scopus and Google Scholar as a warning sign. When the journal is
covered by a citation database that publishes an audited metric, we will link to that
database's own page rather than reproduce a badge.

## Verifying our metadata

Anyone can verify what we publish about ourselves:

* the OAI-PMH endpoint: [`/oai/?verb=Identify`](/oai/?verb=Identify);
* the read-only JSON API: [`/api/v1/`](/api/v1/);
* a DOAJ-shaped metadata export: [`/api/v1/doaj-export/`](/api/v1/doaj-export/);
* any article's Crossref record via its DOI.""",
            "uz": """Biz faqat jurnal **haqiqatan** indekslangan xizmatlarni koʻrsatamiz. Saytda
asoslay olmaydigan hech qanday koʻrsatkich yoki nishon namoyish etilmaydi.

## Hozirda

Quyidagi roʻyxat tahririyat tomonidan yuritiladi va ariza qoniqtirilishi bilan
yangilanadi. Bosh sahifada koʻrsatiladigan xizmatlar — aynan shu yerda faol deb
belgilanganlari.

## Rejalashtirilgan arizalar

Koʻpchilik nufuzli bazalar arizani koʻrib chiqishdan oldin nashr tarixini talab qiladi.
Bizning ketma-ketligimiz:

| Qachon | Baza | Bajarilayotgan talab |
|---|---|---|
| 1-sondan | Crossref | aʼzolik va har bir maqola uchun DOI |
| 1-sondan | Google Scholar | Highwire `citation_*` metamaʼlumotlari, indekslanadigan PDF, sayt xaritalari |
| 1-sondan | ORCID | tasdiqlangan muallif identifikatorlari |
| 12 oydan keyin | **DOAJ** | bir yillik uzluksiz nashr, kamida 5 ilmiy maqola, toʻliq siyosatlar |
| 24 oydan keyin | Scopus (CSAB) | kamida ikki yillik nashr, xalqaro hayʼat va mualliflar, inglizcha annotatsiya va adabiyotlar, iqtibos tarixi |
| Imkoniyatga qarab | milliy va soha bazalari | ularning mezonlariga muvofiq |

## Nega impakt-faktor nishonlarini koʻrsatmaymiz

Jurnal tekshirilmagan provayderlarning «impact factor», «SJIF», «Global Impact Factor»,
«ICV» va shunga oʻxshash nishonlarini ataylab **koʻrsatmaydi**. Bunday koʻrsatkichlar
qozonilmaydi, sotib olinadi va DOAJ, Scopus hamda Google Scholar tomonidan ogohlantiruvchi
belgi sifatida qabul qilinadi. Jurnal auditdan oʻtgan koʻrsatkich eʼlon qiladigan iqtibos
bazasiga kiritilganda, biz nishon oʻrniga oʻsha bazaning oʻz sahifasiga havola beramiz.

## Metamaʼlumotlarimizni tekshirish

Oʻzimiz haqimizda eʼlon qilgan maʼlumotlarni har kim tekshirishi mumkin:

* OAI-PMH interfeysi: [`/oai/?verb=Identify`](/oai/?verb=Identify);
* faqat oʻqish uchun JSON API: [`/api/v1/`](/api/v1/);
* DOAJ formatidagi metamaʼlumot eksporti: [`/api/v1/doaj-export/`](/api/v1/doaj-export/);
* har qanday maqolaning DOI orqali Crossref yozuvi.""",
            "ru": """Мы указываем только те сервисы, в которых журнал индексируется **фактически**.
На сайте не отображается ни одна метрика или значок, который мы не можем подтвердить.

## В настоящее время

Приведённый ниже перечень ведётся редакцией и обновляется сразу после удовлетворения
заявки. На главной странице отображаются именно те сервисы, которые отмечены здесь как
активные.

## Планируемые заявки

Большинство авторитетных баз требует истории публикаций до рассмотрения заявки. Наша
последовательность:

| Когда | База | Выполняемое требование |
|---|---|---|
| С выпуска 1 | Crossref | членство и регистрация DOI для каждой статьи |
| С выпуска 1 | Google Scholar | метаданные Highwire `citation_*`, индексируемые PDF, карты сайта |
| С выпуска 1 | ORCID | подтверждённые идентификаторы авторов |
| Через 12 месяцев | **DOAJ** | год непрерывного выпуска, не менее 5 научных статей, полные политики |
| Через 24 месяца | Scopus (CSAB) | не менее двух лет выпуска, международный состав редколлегии и авторов, английские аннотации и списки литературы, история цитирования |
| По мере возможности | национальные и отраслевые базы | согласно их критериям |

## Почему мы не показываем значки импакт-фактора

Журнал сознательно **не** показывает значки «impact factor», «SJIF», «Global Impact
Factor», «ICV» и подобные от непроверенных поставщиков. Такие метрики продаются, а не
зарабатываются, и воспринимаются DOAJ, Scopus и Google Scholar как тревожный признак.
Когда журнал будет включён в базу цитирования, публикующую аудируемую метрику, мы дадим
ссылку на страницу самой базы, а не воспроизведём значок.

## Проверка наших метаданных

Опубликованные нами сведения о себе может проверить каждый:

* интерфейс OAI-PMH: [`/oai/?verb=Identify`](/oai/?verb=Identify);
* JSON API только для чтения: [`/api/v1/`](/api/v1/);
* экспорт метаданных в формате DOAJ: [`/api/v1/doaj-export/`](/api/v1/doaj-export/);
* запись Crossref любой статьи по её DOI.""",
        },
    },
    {
        "slug": "privacy",
        "menu_group": "about",
        "order": 10,
        "title": {
            "en": "Privacy Policy",
            "uz": "Maxfiylik siyosati",
            "ru": "Политика конфиденциальности",
        },
        "seo": {
            "en": "What personal data the journal collects, why, how long it is kept, where it is stored, and your rights under Uzbek law ZRU-547.",
            "uz": "Jurnal qanday shaxsiy maʼlumotlarni yigʻadi, nima uchun, qancha saqlaydi, qayerda saqlaydi va OʻzR ZRU-547 boʻyicha huquqlaringiz.",
            "ru": "Какие персональные данные собирает журнал, зачем, как долго и где они хранятся, и ваши права по закону РУз ЗРУ-547.",
        },
        "body": {
            "en": """This policy explains what personal data the journal processes, why, and what you
can do about it. It is written to comply with the Law of the Republic of Uzbekistan
"On Personal Data" (**ZRU-547**) and with general good practice in scholarly publishing.

## Who is responsible

The publisher named on the [Contact](/en/about/contact/) page is the data controller. The
editorial office answers data-protection enquiries at the contact e-mail address.

## What we collect and why

| Data | Why | Legal basis |
|---|---|---|
| Name, e-mail address, password hash | to operate your account | performance of your request to use the service |
| Affiliation, country, ORCID iD, academic degree, areas of expertise | to identify authors correctly and to match reviewers to manuscripts | legitimate interest in editorial quality |
| Manuscript files, metadata, correspondence | to run peer review and publish | performance of the publishing process |
| Reviewer availability, workload, average turnaround, quality rating | to assign reviews fairly | legitimate interest |
| Salted hash of IP address and user agent, session hash | to count article views and downloads without storing identifying data | legitimate interest in usage statistics |
| Contact form messages | to answer your enquiry | your request |

We do **not** collect special categories of personal data, we do not run advertising, and
we do not sell or rent any data to anyone.

## What is public

The following becomes public when an article is published, because it is part of the
scholarly record: author names, affiliations, countries, ORCID iDs, the e-mail address of
the corresponding author only, and the article content. Reviewer identities are **never**
published or disclosed to authors.

## Cookies

The site sets a session cookie when you sign in, a CSRF-protection cookie, and a language
cookie recording your interface language. No advertising or cross-site tracking cookies
are set. If web analytics is enabled, it is a self-hosted Matomo instance configured
without cookies and honouring "Do Not Track".

## Storage and location

Personal data — accounts, reviewer records, manuscripts — is stored in the journal's
primary PostgreSQL database on servers in Uzbekistan. Public article metadata is
additionally distributed to Crossref, indexing services and preservation networks abroad,
as is required for a journal to be citable and archived.

## How long we keep data

* Account and profile data: while the account exists, and for two years afterwards for
  editorial record-keeping.
* Manuscripts that were rejected or withdrawn: five years, then deleted.
* Published articles and their metadata: permanently — they are the scholarly record.
* Raw access events: 90 days, after which only aggregated daily counts are retained.
* Audit log entries: two years.

## Your rights

You may ask us to confirm what data we hold about you, correct it, delete it, or restrict
its processing, and you may object to processing based on legitimate interest. Write to the
editorial office; we answer within 30 days. Some data cannot be deleted: the authorship of
a published article is part of the permanent scholarly record and cannot be withdrawn
without a formal retraction.

## Security

Passwords are stored only as Argon2 hashes. Two-factor authentication is mandatory for
editorial staff. Transport is encrypted with TLS. Access to manuscripts is restricted by
role and logged. Backups are encrypted. Any personal-data breach is reported to affected
users and to the competent authority as the law requires.

## Changes

Material changes to this policy are announced on the site's announcements page. The date
below shows when this text was last updated.""",
            "uz": """Ushbu siyosat jurnal qanday shaxsiy maʼlumotlarni qayta ishlashini, nima uchun
va siz nima qila olishingizni tushuntiradi. U Oʻzbekiston Respublikasining «Shaxsga doir
maʼlumotlar toʻgʻrisida»gi qonuni (**OʻRQ-547**) va ilmiy nashriyot amaliyotining umumiy
qoidalariga muvofiq yozilgan.

## Kim javobgar

[Bogʻlanish](/uz/about/contact/) sahifasida koʻrsatilgan nashriyot maʼlumotlarni qayta
ishlovchi hisoblanadi. Tahririyat maʼlumotlar himoyasi boʻyicha murojaatlarga aloqa
elektron pochtasi orqali javob beradi.

## Nimalarni yigʻamiz va nima uchun

| Maʼlumot | Nima uchun | Huquqiy asos |
|---|---|---|
| Ism, elektron pochta, parol xeshi | hisobingizni yuritish uchun | xizmatdan foydalanish soʻrovingizni bajarish |
| Ish joyi, mamlakat, ORCID, ilmiy daraja, mutaxassislik sohalari | mualliflarni toʻgʻri aniqlash va taqrizchilarni mos qoʻlyozmalarga biriktirish | tahririy sifatdagi qonuniy manfaat |
| Qoʻlyozma fayllari, metamaʼlumotlar, yozishmalar | taqriz jarayonini oʻtkazish va chop etish | nashr jarayonini bajarish |
| Taqrizchining bandligi, yuklamasi, oʻrtacha muddati, sifat bahosi | taqrizlarni adolatli taqsimlash | qonuniy manfaat |
| IP manzil va brauzerning tuzlangan xeshi, sessiya xeshi | shaxsni aniqlovchi maʼlumot saqlamasdan koʻrishlar va yuklab olishlarni hisoblash | statistikaga oid qonuniy manfaat |
| Aloqa shakli xabarlari | murojaatingizga javob berish | soʻrovingiz |

Biz shaxsiy maʼlumotlarning maxsus toifalarini **yigʻmaymiz**, reklama koʻrsatmaymiz va
hech qanday maʼlumotni hech kimga sotmaymiz yoki ijaraga bermaymiz.

## Nima ochiq boʻladi

Maqola chop etilganda quyidagilar ochiq boʻladi, chunki ular ilmiy yozuvning bir qismi:
mualliflar ismi, ish joyi, mamlakati, ORCID identifikatorlari, faqat masʼul muallifning
elektron pochtasi va maqola mazmuni. Taqrizchilar shaxsi **hech qachon** eʼlon
qilinmaydi va mualliflarga oshkor etilmaydi.

## Kukilar

Sayt tizimga kirganingizda sessiya kukisi, CSRF himoyasi kukisi va interfeys tilini
saqlaydigan til kukisini oʻrnatadi. Reklama yoki saytlararo kuzatuv kukilari
oʻrnatilmaydi. Veb-analitika yoqilgan boʻlsa, u kukisiz sozlangan va «Do Not Track»
soʻrovini hurmat qiladigan oʻz serverimizdagi Matomo nusxasidir.

## Saqlash va joylashuv

Shaxsiy maʼlumotlar — hisoblar, taqrizchi yozuvlari, qoʻlyozmalar — Oʻzbekistondagi
serverlarda joylashgan jurnalning asosiy PostgreSQL bazasida saqlanadi. Maqolalarning
ommaviy metamaʼlumotlari qoʻshimcha ravishda Crossref, indeksatsiya xizmatlari va chet
eldagi saqlash tarmoqlariga uzatiladi — bu jurnalning iqtibos qilinishi va arxivlanishi
uchun zarur.

## Qancha vaqt saqlaymiz

* Hisob va profil maʼlumotlari: hisob mavjud boʻlgunga qadar va undan keyin tahririy
  hisobot uchun ikki yil.
* Rad etilgan yoki qaytarib olingan qoʻlyozmalar: besh yil, soʻngra oʻchiriladi.
* Chop etilgan maqolalar va ularning metamaʼlumotlari: doimiy — bu ilmiy yozuv.
* Xom kirish hodisalari: 90 kun, undan keyin faqat kunlik jamlanma saqlanadi.
* Audit jurnali yozuvlari: ikki yil.

## Huquqlaringiz

Siz bizdan sizga oid qanday maʼlumot saqlanayotganini tasdiqlashni, uni tuzatishni,
oʻchirishni yoki qayta ishlashni cheklashni soʻrashingiz, shuningdek qonuniy manfaatga
asoslangan qayta ishlashga eʼtiroz bildirishingiz mumkin. Tahririyatga yozing; biz 30 kun
ichida javob beramiz. Baʼzi maʼlumotlarni oʻchirib boʻlmaydi: chop etilgan maqola
mualligi doimiy ilmiy yozuvning qismi boʻlib, rasmiy chaqirib olishsiz bekor qilinmaydi.

## Xavfsizlik

Parollar faqat Argon2 xeshi sifatida saqlanadi. Tahririyat xodimlari uchun ikki bosqichli
autentifikatsiya majburiy. Uzatish TLS bilan shifrlanadi. Qoʻlyozmalarga kirish rol
boʻyicha cheklangan va qayd etiladi. Zaxira nusxalar shifrlanadi. Shaxsiy maʼlumotlar
buzilishi haqida qonun talab qilganidek foydalanuvchilarga va vakolatli organga xabar
beriladi.

## Oʻzgarishlar

Ushbu siyosatdagi jiddiy oʻzgarishlar saytning eʼlonlar sahifasida bildiriladi. Quyidagi
sana matn oxirgi marta qachon yangilanganini koʻrsatadi.""",
            "ru": """Настоящая политика объясняет, какие персональные данные обрабатывает журнал,
зачем и что вы можете с этим сделать. Она составлена в соответствии с Законом Республики
Узбекистан «О персональных данных» (**ЗРУ-547**) и общей добросовестной практикой научного
издательского дела.

## Кто отвечает

Издатель, указанный на странице [Контакты](/ru/about/contact/), является оператором
персональных данных. Редакция отвечает на обращения по защите данных по контактному
адресу электронной почты.

## Что мы собираем и зачем

| Данные | Зачем | Правовое основание |
|---|---|---|
| Имя, адрес электронной почты, хеш пароля | ведение вашей учётной записи | исполнение вашего запроса на использование сервиса |
| Место работы, страна, ORCID, учёная степень, области экспертизы | корректная идентификация авторов и подбор рецензентов | законный интерес в качестве рецензирования |
| Файлы рукописей, метаданные, переписка | проведение рецензирования и публикация | исполнение издательского процесса |
| Доступность рецензента, нагрузка, средний срок, оценка качества | справедливое распределение рецензий | законный интерес |
| Солёный хеш IP-адреса и user agent, хеш сессии | подсчёт просмотров и загрузок без хранения идентифицирующих данных | законный интерес в статистике |
| Сообщения из формы обратной связи | ответ на ваше обращение | ваш запрос |

Мы **не** собираем специальные категории персональных данных, не показываем рекламу и не
продаём и не сдаём данные никому.

## Что становится публичным

При публикации статьи публичными становятся, как часть научной записи: имена авторов,
места работы, страны, идентификаторы ORCID, адрес электронной почты только
корреспондирующего автора и содержание статьи. Личности рецензентов **никогда** не
публикуются и не раскрываются авторам.

## Файлы cookie

Сайт устанавливает сессионный cookie при входе, cookie защиты от CSRF и языковой cookie,
запоминающий язык интерфейса. Рекламные и межсайтовые отслеживающие cookie не
устанавливаются. Если включена веб-аналитика, это собственный экземпляр Matomo,
настроенный без cookie и соблюдающий «Do Not Track».

## Хранение и местоположение

Персональные данные — учётные записи, сведения о рецензентах, рукописи — хранятся в
основной базе PostgreSQL на серверах в Узбекистане. Публичные метаданные статей
дополнительно передаются в Crossref, службы индексации и зарубежные сети хранения, что
необходимо для цитируемости и архивирования журнала.

## Сроки хранения

* Данные учётной записи и профиля: пока существует учётная запись, и два года после — для
  редакционного учёта.
* Отклонённые или отозванные рукописи: пять лет, затем удаляются.
* Опубликованные статьи и их метаданные: бессрочно — это научная запись.
* Необработанные события доступа: 90 дней, далее хранятся только суточные агрегаты.
* Записи журнала аудита: два года.

## Ваши права

Вы вправе запросить подтверждение того, какие данные о вас хранятся, их исправление,
удаление или ограничение обработки, а также возразить против обработки на основании
законного интереса. Напишите в редакцию; мы ответим в течение 30 дней. Некоторые данные
удалить нельзя: авторство опубликованной статьи является частью постоянной научной записи
и не может быть отозвано без официального ретрагирования.

## Безопасность

Пароли хранятся только в виде хешей Argon2. Двухфакторная аутентификация обязательна для
редакционного персонала. Передача данных шифруется по TLS. Доступ к рукописям ограничен
ролями и журналируется. Резервные копии шифруются. О любом инциденте с персональными
данными сообщается затронутым пользователям и уполномоченному органу в соответствии с
законом.

## Изменения

О существенных изменениях этой политики сообщается на странице объявлений сайта. Дата ниже
показывает, когда текст был обновлён в последний раз.""",
        },
    },
    {
        "slug": "contact",
        "menu_group": "about",
        "order": 11,
        "title": {"en": "Contact", "uz": "Bogʻlanish", "ru": "Контакты"},
        "seo": {
            "en": "How to reach the editorial office of ALGORITHM: Review of Economic Research.",
            "uz": "«ALGORITM» — iqtisodiy tadqiqotlar sharhi tahririyati bilan qanday bogʻlanish mumkin.",
            "ru": "Как связаться с редакцией журнала «АЛГОРИТМ» — обзор экономических исследований.",
        },
        "body": {
            "en": """The editorial office answers within three working days. Please use the form
below or write to the address shown beside it.

**Before you write:** most questions are already answered in the
[Author Guidelines](/en/for-authors/guidelines/), the
[Peer Review Process](/en/about/peer-review/) and the
[Publication Ethics](/en/about/publication-ethics/) statement.

## Who to write to about what

* **Status of a submitted manuscript** — sign in and open your dashboard first; it shows
  the current state and the responsible editor. Write to us only if the state has not
  changed for longer than the stated target duration.
* **Technical problems with the submission system** — describe what you did, what you
  expected and what happened, and include the submission reference (`ARER-YYYY-NNNN`).
* **Reviewer invitations** — reply to the invitation e-mail, or accept or decline from your
  reviewer dashboard.
* **Ethical concerns about a published article** — write to the editorial office with the
  DOI and a specific, substantiated description of the concern.
* **Media and partnership enquiries** — use the general contact address.

## Postal correspondence

Official letters should be sent to the publisher's postal address shown beside this text.
Please do not post manuscripts: they are accepted only through the online system.""",
            "uz": """Tahririyat uch ish kuni ichida javob beradi. Quyidagi shakldan foydalaning yoki
yonida koʻrsatilgan manzilga yozing.

**Yozishdan oldin:** koʻpchilik savollarga
[Mualliflar uchun yoʻriqnoma](/uz/for-authors/guidelines/),
[Taqriz jarayoni](/uz/about/peer-review/) va
[Nashr etikasi](/uz/about/publication-ethics/) sahifalarida javob berilgan.

## Qaysi masala boʻyicha kimga yozish kerak

* **Yuborilgan qoʻlyozma holati** — avval tizimga kiring va boshqaruv panelini oching; u
  yerda joriy holat va masʼul muharrir koʻrsatilgan. Holat belgilangan muddatdan uzoq
  vaqt oʻzgarmasa, bizga yozing.
* **Yuborish tizimidagi texnik muammolar** — nima qilganingiz, nimani kutganingiz va nima
  yuz berganini tavsiflang, qoʻlyozma raqamini (`ARER-YYYY-NNNN`) koʻrsating.
* **Taqriz takliflari** — taklif xatiga javob bering yoki taqrizchi panelidan qabul qiling
  yoxud rad eting.
* **Chop etilgan maqolaga oid etik masalalar** — DOI va aniq, asoslangan tavsif bilan
  tahririyatga yozing.
* **Ommaviy axborot vositalari va hamkorlik** — umumiy aloqa manzilidan foydalaning.

## Pochta orqali yozishmalar

Rasmiy xatlar ushbu matn yonida koʻrsatilgan nashriyot pochta manziliga yuboriladi.
Qoʻlyozmalarni pochta orqali yubormang: ular faqat onlayn tizim orqali qabul
qilinadi.""",
            "ru": """Редакция отвечает в течение трёх рабочих дней. Воспользуйтесь формой ниже или
напишите по адресу, указанному рядом.

**Перед тем как писать:** на большинство вопросов уже отвечают
[Руководство для авторов](/ru/for-authors/guidelines/),
[Процесс рецензирования](/ru/about/peer-review/) и
[Издательская этика](/ru/about/publication-ethics/).

## Кому писать по какому вопросу

* **Статус поданной рукописи** — сначала войдите в систему и откройте личный кабинет; там
  указаны текущее состояние и ответственный редактор. Пишите нам, если состояние не
  меняется дольше заявленного срока.
* **Технические проблемы системы подачи** — опишите, что вы делали, что ожидали и что
  произошло, укажите номер рукописи (`ARER-YYYY-NNNN`).
* **Приглашения к рецензированию** — ответьте на письмо-приглашение либо примите или
  отклоните его в кабинете рецензента.
* **Этические вопросы по опубликованной статье** — напишите в редакцию, указав DOI и
  конкретное обоснованное описание проблемы.
* **СМИ и партнёрство** — используйте общий контактный адрес.

## Почтовая переписка

Официальные письма направляйте на почтовый адрес издателя, указанный рядом с этим
текстом. Не присылайте рукописи почтой: они принимаются только через онлайн-систему.""",
        },
    },
]
