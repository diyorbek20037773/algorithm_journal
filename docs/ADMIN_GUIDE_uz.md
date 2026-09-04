# Administrator qoʻllanmasi

**«ALGORITM» — iqtisodiy tadqiqotlar sharhi (ARER)**

Ushbu hujjat texnik administrator uchun: sayt sozlamalari, sahifalar, tahrir
hayʼati, foydalanuvchilar, integratsiyalar va kundalik texnik xizmat.
Skrinshotlar [`screenshots/`](screenshots/) papkasida.

---

## 1. Kirish va xavfsizlik

1. `/accounts/login/` orqali `admin@algorithm-journal.uz` hisobi bilan kiring
   (dastlabki parol `Algorithm2026!` — **darhol almashtiring**).
2. Tizim TOTP autentifikatorini roʻyxatdan oʻtkazishni talab qiladi. QR kodni
   skanerlang, olti xonali kodni kiriting va **oʻnta tiklash kodini** parol
   menejeringizda saqlang.
3. Django admin paneli `/admin/` manzilida. U ham 2FA bilan himoyalangan.

**Parol siyosati:** kamida 12 belgi, keng tarqalgan parollar taqiqlangan,
Argon2 xeshlash. **Bloklash:** 10 marta xato kiritishdan keyin IP 30 daqiqaga
bloklanadi (django-axes).

---

## 2. Sayt sozlamalari — birinchi navbatda toʻldiring

**Admin → Core → Site settings**. Bu yagona yozuv; uni oʻchirib boʻlmaydi.

Har bir matn maydoni toʻrt tilda (yorliqlar: EN, UZ, ЎЗ, RU). Oʻzbek kirill
varianti lotin matnidan avtomatik yaratiladi — kerak boʻlsa qoʻlda tuzating.

| Maydon | Nima yoziladi | Toʻldirilmasa |
|---|---|---|
| Jurnal nomi | Toʻliq nom, toʻrt tilda | Standart nom koʻrsatiladi |
| e-ISSN | ISSN markazidan olingan raqam | «e-ISSN: kutilmoqda» deb chiqadi, Crossref depozitida ISSN boʻlmaydi |
| Guvohnoma raqami va sanasi | OAV guvohnomasi | Pastki panelda koʻrsatilmaydi |
| Nashriyot nomi va manzili | Muassis tashkilotning rasmiy nomi | «Muassis tashkilot (tasdiqlanishi kerak)» |
| DOI prefiksi | Crossref bergan `10.xxxxx` | `.env` dagi `DOI_PREFIX` ishlatiladi |
| Aloqa e-pochtasi, telefoni, manzili | Tahririyat maʼlumotlari | Standart qiymatlar |
| Logotip, favicon | SVG yoki PNG | Matnli word-mark chiziladi |
| Maksimal oʻxshashlik (%) | Standart 20 | 20 % |
| Eʼlon paneli matni | Vaqtinchalik xabar (masalan, chaqiruv) | Panel koʻrsatilmaydi |
| Indeksatsiya xizmatlari | Faqat haqiqiylarini belgilang | Bosh sahifada blok chiqmaydi |

---

## 3. Sahifalar (CMS)

**Admin → Core → Pages**. Har bir sahifa Markdown formatida, toʻrt tilda.

* Seed bilan kelgan barcha sahifalarda **«Tahririy tekshiruv talab qiladi»**
  belgisi qoʻyilgan — oʻzbek, oʻzbek kirill va rus matnlarini tekshirib, keyin
  belgini olib tashlang.
* `menu_group` sahifa qayerda chiqishini belgilaydi: `about`, `authors`,
  `reviewers`, `footer` yoki `none`.
* `menu_order` menyudagi tartibni belgilaydi.
* Slugni oʻzgartirmang: ular URL manzillarida va boshqa sahifalardagi
  havolalarda ishlatiladi.

Markdown quyidagilarni qoʻllab-quvvatlaydi: sarlavhalar, roʻyxatlar, jadvallar,
havolalar, iqtiboslar, `code`. HTML tozalanadi — skript ishlamaydi.

---

## 4. Tahrir hayʼati

**Admin → Journal → Editorial board members**.

Seed 12 ta **«DEMO — replace»** yozuvini yaratadi. Ular saytda ogohlantirish
banneri bilan koʻrsatiladi. Har birini haqiqiy aʼzo bilan almashtiring:

* toʻliq ism (toʻrt tilda), ilmiy daraja va unvon, ish joyi, mamlakat;
* ORCID (`0000-0000-0000-0000` formatida) va Scopus Author ID, agar boʻlsa;
* elektron pochta (saytda `@` belgisi maskalanadi);
* rol: bosh muharrir, oʻrinbosar, masʼul kotib, boʻlim muharriri, hayʼat aʼzosi,
  xalqaro maslahat kengashi, taqrizchilar kengashi;
* `is_demo` belgisini **olib tashlang** — banner shundan keyin yoʻqoladi.

OAK talabi: kamida uchta fan doktori (DSc). Bu daraja maydoniga yoziladi.

---

## 5. Boʻlimlar va boʻlim muharrirlari

**Admin → Journal → Sections**. Toʻqqizta boʻlim seed bilan keladi. Har bir
boʻlimga **boʻlim muharrirlarini** biriktiring — ular oʻsha boʻlimning
navbatlarini koʻradi va yangi qoʻlyozma kelganda xabar oladi. Boʻlimda aynan
bitta muharrir boʻlsa, tizim uni avtomatik masʼul qilib tayinlaydi.

---

## 6. Foydalanuvchilar va rollar

**Admin → Accounts → Users**. Rol — bu Django guruhi:

| Guruh | Nimaga ruxsat |
|---|---|
| `author` | Qoʻlyozma yuborish, oʻz holatini kuzatish |
| `reviewer` | Taqriz taklifi va shakli |
| `section_editor` | Oʻz boʻlimlari navbatlari, taqrizchi taklifi, tavsiya |
| `editor_in_chief` | Barcha qoʻlyozmalar, yakuniy qaror, sonni chop etish |
| `production_editor` | Nashrga tayyorlash, nashr fayllari, DOI, son yigʻuvchi |
| `admin` | Django admin, sozlamalar, integratsiyalar, audit |

Taqrizchi sifatida ishlashi uchun foydalanuvchida **«Taqrizchi sifatida
mavjud»** belgisi boʻlishi kerak — u taqrizchi qidiruviga shu orqali tushadi.
Profilida mutaxassislik va JEL kodlarini toʻldiring: qidiruv shularga tayanadi.

Hisobni **oʻchirmang** — u qoʻlyozmalar va taqrizlarga bogʻlangan. Faoliyatini
toʻxtatish uchun `is_active` ni olib tashlang.

---

## 7. Elektron xat shablonlari

**Admin → Core → E-mail templates**. Har bir hodisa uchun bitta shablon, toʻrt
tilda. Matn Markdown; `{title}`, `{reference}`, `{dashboard_url}` kabi
oʻrin egallovchilar «Mavjud oʻrin egallovchilar» maydonida sanab oʻtilgan.

Xatlar qabul qiluvchining **afzal koʻrgan tilida** yuboriladi (profilidagi
sozlama). Shablon oʻchirilgan boʻlsa, tizim kodga kiritilgan zaxira matndan
foydalanadi — xat hech qachon yoʻqolmaydi.

---

## 8. Integratsiyalar

Barcha kalitlar `.env` faylida, admin panelda emas. Toʻliq yoʻriqnoma:
`docs/INTEGRATIONS.md`.

| Integratsiya | `.env` oʻzgaruvchilari | Tekshirish |
|---|---|---|
| Crossref | `DOI_PREFIX`, `CROSSREF_USER`, `CROSSREF_PASSWORD`, `CROSSREF_TEST` | `manage.py crossref_validate --all`, keyin `crossref_deposit --article <id>` |
| ORCID | `ORCID_BASE`, `ORCID_CLIENT_ID`, `ORCID_CLIENT_SECRET` | Kirish sahifasidagi ORCID tugmasi |
| Pochta | `RESEND_API_KEY` yoki SMTP sozlamalari | Sinov hisobi yaratib, tasdiqlash xatini kuting |
| Matomo | `MATOMO_URL`, `MATOMO_SITE_ID` | Sahifa manbasida skript bor-yoʻqligi |
| Zaxira | `BACKUP_S3_TARGET`, S3 kalitlari | `docs/BACKUP_RESTORE.md` |

Depozit holatini **Admin → Crossref → Deposit batches** da koʻrasiz: har bir
paketning XML fayli, holati va Crossref javobi saqlanadi.

---

## 9. Audit jurnali

**Admin → Core → Audit log** — oʻzgartirib boʻlmaydigan yozuvlar: kirish va
chiqish, muvaffaqiyatsiz urinishlar, rol oʻzgarishi, tahririy qarorlar, nashr,
sozlamalar oʻzgarishi, Crossref depozitlari, qoidadan chetlanishlar. Har bir
yozuvda kim, qachon, nima va qaysi IP dan. Saqlash muddati — ikki yil.

---

## 10. Kundalik texnik xizmat

```bash
# Holat
docker compose -f docker-compose.prod.yml ps
curl -s https://algorithm-journal.uz/healthz/

# Jurnallar
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f worker

# Rejalashtirilgan vazifalar
docker compose -f docker-compose.prod.yml exec worker celery -A config inspect active

# Zaxira nusxa (odatda avtomatik)
docker compose -f docker-compose.prod.yml exec backup sh /scripts/backup.sh

# Yangilash
bash scripts/deploy.sh
```

**Har oy bajariladigan ishlar:**

1. Zaxira nusxadan tiklashni sinab koʻring (`docs/BACKUP_RESTORE.md` §3.1).
2. `manage.py check_metadata` — chop etilgan maqolalar toʻliqligini tekshiring.
3. `manage.py crossref_status` — barcha depozitlar qabul qilinganini tasdiqlang.
4. `/dashboard/reports/` dan KPI larni CSV ga eksport qiling va saqlang.
5. Har bir son uchun `manage.py export_issue_bundle <id>` — toʻplamni server
   tashqarisida saqlang.
6. Disk boʻsh joyini tekshiring: `df -h`, `docker system df`.

---

## 11. Tez-tez uchraydigan muammolar

| Belgi | Sabab | Yechim |
|---|---|---|
| `/uz-cyrl/` sahifalari inglizcha chiqmoqda | `compilemessages` bajarilmagan | `docker compose ... run --rm web python manage.py compilemessages` |
| Statik fayllar yoʻq | `collectstatic` bajarilmagan | `bash scripts/deploy.sh` |
| Xatlar yetib bormayapti | `RESEND_API_KEY` yoʻq yoki SPF/DKIM sozlanmagan | `docs/INTEGRATIONS.md` §3 |
| Depozit `pending` da qolmoqda | Crossref maʼlumotlari kiritilmagan | `.env` ga `CROSSREF_USER`/`CROSSREF_PASSWORD` |
| Muharrir panelga kira olmayapti | 2FA roʻyxatdan oʻtmagan | `/dashboard/two-factor/setup/` |
| Hisob bloklangan | 10 marta xato parol | 30 daqiqa kutish yoki admin panelda Axes yozuvini oʻchirish |
| Sertifikat olinmayapti | DNS yoki 80-port | `dig`, `ufw status`, `docker compose logs caddy` |
