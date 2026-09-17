"""Uzbek (Latin) and Russian translations — part 9: the journal PDF.

Strings for the issue builder's journal layout (issue PDF, offprints, sending
to authors) and the labels printed inside the PDF.  Same shape as the other
parts.
"""

from __future__ import annotations

PART_9: dict[str, tuple[str, str]] = {
    "%(count)s article(s) added to the issue.": (
        "Songa %(count)s ta maqola qoʻshildi.",
        "В выпуск добавлено статей: %(count)s.",
    ),
    "%(count)s article(s) removed from the issue.": (
        "Sondan %(count)s ta maqola olib tashlandi.",
        "Из выпуска удалено статей: %(count)s.",
    ),
    "%(month)s %(year)s · No. %(number)s": (
        "%(year)s-yil, %(month)s · %(number)s-son",
        "%(month)s %(year)s г. · № %(number)s",
    ),
    "%(month)s · No. %(number)s": ("%(month)s · %(number)s-son", "%(month)s · № %(number)s"),
    "%(pages)s pages": ("%(pages)s sahifa", "Страниц: %(pages)s"),
    "Add articles to this issue": ("Songa maqola qoʻshish", "Добавить статьи в выпуск"),
    "Add selected to the issue": ("Tanlanganlarni songa qoʻshish", "Добавить выбранные в выпуск"),
    "Address: %(address)s": ("Manzil: %(address)s", "Адрес: %(address)s"),
    "All articles are published in open access under the Creative Commons Attribution 4.0 International licence (CC BY 4.0).": (
        "Barcha maqolalar Creative Commons Attribution 4.0 International (CC BY 4.0) litsenziyasi asosida ochiq kirishda nashr etiladi.",
        "Все статьи публикуются в открытом доступе по лицензии Creative Commons Attribution 4.0 International (CC BY 4.0).",
    ),
    "Article #%(pk)s has no PDF galley.": (
        "#%(pk)s-maqolaning PDF fayli (galley) yoʻq.",
        "У статьи #%(pk)s нет PDF-файла (гранки).",
    ),
    "Assembles the cover, editorial board, contents and every article in the journal layout, numbers the pages and prepares an offprint for each author.": (
        "Muqova, tahrir hayʼati, mundarija va barcha maqolalarni jurnal maketiga yigʻadi, sahifalarni raqamlaydi hamda har bir muallif uchun alohida nusxa tayyorlaydi.",
        "Собирает обложку, редколлегию, содержание и все статьи в макет журнала, нумерует страницы и готовит оттиск для каждого автора.",
    ),
    "Build the issue PDF first; this article has no offprint yet.": (
        "Avval son PDF faylini shakllantiring: bu maqolaning nusxasi hali yoʻq.",
        "Сначала соберите PDF выпуска: у этой статьи ещё нет оттиска.",
    ),
    "Build the journal PDF": ("Jurnal PDF faylini shakllantirish", "Сформировать PDF журнала"),
    "Contents": ("Mundarija", "Содержание"),
    "Dear author,\n\nYour article **%(title)s** has been typeset in the journal layout (%(issue)s, pp. %(start)s–%(end)s).\n\nThe PDF is attached. You can also download it from your dashboard: %(url)s\n\nWith best regards,\nthe editorial office": (
        "Hurmatli muallif,\n\n**%(title)s** nomli maqolangiz jurnal maketiga joylashtirildi (%(issue)s, %(start)s–%(end)s-betlar).\n\nPDF fayl xatga ilova qilingan. Uni shaxsiy kabinetingizdan ham yuklab olishingiz mumkin: %(url)s\n\nHurmat bilan,\ntahririyat",
        "Уважаемый автор!\n\nВаша статья **%(title)s** свёрстана в макете журнала (%(issue)s, с. %(start)s–%(end)s).\n\nPDF-файл приложен к письму. Его также можно скачать в личном кабинете: %(url)s\n\nС уважением,\nредакция",
    ),
    "Download the journal PDF": ("Jurnal PDF faylini yuklab olish", "Скачать PDF журнала"),
    "Download the offprint": ("Maqola nusxasini yuklab olish", "Скачать оттиск"),
    "Electronic edition, %(month)s %(year)s.": (
        "Elektron nashr, %(year)s-yil, %(month)s.",
        "Электронное издание, %(month)s %(year)s г.",
    ),
    "Every article needs a PDF galley before the journal can be built.": (
        "Jurnalni shakllantirishdan oldin har bir maqolaga PDF fayl yuklanishi kerak.",
        "Перед сборкой журнала у каждой статьи должен быть PDF-файл.",
    ),
    "Every ready article is already in an issue.": (
        "Tayyor maqolalarning barchasi allaqachon sonlarga kiritilgan.",
        "Все готовые статьи уже включены в выпуски.",
    ),
    "First page number": ("Birinchi sahifa raqami", "Номер первой страницы"),
    "Journal PDF": ("Jurnal PDF fayli", "PDF журнала"),
    "Journal layout": ("Jurnal maketi", "Макет журнала"),
    "Keep 1, or continue the numbering of a previous part.": (
        "1 qoldiring yoki oldingi qismning raqamlashini davom ettiring.",
        "Оставьте 1 или продолжите нумерацию предыдущей части.",
    ),
    "Language of the layout": ("Maket tili", "Язык макета"),
    "No author e-mail address is recorded for this article.": (
        "Bu maqola mualliflarining e-pochta manzili kiritilmagan.",
        "Для этой статьи не указан e-mail авторов.",
    ),
    "Optional page after the editorial board in every issue PDF, e.g. the list of accredited specialities. One item per line; a line starting with # is a heading.": (
        "Har bir son PDF faylida tahrir hayʼatidan keyingi ixtiyoriy sahifa, masalan, OAK ixtisosliklari roʻyxati. Har bir band alohida qatorda; # bilan boshlangan qator sarlavha boʻladi.",
        "Необязательная страница после редколлегии в каждом PDF выпуска, например перечень специальностей ВАК. Один пункт на строку; строка, начинающаяся с #, — заголовок.",
    ),
    "Order": ("Tartib", "Порядок"),
    "Page number of the cover; raise it to continue the pagination of a previous part.": (
        "Muqovaning sahifa raqami; oldingi qism raqamlashini davom ettirish uchun oshiring.",
        "Номер страницы обложки; увеличьте, чтобы продолжить нумерацию предыдущей части.",
    ),
    "Publisher: %(name)s": ("Nashriyot: %(name)s", "Издатель: %(name)s"),
    "Rebuild the journal PDF": (
        "Jurnal PDF faylini qayta shakllantirish",
        "Пересобрать PDF журнала",
    ),
    "Registration certificate No. %(number)s": (
        "Roʻyxatdan oʻtganlik guvohnomasi № %(number)s",
        "Свидетельство о регистрации № %(number)s",
    ),
    "Remove selected from the issue": (
        "Tanlanganlarni sondan chiqarish",
        "Убрать выбранные из выпуска",
    ),
    "Section Editors": ("Boʻlim muharrirlari", "Редакторы разделов"),
    "Select": ("Tanlash", "Выбрать"),
    "Select all": ("Barchasini tanlash", "Выбрать все"),
    "Send again": ("Qayta yuborish", "Отправить снова"),
    "Send to authors": ("Mualliflarga yuborish", "Отправить авторам"),
    "Sent to the authors on %(date)s.": (
        "Mualliflarga %(date)s da yuborilgan.",
        "Отправлено авторам %(date)s.",
    ),
    "The PDF galley of article #%(pk)s could not be placed.": (
        "#%(pk)s-maqolaning PDF faylini maketga joylab boʻlmadi.",
        "PDF-файл статьи #%(pk)s не удалось разместить в макете.",
    ),
    "The PDF galley of article #%(pk)s could not be read.": (
        "#%(pk)s-maqolaning PDF faylini oʻqib boʻlmadi.",
        "PDF-файл статьи #%(pk)s не удалось прочитать.",
    ),
    "The PDF galley of article #%(pk)s is damaged.": (
        "#%(pk)s-maqolaning PDF fayli buzilgan.",
        "PDF-файл статьи #%(pk)s повреждён.",
    ),
    "The PDF galley of article #%(pk)s is empty.": (
        "#%(pk)s-maqolaning PDF fayli boʻsh.",
        "PDF-файл статьи #%(pk)s пуст.",
    ),
    "The article in the journal layout, built with the issue PDF.": (
        "Jurnal maketidagi maqola; son PDF fayli bilan birga yaratiladi.",
        "Статья в макете журнала; создаётся вместе с PDF выпуска.",
    ),
    "The issue PDF could not be built. The error has been logged.": (
        "Son PDF faylini shakllantirib boʻlmadi. Xato jurnalga yozildi.",
        "Не удалось собрать PDF выпуска. Ошибка записана в журнал.",
    ),
    "The issue PDF is being built. This page updates when it is ready.": (
        "Son PDF fayli shakllantirilmoqda. Tayyor boʻlganda sahifa yangilanadi.",
        "PDF выпуска собирается. Страница обновится, когда он будет готов.",
    ),
    "The offprint appears here after the journal PDF of its issue has been built in the issue builder.": (
        "Maqola nusxasi son konstruktorida jurnal PDF fayli shakllantirilgandan keyin shu yerda paydo boʻladi.",
        "Оттиск появится здесь после сборки PDF выпуска в конструкторе выпуска.",
    ),
    "The offprint has been sent to the authors.": (
        "Maqola nusxasi mualliflarga yuborildi.",
        "Оттиск отправлен авторам.",
    ),
    "Typeset in %(issue)s, pages %(start)s–%(end)s.": (
        "%(issue)s soniga joylashtirilgan, %(start)s–%(end)s-betlar.",
        "Свёрстано в выпуске %(issue)s, с. %(start)s–%(end)s.",
    ),
    "Upload a PDF galley for these articles first: %(items)s": (
        "Avval quyidagi maqolalarga PDF fayl yuklang: %(items)s",
        "Сначала загрузите PDF-файлы для статей: %(items)s",
    ),
    "Your article in the journal layout": (
        "Maqolangiz jurnal maketida",
        "Ваша статья в макете журнала",
    ),
    "Your article in the journal layout: %(title)s": (
        "Maqolangiz jurnal maketida: %(title)s",
        "Ваша статья в макете журнала: %(title)s",
    ),
    "building": ("shakllantirilmoqda", "собирается"),
    "failed": ("xato", "ошибка"),
    "first page number": ("birinchi sahifa raqami", "номер первой страницы"),
    "issue PDF information page": (
        "son PDF faylidagi maʼlumot sahifasi",
        "информационная страница PDF выпуска",
    ),
    "layout built at": ("maket yaratilgan vaqt", "макет собран"),
    "layout error": ("maket xatosi", "ошибка макета"),
    "layout status": ("maket holati", "статус макета"),
    "no PDF galley": ("PDF fayl yoʻq", "нет PDF-файла"),
    "not built": ("shakllantirilmagan", "не собран"),
    "offprint PDF": ("maqola nusxasi (PDF)", "оттиск (PDF)"),
    "offprint sent to authors": ("nusxa mualliflarga yuborilgan", "оттиск отправлен авторам"),
    "pages in the issue PDF": ("son PDF faylidagi sahifalar", "страниц в PDF выпуска"),
    "print language": ("maket tili", "язык макета"),
    "queued": ("navbatda", "в очереди"),
    "ready": ("tayyor", "готов"),
    "sent": ("yuborilgan", "отправлено"),
    "Abstracting and indexing": ("Referatlash va indekslash", "Реферирование и индексирование"),
    "Full-page picture behind the back cover. Leave empty for the built-in artwork.": (
        "Orqa muqova ortidagi butun sahifali rasm. Boʻsh qoldirilsa, tayyor bezak ishlatiladi.",
        "Полностраничное изображение на задней обложке. Оставьте пустым для встроенного оформления.",
    ),
    "Full-page picture behind the generated cover (A4 portrait, at least 1240×1754 px). It is darkened so the title stays readable. Leave empty for the built-in artwork.": (
        "Muqova ortidagi butun sahifali rasm (A4 tik, kamida 1240×1754 px). Sarlavha oʻqilishi uchun u qoraytiriladi. Boʻsh qoldirilsa, tayyor bezak ishlatiladi.",
        "Полностраничное изображение под обложкой (A4 книжная, не менее 1240×1754 px). Оно затемняется, чтобы заголовок читался. Оставьте пустым для встроенного оформления.",
    ),
    "In this issue": ("Ushbu sonda", "В этом выпуске"),
    "Light full-page picture (frame, watermark) behind the editorial board, contents and article pages. Keep it pale: the text is printed on top.": (
        "Tahrir hayʼati, mundarija va maqola sahifalari ortidagi och rangli butun sahifali rasm (ramka, suv belgisi). Och boʻlsin: matn uning ustida chiqadi.",
        "Светлое полностраничное изображение (рамка, водяной знак) под страницами редколлегии, содержания и статей. Оно должно быть бледным: текст печатается поверх.",
    ),
    "Open access · CC BY 4.0": ("Ochiq kirish · CC BY 4.0", "Открытый доступ · CC BY 4.0"),
    "Phone": ("Telefon", "Телефон"),
    "Website": ("Veb-sayt", "Сайт"),
    "issue PDF back cover background": (
        "son PDF fayli orqa muqovasi foni",
        "фон задней обложки PDF выпуска",
    ),
    "issue PDF cover background": ("son PDF fayli muqovasi foni", "фон обложки PDF выпуска"),
    "issue PDF page background": ("son PDF fayli sahifalari foni", "фон страниц PDF выпуска"),
}
