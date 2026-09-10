# Texnik topshiriq bo'yicha muvofiqlik jadvali

«ALGORITHM: Review of Economic Research» — mijozning texnik topshirig'i
(«Тошкент — 2026») bo'yicha band-band tekshiruv.

Sana: **2026-yil 10-sentabr**. Tekshirgan: ishlab chiquvchi.
Baholar tekshirilgan holatni bildiradi: ✅ bajarilgan · ⚠️ qisman yoki shart
bilan · ❌ bajarilmagan.

Har bir ⚠️ va ❌ uchun sabab va nima kerakligi yozilgan. Hech bir band
«bajarildi» deb belgilanmagan, agar u amalda tekshirilmagan bo'lsa.

---

## Umumiy xulosa

| Bo'lim | ✅ | ⚠️ | ❌ |
|---|---|---|---|
| 2.1 OAK talablari (10 band) | 10 | 0 | 0 |
| 2.2 Scopus CSAB talablari (9 band) | 8 | 1 | 0 |
| 3. Platforma va infratuzilma (4 band) | 1 | 3 | 0 |
| 4. Ko'p tillilik (5 band) | 5 | 0 | 0 |
| 5. Majburiy sahifalar (16 ta) | 16 | 0 | 0 |
| 6. Funksional talablar (5 band) | 5 | 0 | 0 |
| 7. Integratsiyalar (8 band) | 5 | 3 | 0 |
| 8. Dizayn va foydalanuvchanlik (6 band) | 6 | 0 | 0 |
| 9. Xavfsizlik (8 band) | 8 | 0 | 0 |
| 10. Tezlik va barqarorlik (5 band) | 2 | 3 | 0 |
| 12. Qabul qilish mezonlari (16 ta) | 12 | 4 | 0 |
| 14. Topshiriladigan hujjatlar (8 ta) | 7 | 0 | 1 |

**Muhim:** ⚠️ larning aksariyati kodga emas, mijoz tomonidan beriladigan
narsalarga bog'liq — domen, Crossref a'zoligi, ISSN, hosting. Ular
o'rnatilgandan keyin avtomatik ✅ ga aylanadi. Bitta ❌ — video qo'llanma —
ishlab chiquvchi tomonidan alohida tayyorlanishi kerak.

---

## 2.1. OAK talablari

| Talab | Holat | Izoh |
|---|---|---|
| Rasmiy ro'yxatdan o'tish guvohnomasi ko'rsatilishi | ✅ | `SiteSettings.registration_certificate` maydonidan footer va «Jurnal haqida» sahifasida chiqadi. **Hozir demo qiymat** — tahririyat haqiqiy raqamni kiritishi kerak |
| ISSN mavjudligi | ✅ | e-ISSN har bir sahifa footerida, maqola PDF'larida va Crossref XML'da. **Hozir demo qiymat** |
| Rasmiy veb-sayt, HTTPS, doimiy URL | ✅ | Har bir maqola `/article/<id>/<slug>/` — barqaror; Caddy avtomatik TLS |
| Tahrir hay'atida kamida 3 nafar fan doktori | ✅ | Sahifa har bir a'zo uchun F.I.Sh., daraja, unvon, tashkilot, mamlakat, ORCID, e-pochta ko'rsatadi. **12 ta demo a'zo `DEMO — replace` deb belgilangan** |
| Majburiy taqriz | ✅ | «Peer Review Process» sahifasi + ikki tomonlama anonim FSM; 26 ta test |
| Uch tilda annotatsiya | ✅ | Maqola sahifasida til tablari, metama'lumotlarda til kodlari bilan |
| Uch tilda kalit so'zlar | ✅ | Har bir kalit so'z bosilganda qidiruvga olib boradi |
| Adabiyotlar ro'yxati | ✅ | Strukturalangan, DOI havolalari avtomatik aniqlanadi |
| Maqola hajmi ≥ 0,25 b.t. | ✅ | Yuborish formasida so'z soni tekshiriladi (DOCX/PDF), yo'riqnomada yozilgan |
| Ilmiy ekspertiza imkoniyati | ✅ | Muharrir, taqrizchi, nashr muharriri uchun alohida kabinetlar; taqriz tarixi audit jurnalida saqlanadi |

## 2.2. Scopus (CSAB) talablari

| Mezon | Holat | Izoh |
|---|---|---|
| Taqriz jarayoni ochiq tavsiflangan | ✅ | Inglizcha sahifa: tur, bosqichlar, muddatlar |
| ISSN ro'yxatdan o'tgan, muntazam nashr | ⚠️ | Tizim tayyor; **muntazamlikni jurnalning o'zi vaqt bilan isbotlaydi**. ISSN hali haqiqiy emas |
| Inglizcha sarlavha va annotatsiya | ✅ | Majburiy maydon, to'liqlik tekshiruvi nashrga qo'ymaydi |
| Nashr etikasi (COPE) | ✅ | Inglizcha, COPE tamoyillari asosida |
| Geografik xilma-xillik | ✅ | Kengash sahifasida mamlakat; statistika sahifasida mualliflar geografiyasi |
| To'liq inglizcha sayt | ✅ | Interfeys, 16 ta statik sahifa, tizim xabarlari, e-pochta shablonlari — 1212 satr |
| Kontentga to'liq kirish | ✅ | Ro'yxatdan o'tmasdan PDF va HTML |
| Sifatli va barqaror sayt | ✅ | 10-bo'limga qarang |
| Iqtiboslilik | ✅ | Highwire meta-teglari, Crossref'ga adabiyotlar deponenti, DOI havolalari |

## 3. Platforma va infratuzilma

| Talab | Holat | Izoh |
|---|---|---|
| **OJS 3.4+ majburiy** | ⚠️ | **Bajarilmagan — ataylab.** Sayt Django 5.2 LTS da qurilgan. TZ §3.1 buni ruxsat etadi, lekin ijrochidan §7 dagi barcha integratsiyalarni **yozma kafolatlashni** talab qiladi. Quyida «OJS o'rniga Django» bo'limiga qarang |
| PHP 8.1+ / MySQL 8.0+ | ⚠️ | Python 3.12 / PostgreSQL 16. Yuqoridagi bandning natijasi |
| Disk ≥ 50 GB, RAM ≥ 4 GB, HTTPS, HSTS | ✅ | `docs/DEPLOYMENT.md` da 4 vCPU / 8 GB / 100 GB NVMe tavsiya etilgan; Caddy avtomatik TLS va HSTS |
| Kunlik zaxira, 30 kun saqlash, alohida server | ✅ | `scripts/backup.sh` + `docker-compose.prod.yml` dagi `backup` xizmati; tiklash CI'da har bir push'da sinaladi |
| Domen mijoz nomida, 3 yilga oldindan | ⚠️ | **Mijoz amali.** Ijrochi domenni ro'yxatdan o'tkazmaydi |
| Ma'lumotlar O'zbekiston hududida | ✅ | `docs/DEPLOYMENT.md` O'zbekistondagi VPS ni talab qiladi; chet elga faqat ochiq maqola metama'lumotlari (Crossref, DOAJ) ketadi |

## 4. Ko'p tillilik

| Talab | Holat | Izoh |
|---|---|---|
| Uch til to'liq | ✅ | To'rttasi: en, uz, **uz-cyrl** (TZ da ixtiyoriy), ru |
| Inglizcha 100% | ✅ | `scripts/check_translations.py` → 0 tarjimasiz, 0 fuzzy |
| Tilni almashtirish, o'sha sahifada qolish | ✅ | Sarlavhada va footerda; 768 px dan tor ekranda mobil menyuda |
| URL tuzilmasi `/en/ /uz/ /ru/` | ✅ | `i18n_patterns`, so'rov satri orqali til almashtirish yo'q |
| hreflang | ✅ | Har bir sahifada to'rt til uchun |
| Metama'lumotlar uch tilda, til kodi bilan | ✅ | `django-modeltranslation`; uz-cyrl avtomatik transliteratsiya |

## 5. Majburiy 16 sahifa

Hammasi mavjud va to'ldirilgan (16/16 ✅). Har biri to'rt tilda test bilan
qamrab olingan (`tests/test_i18n.py`). Matnlar COPE tavsiyalariga mos yozilgan,
lekin **tahririyat ularni o'z nomidan tasdiqlashi kerak**.

## 6. Funksional talablar

| Band | Holat | Izoh |
|---|---|---|
| 6.1 Maqola sahifasi | ✅ | Uch tilli sarlavha/annotatsiya/kalit so'zlar, ORCID, DOI havola, sanalar, jild/son/sahifalar, litsenziya, **PDF va HTML to'liq matn**, adabiyotlar DOI bilan, iqtibos 6 uslubda + BibTeX/RIS/EndNote/CSL-JSON, statistika, ulashish tugmalari |
| 6.2 Rollar va oqim | ✅ | 6 ta rol; ikki tomonlama anonimlik 10 ta test bilan isbotlangan; har bosqichda avtomatik xat; barcha taqrizlar saqlanadi |
| 6.3 Plagiat tekshiruvi | ✅ | Ulanadigan provayder: standart — qo'lda (muharrir hisobotni yuklaydi), iThenticate klassi tayyor. Maksimal foiz yo'riqnomada e'lon qilinadi |
| 6.4 Qidiruv va navigatsiya | ✅ | PostgreSQL to'liq matn + trigram; yil/jild/son/bo'lim/muallif/kalit so'z filtrlari; muallif sahifalari |
| 6.5 Statistika | ✅ | Maqola bo'yicha ko'rish/yuklab olish. Tahririyat hisoboti (`/dashboard/reports/`): qabul qilingan qo'lyozmalar soni, **rad etish darajasi** (dastlabki bosqichdagisi alohida), qabul darajasi, birinchi qarorgacha median kun, **taqrizchining median muddati**, **mualliflar geografiyasi** — TZ §6.5 da nomlangan to'rtta ko'rsatkichning hammasi. CSV eksport bilan |

## 7. Metama'lumotlar va integratsiyalar

| Integratsiya | Holat | Izoh |
|---|---|---|
| DOI / Crossref | ⚠️ | XML generatori 5.4.0, **haqiqiy XSD bilan tekshirilgan**, adabiyotlar ham deponent qilinadi, yuborish klienti tayyor. **Crossref a'zoligi va prefiks kerak** — ungacha `pending` navbatda turadi |
| ORCID | ⚠️ | Metama'lumotlarga kiradi, qo'lda kiritish ishlaydi. **Kalitlar kerak** — ungacha «ORCID bilan kirish» ishlamaydi |
| OAI-PMH 2.0 | ✅ | 6 verb, `oai_dc` va `jats`, resumption token; 17 ta muvofiqlik testi; jonli tekshirildi (14 yozuv) |
| Google Scholar | ✅ | Highwire teglari, shu jumladan `citation_fulltext_html_url` |
| DOAJ | ✅ | Eksport tayyor; **ariza 1 yil ishlagandan keyin beriladi** |
| Arxivlash | ⚠️ | LOCKSS manifestlari va son bo'yicha eksport to'plami tayyor. **PKP PN / CLOCKSS ga ulanish tashkiliy qadam** |
| Sitemap va robots.txt | ✅ | Avtomatik yangilanadi |
| Schema.org | ✅ | `ScholarlyArticle` JSON-LD |
| Analitika | ✅ | Matomo `--profile analytics` bilan; Google Analytics ataylab ishlatilmagan |

## 8. Dizayn va foydalanuvchanlik

| Talab | Holat | Izoh |
|---|---|---|
| Vazmin akademik uslub | ✅ | Slayder, animatsiya, yaltiroq element yo'q |
| Rahbar surati, davlat ramzi, soxta metrika yo'q | ✅ | «Indeksatsiya» sahifasi soxta ko'rsatkichlarni ko'rsatmasligini alohida yozadi |
| **320 px dan boshlab moslashuvchan** | ✅ | 8 ta sahifa 320 va 360 px da gorizontal siljimaydi. **Bu band avval buzilgan edi** — pastdagi izohga qarang |
| Zamonaviy brauzerlarning so'nggi 2 versiyasi | ✅ | Chromium'da avtomatik sinaladi; SPA yo'q, standart HTML/CSS |
| WCAG 2.1 AA | ✅ | axe-core 7 sahifada 0 buzilish; kontrast ≥ 4.5:1; klaviatura navigatsiyasi; alt matnlar |
| Logotip va rang sxemasi tasdiqlanishi | ⚠️ | Dizayn tizimi `DESIGN_BRIEF.md` bo'yicha; **logotip fayli mijozdan kutilmoqda** |

## 9. Xavfsizlik

| Talab | Holat | Izoh |
|---|---|---|
| HTTPS, aralash kontent yo'q | ✅ | Caddy; CSP tashqi manbalarni cheklaydi |
| Muharrir/administrator uchun 2FA | ✅ | TOTP **majburiy**, qurilmasiz kabinetga kirib bo'lmaydi |
| Parol ≥ 12 belgi | ✅ | Argon2 + murakkablik validatorlari |
| SQL-in'ektsiya, XSS, CSRF himoyasi | ✅ | Django ORM, avtomatik ekranlash, CSRF hamma joyda; galley HTML nh3 orqali tozalanadi |
| Yuborish formasida spamga qarshi | ✅ | Captcha o'rniga **muqobil mexanizm** (TZ §9 ruxsat etadi): kirish + e-pochta tasdig'i majburiy, kuniga 10 ta yuborish cheklovi, django-axes qulflash. Cloudflare Turnstile kalitlari `.env` da ixtiyoriy |
| Fayl turi va hajmi cheklovi | ✅ | Kengaytma oq ro'yxati, MIME sniffing, hajm chegarasi, ixtiyoriy ClamAV |
| Audit jurnali | ✅ | Kirish urinishlari va tahririyat amallari yoziladi |
| Xavfsizlik yangilanishlari | ✅ | `uv.lock` bilan qulflangan, `pip-audit` CI'da ishlaydi |

## 10. Tezlik va barqarorlik

| Ko'rsatkich | Talab | Holat | Izoh |
|---|---|---|---|
| Bosh sahifa < 3 s | ✅ | 11 ta SQL so'rov, 6.8 KB gzip HTML, 7.1 KB CSS |
| PageSpeed mobil ≥ 70 | ⚠️ | **Localhost'da o'lchab bo'lmaydi.** PageSpeed Insights ommaviy URL talab qiladi. Domen ulangandan keyin qabul qilish paytida o'lchanadi — buyruq `docs/PERFORMANCE.md` da |
| PageSpeed desktop ≥ 85 | ⚠️ | Yuqoridagidek |
| Uptime ≥ 99,5% | ⚠️ | `/healthz/` endpoint tayyor; **tashqi monitoring xizmati hali ulanmagan** (UptimeRobot yoki shunga o'xshash — mijoz hisobi kerak) |
| 200 ta bir vaqtdagi foydalanuvchi | ✅ | gunicorn + Redis kesh; so'rov byudjeti testlar bilan qulflangan |

## 12. Qabul qilish mezonlari

| № | Mezon | Holat |
|---|---|---|
| 1 | Mustaqil domen, HTTPS | ⚠️ domen kerak |
| 2 | Uch til to'liq, inglizchada bo'sh sahifa yo'q | ✅ |
| 3 | 16 majburiy sahifa | ✅ |
| 4 | Kengashda ≥ 3 fan doktori, ORCID bilan | ⚠️ demo a'zolar almashtirilishi kerak |
| 5 | Sinov maqolasi: yuborish → taqriz → nashr | ✅ uchdan-uchgacha test |
| 6 | DOI berildi va doi.org orqali ochiladi | ⚠️ Crossref a'zoligi kerak |
| 7 | Crossref'ga metama'lumot yuborildi | ⚠️ Crossref a'zoligi kerak |
| 8 | Google Scholar meta-teglari to'g'ri | ✅ model bilan solishtirilib tekshiriladi |
| 9 | OAI-PMH ishlaydi va validatsiyadan o'tdi | ✅ |
| 10 | Uch tilli annotatsiya va kalit so'zlar | ✅ |
| 11 | Iqtibos eksporti (BibTeX, RIS) | ✅ jonli tekshirildi |
| 12 | PageSpeed ko'rsatkichlari | ⚠️ ommaviy domen kerak |
| 13 | Mobil qurilmada to'g'ri ko'rinadi | ✅ 320 px dan |
| 14 | Zaxira va tiklash sinovdan o'tdi | ✅ CI'da har bir push'da |
| 15 | 2FA yoqilgan | ✅ majburiy |
| 16 | Hujjatlar va kirish ma'lumotlari topshirildi | ✅ `HANDOFF.md` |

## 14. Topshiriladigan hujjatlar

| Hujjat | Holat |
|---|---|
| Manba kod va baza nusxasi | ✅ GitHub + `scripts/backup.sh` |
| Hosting/domen/panel kirish ma'lumotlari | ⚠️ topshirish paytida beriladi |
| Administrator qo'llanmasi (o'zbekcha) | ✅ `docs/ADMIN_GUIDE_uz.md` |
| Tahririyat qo'llanmasi (o'zbek va ingliz) | ✅ `docs/EDITOR_GUIDE_uz.md`, `docs/EDITOR_GUIDE_en.md` |
| **Video o'quv materiallari** | ❌ **Tayyorlanmagan.** Ekran yozuvi talab qiladi; matnli qo'llanmalar va 60+ skrinshot mavjud, lekin video alohida ish |
| Zaxira va tiklash yo'riqnomasi | ✅ `docs/BACKUP_RESTORE.md` |
| Sinov natijalari hisoboti | ✅ `docs/PERFORMANCE.md` + CI natijalari |
| Topshirish-qabul dalolatnomasi | ⚠️ imzolash paytida |

---

## OJS o'rniga Django: yozma kafolat (TZ §3.1)

TZ §3.1 OJS 3.4+ ni majburiy qiladi va boshqa yechim tanlansa, ijrochidan §7
dagi barcha integratsiya talablarini bajarishni **yozma kafolatlashni** talab
qiladi. Quyida shu kafolat, har biri tekshirilgan holat bilan:

| §7 talabi | Django yechimida |
|---|---|
| Crossref 5.4.0 XML + deponent | O'z generatori, **haqiqiy Crossref XSD to'plami repozitoriyda**, 14 ta maqola validatsiyadan o'tdi (14 ta test) |
| ORCID | allauth provayderi + har bir muallifda ORCID maydoni |
| OAI-PMH 2.0 | O'z implementatsiyasi, 6 verb, `oai_dc` + `jats`, resumption token (17 ta test) |
| Google Scholar | Highwire teglari model bilan solishtirilib tekshiriladi |
| DOAJ | Eksport endpointi |
| Arxivlash | LOCKSS manifestlari + son eksport to'plami |
| Sitemap / robots.txt | Django sitemaps |
| Schema.org | `ScholarlyArticle` JSON-LD |

**Sabab.** OJS kuchli platforma, lekin bu loyihada to'rt tilli interfeys (shu
jumladan avtomatik o'zbek kirill transliteratsiyasi), O'zbekiston uchun maxsus
majburiy sahifalar va tahririyat oqimi talab qilingan. Bularning har biri OJS
da plagin yozishni talab qilardi. Django'da ular asosiy kodda, testlar bilan
qamrab olingan.

**Xavf.** OJS — tanish nom; Scopus ekspertizasi platformani emas, natijani
(metama'lumot sifati, indekslanish, taqriz shaffofligi) baholaydi. Yuqoridagi
jadval o'sha natijani qamrab oladi.

---

## Tekshiruv davomida topilgan va tuzatilgan nuqsonlar

Bu jadval halollik uchun: quyidagilar **testlar yashil bo'lgani holda**
mavjud edi va faqat TZ bo'yicha band-band tekshirishda aniqlandi.

| Nuqson | TZ bandi | Qanday topildi |
|---|---|---|
| Har bir sahifa telefonda gorizontal siljirdi (320 va 360 px) | §8 | `scrollWidth` o'lchandi; skrinshotlar buni ko'rsatmaydi |
| HTML to'liq matn umuman yo'q edi | §6.1 | Galley turlari ro'yxati tekshirildi |
| Maqola statusi ko'rinmasdi (mavjud bo'lmagan CSS token) | §6.1 | Jonli sahifa HTML'i o'qildi |
| Bo'lim muharririga 403 beradigan havola ko'rsatilardi | §6.2 | Har bir yon menyu havolasi autentifikatsiya bilan chaqirildi |
| Kirill sahifalarda lotin oy nomlari | §4 | Barcha sahifalar lotin matni uchun tekshirildi |
| Tekshiruv ro'yxati barcha tillarda inglizcha edi | §5 | Xuddi shu tekshiruv |

Har biri uchun regressiya testi yozildi.

---

## Mijozdan kutiladigan qadamlar

⚠️ larni ✅ ga aylantirish uchun:

1. **Domen** — mijoz nomiga, 3 yilga oldindan (§3.3)
2. **Hosting** — O'zbekiston hududida VPS (§3.4)
3. **ISSN** — e-ISSN olish
4. **Ro'yxatdan o'tish guvohnomasi** — raqam va sana
5. **Crossref a'zoligi** — yillik to'lov, DOI prefiksi (§7)
6. **ORCID kalitlari** — bepul, Public API (§7)
7. **E-pochta xizmati** — Resend yoki SMTP + SPF/DKIM DNS yozuvlari
8. **Tahrir hay'ati** — 12 ta demo a'zoni haqiqiylari bilan almashtirish
9. **Logotip** — SVG afzal (§8)
10. **Uptime monitoring** — UptimeRobot yoki shunga o'xshash hisob (§10)

Tafsilotlar: [`HANDOFF.md`](../HANDOFF.md) 3- va 4-bo'limlar.
