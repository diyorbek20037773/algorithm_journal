# PROGRESS.md

Status log for **ALGORITHM: Review of Economic Research (ARER)**.
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

## Test suite

359 tests, all passing:

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
