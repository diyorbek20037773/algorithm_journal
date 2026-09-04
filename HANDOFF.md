# HANDOFF — ALGORITHM: Review of Economic Research (ARER)

Topshirish hujjati. Sana: **2026-yil 5-sentabr**.
Repozitoriy: <https://github.com/diyorbek20037773/algorithm_journal> (`main`).

Bu hujjat oʻzbek tilida (lotin yozuvida) yozilgan. Texnik hujjatlar ingliz
tilida: [`SPEC.md`](SPEC.md) — muhandislik talablari, [`DESIGN_BRIEF.md`](DESIGN_BRIEF.md)
— dizayn tizimi, [`PROGRESS.md`](PROGRESS.md) — bosqichlar tarixi,
[`DECISIONS.md`](DECISIONS.md) — qabul qilingan muhandislik qarorlari,
[`docs/`](docs/) — oʻrnatish, zaxira, integratsiya va foydalanuvchi qoʻllanmalari.

---

## 1. Nima qilindi

Jurnalning toʻliq elektron tizimi qurildi: ochiq kirishli ommaviy sayt va
tahririyat tizimi (maqola qabul qilish → ikki tomonlama anonim taqriz →
ishlab chiqarish → DOI → nashr → indekslash).

Texnologiya: Python 3.12 · Django 5.2 LTS · PostgreSQL 16 · Redis 7 · Celery 5 ·
Tailwind CSS v4 (Node talab qilinmaydi) · HTMX · Alpine.js. Barcha sahifalar
serverda render qilinadi.

Toʻrt til: **English**, **Oʻzbekcha (lotin)**, **Ўзбекча (kirill)**, **Русский**.
Til URL prefiksi orqali tanlanadi (`/en/`, `/uz/`, `/uz-cyrl/`, `/ru/`).
Kirill matni loyihaning oʻz translyteratori (`apps/core/translit.py`) yordamida
lotin matnidan avtomatik hosil qilinadi — 1 170 ta interfeys satri va model
maydonlari uchun.

### Bosqichlar

| Bosqich | Mazmuni | Holat |
|---|---|---|
| 0 | Repozitoriy, sozlamalar, Docker, CI | ✅ |
| 1 | Foydalanuvchilar, rollar, 2FA, i18n, dizayn tizimi | ✅ |
| 2 | Jurnal modellari, ommaviy sayt, demo maʼlumotlar | ✅ |
| 3 | Iqtiboslar, statistika, ochiq API | ✅ |
| 4 | Maqola yuborish sehrgari (5 qadam) | ✅ |
| 5 | Tahririyat jarayoni (FSM), taqriz, qarorlar | ✅ |
| 6 | Ishlab chiqarish, Crossref, OAI-PMH, arxivlash | ✅ |
| 7 | Xavfsizlik, unumdorlik, imkoniyatlilik, tarjimalar | ✅ |
| 8 | Prod stek, hujjatlar, qoʻllanmalar | ✅ |

Tafsilotlar: [`PROGRESS.md`](PROGRESS.md).

### Testlar

```
360 test — hammasi oʻtdi
ruff check      → All checks passed
ruff format     → 195 files already formatted
djlint          → 0 files would be updated
makemigrations --check → No changes detected
```

Qamrov: translyterator (51 holat), ommaviy sahifalar, 4 til × 22 sahifa,
tahririyat FSM (26 test), anonimlikning buzilmasligi (10 test), Crossref XSD,
OAI-PMH (17 test), API, ishlab chiqarish, statistika, xavfsizlik, unumdorlik va
toʻliq uchdan-uchgacha (end-to-end) tahririyat jarayoni.

### SPEC §15 qabul qilish roʻyxati

| № | Tekshiruv | Holat | Izoh |
|---|---|---|---|
| 1 | `docker compose up --build` + `migrate` + `seed_demo` toza mashinada, ≤ 5 daqiqa | ⚠️ | Docker image va butun stek shu seans davomida muvaffaqiyatli qurildi va ishga tushdi. **Yakuniy qayta tekshiruv tugallanmadi**: qurilish mashinasining `C:` diski toʻlib qoldi (260 MB boʻsh) va Docker Desktop demoni ishdan chiqdi. Bu loyihaning nuqsoni emas — muhit muammosi. Oʻz mashinangizda 4-bandagi buyruqlar bilan tekshiring; kutilayotgan natija quyida 2-boʻlimda. |
| 2 | 4 tilda har bir ommaviy sahifa, tarjima qilinmagan satrsiz | ✅ | `tests/test_i18n.py`; `scripts/check_translations.py` → 0 untranslated, 0 fuzzy |
| 3 | Texnik topshiriqdagi 22 majburiy sahifa mavjud va boʻsh emas | ✅ | Har bir til uchun alohida tekshiriladi |
| 4 | Tahririyat kengashi sahifasida daraja, tashkilot, mamlakat, ORCID, e-pochta | ✅ | 12 nafar demo aʼzo, hammasi "DEMO — replace" deb belgilangan |
| 5 | Playwright E2E jarayoni: yuborish → skrining → taqriz → qaror → qayta ishlash → DOI → nashr | ✅ | `tests/test_e2e_flow.py` (ikkita test: HTTP va brauzer) |
| 6 | Har bir maqola uchun Crossref XML XSD boʻyicha haqiqiy | ✅ | Haqiqiy Crossref 5.4.0 XSD toʻplami repozitoriyda; 14 ta maqola tekshirildi |
| 7 | Highwire `citation_*` metateglari toʻgʻri | ✅ | Model bilan solishtiriladi |
| 8 | OAI-PMH: 6 ta verb, resumption token, `oai_dc` va `jats` | ✅ | 17 ta muvofiqlik testi |
| 9 | Annotatsiya va kalit soʻzlar 4 tilda maqola sahifasida | ✅ | |
| 10 | Iqtibos oynasi 6 uslub; BibTeX/RIS/EndNote/CSL-JSON | ✅ | `bibtexparser` va `rispy` bilan parse qilinadi |
| 11 | Filtrli qidiruv; muallif ismida xatoga chidamli | ✅ | PostgreSQL FTS + trigram |
| 12 | Unumdorlik: soʻrov soni, bundle hajmi, Lighthouse | ✅ | [`docs/PERFORMANCE.md`](docs/PERFORMANCE.md). Lighthouse oʻrniga axe-core va soʻrov/hajm oʻlchovlari — sabab hujjatda yozilgan (loyihada Node yoʻq) |
| 13 | 360 / 768 / 1280 / 1920 px skrinshotlar | ✅ | `docs/screenshots/responsive/` |
| 14 | `backup.sh` va `restore.sh` CI ishida sinaladi | ✅ | GitHub Actions’dagi “Backup / restore drill” qadami yashil (run 33919274518) |
| 15 | Xodimlar uchun 2FA majburiy | ✅ | TOTP qurilmasisiz muharrir roʻyxatdan oʻtish sahifasiga yoʻnaltiriladi |
| 16 | Audit jurnali qaror va nashr amallarini yozadi | ✅ | |
| 17 | `docs/` toʻliq; HANDOFF oʻzbekcha; CI yashil; GitHub’ga yuborilgan | ✅ | Kod GitHub’da; ikkala CI ishi ham yashil (run 33919274518) |
| 18 | Anonimlik: taqrizchi sahifalarida muallif maʼlumoti yoʻq va aksincha | ✅ | 10 ta test; API va OAI faqat nashr etilganini koʻrsatadi |

Jami: **17 ✅**, **1 ⚠️**. Yagona ogohlantirish kod bilan emas, qurilish
mashinasining diski toʻlgani bilan bogʻliq — va u CI’da emas, faqat shu
kompyuterda yuz berdi.

---

## 2. Qanday ishga tushirish

### 2.1. Mahalliy (faqat Docker kerak)

Toza mashinada faqat Docker Desktop (yoki Docker Engine + Compose) boʻlishi
yetarli. Python, Node, PostgreSQL alohida oʻrnatilmaydi.

```bash
git clone https://github.com/diyorbek20037773/algorithm_journal.git
cd algorithm_journal
cp .env.example .env
docker compose up --build
```

Boshqa terminalda:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_demo
```

| Xizmat | Manzil |
|---|---|
| Sayt | <http://localhost:8000> |
| Admin panel | <http://localhost:8000/admin/> |
| Mailpit (barcha chiquvchi xatlar) | <http://localhost:8025> |
| OAI-PMH | <http://localhost:8000/oai/?verb=Identify> |
| JSON API | <http://localhost:8000/api/v1/> |
| Salomatlik tekshiruvi | <http://localhost:8000/healthz/> |

Agar mashinangizda 8000, 5432, 6379 yoki 8025 portlari band boʻlsa, `.env`
faylida oʻzgartiring — konteynerlar orasidagi aloqa oʻzgarmaydi:

```bash
WEB_PORT=8010
POSTGRES_HOST_PORT=5452
REDIS_HOST_PORT=6389
MAILPIT_UI_PORT=8026
```

**Demo hisoblar.** Barchasining paroli: `Algorithm2026!`

| E-pochta | Rol |
|---|---|
| `admin@algorithm-journal.uz` | Superuser / texnik administrator |
| `eic@algorithm-journal.uz` | Bosh muharrir |
| `editor@algorithm-journal.uz` | Boʻlim muharriri |
| `production@algorithm-journal.uz` | Ishlab chiqarish muharriri |
| `reviewer1..3@algorithm-journal.uz` | Taqrizchilar |
| `author@algorithm-journal.uz` | Muallif |

Tahririyat hisoblari (`eic`, `editor`, `production`, `admin`) birinchi kirishda
TOTP ilovasini ulashi **shart** — bu xatolik emas, majburiy ikki bosqichli
autentifikatsiya siyosati. Google Authenticator, Aegis yoki shunga oʻxshash
istalgan ilova ishlaydi; QR kod ekranda chiqadi.

Foydali buyruqlar:

```bash
make dev          # build + migrate + seed_demo + up
make test         # 360 test
make lint         # ruff + djlint
make compile      # tarjima katalogini kompilatsiya qilish (.mo)
make tailwind     # CSS ni qayta yigʻish
make screenshots  # skrinshot va axe-core hisoboti
make backup       # baza + media zaxirasi
```

### 2.2. Ishlab chiqarish (VPS)

Toʻliq bayoni: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md). Qisqacha:

Talablar: Ubuntu 22.04+ (2 vCPU, 4 GB RAM, 40 GB SSD), Docker Engine +
Compose plugin, domen A-yozuvi serverga yoʻnaltirilgan.

```bash
git clone https://github.com/diyorbek20037773/algorithm_journal.git /srv/arer
cd /srv/arer
cp .env.example .env
nano .env          # 3-boʻlimdagi barcha sirlarni toʻldiring
```

`.env` da ishlab chiqarish uchun majburiy:

```bash
DJANGO_SETTINGS_MODULE=config.settings.prod
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=<50 belgili tasodifiy satr>
DJANGO_ALLOWED_HOSTS=algorithm-journal.uz,www.algorithm-journal.uz
SITE_DOMAIN=algorithm-journal.uz
CADDY_EMAIL=admin@algorithm-journal.uz
POSTGRES_PASSWORD=<kuchli parol>
```

Ishga tushirish:

```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
docker compose -f docker-compose.prod.yml exec web python manage.py bootstrap_site
```

Caddy TLS sertifikatini Let's Encrypt’dan avtomatik oladi — 80 va 443 portlari
ochiq boʻlishi kerak. Yangilanish va orqaga qaytarish:

```bash
bash scripts/deploy.sh          # pull → build → migrate → collectstatic → restart
bash scripts/deploy.sh rollback # oldingi image’ga qaytish
```

Kunlik zaxira `backup` xizmati orqali avtomatik ishlaydi
([`docs/BACKUP_RESTORE.md`](docs/BACKUP_RESTORE.md)). Tiklashni **hech boʻlmaganda
bir marta sinab koʻring** — zaxira sinalmagunicha zaxira hisoblanmaydi:

```bash
bash scripts/restore.sh backups/arer-YYYY-MM-DD.sql.gz
```

---

## 3. Sozlash kerak boʻlgan sirlar

Quyidagilarning barchasi `.env` faylida. `.env` git’ga **kirmaydi**;
`.env.example` esa har bir oʻzgaruvchini xavfsiz standart qiymat bilan
hujjatlashtiradi. Toʻliq yoʻriqnoma: [`docs/INTEGRATIONS.md`](docs/INTEGRATIONS.md).

| Oʻzgaruvchi | Qayerdan olinadi | Toʻldirilmasa nima boʻladi |
|---|---|---|
| `DJANGO_SECRET_KEY` | `python -c "import secrets;print(secrets.token_urlsafe(50))"` | Prod sozlamasi ishga tushmaydi (ataylab) |
| `POSTGRES_PASSWORD` | Oʻzingiz belgilaysiz | Standart dev parol prod’da xavfli |
| `DJANGO_ALLOWED_HOSTS`, `SITE_DOMAIN` | Sizning domeningiz | Sayt 400 qaytaradi; kanonik URL’lar notoʻgʻri |
| `CROSSREF_USERNAME`, `CROSSREF_PASSWORD`, `CROSSREF_DEPOSITOR_EMAIL` | Crossref aʼzoligi (yillik toʻlov, ~$275 dan) — <https://www.crossref.org/membership/> | XML yaratiladi va saqlanadi, lekin yuborilmaydi: `pending` holatida navbatda turadi va panelda ogohlantirish chiqadi |
| `CROSSREF_PREFIX` | Crossref aʼzolikdan keyin beradi (masalan `10.51349`) | DOI’lar `10.xxxxx/...` shaklida — bu **vaqtinchalik**, nashrdan oldin almashtiring |
| `CROSSREF_TEST_MODE` | `true` — sinov, `false` — haqiqiy deponent | `true` boʻlsa Crossref sinov serveriga yuboriladi |
| `ORCID_CLIENT_ID`, `ORCID_CLIENT_SECRET` | <https://orcid.org/developer-tools> (Public API bepul) | "ORCID bilan kirish" tugmasi ishlamaydi; ORCID’ni qoʻlda kiritish ishlaydi |
| `ORCID_SANDBOX` | `true` — sandbox, `false` — haqiqiy ORCID | |
| `RESEND_API_KEY` yoki `EMAIL_HOST*` | <https://resend.com> yoki oʻz SMTP serveringiz | Prod’da xat yuborilmaydi; dev’da hammasi Mailpit’ga tushadi |
| `DEFAULT_FROM_EMAIL` | Domeningizdagi manzil | Xatlar spam’ga tushishi mumkin |
| SPF / DKIM / DMARC DNS yozuvlari | Domen DNS panelingiz | Taqrizchi va mualliflarga xat yetib bormaydi — **eng koʻp uchraydigan muammo** |
| `IP_HASH_SALT` | Tasodifiy satr | Statistikadagi IP xeshlari oldindan aytiladigan boʻlib qoladi |
| `S3_*` (ixtiyoriy) | Har qanday S3-mos xizmat | Fayllar serverning oʻzida saqlanadi (standart holat) |
| `TURNSTILE_SITE_KEY`, `TURNSTILE_SECRET_KEY` (ixtiyoriy) | <https://dash.cloudflare.com> | Bogʻlanish formasi captcha’siz ishlaydi |
| `ITHENTICATE_*` (ixtiyoriy) | Crossref Similarity Check obunasi | Plagiat tekshiruvi qoʻlda: muharrir hisobotni oʻzi yuklaydi |
| `MATOMO_*` (ixtiyoriy) | `--profile analytics` bilan oʻz serveringizda | Tashqi analitika ulanmaydi (maxfiylik uchun standart holat) |

---

## 4. Tahririyat kiritishi kerak boʻlgan maʼlumotlar

Bularsiz sayt ishlaydi, lekin demo maʼlumotlar bilan. Hammasi admin panel yoki
sayt sozlamalari orqali kiritiladi — **shablonlarda hech narsa qatʼiy
yozilmagan**.

1. **Tahririyat kengashi.** Hozir 12 nafar demo aʼzo bor va har biri
   **"DEMO — replace"** deb belgilangan. Har bir aʼzo uchun kerak: F.I.Sh.
   (lotin va kirill), ilmiy daraja va unvon, tashkilot, shahar, mamlakat,
   ORCID iD, e-pochta, qisqacha CV, fotosurat (ixtiyoriy).
   Joyi: `/admin/journal/editorialboardmember/`. Taqrizchilar kengashi ham shu
   yerda, `board_type` maydoni orqali ajratiladi.

2. **ISSN.** Elektron ISSN (eISSN) va, agar bosma nashr boʻlsa, bosma ISSN.
   Joyi: sayt sozlamalari → `eissn`, `pissn`. Hozir demo qiymat turibdi va u
   sahifa pastida hamda Crossref XML’da koʻrinadi.

3. **Roʻyxatdan oʻtish guvohnomasi.** OAK / Oʻzbekiston Matbuot agentligi
   guvohnomasi raqami va sanasi — sayt sozlamalarida
   `registration_certificate` maydoni; footer’da chiqadi.

4. **DOI prefiksi.** Crossref aʼzoligidan keyin beriladigan prefiks
   (`10.xxxxx`). `.env` dagi `CROSSREF_PREFIX` ga yoziladi. **Muhim:** DOI
   nashr etilgandan keyin oʻzgartirilmaydi, shuning uchun birinchi haqiqiy
   nashrdan oldin toʻgʻri prefiksni qoʻying.

5. **Aloqa maʼlumotlari.** Tahririyat manzili, telefon, e-pochta, ish vaqti —
   sayt sozlamalarida. Bosh muharrir va masʼul kotib ismlari ham shu yerda.

6. **Logotip va gerb.** `SiteSettings.logo` (SVG afzal, PNG ham boʻladi) va
   `favicon`. Yuklash joyi: `/admin/core/sitesettings/`. Yuklanmasa, jurnal
   nomining matnli belgisi (wordmark) ishlatiladi — u ham toʻliq ishlaydigan
   yechim.

7. **Nashr siyosati matnlari.** 16 ta sahifa (etika, ochiq kirish, litsenziya,
   AI siyosati, taqriz tartibi, mualliflarga koʻrsatma va h.k.) toʻrt tilda
   toʻldirilgan va COPE tavsiyalariga mos yozilgan. Ular **tayyor matn**, lekin
   tahririyat ularni oʻz nomidan tasdiqlashi va kerak boʻlsa tahrirlashi zarur.
   Joyi: `/admin/core/page/`.

8. **Toʻliq JEL roʻyxati (ixtiyoriy).** Hozir 326 ta kod yuklangan — demo va
   odatdagi maqolalar uchun yetarli. AEA saytidan toʻliq roʻyxatni yuklab olib:

   ```bash
   docker compose exec web python manage.py import_jel /app/jel_full.csv
   ```

---

## 5. Maʼlum cheklovlar va Phase-2 roʻyxati

### Bilib turib qilinmagan ishlar (SPEC §18 boʻyicha v1 doirasidan tashqarida)

* **DOCX → JATS/HTML** toʻliq matn konversiyasi. Hozir maqola PDF galley
  sifatida chiqadi; JATS metama'lumotlari OAI-PMH’da bor, lekin toʻliq matn
  XML’i yoʻq.
* **iThenticate jonli chaqiruvlari.** Klient sinfi va sozlamalari tayyor,
  faqat obuna va kalitlar kerak. Hozir plagiat tekshiruvi qoʻlda: muharrir
  hisobot faylini yuklaydi va foizni kiritadi.
* **ORCID Member API** orqali nashr etilgan maqolani muallif profiliga avtomatik
  qoʻshish. Public API (kirish va iD tasdiqlash) ishlaydi.
* **Crossmark** va **Similarity Check** roʻyxatdan oʻtishi.
* **Elasticsearch** — ataylab ishlatilmadi. PostgreSQL toʻliq matnli qidiruvi
  (FTS + trigram) jurnal hajmi uchun yetarli va bitta xizmatni kamaytiradi
  (DECISIONS.md, D1).
* **Toʻlov tizimi** — kerak emas: jurnal "diamond open access", APC yoʻq.
* **Mobil ilova** — yoʻq; sayt moslashuvchan (responsive).
* **Koʻp jurnalli rejim** — yoʻq, lekin `SiteSettings` singleton sifatida
  saqlangani uchun kelajakda kengaytirish mumkin.

### Amaliy eslatmalar

* **`.mo` fayllari repozitoriyda saqlanmaydi.** Ular Docker image ichida,
  `scripts/entrypoint.sh` va `scripts/deploy.sh` da avtomatik kompilatsiya
  qilinadi. Agar Docker’siz, toʻgʻridan-toʻgʻri checkout qilib ishga tushirsangiz,
  bir marta `make compile` qiling — aks holda `/uz-cyrl/` sahifalari inglizchaga
  qaytadi.
* **`static/css/output.css` repozitoriyda saqlanadi**, chunki Tailwind CLI
  birinchi ishga tushganda binar fayl yuklab oladi; internetsiz mashinada ham
  sayt toʻgʻri koʻrinishi uchun. Qayta yigʻish: `make tailwind`.
* **Demo maʼlumotlar haqiqiy emas.** 14 ta maqola, mualliflar, ORCID raqamlari
  va adabiyotlar roʻyxati oʻylab topilgan (lekin iqtisodiyot maqolasi kabi
  mazmunli). Haqiqiy nashrni boshlashdan oldin bazani tozalang:

  ```bash
  docker compose exec web python manage.py flush
  docker compose exec web python manage.py migrate
  docker compose exec web python manage.py bootstrap_site   # demo maqolasiz
  ```

* **Kirill tarjimasi mashina orqali hosil qilingan.** Translyterator 51 ta test
  bilan tekshirilgan va istisnolar lugʻati bor, lekin atamashunoslikni tilchi
  koʻrib chiqishi tavsiya etiladi. Har qanday qoʻlda kiritilgan kirill matni
  saqlanadi — avtomatik hosil qilingan qiymatlar `auto_translit` maydonida
  belgilangani uchun ustidan yozilmaydi.
* **Qurilish mashinasidagi muammo.** Ushbu ish yakunlanayotgan paytda
  ishlab chiqish kompyuterining `C:` diski toʻlib qoldi (260 MB boʻsh) va
  Docker Desktop demoni ishdan chiqdi. Shu sababli 1-tekshiruv (toza mashinada
  `docker compose up --build`) qayta oʻtkazilmadi. Loyihaning oʻzi bunga sabab
  emas — image oldinroq shu seansda muvaffaqiyatli qurilgan edi, qolgan hamma
  narsa esa GitHub Actions’da toza konteynerlarda yashil. Docker gʻalati
  ishlasa, avval boʻsh disk hajmini tekshiring.

---

## 6. GitHub push holati

**Holat: yuborilgan.** Barcha ish
<https://github.com/diyorbek20037773/algorithm_journal> repozitoriysining `main`
tarmogʻiga commit qilingan va push qilingan. GitHub Actions ikkala ishni ham
bajarib, **yashil** natija berdi — lint, format, shablon tekshiruvi, tarjima
toʻliqligi, migratsiyalar, prod sozlamalari tekshiruvi, 360 test, Playwright
E2E va zaxira/tiklash mashqi:
<https://github.com/diyorbek20037773/algorithm_journal/actions/runs/33919274518>

Keyingi oʻzgarishlarni yuborish uchun:

```bash
cd d:/myprojects/journal
git add -A
git commit -m "..."
git push origin main
```

Agar push muvaffaqiyatsiz boʻlsa (autentifikatsiya yoki tarmoq sababli),
quyidagi buyruqni oʻzingiz bajaring:

```bash
cd d:/myprojects/journal
git push -u origin main
```

GitHub endi parol qabul qilmaydi. Ikki yoʻldan biri:

**1) Personal Access Token.** <https://github.com/settings/tokens> →
"Generate new token (classic)" → `repo` huquqi. Soʻralganda foydalanuvchi nomi
sifatida GitHub login’ingizni, parol sifatida token’ni kiriting.

**2) GitHub CLI** (osonroq):

```bash
gh auth login
git push -u origin main
```

Agar remote hali qoʻshilmagan boʻlsa:

```bash
git remote add origin https://github.com/diyorbek20037773/algorithm_journal.git
git branch -M main
git push -u origin main
```

Har bir push’dan keyin GitHub Actions avtomatik ishga tushadi
(`.github/workflows/ci.yml`): lint, 360 test, migratsiya tekshiruvi, zaxira va
tiklash mashqi. Natijani repozitoriyning **Actions** boʻlimida koʻrasiz.

---

Savol tugʻilsa, avval [`docs/`](docs/) ichidagi qoʻllanmalarga qarang:
[`ADMIN_GUIDE_uz.md`](docs/ADMIN_GUIDE_uz.md) — administrator uchun,
[`EDITOR_GUIDE_uz.md`](docs/EDITOR_GUIDE_uz.md) — muharrir uchun,
[`INTEGRATIONS.md`](docs/INTEGRATIONS.md) — Crossref, ORCID, DOAJ, Scopus va
Google Scholar bilan bogʻlanish tartibi.
