# PROGRESS.md

Status log for **MEZON: Review of Economic Research (MRER)**.
Updated at the end of every delivery phase (SPEC §14). The acceptance checklist
of SPEC §15, marked ✅/⚠️, is in `HANDOFF.md`.

---

## Phase 0 — Repository bootstrap ✅

**Done**

- `uv` project (`pyproject.toml`) on Python 3.12 / Django 5.2 LTS, with a `dev`
  extra covering pytest, Playwright, ruff, djlint and mypy.
- Settings split into `config/settings/{base,dev,prod,test}.py`, everything
  environment-driven through `django-environ`; `.env.example` documents every
  variable with a safe default.
- Custom `uz-cyrl` locale registered in `config/locale_info.py`; date and number
  formats for `en`, `uz`, `uz_Cyrl`, `ru` in `config/formats/`.
- Docker Compose development stack: `db` (Postgres 16), `redis`, `web`,
  `tailwind`, `worker`, `beat`, `mailpit`, plus an `analytics` profile with
  Matomo. `Dockerfile` is multi-stage and compiles the message catalogues.
- `Makefile`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`.

**Verified** — `manage.py check` clean; `makemigrations --check` clean; the
image builds and `docker compose up` serves the site.

---

## Phase 1 — Accounts, i18n and the design system ✅

**Done**

- Custom `accounts.User` (e-mail login, Argon2), `Profile` with ORCID,
  affiliation, expertise and reviewer statistics; role groups per SPEC §3 with
  permission mixins.
- django-allauth with mandatory e-mail verification and the ORCID provider
  (sandbox by default); adapters store the authenticated ORCID iD.
- `StaffTwoFactorMiddleware` forces TOTP enrolment for editorial roles;
  enrolment page with QR code and ten single-use recovery codes.
- `apps/core/translit.py`: deterministic Uzbek Latin ↔ Cyrillic transliterator
  with digraph, apostrophe and capitalisation handling, an exception dictionary
  and placeholder protection, plus a `pre_save` hook that fills empty
  `*_uz_cyrl` fields and records what it generated.
- Design system from `DESIGN_BRIEF.md` as Tailwind v4 `@theme` tokens and
  component classes; `base.html` with sticky header, four-language switcher,
  footer, skip link, `hreflang`, Open Graph and feed discovery.
- Error pages 400/403/404/500 and the lockout page.

**Verified** — 51 transliterator tests; 2FA redirect test; every page renders in
four languages.

---

## Phase 2 — Journal content and the public site ✅

**Done**

- Journal models (`Section`, `Volume`, `Issue`, `Article`, `Author`, `Keyword`,
  `JELCode`, `Reference`, `Galley`, `License`, `EditorialBoardMember`), all
  translated, indexed and admin-registered; CMS models in `apps.core`.
- Public pages: home, archive, issue TOC, article landing (Highwire, Dublin
  Core, JSON-LD `ScholarlyArticle`), Online First, section/keyword/JEL/author
  pages, both boards, every policy page, announcements, contact, statistics.
- Machine endpoints: `robots.txt`, sitemap index and sections, RSS and Atom
  feeds (journal-wide and per section), `/healthz/`.
- `seed_demo`: site settings, nine sections, 326 JEL codes, sixteen policy and
  author pages in four languages, thirteen e-mail templates, indexing services,
  a twelve-member DEMO board, eight demo users, Volume 1 with three published
  issues, fourteen articles with generated PDF galleys and 20–35 references,
  ninety days of usage statistics, and twenty-two submissions covering every
  workflow state.

**Verified** — every public URL returns 200 in all four languages; 22 mandatory
pages tested per language.

---

## Phase 3 — Citations, metrics, API ✅

**Done**

- `apps/citations`: CSL rendering in six styles (APA, MLA, Chicago, Harvard,
  Vancouver, GOST) with a hand-written fallback; BibTeX / RIS / EndNote /
  CSL-JSON exports; HTMX cite modal.
- `apps/metrics`: `AccessEvent` with salted-hash identifiers, COUNTER-style bot
  filter, 30-second double-click filter, nightly aggregation, `EditorialKPI`
  snapshots, public statistics page with a server-rendered SVG bar chart.
- `apps/api`: read-only DRF endpoints for articles, issues, sections, search and
  a DOAJ-shaped export; CORS-open for GET, throttled at 60/min.

**Verified** — exports parse with `bibtexparser` and `rispy`; bot and
double-click filtering tested; API hides unpublished data.

---

## Phase 4 — Submission wizard ✅

**Done**

- Five-step wizard with per-step saving, resumable drafts and a completeness
  gate; file validation (extension allow-list, size cap, MIME sniffing, optional
  ClamAV, DOCX/PDF word counting, UUID storage paths).
- Multilingual metadata capture with automatic Uzbek Cyrillic generation,
  authors formset with ORCID validation, JEL picker, statements.
- Author dashboard with a status timeline, revision upload and withdrawal.

---

## Phase 5 — Editorial workflow ✅

**Done**

- Hand-written FSM in `apps/submissions/workflow.py`: every transition performs
  a permission check, timestamps, an `AuditLog` entry, a system message and
  asynchronous notification.
- Screening with the pluggable plagiarism provider (`ManualProvider` default,
  `IThenticateProvider` config-gated), threshold gate with EIC override.
- Reviewer finder, invitations with one-click e-mail tokens, structured
  six-criterion review form with drafts and PDF metadata scrubbing, decisions
  with merged letters, revision rounds, Celery reminders.

**Verified** — 26 workflow tests and 10 non-leakage tests proving reviewer pages
carry no author identity and author pages no reviewer identity.

---

## Phase 6 — Production, Crossref, OAI-PMH, preservation ✅

**Done**

- Production stages and checklist, galley upload, metadata completeness check,
  DOI reservation (`10.xxxxx/arer.{year}.{id:04d}`, issue-independent), PDF
  stamping, Online First publication, issue builder and issue publication.
- Crossref 5.4.0 XML generator with abstracts, ORCID, licence, crawler and
  text-mining collections and the citation list; **the real Crossref XSD bundle
  is committed** and all fourteen seeded articles validate against it; deposit
  client, status polling, cited-by fetch.
- OAI-PMH 2.0: all six verbs, `oai_dc` and `jats`, sets for sections and
  volumes, resumption tokens, deleted records for retractions.
- LOCKSS manifests, per-issue export bundle, DOAJ export.

**Verified** — 17 OAI conformance tests; 14 Crossref tests; export bundle
produced for issue 1.

---

## Phase 7 — Hardening ✅

**Done**

- Security settings, CSP, rate limits, django-axes, audit log, upload scanning
  hooks, Redis caching with publication invalidation.
- Query-count assertions (home, issue, article ≤ 15 queries), static bundle size
  assertions (CSS 4.7 KB gzipped, JS 30 KB gzipped).
- Accessibility pass with axe-core over home, issue, article, search, board,
  submit and dashboard: the ORCID mark became a real SVG logo, `--color-ink-3`
  was darkened to pass 4.5:1, links inside running text are underlined, and the
  search results heading level was corrected.
- Complete translations: 1,170 interface strings in English, Uzbek Latin, Uzbek
  Cyrillic (generated by the project's own transliterator) and Russian, with
  `scripts/check_translations.py` reporting 0 untranslated and 0 fuzzy.
- End-to-end editorial flow test and Playwright screenshots at 360/768/1280/1920
  in `docs/screenshots/`.

---

## Phase 8 — Production stack and documentation ✅

**Done**

- `docker-compose.prod.yml` (Caddy with automatic TLS, gunicorn, worker, beat,
  nightly backup service, optional Matomo profile), `Caddyfile`,
  `scripts/{backup,restore,deploy,ci_backup_restore}.sh`.
- `docs/`: `DEPLOYMENT.md`, `BACKUP_RESTORE.md`, `INTEGRATIONS.md`,
  `ADMIN_GUIDE_uz.md`, `EDITOR_GUIDE_en.md`, `EDITOR_GUIDE_uz.md`,
  `screenshots/README.md`.
- Manuscript, title-page, LaTeX and cover-letter templates in
  `static/templates/`.
- `README.md` with the demo accounts; `HANDOFF.md` in Uzbek.

---

## Post-handover — the `design/` refresh ✅ (16 September 2026)

**Done**

- The client supplied a Stitch export of three pages (home, About, issue table
  of contents). It is committed as `design/` and is now the visual reference
  (CLAUDE.md §3; decision D39): Merriweather titles, archival navy + burnished
  gold on alabaster, 4 px controls / 8 px cards, feather card shadows, a dark
  utility bar above the header, underline tabs, a dark four-column footer.
- Rebuilt: `static/src/css/input.css` tokens and components,
  `includes/header.html` (utility bar, tabs with `active_nav`, `/` search
  shortcut), `includes/footer.html`, `includes/wordmark.html` (square mark),
  `includes/icon.html` (inline SVG icons — no icon font), `journal/home.html`
  (hero with fact strip, discovery console, lead article, Online First / EiC /
  For-researchers / announcements / most-read rail, standards pillars, indexing
  tiles), `journal/partials/article_card.html` (lead / compact variants with
  abstract box and JEL chips), `journal/issue_detail.html` (issue hero with grid
  cover, sidebar with volume list, metrics and call for papers),
  `journal/archive.html`, `core/_page_shell.html` (title band, side navigation
  card, submission kit) and `core/about.html` (profile, what we publish, how we
  work, editorial leadership, indexing, contact band).
- Nothing invented: the mock-up's CiteScore, Crossref member number and
  "official publication" line render only from `SiteSettings` /
  `EditorialKPI` / `IndexingService` data or are omitted.
- `SiteSettings.frequency_short`, `Article.affiliations_display()`,
  `active_nav` context value; `get_site_settings()` now carries the
  Editor-in-Chief relation; the home page fetches issue and Online First papers
  in one query so the 15-query budget still holds.
- 89 new UI strings translated in all four languages
  (`scripts/i18n_catalogue_7.py`).

**Verified** — lint clean; 411 tests; every catalogue 100 %; no horizontal
scroll at 320 px in any language; axe-core: zero serious/critical violations on
the seven audited pages; screenshots regenerated in `docs/screenshots/`.

---

## Delivery pipeline audit — Local → CI → CD → Monitoring ✅ (17 September 2026)

**Found and fixed**

- `STORAGE_BACKEND=s3` crashed start-up: `django-storages` was never a dependency (D43).
- The production image carried every dev tool (1.15 GB → 724 MB, D44).
- First end-to-end tracing run produced only orphan spans: instrumentation ran
  after the WSGI handler was built (fixed and regression-tested, D48).

**Added**

- CI: `manifests` (kustomize + kubeconform), `sonarqube` (Quality Gate),
  `image` (GHCR push, immutable tags), `gitops` (overlay bump, `[skip ci]`).
- CD: `k8s/` — Kustomize base/overlays, in-cluster data component with nightly
  `pg_dump`, migrate hook Job, HPA/PDB/NetworkPolicy, Argo CD app-of-apps.
- Monitoring: OpenTelemetry tracing → Collector → Jaeger; JSON logs → Fluent Bit →
  Elasticsearch/Kibana; audit stream `arer.audit` + kube-apiserver audit policy;
  index retention CronJob.
- Local: `make build`, `make k8s-validate`, `make verify`, `make release`;
  `pre-push` hook runs the tests. `/livez/` liveness endpoint.
- Guide: `docs/PIPELINE_uz.md`; rules: CLAUDE.md §9.

**Verified** — ruff/djlint clean; migrations and translations complete; full
pytest suite green; prod image builds and boots with S3 settings; 70/70
manifests valid (kubeconform, incl. Argo CD CRDs); Fluent Bit `--dry-run` and
OTel Collector `validate` pass; actionlint clean; prod image + Jaeger end to end:
`GET /oai/` → one trace with 1 HTTP, 8 SQL and 15 Redis spans; JSON log lines
carry service, environment and version.

**Needs real credentials / a cluster** — SonarQube token, registry push on the
first `main` run, Argo CD sync on the Uzbek VPS (steps in `docs/PIPELINE_uz.md`).

---

## Test suite

360 tests at handover (see the pipeline audit above for the current count), all passing:

| Module | Covers |
|---|---|
| `test_translit.py` | 51 transliteration cases, both directions |
| `test_core.py` | settings singleton, Markdown sanitisation, machine endpoints, contact form, auto-transliteration |
| `test_journal_models.py` | model properties, URLs, querysets |
| `test_public_views.py` | every public page, Highwire tags, JSON-LD, counters, feeds, search |
| `test_i18n.py` | 22 mandatory pages × 4 languages |
| `test_workflow.py` | the finite-state machine, permissions, deadlines, audit |
| `test_non_leakage.py` | double-blind guarantees |
| `test_citations.py` | six styles, four export formats |
| `test_crossref.py` | deposit XML against the real XSD |
| `test_oai.py` | all six verbs, errors, resumption tokens |
| `test_api.py` | read-only API and DOAJ export |
| `test_production.py` | DOI, completeness, stamping, publication |
| `test_metrics.py` | bot filtering, aggregation, KPIs |
| `test_security.py` | 2FA, permissions, uploads, headers, PDF scrubbing |
| `test_performance.py` | query counts and bundle sizes |
| `test_e2e_flow.py` | the complete editorial flow end to end |
| `test_observability.py` | JSON log format, trace ids, tracing switches, audit stream, `/livez/` |
| `test_k8s_manifests.py` | pod hardening, probes, migrate hook, single beat, audit routing, Argo CD paths, no secrets |

---

## Journal PDF and author offprints ✅ (2026-09-17)

**Done**

- Issue builder: tick articles to add to / remove from an issue; running order.
- `apps/production/print_layout.py` (reportlab + pypdf): brand cover (or the
  uploaded issue cover), editorial board and imprint, optional information page
  (`SiteSettings.print_info_page`), multilingual contents with section bands,
  article galley pages trimmed and fitted into the journal frame with a running
  head and a page-number tab, back cover. Noto Sans (subset, OFL) is vendored in
  `apps/production/fonts/` for Uzbek ʻ ʼ and ғ қ ҳ.
- `apps/production/issue_print.py`: two-pass pagination (contents length →
  article page numbers), writes `pages_start`/`pages_end` back (re-deposits
  Crossref for already public articles), stores `Issue.full_issue_pdf` and one
  `Article.offprint_pdf` per article; Celery task `build_issue_print` with
  `Issue.print_status` polled over HTMX; e-mail to corresponding authors with
  the PDF attached (linked above `OFFPRINT_ATTACH_MAX_BYTES`); authors download
  it from their submission page.
- Security fix: every production function view now requires the production
  role (`production_required`); before, any signed-in account could reach them.

**Verified** — `tests/test_issue_print.py` (12 tests: page counts, pagination,
first-page offset, offprint content, failure states, e-mail attachment,
permissions); full suite 459 passed; a 4-article demo issue built in 1.7 s
(32 pages) — `docs/screenshots/journal-pdf-pages.png`,
`docs/screenshots/journal-pdf-issue-builder.png`.

---

## Editorial console re-skin ✅ (2026-09-19)

**Done** — the dashboard now follows
`design/stitch_modern_economic_journal_dashboard/` (Academic Royal Prestige,
White Ink Edition) instead of the public site's Mint Glass.

- `static/src/css/console.css` (imported by `input.css`): the design's tokens —
  `#2A164D` primary, `#6C28D6` secondary, `#FAF9FD` paper, `#E7E0F2` hairlines,
  2–8 px radii, Merriweather headlines over Inter interface text — scoped to
  `body.console`, where they also re-point the shared Mint Glass tokens so every
  existing component class (`.card`, `.btn`, `.table`, `.chip`, `.progress`…)
  follows without template edits. The public site is untouched.
- `templates/dashboard/_base.html` rebuilt as a standalone console shell: white
  masthead (brand, journal search, language switcher, submit, user menu),
  role-aware section tabs, sticky navigation rail with icons and active states,
  ink footer carrying e-ISSN and DOI prefix. `noindex`.
- All fifteen console pages converted to the design's panel / stat-tile /
  hairline-table idiom: overview, queue, manuscript record (tabs), decision,
  reviewer finder, reports, profile, two-factor, reviewer dashboard, assignment,
  review form, production queue, production submission, article record, issue
  builder — plus the queue, reviewer and submission-card partials.
- `templates/includes/icon.html` gained the console icons (grid, inbox, layers,
  chart, settings, key, logout, plus, alert, users, edit).
- Below `lg` the rail collapses behind a toggle; `[x-cloak]` now has a rule, so
  the user menu and the mobile nav no longer flash open before Alpine boots.

**Verified** — `djlint templates apps --check` and `--lint` clean (the one
remaining lint error, `H005` in `templates/emails/base_email.html`, predates
this work and is not in `make lint`'s `--check` run); `manage.py check` clean;
all twenty console templates compile and render; every `{% url %}` name in them
resolves; screenshots at 1440 px and 390 px in `docs/screenshots/console-*.png`.

**Not verified here** — `pytest` did not run: Docker Desktop is down on this
machine and Postgres is unreachable on `localhost:5452`, so the suite cannot
start. Run `make test` once the stack is up. No Python was changed, only
templates, CSS and the compiled `static/css/output.css`.

---

## Site-wide Academic Royal Prestige skin ✅ (2026-09-19)

**Done** — the reading site joins the console on the design system of
`design/stitch_modern_economic_journal_dashboard/`. Mint Glass is retired.

- `input.css` `@theme`: the royal-ink palette under the existing token names
  (`surface` `#FAF9FD`, `paper` `#FFFFFF`, `ink` `#1F1435`, `line` `#E7E0F2`,
  `accent` `#2A164D`, `accent-2` `#6C28D6`), Merriweather / Inter / JetBrains
  Mono, radii 2-8px, the design's three shadows, 1360px container. Because the
  names did not change, all 80+ public templates picked the new look up with no
  markup edits.
- Base layer: the night palette is gone (`color-scheme: light`), the page is
  flat paper instead of a mint-lit gradient, headlines are the editorial serif.
- Chrome rewritten: white sticky masthead with a hairline rule and uppercase
  tabs underlined in violet, lavender utility strip, royal-ink wordmark stamp,
  white mobile sheet, ink footer.
- Components squared up: buttons and cards at 4px with 1px hairlines instead of
  pills and frosted glass, chips as 2px archival stamps, amber citation stamps,
  open-access green.
- Contrast fixes the swap exposed: the eyebrow on the ink panel, the Online
  First badge, the mini issue spine.
- `console.css` keeps only the console's own furniture; its token block is gone
  now that the palette is site-wide. The dashboard root class became
  `editorial-console` because `.console` already belonged to the home page
  search panel — that collision had been drawing a frame around the dashboard.
- `docs/DESIGN-SYSTEM.md` rewritten for the new system.

**Verified** — `djlint templates apps --check` clean; `manage.py check` clean;
screenshots at 1440px and 390px in `docs/screenshots/site-*.png` (home, about,
for-authors, search, sign-in) and `console-*.png`. The public pages were
previewed by taking the live Railway HTML and re-pointing it at the new
stylesheet, so the content in the shots is the real site.

**Not verified here** — `pytest` still cannot run: Docker is down on this
machine and Postgres is unreachable. No Python changed; CI runs the suite.

---

## Deferred (Phase 2 of the project — see HANDOFF.md)

- DOCX → JATS/HTML full-text conversion.
- Live iThenticate calls (the client structure is in place; credentials needed).
- ORCID Member API push of published works.
- Crossmark and Similarity Check registration.
- Elasticsearch — Postgres full-text search is used instead, by design (D1).

## Notes for the next engineer

- The build machine's `C:` drive filled up during Phase 7, which repeatedly
  crashed Docker Desktop. Nothing in the project caused it and nothing depends
  on it; if Docker misbehaves, check free disk space first.
- `.mo` files are **not** committed. `compilemessages` runs in the Dockerfile,
  in `scripts/entrypoint.sh` and in `scripts/deploy.sh`; on a bare-metal
  checkout run `make compile` or the `/uz-cyrl/` pages fall back to English.
- `static/css/output.css` **is** committed so the site renders on a machine that
  cannot download the Tailwind binary; `make tailwind` regenerates it.
