# CLAUDE.md — Operating rules for building ALGORITHM: Review of Economic Research

You are the sole engineer building a production-grade, open-access scholarly journal
platform for **"ALGORITHM: Review of Economic Research"** (short code: **ARER**).
The full requirements are in `SPEC.md`. The visual brief is in `DESIGN_BRIEF.md`.
The client-facing formal terms of reference (Uzbek) are in `TEXNIK_TOPSHIRIQ.md` —
`SPEC.md` is the engineering source of truth; if the two ever disagree, follow `SPEC.md`.

The client will NOT be available while you work. Read this file completely before touching code.

---

## 0. Prime directive: work unattended, never block

1. **Never ask the user a question.** Every decision you might want to ask about has a
   default in `SPEC.md §2 "Decision register"`. If something is genuinely undefined, choose the
   option that (a) is most standard for scholarly publishing, (b) is simplest, (c) is reversible —
   then record it in `DECISIONS.md` (append-only, one line per decision, with date and reason).
2. **Never stop early.** Work phase by phase (`SPEC.md §14`) until every acceptance check in
   `SPEC.md §15` passes. If a phase is blocked by an external secret you don't have
   (Crossref credentials, ORCID keys, SMTP keys), implement the feature against the sandbox/test
   mode, make it fully configurable via environment variables, write a mocked test, and move on.
3. **Never wait for approval** of design, naming, or scope. Do the work, commit, continue.
4. If a tool, package, or network call fails, try an alternative once, then fall back to the
   simplest working solution and log it in `DECISIONS.md`. Do not loop on the same failure.
5. Keep `PROGRESS.md` updated at the end of every phase: what is done, what is verified, what is
   deferred (with reason). The client will read this first when they return.
6. When completely finished, write `HANDOFF.md` (see §7 below).

## 1. Non-negotiable technical choices (do not re-litigate)

| Area | Choice |
|---|---|
| Language / framework | Python 3.12, Django 5.2 LTS |
| Database | PostgreSQL 16 (never SQLite, even for dev — use Docker) |
| Async / scheduled jobs | Celery 5 + Redis 7 (beat for schedules) |
| Frontend | Server-rendered Django templates + **HTMX** + **Alpine.js** + **Tailwind CSS v4** via `django-tailwind-cli` (standalone binary, no Node required). No React/Vue/SPA anywhere. |
| Multilingual content | `django-modeltranslation` for model fields (language codes hyphenated exactly as in `LANGUAGES`, incl. `uz-cyrl`); Django i18n (`gettext`) for UI strings; `i18n_patterns` URLs; `compilemessages` runs in Dockerfile and `make dev` |
| Languages | `en` (default), `uz` (Uzbek Latin), `uz-cyrl` (Uzbek Cyrillic), `ru` |
| Auth | `django-allauth` (email + password, mandatory email verification) + ORCID OAuth (Public API, sandbox in dev); `django-otp` TOTP 2FA required for editor/admin roles |
| Files | Local filesystem under `MEDIA_ROOT` in dev; `django-storages` S3-compatible backend switchable via env for production |
| Search | PostgreSQL full-text search (`django.contrib.postgres`), trigram for author names. No Elasticsearch. |
| Email | `django-anymail` (Resend backend by default, SMTP fallback); Mailpit container in dev |
| Citations | `citeproc-py` + `citeproc-py-styles` with CSL styles (APA 7, MLA 9, Chicago author-date, Vancouver, Harvard, GOST R 7.0.5-2008); if a style fails in citeproc-py, render it from a hand-written template with the same interface and log in `DECISIONS.md`. BibTeX/RIS/EndNote generated from templates |
| Crossref | Own XML generator (schema 5.4.0, validated against XSD) + HTTPS POST deposit; sandbox `test.crossref.org` by default |
| OAI-PMH | Own implementation in app `oai` (oai_dc + jats formats) — small, spec-exact, fully tested |
| Analytics | Matomo (self-hosted container, optional via env) — never Google Analytics |
| Containerisation | Docker Compose for dev (`docker-compose.yml`) and prod (`docker-compose.prod.yml` with Caddy for automatic HTTPS) |
| Tests | `pytest` + `pytest-django` + `factory_boy`; Playwright (Python) smoke test for the end-to-end submission→publication flow |
| Lint / format | `ruff` (lint + format), `djlint` for templates, `mypy` (lenient), `pre-commit` config |
| Package manager | `uv` (with `pyproject.toml` + `uv.lock`) |

## 2. Repository & git

- Remote: `https://github.com/diyorbek20037773/algorithm_journal` (branch `main`).
- If the current directory is not a git repo: `git init`, add the remote, create `main`.
- If the remote already has commits, `git pull --rebase` first and build on top; never force-push.
- Commit after every meaningful step, at minimum once per phase, using Conventional Commits
  (`feat(submissions): reviewer assignment flow`, `chore: docker compose for dev`, …).
- Push after every phase: `git push -u origin main`. If push fails because of missing
  credentials, **do not stop** — keep committing locally, retry the push at the end of each later
  phase, and describe in `HANDOFF.md` exactly what the client must run to push (`gh auth login` then
  `git push -u origin main`).
- Never commit secrets. `.env` is git-ignored; `.env.example` documents every variable with a safe
  default.
- Add a GitHub Actions workflow `.github/workflows/ci.yml`: ruff, djlint, `manage.py check`,
  `makemigrations --check`, pytest with a Postgres service. It must be green on the final push.

## 3. Project layout (create exactly this)

```
algorithm_journal/
├── CLAUDE.md  SPEC.md  DESIGN_BRIEF.md  TEXNIK_TOPSHIRIQ.md   (given)
├── README.md  PROGRESS.md  DECISIONS.md  HANDOFF.md            (you write)
├── pyproject.toml  uv.lock  .env.example  .gitignore  .pre-commit-config.yaml
├── Makefile                      # make dev / test / lint / seed / tailwind / backup
├── docker-compose.yml  docker-compose.prod.yml  Dockerfile  Caddyfile
├── config/                       # Django project: settings/{base,dev,prod,test}.py, urls.py, celery.py, asgi/wsgi
├── apps/
│   ├── core/          # SiteSettings singleton, Page (CMS), Menu, Announcement, ContactMessage, utilities, context processors, sitemaps, robots
│   ├── accounts/      # User (custom, email login), Profile (ORCID, affiliation, country, bio), roles, 2FA hooks, allauth adapters
│   ├── journal/       # Section, Volume, Issue, Article, Author(ship), Keyword, JELCode, Reference, Galley(file), License, EditorialBoardMember, Statistics
│   ├── submissions/   # Submission, SubmissionFile, Round, ReviewAssignment, Review, Decision, RevisionRequest, EditorNote, Discussion messages, workflow FSM
│   ├── review/        # reviewer-facing views/forms (may be merged into submissions if simpler — decide and record)
│   ├── production/    # copyediting/typesetting stage, issue scheduling, DOI assignment, publish action
│   ├── crossref/      # XML generation, XSD validation, deposit client, DepositLog, Celery tasks, management commands
│   ├── orcid/         # allauth provider glue, ORCID verification badge
│   ├── oai/           # OAI-PMH 2.0 endpoint
│   ├── citations/     # CSL rendering, BibTeX/RIS/EndNote export, "cite this" widget
│   ├── metrics/       # view/download events, bot filtering, daily aggregation, editor KPI reports
│   ├── plagiarism/    # PlagiarismProvider interface, ManualProvider (default), IThenticateProvider (stub, config-gated)
│   ├── preservation/  # LOCKSS manifest pages, per-issue export bundle (ZIP: PDF+JATS+Crossref XML), archive policy hooks
│   ├── search/        # search views, indexing signals, filters
│   ├── dashboard/     # role-based editorial dashboard (author/reviewer/editor/EIC/production/admin)
│   └── api/           # small read-only JSON API (DRF) for articles/issues (used by widgets and future needs)
├── templates/         # base.html, includes/, per-app templates; all text via {% trans %}
├── static/            # src/css/input.css (Tailwind), js/ (htmx.min.js, alpine.min.js vendored), img/
├── locale/            # en, uz, uz_Cyrl, ru .po/.mo — 100% translated (no fuzzy/untranslated strings at the end)
├── fixtures/ or seed/ # seed data & demo content used by `manage.py seed_demo`
├── scripts/           # backup.sh, restore.sh, deploy.sh
├── tests/             # pytest suites mirrored per app + e2e/
└── docs/              # ADMIN_GUIDE_uz.md, EDITOR_GUIDE_en.md, EDITOR_GUIDE_uz.md, DEPLOYMENT.md, BACKUP_RESTORE.md, INTEGRATIONS.md
```

If the `design/` folder exists (output of Claude Design), its HTML/Tailwind pages are the visual
reference: convert them faithfully into Django templates. If it does not exist, implement the
design system and page layouts exactly as described in `DESIGN_BRIEF.md` — it is written to be
sufficient on its own. Either way the result must look finished, not like a wireframe.

## 4. Coding standards

- Type hints everywhere in Python; docstrings on every model, service and task.
- Business logic lives in `services.py` / `workflow.py` modules, not in views or templates.
- Every model that is public-facing has: `__str__`, `get_absolute_url`, sensible `Meta.ordering`,
  indexes on filter/sort fields, `created_at`/`updated_at`.
- All user-visible strings wrapped in `gettext`/`{% trans %}` / `{% blocktrans %}`. Run
  `makemessages` for all 4 languages and fill translations (you write them; Uzbek Cyrillic is a
  transliteration of Uzbek Latin — implement `apps/core/translit.py` for automatic Latin→Cyrillic
  conversion of Uzbek text and use it to pre-fill `uz-cyrl` model fields when empty).
- Templates: one `base.html`, semantic HTML5, WCAG 2.1 AA (contrast ≥ 4.5:1, skip link, focus
  styles, alt text, keyboard-operable menus), `lang` attribute per page, `hreflang` alternates,
  canonical link, Open Graph + Twitter cards, Highwire Press `citation_*` meta tags and JSON-LD
  `ScholarlyArticle` on article pages.
- Never expose stack traces; custom 400/403/404/500 pages in all languages.
- Security: `SECURE_*` settings in prod, CSRF everywhere, rate limiting on auth and submission
  endpoints (`django-ratelimit`), file upload validation (extension + MIME via `python-magic`,
  max sizes), `django-axes` for login lockout, audit log (`apps/core/audit.py` or `django-auditlog`)
  for admin/editor actions, password policy ≥ 12 chars.
- Performance: `select_related`/`prefetch_related` on list views, DB query count assertions in
  tests for the home page, issue page and article page (≤ 15 queries each), per-view caching of
  public pages (Redis) with invalidation on publish, compressed static files (`whitenoise` in
  dev/simple prod, Caddy in prod), lazy-loaded images, no render-blocking JS.

## 5. Definition of done for every phase

A phase is done only when:
1. `make lint` passes (ruff, djlint) and `make test` passes.
2. `python manage.py makemigrations --check` reports no changes.
3. `python manage.py check --deploy` has no errors under prod settings (warnings allowed only if documented).
4. The feature is visible and usable in the browser with `make dev` running — verify with a
   Playwright screenshot saved to `docs/screenshots/<phase>-<page>.png` (keep these; the client will
   look at them).
5. `PROGRESS.md` is updated and a commit is pushed (or push attempt logged).

## 6. Local run (must work on a clean machine with only Docker installed)

```
cp .env.example .env
docker compose up --build        # web (Django + Tailwind watcher), db, redis, worker, beat, mailpit, matomo(optional profile)
# in another shell:
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_demo   # journal settings, sections, JEL, pages, board, Vol 1 / Issues 1–3 (12 articles) + 2 Online First, submissions in every state, demo users
```
→ http://localhost:8000 (site), http://localhost:8025 (Mailpit), http://localhost:8000/admin.
`make dev` must wrap the above (including `compilemessages` so the `uz-cyrl` locale is active).
Document demo accounts in `README.md` (admin, eic, editor, production, reviewer1, reviewer2,
reviewer3, author — password `Algorithm2026!`).

Also support a non-Docker path for Python-native dev: `uv sync && make dev-local`
(expects Postgres+Redis reachable via `.env`).

## 7. HANDOFF.md (write at the very end)

Must contain, in Uzbek (Latin script) with commands in code blocks:
1. Nima qilindi — phases, and the full list of acceptance checks from `SPEC.md §15` with ✅/⚠️.
2. Qanday ishga tushirish — local (Docker) va prod (VPS) qadamlari.
3. Sozlash kerak bo'lgan sirlar — every env var that needs a real value (Crossref, ORCID, Resend,
   S3, domain), where to get it, and what happens until it's set.
4. Tahririyat kiritishi kerak bo'lgan ma'lumotlar — editorial board (replace demo entries), ISSN,
   registration certificate, DOI prefix, contact details, logo file location.
5. Ma'lum cheklovlar / Phase-2 ro'yxati.
6. GitHub push holati.

## 8. Things that are forbidden

- Asking questions, pausing for confirmation, or leaving TODOs in place of working code.
- SPA frameworks, Node build pipelines, Bootstrap, jQuery.
- Fake metrics badges ("Impact Factor", "SJIF", "Global Impact Factor"), visitor counters, flag
  counters, state emblems, photos of officials, marquee/sliders/auto-playing carousels.
- Query-string language switching (`?lang=`); languages are URL prefixes only.
- Storing files with user-supplied names; always rename to UUID-based paths.
- Hard-coding the domain, ISSN, DOI prefix or journal name in templates — all come from
  `SiteSettings` / env.
- Lorem ipsum in the final seed. Demo articles must read like plausible economics papers
  (invented but sensible titles, abstracts, keywords, JEL codes, references with real DOI formats
  marked as examples). Editorial board demo entries must be clearly labelled "DEMO — replace".
