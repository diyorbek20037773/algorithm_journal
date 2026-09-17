# Mint Glass (Light) — MEZON dizayn tizimi

> Ushbu loyihada **"Mint Glass"** dizayn tizimining **yorug' (light)** moslashuvi amal qiladi.
> Asl tizim faqat tungi (dark) temada edi; bu yerda u ilmiy jurnal uchun light temaga
> o'girilgan, asl tungi palitra esa `prefers-color-scheme: dark` rejimida saqlangan.
> Manba kod: `static/src/css/input.css` (`@theme` tokenlari + `@layer components`).

---

## 0. Kod yozuvchi uchun qoidalar (o'zgartirmang)

1. Rangni hech qachon to'g'ridan-to'g'ri yozma (hex/rgb). Faqat `--color-*` tokenlari yoki
   ularning Tailwind utilitalari (`bg-paper-2`, `text-ink-2`, `border-[--color-line]` …).
2. Yangi rang qo'shma. Palitra yopiq: fon qatlamlari, shisha sirtlar, bitta mint urg'u, semantik 3 rang.
3. `box-shadow` ishlatma. Yagona istisno — `.btn-primary` / `.btn-gold` hover nuri (`--shadow-glow`).
4. Har qanday ajratilgan blok — `.card` (shisha karta). Yangi karta turini o'ylab topma.
5. Sarlavhalar: `font-weight: 800`, manfiy `letter-spacing` (h1 −0.03em, h2 −0.025em, h3 −0.02em).
6. Mint urg'u ekran maydonining ~5% dan oshmasin. **Bir ekranda bitta** to'ldirilgan mint tugma.
7. Sahifa 400px kenglikda gorizontal scrollsiz ishlashi shart.

---

## 1. Light moslashuv falsafasi

| Asl (dark) g'oya | Light'dagi talqini |
|---|---|
| Ko'kimtir-qora fon + yashil nur | Yalpizrang oq qog'oz `#f3f8f5` + yuqoridan yumshoq mint nur (radial gradient) |
| Chegaralar — oqning shaffofligi | Chegaralar — siyohning shaffofligi: `rgb(1 20 26 / .10)` |
| Shisha — to'q, 40% | Shisha — oq, 62% + `backdrop-filter: blur(10px)` |
| Matn toza oq emas (`#f2f7f5`) | Matn toza qora emas (`#0c1a1e`) |
| Mint `#84ffc1` matn ham bo'la oladi | Oq fonda `#84ffc1` o'qilmaydi → **ikki rol**: to'ldirish `--color-mint #3ddc97`, matn `--color-mint-text #047a4f` (oqda 5.4:1) |
| — | Footer va `.card-navy` — asl tungi palitraning bo'lagi ("qorong'u langar") |

---

## 2. Shrift

- **Manrope** 300–800 — hamma matn va sarlavhalar (`--font-sans`, `--font-serif` ikkalasi ham Manrope).
- **JetBrains Mono** — faqat identifikatorlar: DOI, ISSN, JEL, sana, metama'lumot (`.meta`, `.doi-line`).
  Ilmiy jurnalda bu identifikatorlarni ajratib ko'rsatish uchun saqlangan.
- Raqamlar ustunda: `font-variant-numeric: tabular-nums` (`.stat-num`, `.fact-value`, `.table`, `.queue-count`).
- O'qiladigan paragraf: `max-width: 64ch` (`.prose-journal`, `.masthead-lede`).

| Rol | Klass / qoida | O'lcham | Og'irlik | letter-spacing |
|---|---|---|---|---|
| Hero h1 | `.masthead-name`, `.page-hero h1` | `clamp(1.9rem, 1.3rem + 2.4vw, 3rem)` | 800 | −0.03em |
| h2 | `h2`, `.section-heading h2` | `clamp(1.35rem, 1.1rem + 1vw, 1.75rem)` | 800 | −0.025em |
| h3 / karta sarlavhasi | `h3`, `.article-title` | 1.15rem | 700–800 | −0.02em |
| Katta raqam | `.stat-num`, `.queue-count` | 2rem | 800 | −0.04em |
| Lead | `.masthead-lede` | `clamp(1.1rem, 1rem + .5vw, 1.3rem)` | 400 | 0 |
| Eyebrow | `.eyebrow` | .72rem UPPERCASE | 600 | +0.14em |

---

## 3. Tokenlar

| Token | Light | Dark (asl) | Vazifa |
|---|---|---|---|
| `--color-surface` | `#f3f8f5` | `#01141a` | sahifa foni |
| `--color-paper` | `#ffffff` | `#02151b` | shaffof bo'lmagan varaq: input, menyu |
| `--color-paper-2` | `#eaf2ee` | `#0c1a1e` | panel, tonal to'ldirish |
| `--color-paper-3` | `#dde8e3` | `#13252a` | chuqurroq katak (kbd) |
| `--color-glass` | `rgb(255 255 255/.62)` | `rgb(18 27 38/.40)` | karta foni |
| `--color-glass-deep` | `rgb(255 255 255/.82)` | `rgb(18 27 38/.60)` | navbar, ustma-ust karta |
| `--color-glass-soft` | `rgb(255 255 255/.55)` | `rgb(255 255 255/.05)` | ghost tugma, chip |
| `--color-glass-hover` | `rgb(1 20 26/.05)` | `rgb(255 255 255/.09)` | hover |
| `--color-line` / `-2` | `rgb(1 20 26/.10)` / `.17` | `rgb(255 255 255/.10)` / `.16` | chegaralar |
| `--color-ink` | `#0c1a1e` | `#f2f7f5` | asosiy matn, sarlavha |
| `--color-ink-2` | `#46565a` | `rgb(242 247 245/.72)` | tavsif (muted) |
| `--color-ink-3` | `#5b6b6f` | `rgb(242 247 245/.62)` | izoh (≥4.5:1) |
| `--color-mint` | `#3ddc97` | `#84ffc1` | **to'ldirish**: asosiy tugma, chip, progress |
| `--color-mint-ink` | `#04241a` | `#04241a` | mint ustidagi matn |
| `--color-mint-text` | `#047a4f` | `#84ffc1` | **matn** sifatidagi urg'u, focus kontur |
| `--color-mint-tint` / `-edge` | `.12` / `.26` | `.08` / `.22` | eyebrow foni/chegarasi, karta hover |
| `--color-navy-deep` | `#01141a` | `#0c1a1e` | qorong'u langar: logo belgisi, `.card-navy` |
| `--color-on-dark(-muted)` | `#f2f7f5` | — | qorong'u langar ustidagi matn |
| `--color-success/warning/danger` | `#15803d` / `#a16207` / `#b91c1c` | `#22c55e` / `#eab308` / `#f87171` | semantik (urg'udan alohida) |

Eski nomlar (`accent`, `gold`, `gold-bright` …) shablonlar buzilmasligi uchun saqlangan va yangi
qiymatlarga yo'naltirilgan: `accent` = siyoh, `gold*` = mint.

O'lchovlar: `--radius-badge 8px`, `--radius-control 12px`, `--radius-card 16px`,
`--radius-panel 24px`, `--radius-pill 100px`; konteyner `--container-page 1280px`, gutter 16px (md+ 32px).

---

## 4. Komponentlar

| Komponent | Klass | Eslatma |
|---|---|---|
| Suzuvchi navbar (qora shisha) | `.site-header > .container-page > .nav-pill` | sticky pill, `--color-glass-nav` = `rgb(1 20 26 / .92)` + blur 12px; ichida tungi palitra (och matn, `#84ffc1` tugma). Mobil menyu `.mobile-nav` ham shunday |
| Panel | `.panel`, `.console` | radius 24px |
| Shisha karta | `.card`, `.article-card`, `.section-card`, `.fact-tile`, `.pillar`, `.queue-tile` | 0.8px chegara, hover → `--color-mint-edge` |
| Qorong'u langar | `.card-navy`, `.site-footer` | asl tungi palitra + mint nur |
| Asosiy tugma | `.btn .btn-primary` | mint to'ldirish, hover −1px + nur. **Ekranda bitta** |
| Ghost tugma | `.btn-secondary`, `.btn-tonal`, `.btn-ghost` | qolgan barcha harakatlar |
| Eyebrow | `.eyebrow` | mint-tint pill |
| Chip | `.chip`, `.chip-gold` (tint), `.chip-navy` (mint to'ldirilgan) | |
| Raqamli karta | `.card.stat > .stat-num + .stat-lbl` + `.chip-navy` | |
| Lenta | `.ribbon` | sahifada 1–2 marta |
| Tasdiq ro'yxati | `ul.checks > li > .tick` | muhim so'z `<b>` |
| Iqtibos | `.quote`, `.prose-journal blockquote` | chapda 3px mint |
| Logotip to'ri | `.index-tile` | grayscale → rangli hover |
| Faol holat | `.nav-tab[aria-current]`, `.side-nav a[aria-current]` | mint-tint fon + mint nuqta |

---

## 5. Harakat

- Tugma hover: `translateY(-1px)` + `--shadow-glow`; karta hover: chegara → mint-edge; havola: muted → ink.
- Davomiylik 180–240ms, `ease`.
- `prefers-reduced-motion: reduce` — barcha animatsiya va transition o'chadi.
- Taqiqlangan: parallax, aylanuvchi gradient, doimiy pulsatsiya, slayderlar.

---

## 6. Tekshiruv ro'yxati

- [ ] Shablon va komponentlarda qattiq yozilgan hex yo'q — faqat `@theme` tokenlarida
- [ ] Mint ekranning ~5% dan ko'p emas; bir ekranda bitta `.btn-primary`
- [ ] `box-shadow` faqat asosiy tugma hover'ida
- [ ] Sarlavhalar 800 + manfiy letter-spacing
- [ ] Matn `#0c1a1e`, tavsif `--color-ink-2`
- [ ] Karta radiusi 16px, panel 24px
- [ ] 400px'da gorizontal scroll yo'q
- [ ] `:focus-visible` — 2px `--color-mint-text` kontur
- [ ] `prefers-reduced-motion` hisobga olingan
- [ ] Rasmlar `alt` ga ega; kontrast ≥ 4.5:1
