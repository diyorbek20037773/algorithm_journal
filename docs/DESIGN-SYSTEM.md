# Academic Royal Prestige — MEZON dizayn tizimi

> Loyihada **"Academic Royal Prestige / White Ink Edition"** dizayn tizimi amal qiladi.
> Manba: `design/stitch_modern_economic_journal_dashboard/academic_royal_prestige/DESIGN.md`
> va oʻsha papkadagi uchta maket. Bitta palitra butun saytga — ommaviy oʻqish qismiga ham,
> tahririyat konsoliga (dashboard) ham — tegishli.
> Kod: `static/src/css/input.css` (`@theme` tokenlari + `@layer components`),
> konsolga xos mebel: `static/src/css/console.css`.

---

## 0. Kod yozuvchi uchun qoidalar (oʻzgartirmang)

1. Rangni hech qachon toʻgʻridan-toʻgʻri yozmang (hex/rgb). Faqat `--color-*` tokenlari yoki
   ularning Tailwind utilitalari (`bg-paper-2`, `text-ink-2`, `border-[--color-line]` …).
2. Yangi rang qoʻshmang. Palitra yopiq: fon qatlamlari, qirol siyohi + binafsha, uchta semantik rang.
3. Soya — faqat tizimdagi uchta token (`--shadow-card`, `--shadow-hover`, `--shadow-menu`).
   Hajm soya bilan emas, **1px `--color-line` chizigʻi va tonal qatlam** bilan beriladi.
4. Har qanday ajratilgan blok — `.card` (oq varaq). Yangi karta turini oʻylab topmang.
5. Sarlavhalar — **Merriweather** (`--font-serif`), interfeys va matn — **Inter** (`--font-sans`),
   identifikatorlar (DOI, ISSN, JEL, sana) — **JetBrains Mono** (`--font-mono`).
6. Yumaloq "pill" shakllar taqiqlangan: radius 2px (shtamp), 4px (boshqaruv, karta), 8px (panel).
7. Sahifa 400px kenglikda gorizontal scrollsiz ishlashi shart.

---

## 1. Falsafa

| Gʻoya | Amalda |
|---|---|
| Toza qogʻoz kanvasi | Fon `#faf9fd` — gradient ham, nur ham yoʻq; varaqlar toza `#ffffff` |
| Chuqur akademik siyoh | Sarlavhalar `#1f1435`, matn `#2d2245` — qora emas, qirol siyohi |
| Ilmiy qatʼiylik | 1px `#e7e0f2` hairline chiziqlar, oʻtkir 2–4px burchaklar |
| Tipografik keskinlik | Klassik serif sarlavha + analitik sans interfeys |
| Bitta urgʻu | `#2a164d` toʻldirish, `#6c28d6` ikkilamchi — ikkalasi ham binafsha-siyoh |
| Bitta palitra | Tungi (dark) tema yoʻq: bu "White Ink Edition", `color-scheme: light` |

---

## 2. Shrift

- **Merriweather** 400/600/700 — masthead, maqola sarlavhalari, boʻlim sarlavhalari (`--font-serif`).
- **Inter** 400–700 — interfeys, matn, jadval, muallif satrlari, filtrlar (`--font-sans`).
- **JetBrains Mono** — identifikatorlar: DOI, ISSN, JEL, sana, metama'lumot (`.meta`, `.doi-line`).
- Yorliqlar (`.eyebrow`, `.chip`, `.nav-tab`, `.stat-label`) — **UPPERCASE**, tracking +0.04…+0.06em:
  arxiv kartotekasi shtampi taassuroti.
- Raqamlar ustunda: `font-variant-numeric: tabular-nums`.
- Oʻqiladigan paragraf: `max-width: 64ch` (`.prose-journal`, `.masthead-lede`).

| Rol | Klass / qoida | Shrift | Ogʻirlik | letter-spacing |
|---|---|---|---|---|
| Hero h1 | `.masthead-name` | Merriweather | 700 | −0.02em |
| h2 | `h2`, `.section-heading h2` | Merriweather | 700 | −0.015em |
| h3 / karta sarlavhasi | `h3`, `.article-title` | Merriweather | 600 | −0.01em |
| Sahifa sarlavhasi (konsol) | `.page-title` | Merriweather 32/42 | 700 | −0.015em |
| Katta raqam | `.stat-value`, `.queue-count` | Inter | 700 | 0 |
| Matn | `body`, `.prose-journal p` | Inter 15/24 | 400 | 0 |
| Eyebrow / chip | `.eyebrow`, `.chip` | Inter 11px UPPERCASE | 600 | +0.05em |

---

## 3. Tokenlar

| Token | Qiymat | Vazifa |
|---|---|---|
| `--color-surface` | `#faf9fd` | sahifa foni (arxiv qogʻozi) |
| `--color-paper` | `#ffffff` | varaq: karta, input, menyu |
| `--color-paper-2` | `#f7f5fc` | tonal toʻldirish: inset panel, izoh bloki |
| `--color-paper-3` | `#ede9f5` | chuqurroq katak (kbd, hover) |
| `--color-glass*` | `#ffffff` / `#f4f1fa` | eski "shisha" nomlari — endi qattiq varaq va hover |
| `--color-line` / `-2` | `#e7e0f2` / `#d8d1e5` | hairline chegaralar |
| `--color-ink` | `#1f1435` | sarlavha (royal ink) |
| `--color-ink-2` | `#2d2245` | matn (plum body) |
| `--color-ink-3` | `#554d68` | izoh, meta (≥4.5:1) |
| `--color-accent` | `#2a164d` | **toʻldirish**: asosiy tugma, masthead, faol indeks |
| `--color-accent-2` | `#6c28d6` | ikkilamchi: havola, faol tab, iqtibos asboblari |
| `--color-accent-soft` | `#ede9fe` | eyebrow foni, faol rail elementi |
| `--color-mint` → `#2a164d` | `--color-mint-ink` `#ffffff` | eski nomlar: toʻldirish va ustidagi matn |
| `--color-mint-text` | `#4a1d7a` | **matn** sifatidagi urgʻu (oqda 7.4:1) |
| `--color-mint-bright` | `#a67ffd` | qorongʻu langar ustidagi yorugʻ binafsha |
| `--color-gold*` | `#9c5700` / `#fef7ed` / `#fcd9bd` | iqtibos-amber shtampi: "Peer-reviewed", CFP, Online First |
| `--color-success*` | `#1b6e4a` / `#ebf7f1` / `#b8e5d1` | ochiq kirish (open access) yashili |
| `--color-navy-deep` | `#1f103a` | qorongʻu langar: footer, `.card-navy` |
| `--color-on-dark(-muted)` | `#ffffff` / 72% | langar ustidagi matn |
| `--color-danger` | `#ba1a1a` | xato |

Eski nomlar (`mint*`, `gold*`, `glass*`) shablonlar buzilmasligi uchun saqlangan va yangi
qiymatlarga yoʻnaltirilgan — shuning uchun 80 dan ortiq shablon bitta ham oʻzgarishsiz yangi
koʻrinishga oʻtdi.

Oʻlchovlar: `--radius-badge 2px`, `--radius-control 4px`, `--radius-card 4px`,
`--radius-panel 8px`, `--radius-pill 4px` (pill qasddan oʻchirilgan);
konteyner `--container-page 1360px`, oʻqish ustuni 760px.

Soyalar: `--shadow-card` `0 1px 2px rgb(42 22 77/.04)`,
`--shadow-hover` `0 4px 16px -2px rgb(42 22 77/.08)`,
`--shadow-menu` `0 20px 28px -6px rgb(31 20 53/.14)`.

---

## 4. Komponentlar

| Komponent | Klass | Eslatma |
|---|---|---|
| Masthead | `.site-header > .container-page > .nav-pill` | oq sticky satr, pastda 1px hairline; tab qatori ikkinchi qator |
| Tab | `.nav-tab` | UPPERCASE label; faol holatda 2px `--color-accent-2` chizigʻi |
| Utility bar | `.utility-bar` | `#f3effb` tasma: ISSN, DOI, litsenziya, til |
| Karta | `.card`, `.article-card`, `.section-card`, `.fact-tile` | oq varaq + 1px hairline + `--shadow-card` |
| Panel | `.panel`, `.console` (bosh sahifadagi qidiruv) | radius 8px |
| Qorongʻu langar | `.card-navy`, `.site-footer` | `#1f103a`; ichida `.eyebrow` va tugmalar teskari rangda |
| Asosiy tugma | `.btn .btn-primary` | siyoh toʻldirish, hover `#3b1e6d`. **Ekranda bitta** |
| Ikkilamchi | `.btn-secondary` | oq fon + 1px siyoh chegara; `.btn-tonal`, `.btn-ghost` — tinchroq |
| Eyebrow | `.eyebrow` | `#ede9fe` shtamp, 2px radius |
| Chip | `.chip`, `.chip-green` (OA), `.chip-gold` (amber), `.chip-jel` (mono) | |
| Jadval | `.table` | 1px gorizontal chiziq, vertikal chiziq yoʻq, UPPERCASE ustun sarlavhasi |
| Konsol mebeli | `.console-header`, `.console-tab`, `.console-rail`, `.rail-item`, `.panel-head`, `.stat-tile`, `.attention-row` | faqat `body.editorial-console` ichida, `console.css` |

---

## 5. Harakat

- Tugma hover: rang + `--shadow-hover` (koʻtarilish yoʻq); karta hover: soya + chegara.
- Davomiylik 160–200ms, `ease`.
- `prefers-reduced-motion: reduce` — barcha animatsiya va transition oʻchadi.
- Taqiqlangan: parallax, aylanuvchi gradient, doimiy pulsatsiya, slayderlar, karusel.

---

## 6. Tekshiruv roʻyxati

- [ ] Shablon va komponentlarda qattiq yozilgan hex yoʻq — faqat `@theme` tokenlari
- [ ] Bir ekranda bitta `.btn-primary`
- [ ] Soya faqat tizim tokenlaridan; hajm hairline bilan beriladi
- [ ] Sarlavhalar Merriweather, interfeys Inter, identifikatorlar JetBrains Mono
- [ ] Yorliqlar UPPERCASE + tracking
- [ ] Karta radiusi 4px, panel 8px, shtamp 2px; pill yoʻq
- [ ] 400px'da gorizontal scroll yoʻq
- [ ] `:focus-visible` — 2px `--color-accent` kontur
- [ ] `prefers-reduced-motion` hisobga olingan
- [ ] Rasmlar `alt` ga ega; kontrast ≥ 4.5:1
