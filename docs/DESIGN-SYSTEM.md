# MEZON dizayn tizimi

> Manba: mijoz bergan **TEXNIK TOPSHIRIQ** (ilmiy jurnal veb-sayti, maqola
> sahifasi). Namuna sifatida Taylor & Francis Online maqola sahifasining
> tuzilishi va ishlash mantigʻi olingan; **logotip, nom, brend va matnlar
> bizniki** — T&F belgilari ishlatilmaydi.
> Kod: `static/src/css/input.css` (`@theme` + `@layer components`),
> maqola sahifasi mebeli: `static/src/css/article.css`,
> tahririyat konsoli: `static/src/css/console.css`.

---

## 0. Kod yozuvchi uchun qoidalar

1. Rangni qattiq yozmang — faqat `--color-*` tokenlari.
2. Palitra yopiq: navy, yashil aksent, ochiq kirish uchun toʻq sariq, uchta semantik rang.
3. Sarlavhalar **PT Serif**, interfeys va matn **Open Sans**.
4. Radius 4px (tugma, karta), 2px (belgi). Yumaloq pill yoʻq.
5. Sahifa 400px kenglikda gorizontal scrollsiz ishlashi shart.

---

## 1. Tokenlar (TEXNIK TOPSHIRIQ §2)

| Token | Qiymat | Vazifa |
|---|---|---|
| `--color-accent` | `#10147e` | navy: havola, breadcrumb, sticky panel, footer, tugma |
| `--color-navy-midnight` | `#0a0d5c` | footer ustidagi toʻqroq qator |
| `--color-mint` | `#6cd775` | yashil aksent: "Maqola yuborish", "PDF koʻrish", faol tab |
| `--color-mint-text` | `#2f7a37` | oq fonda oʻqiladigan yashil (4.6:1) |
| `--color-ink` | `#333333` | asosiy matn |
| `--color-ink-2` | `#666666` | sana, sahifalar, metama'lumot |
| `--color-surface` / `--color-paper` | `#ffffff` | sahifa va varaq |
| `--color-paper-2` | `#f5f5f5` | maqola sarlavhasi bloki, tonal toʻldirish |
| `--color-gold-bright` | `#f29100` | Open Access qulfi va burchak belgisi |
| `--color-gold` | `#b06a00` | oʻsha rangning matn uchun qoraytirilgani (4.6:1) |
| `--color-line` / `-2` | `#e0e0e0` / `#cccccc` | chegaralar |

Oʻlchov: konteyner `--container-page 1280px`, oʻqish ustuni 680px,
radius `--radius-control 4px`, `--radius-badge 2px`.

Eski nomlar (`mint*`, `gold*`, `glass*`) saqlangan va yangi qiymatlarga
yoʻnaltirilgan — shuning uchun 80 dan ortiq shablon markup tahririsiz yangi
koʻrinishni oldi.

---

## 2. Shrift

| Rol | Shrift | Oʻlcham |
|---|---|---|
| H1 | PT Serif 700 | 34px |
| H2 | PT Serif 700 | 22px |
| H3 | PT Serif 700 | 18px |
| Matn | Open Sans 400 | 16px / 1.6 |
| Abstrakt | Open Sans 400 | 17.6px / 1.7 |
| Mayda (breadcrumb, tab, meta) | Open Sans | 13–14px |

---

## 3. Maqola sahifasi (TEXNIK TOPSHIRIQ §3)

| Boʻlak | Klass | Izoh |
|---|---|---|
| Breadcrumb tasmasi | `.crumb-bar` | navy fon, oq 13px matn, `›` ajratgich |
| Jurnal bloki | `.journal-strip`, `.journal-cover` | muqova 80×130, jurnal nomi, jild/son, yashil + navy tugma, qidiruv |
| Sarlavha bloki | `.article-band` | och kulrang `#f5f5f5`, tepasida uchburchak koʻrsatkich |
| Metrikalar ustuni | `.band-metrics`, `.band-metric` | katta raqam + kichik yozuv, orasida chiziq |
| Open Access belgisi | `.oa-flag` | toʻq sariq qulf |
| Tab qatori | `.tab-bar`, `.tab-item` | faol tab navy fon + oq matn; har tab oʻz URL'i |
| Scroll paneli | `.scroll-bar` | 320px dan pastga aylantirilganda navy panel |
| 3 ustunli layout | `.read-grid` | 180px mundarija · maqola · 280px tavsiyalar |
| Mundarija | `.toc-rail`, `.toc-list` | scroll-spy, navy vertikal chiziq, faol boʻlim kulrang fonda |
| Rasm/jadval | `.figure-block`, `.figure-caption` | "Figure 1." izohi va yuklab olish havolalari |
| Adabiyotlar | `.ref-list`, `.ref-links` | har manba ostida Crossref / Google Scholar |
| Tavsiyalar paneli | `.related-panel`, `.related-tab`, `.related-card` | 3 tab, kartochka tepasida navy chiziq, OA burchagi |
| Footer | `.site-footer`, `.footer-top` | navy, 5 ustun, obuna va ijtimoiy ikonkalar |

Tab manzillari: `/article/<pk>/`, `…/figures/`, `…/references/`,
`…/citations/`, `…/metrics/`, `…/licensing/` — hammasi bitta shablon,
`ArticleDetailView.tab` bilan farqlanadi.

Mundarija va rasm/jadval roʻyxati toʻliq matn HTML'idan avtomatik olinadi:
`apps/journal/fulltext.py` (`outline`, `with_anchors`, `floats`).

---

## 4. Responsiv (TEXNIK TOPSHIRIQ §7)

- **≥1200px** — 3 ustun.
- **768–1199px** — tavsiyalar paneli yashiriladi, mundarija chapda qoladi.
- **<768px** — mundarija "☰ Ushbu maqolada" tugmasi ostida, tablar gorizontal
  scroll, metrikalar bir qatorda.

---

## 5. Tekshiruv roʻyxati

- [ ] Shablonlarda qattiq yozilgan hex yoʻq
- [ ] Bir ekranda bitta yashil `.btn-primary`
- [ ] Sarlavhalar PT Serif, matn Open Sans 16px `#333`
- [ ] Radius 4px; pill yoʻq
- [ ] 400px'da gorizontal scroll yoʻq
- [ ] `:focus-visible` — 2px navy kontur
- [ ] Kontrast ≥ 4.5:1 (yashil matn `#2f7a37`, toʻq sariq matn `#b06a00`)
- [ ] `prefers-reduced-motion` hisobga olingan
