# DESIGN_BRIEF.md — Visual design for ALGORITHM: Review of Economic Research

This brief serves two readers:
1. **Claude Design** — to produce the visual design (HTML + Tailwind pages) into a `design/` folder.
2. **Claude Code** — to implement the templates. If `design/` is absent, this document is the design.

Journal: **ALGORITHM: Review of Economic Research** (short: ARER). Open-access, peer-reviewed,
monthly economics journal from Uzbekistan aiming at Scopus. Four languages (EN, UZ Latin,
UZ Cyrillic, RU). The client's one-line direction: **"simple, cool"** — the calm confidence of a
top international journal, not a government portal and not a startup landing page.

---

## 1. Design principles

1. **Editorial, not promotional.** Content (titles, authors, abstracts) is the interface. Whitespace
   and typography do the work. No hero images of skyscrapers, no stock photos, no sliders.
2. **Credibility at a glance.** ISSN, DOI, license, "No APC", peer-review type are visible on the
   home page within the first screen, in a restrained "credibility strip".
3. **One accent colour.** Everything else is ink, paper and grey.
4. **Structured like an algorithm.** The name is the concept: subtle grid, precise alignment, a
   monospace detail face for identifiers (DOI, ISSN, JEL codes, dates), thin rules, numbered
   steps. Nothing gimmicky — no circuit-board graphics, no binary code decorations.
5. **Four scripts, one look.** Latin (with Uzbek `oʻ gʻ`), Cyrillic — chosen fonts must render all
   of them; layouts must survive longer Uzbek/Russian strings (+30 %).
6. **Accessibility is design.** WCAG 2.1 AA: contrast ≥ 4.5:1, visible focus rings, 16 px base,
   touch targets ≥ 44 px, reduced-motion respected.

## 2. Design tokens (Claude Code: put these in `static/src/css/input.css` as `@theme` for Tailwind v4)

### Colour
| Token | Light | Dark (optional `prefers-color-scheme`) | Use |
|---|---|---|---|
| `--color-paper` | `#FFFFFF` | `#0F1419` | page background |
| `--color-paper-2` | `#F6F7F9` | `#151B22` | subtle sections, cards |
| `--color-ink` | `#111827` | `#E6EAF0` | primary text |
| `--color-ink-2` | `#4B5563` | `#A6B0BD` | secondary text |
| `--color-ink-3` | `#9CA3AF` | `#6B7684` | meta text, placeholders |
| `--color-line` | `#E5E7EB` | `#242D38` | rules, borders |
| `--color-accent` | `#0F4C81` (deep "algorithm blue") | `#5FA8FF` | links, primary buttons, active states |
| `--color-accent-2` | `#0B3A63` | `#8CC2FF` | hover |
| `--color-accent-soft` | `#E8F1FA` | `#12283F` | chips, highlights |
| `--color-success` | `#15803D` | `#4ADE80` | published, accepted |
| `--color-warning` | `#B45309` | `#FBBF24` | overdue, pending |
| `--color-danger` | `#B91C1C` | `#F87171` | reject, errors |
| `--color-orcid` | `#A6CE39` | same | ORCID icon only |

Accent contrast on white: `#0F4C81` ≈ 8.6:1 ✔.

### Typography (Google Fonts, all with Cyrillic + Latin-ext subsets)
- **Display / headings:** `"Source Serif 4"` (600/700; optical size axis) — scholarly, modern serif.
- **Body / UI:** `"Inter"` (400/500/600) — readable at small sizes, full Cyrillic.
- **Mono (identifiers):** `"JetBrains Mono"` (400/500) for DOI, ISSN, JEL, dates in meta lists.
- Fallbacks: `Georgia, "Times New Roman", serif` / `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` / `ui-monospace, "SF Mono", Menlo, monospace`.
- Scale (rem): 0.75, 0.875, 1 (base 16 px), 1.125, 1.25, 1.5, 1.875, 2.25, 3. Line-height 1.6 body,
  1.2 headings. Article title on landing page: 1.875–2.25 rem serif 700, max-width 40 ch.
- Measure: body text max-width 70 ch; abstract 75 ch.

### Spacing, radius, shadow
- 4-pt spacing scale; section padding 64/96 px desktop, 40/56 mobile; container max 1200 px,
  article reading column 760 px + 300 px rail.
- Radius: 6 px (inputs, buttons, chips), 10 px (cards). No pill buttons except chips.
- Shadow: cards flat with 1 px `--color-line` border; a single soft shadow only for modals/menus.
- Motion: 150 ms ease for hover/focus, none for layout. Respect `prefers-reduced-motion`.

### Iconography
- Lucide icons (inline SVG, stroke 1.75), 20 px. Official ORCID iD icon, Crossref logo, CC BY
  badge (official SVGs only).

## 3. Logo / word-mark

Claude Design should produce 3 word-mark variants (SVG, horizontal + stacked, mono + colour, dark
variant), all typographic, no mascots, no emblems:
- **A. "ALGORITHM" in Source Serif 4 700, tracking +2 %, with the descriptor "Review of Economic
  Research" in Inter 500 small caps beneath; a thin accent rule between them.**
- B. Same, with the "O" replaced by a precise circle stroke (a nod to a loop/algorithm) — subtle.
- C. Mono-spaced `ALGORITHM` in JetBrains Mono 500 with `Review of Economic Research` serif — the
  "code meets scholarship" reading.
Descriptor must also exist in UZ Latin («ALGORITM» — iqtisodiy tadqiqotlar sharhi), UZ Cyrillic
(«АЛГОРИТМ» — иқтисодий тадқиқотлар шарҳи) and RU («АЛГОРИТМ» — обзор экономических исследований);
the top word "ALGORITHM/ALGORITM/АЛГОРИТМ" changes with language. Favicon: the letter "A" in a
square with the accent colour. Claude Code: if no logo files exist, render the word-mark in
HTML/CSS (variant A) — it must look intentional.

## 4. Global components

- **Header (sticky, 64 px):** word-mark left; primary nav: *Current Issue · Archive · Online First ·
  For Authors · For Reviewers · About*; right: search icon (expands to input), language switcher
  (`EN · UZ · ЎЗ · RU` as a compact segmented control or dropdown), "Submit" primary button,
  "Sign in" text link (avatar menu when logged in). Mobile: hamburger → full-height sheet.
- **Announcement bar** (optional, dismissible per session).
- **Footer (paper-2):** 4 columns: Journal (about, board, contact, ISSN line, certificate line,
  publisher/address) · For Authors (guidelines, template, checklist, fees, ethics) · Browse (current,
  archive, online first, sections, JEL, search) · Machine (RSS, OAI-PMH, sitemap, API, LOCKSS);
  bottom row: © year, CC BY 4.0 with badge, privacy, language links. No counters, no badges walls.
- **Credibility strip:** horizontal list of label/value pairs in mono: `e-ISSN 0000-0000 ·
  DOI 10.xxxxx · Open Access CC BY 4.0 · No APC · Double-blind review · Monthly since 2026`.
- **Article card (list item):** section tag (small caps, accent), serif title (link), authors
  (ink-2, ORCID icons inline), meta line mono (Vol/No, pages, DOI), abstract excerpt (2 lines,
  optional), actions row (PDF · Cite · views/downloads with labels).
- **Issue cover (generated):** if no cover uploaded, render a typographic cover: paper-2
  rectangle 3:4 with "Vol. 1 · No. 3" large serif, month/year, thin grid pattern in line colour.
- **Chips:** keyword (paper-2, ink), JEL (mono, accent-soft), status (coloured dot + text).
- **Buttons:** primary (accent bg, white text), secondary (white, 1 px line), ghost. Sizes 40/44 px.
- **Meta definition list:** two-column `dt` (ink-3 small caps) / `dd` (mono or body).
- **Cite modal:** style select (segmented or dropdown), rendered citation in a paper-2 box with
  copy button, export buttons row (BibTeX, RIS, EndNote, CSL-JSON).
- **Timeline (submission status):** vertical steps with dates; current step accent.
- **Tables (dashboard):** dense, sticky header, zebra none, hover row, sortable indicators.
- **Forms:** labels above, helper text below, error inline red, required asterisk, focus ring
  2 px accent; file dropzones with progress.
- **Empty states:** icon + one sentence + action.
- **Toast** (HTMX-triggered) top-right.

## 5. Page designs (Claude Design: produce each as a full-width desktop artboard at 1440 px and
a mobile artboard at 390 px; name files exactly as below)

| File | Page | Key layout notes |
|---|---|---|
| `01-home.html` | Home | Masthead: journal name as large serif title + descriptor + credibility strip + two CTAs, on paper; below, 2-column: current issue (cover + 6 article cards) left, "Online First" + announcements right; then sections grid (8 cards, each with count), JEL top-level chips, "Most read" list, indexing logos row (small, grey), author journey 4-step strip. |
| `02-issue.html` | Issue TOC | Issue header band (cover, Vol/No/Year, published, DOI, editorial note); articles grouped by section headers; prev/next issue at bottom. |
| `03-article.html` | Article landing | Breadcrumb; badges; title; authors with affiliations; meta dl; abstract with language tabs; sticky right rail (PDF, Cite, Share, Metrics, License); statements; references list; how-to-cite box; related. Mobile: rail becomes a fixed bottom bar with PDF + Cite. |
| `04-archive.html` | Archive | Year filter row; per volume: issue cards grid (cover, No., month, count). |
| `05-search.html` | Search | Left filter panel (collapsible on mobile), results as article cards with highlights, sort control, result count. |
| `06-board.html` | Editorial board | Role group headings; member cards (photo optional circle 72 px, name, degree, affiliation, country, ORCID/Scopus/email icons, expertise). |
| `07-policy.html` | Generic policy/about page | Left sub-navigation of the About group; content column with generous type; right "On this page" TOC. Use for all policy pages. |
| `08-for-authors.html` | Author hub | Guided funnel: 5 numbered steps as cards (Scope → Prepare → Checklist → Submit → After submission), then FAQ accordion, "No fees" callout, template downloads. |
| `09-submit-wizard.html` | Submission wizard | Stepper (5 steps), one step's form shown (Metadata step: multilingual tabs for title/abstract/keywords, JEL picker, authors repeater). |
| `10-dashboard-editor.html` | Editor dashboard | Left nav (queues with counts), KPI cards row, submissions table with status chips and reviewer status dots, filters. |
| `11-dashboard-submission.html` | Submission detail (editor) | Header (ID, title, status, section, dates), tabs (Summary/Files/Reviewers/Reviews/Decision/Discussion/History), reviewer panel, decision drawer. |
| `12-dashboard-reviewer.html` | Reviewer dashboard + review form | Invitations cards, active reviews with due countdown, structured review form (6 score rows + text areas + upload). |
| `13-dashboard-author.html` | Author dashboard | My submissions with status timeline, actions needed, messages. |
| `14-production-issue-builder.html` | Issue builder | Left: unassigned accepted/online-first articles; right: issue sections with draggable articles, page range inputs, "Publish issue" checklist. |
| `15-auth.html` | Sign in / sign up | Centered card, email+password, "Sign in with ORCID" button (green iD), 2FA code screen variant. |
| `16-statistics.html` | Public statistics | KPI cards + one inline SVG bar chart + country list. |
| `17-errors.html` | 404/500 | Minimal, serif heading, links to home/search. |
| `18-email.html` | Email template | 600 px single column, word-mark, body, button, footer — for all notifications. |

Each artboard should exist in **EN**, and `01-home` and `03-article` additionally in **UZ Cyrillic**
to prove the type works with Cyrillic and long strings.

## 6. Content rules for the design (also binding for implementation)

- Never show: state emblems/flags as images, photos of officials, fake metrics ("Impact Factor",
  "SJIF", "ICV"), visitor counters, "best viewed in", marquee text, auto-playing anything.
- Show only real indexing services; grey-scale logos, small.
- Language switcher visible on every page, top right, all four options.
- Every article entry shows DOI and license; every number is labelled ("Views", "Downloads").
- Use real-looking demo content: sensible economics titles (e.g. "Customs Digitalisation and
  Trade Facilitation in Central Asia: Evidence from Firm-Level Data"), real institution-style
  affiliations (fictional names allowed), JEL codes like F13, H26, O33.
- Design in light mode first; dark mode optional but tokens exist.

## 7. Deliverable format from Claude Design

- Folder `design/` with the HTML files above, each self-contained (Tailwind via CDN or compiled
  inline CSS is fine for the mock), shared `design/tokens.css` with the tokens in §2, `design/logo/`
  SVGs (variants A/B/C, light/dark, horizontal/stacked, favicon), `design/README.md` explaining
  component names. Use the exact token names above so implementation maps 1:1.
- Screens must be pixel-clean at 1440 and 390 px widths and must not use images that do not exist
  (use generated typographic covers and initials avatars).
