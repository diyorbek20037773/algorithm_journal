"""Uzbek (Latin) and Russian translations — part 8: the account pages.

Strings for the allauth pages that were still rendered by the stock,
unstyled templates (e-mail verification sent, password reset flow, password
change, e-mail management, reauthentication).  Same shape as the other parts.
"""

from __future__ import annotations

PART_8: dict[str, tuple[str, str]] = {
    "Check your inbox": ("Pochtangizni tekshiring", "Проверьте почту"),
    "We have sent a confirmation link to your e-mail address. Open it to activate your account; the link is valid for three days.": (
        "E-pochtangizga tasdiqlash havolasini yubordik. Hisobingizni faollashtirish uchun uni oching; havola uch kun amal qiladi.",
        "Мы отправили ссылку для подтверждения на ваш e-mail. Откройте её, чтобы активировать аккаунт; ссылка действует три дня.",
    ),
    "Nothing there? Look in the spam folder, or sign in and ask for the message to be sent again.": (
        "Xat kelmadimi? Spam papkasini tekshiring yoki tizimga kirib, xatni qayta yuborishni soʻrang.",
        "Письма нет? Проверьте папку «Спам» или войдите и запросите повторную отправку.",
    ),
    "If an account exists for that address, we have sent a link to choose a new password.": (
        "Agar bu manzilda hisob boʻlsa, yangi parol tanlash uchun havola yubordik.",
        "Если для этого адреса есть аккаунт, мы отправили ссылку для выбора нового пароля.",
    ),
    "Back to sign in": ("Kirish sahifasiga qaytish", "Вернуться ко входу"),
    "Choose a new password": ("Yangi parol tanlang", "Выберите новый пароль"),
    "This link has expired": ("Havola muddati tugagan", "Срок действия ссылки истёк"),
    "The password reset link is invalid, possibly because it has already been used.": (
        "Parolni tiklash havolasi yaroqsiz — ehtimol, u allaqachon ishlatilgan.",
        "Ссылка для сброса пароля недействительна — возможно, она уже использована.",
    ),
    "Request a new link": ("Yangi havola soʻrash", "Запросить новую ссылку"),
    "At least 12 characters; avoid anything that appears in your name or e-mail.": (
        "Kamida 12 belgi; ismingiz yoki e-pochtangizdagi soʻzlardan foydalanmang.",
        "Не менее 12 символов; не используйте части имени или e-mail.",
    ),
    "Save the new password": ("Yangi parolni saqlash", "Сохранить новый пароль"),
    "Password changed": ("Parol oʻzgartirildi", "Пароль изменён"),
    "Your new password is in place. You can sign in with it now.": (
        "Yangi parolingiz oʻrnatildi. Endi u bilan kirishingiz mumkin.",
        "Новый пароль установлен. Теперь можно войти с ним.",
    ),
    "Change your password": ("Parolni oʻzgartirish", "Изменить пароль"),
    "Set a password": ("Parol oʻrnatish", "Установить пароль"),
    "Your account was created through ORCID or Google. A password lets you sign in without them as well.": (
        "Hisobingiz ORCID yoki Google orqali yaratilgan. Parol ularsiz ham kirish imkonini beradi.",
        "Аккаунт создан через ORCID или Google. Пароль позволит входить и без них.",
    ),
    "Save the password": ("Parolni saqlash", "Сохранить пароль"),
    "E-mail addresses": ("E-pochta manzillari", "Адреса e-mail"),
    "Editorial correspondence goes to your primary address.": (
        "Tahririyat xatlari asosiy manzilingizga yuboriladi.",
        "Редакционная переписка приходит на основной адрес.",
    ),
    "Verified": ("Tasdiqlangan", "Подтверждён"),
    "Unverified": ("Tasdiqlanmagan", "Не подтверждён"),
    "Make primary": ("Asosiy qilish", "Сделать основным"),
    "Re-send verification": ("Tasdiqlashni qayta yuborish", "Отправить подтверждение снова"),
    "You have no e-mail address on file. Add one so you can receive editorial correspondence and reset your password.": (
        "Hisobingizda e-pochta manzili yoʻq. Tahririyat xatlarini olish va parolni tiklash uchun manzil qoʻshing.",
        "В аккаунте нет адреса e-mail. Добавьте его, чтобы получать письма редакции и восстанавливать пароль.",
    ),
    "Add an e-mail address": ("E-pochta manzili qoʻshish", "Добавить адрес e-mail"),
    "Add address": ("Manzil qoʻshish", "Добавить адрес"),
    "Change your e-mail address": ("E-pochta manzilini oʻzgartirish", "Изменить адрес e-mail"),
    "A confirmation link has been sent to %(email)s. The change takes effect once you open it.": (
        "%(email)s manziliga tasdiqlash havolasi yuborildi. Oʻzgarish uni ochganingizdan keyin kuchga kiradi.",
        "Ссылка для подтверждения отправлена на %(email)s. Изменение вступит в силу после её открытия.",
    ),
    "Send confirmation": ("Tasdiqlash yuborish", "Отправить подтверждение"),
    "Account inactive": ("Hisob faol emas", "Аккаунт неактивен"),
    "This account has been deactivated. Contact the editorial office if you believe this is a mistake.": (
        "Bu hisob oʻchirilgan. Agar bu xato deb hisoblasangiz, tahririyatga murojaat qiling.",
        "Этот аккаунт деактивирован. Если это ошибка, свяжитесь с редакцией.",
    ),
    "Confirm it is you": ("Bu siz ekaningizni tasdiqlang", "Подтвердите, что это вы"),
    "Enter your password once more to continue with this sensitive change.": (
        "Ushbu muhim oʻzgarishni davom ettirish uchun parolingizni yana bir bor kiriting.",
        "Введите пароль ещё раз, чтобы продолжить это важное изменение.",
    ),
    "Registration closed": ("Roʻyxatdan oʻtish yopiq", "Регистрация закрыта"),
    "New accounts are not being accepted at the moment. Please contact the editorial office.": (
        "Hozircha yangi hisoblar qabul qilinmaydi. Iltimos, tahririyatga murojaat qiling.",
        "Новые аккаунты сейчас не принимаются. Пожалуйста, свяжитесь с редакцией.",
    ),
    # --- account e-mails ---------------------------------------------------
    "Confirm your e-mail address — %(site)s": (
        "E-pochta manzilingizni tasdiqlang — %(site)s",
        "Подтвердите адрес e-mail — %(site)s",
    ),
    "Thank you for registering with %(site)s.\n\nPlease confirm your e-mail address by opening this link:\n\n%(url)s\n\nThe link is valid for three days. If you did not create an account, you can ignore this message.": (
        "%(site)s da roʻyxatdan oʻtganingiz uchun rahmat.\n\nE-pochta manzilingizni tasdiqlash uchun ushbu havolani oching:\n\n%(url)s\n\nHavola uch kun amal qiladi. Agar hisob yaratmagan boʻlsangiz, bu xatni eʼtiborsiz qoldiring.",
        "Спасибо за регистрацию в %(site)s.\n\nПодтвердите адрес e-mail, открыв эту ссылку:\n\n%(url)s\n\nСсылка действует три дня. Если вы не создавали аккаунт, просто проигнорируйте это письмо.",
    ),
    "Reset your password — %(site)s": (
        "Parolni tiklash — %(site)s",
        "Сброс пароля — %(site)s",
    ),
    "Someone asked to reset the password for your %(site)s account.\n\nChoose a new password here:\n\n%(url)s\n\nIf this was not you, no action is needed — your password stays as it is.": (
        "Kimdir %(site)s dagi hisobingiz parolini tiklashni soʻradi.\n\nYangi parolni bu yerda tanlang:\n\n%(url)s\n\nAgar bu siz boʻlmasangiz, hech narsa qilish shart emas — parolingiz oʻzgarmaydi.",
        "Кто-то запросил сброс пароля для вашего аккаунта в %(site)s.\n\nВыберите новый пароль здесь:\n\n%(url)s\n\nЕсли это были не вы, ничего делать не нужно — пароль останется прежним.",
    ),
}
