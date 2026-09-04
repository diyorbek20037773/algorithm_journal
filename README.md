# ALGORITHM: Review of Economic Research (ARER)

Open-access, peer-reviewed, monthly economics journal platform — public website
plus the complete electronic editorial system (submission, double-blind review,
production, DOI registration, indexing endpoints).

* Python 3.12 · Django 5.2 LTS · PostgreSQL 16 · Redis 7 · Celery 5
* Server-rendered templates + HTMX + Alpine.js + Tailwind CSS v4 (no Node build)
* Four languages: English, Oʻzbekcha (Latin), Ўзбекча (Cyrillic), Русский
* Diamond open access — no article processing charges, CC BY 4.0

Engineering specification: [`SPEC.md`](SPEC.md) · visual system:
[`DESIGN_BRIEF.md`](DESIGN_BRIEF.md) · working rules: [`CLAUDE.md`](CLAUDE.md) ·
client terms of reference (Uzbek): [`TEXNIK_TOPSHIRIQ.md`](TEXNIK_TOPSHIRIQ.md).

---

## Quick start (Docker only)

```bash
cp .env.example .env
docker compose up --build
```

Then, in a second terminal:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_demo
```

| Service | URL |
|---|---|
| Website | <http://localhost:8000> |
| Django admin | <http://localhost:8000/admin/> |
| Mailpit (all outgoing e-mail) | <http://localhost:8025> |
| OAI-PMH | <http://localhost:8000/oai/?verb=Identify> |
| JSON API | <http://localhost:8000/api/v1/> |
| Health check | <http://localhost:8000/healthz/> |

Optional self-hosted analytics:

```bash
docker compose --profile analytics up -d matomo matomo-db   # http://localhost:8080
```

`make dev` wraps the whole sequence (build, `compilemessages`, `migrate`,
`seed_demo`, `up`).

If your machine already listens on one of those ports, move the published side
in `.env` — `WEB_PORT`, `POSTGRES_HOST_PORT`, `REDIS_HOST_PORT`,
`MAILPIT_UI_PORT`, `MAILPIT_SMTP_PORT`, `MATOMO_PORT`. Nothing inside the
network changes; the containers always talk to `db:5432`, `redis:6379` and
`mailpit:1025`.

## Demo accounts

Created by `manage.py seed_demo`. **Password for every account:
`Algorithm2026!`**

| E-mail | Role | What it demonstrates |
|---|---|---|
| `admin@algorithm-journal.uz` | Superuser / technical administrator | Django admin, site settings, integrations |
| `eic@algorithm-journal.uz` | Editor-in-Chief | Every queue, final decisions, issue publication |
| `editor@algorithm-journal.uz` | Section editor (sections 2 and 3) | Screening, reviewer invitations, recommendations |
| `production@algorithm-journal.uz` | Production editor | Copyediting, galleys, DOI, issue builder |
| `reviewer1@algorithm-journal.uz` | Reviewer | Invitation, review form, certificate |
| `reviewer2@algorithm-journal.uz` | Reviewer | Accepted and completed review |
| `reviewer3@algorithm-journal.uz` | Reviewer | Overdue review, reminders |
| `author@algorithm-journal.uz` | Author | Submissions in every workflow state |

Editorial accounts (`eic`, `editor`, `production`, `admin`) must enrol a TOTP
authenticator on first sign-in — that is the mandatory two-factor policy, not a
bug. Use any authenticator app; the QR code is on the enrolment page.

## Non-Docker development

Requires a reachable PostgreSQL 16 and Redis 7 (adjust `.env`).

```bash
uv sync --extra dev          # or: uv pip install -r pyproject.toml --extra dev
make dev-local               # compilemessages + migrate + runserver
make seed-demo
```

## Everyday commands

```bash
make help                # list every target
make lint                # ruff + ruff format --check + djlint + manage.py check
make test                # pytest
make ci-check            # lint + migration check + tests (what CI runs)
make messages            # extract translatable strings for en, uz, uz_Cyrl, ru
make check-translations  # fail on any untranslated or fuzzy catalogue entry
make tailwind            # rebuild static/css/output.css
make screenshots         # Playwright screenshots into docs/screenshots/
make backup              # pg_dump + media archive into ./backups
```

## Layout

```
config/      Django project: split settings, URLs, Celery, locale formats
apps/
  core/         SiteSettings, CMS pages, announcements, contact, audit, sitemaps
  accounts/     custom user, profiles, roles, 2FA, allauth adapters
  journal/      sections, volumes, issues, articles, authors, galleys, board
  submissions/  submission wizard models, workflow FSM, reviews, decisions
  review/       reviewer-facing views and forms (anonymised)
  production/   production stages, PDF stamping, DOI, issue builder
  crossref/     deposit XML (schema 5.4.0), validation, client, tasks
  orcid/        ORCID identifiers and OAuth glue
  oai/          OAI-PMH 2.0 endpoint
  citations/    CSL rendering and bibliographic exports
  metrics/      access events, aggregation, editorial KPIs
  plagiarism/   pluggable similarity-check providers
  preservation/ LOCKSS manifests and issue export bundles
  search/       PostgreSQL full-text search
  dashboard/    role-based editorial dashboards
  api/          read-only JSON API
templates/   base layout, includes, per-app templates (all strings translated)
static/      Tailwind source, vendored htmx and Alpine, images
locale/      en, uz, uz_Cyrl, ru gettext catalogues
seed/        JEL classification and seed content
scripts/     backup, restore, deploy, screenshots, translation check
docs/        deployment, backup, integrations, admin and editor guides
tests/       pytest suites mirrored per app plus end-to-end
```

## Documentation

| Document | Contents |
|---|---|
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | VPS setup, DNS, TLS, production compose, updates, rollback |
| [`docs/BACKUP_RESTORE.md`](docs/BACKUP_RESTORE.md) | Backup schedule, off-site copies, verified restore procedure |
| [`docs/INTEGRATIONS.md`](docs/INTEGRATIONS.md) | Crossref, ORCID, Resend, CLOCKSS, DOAJ and Scopus checklists |
| [`docs/ADMIN_GUIDE_uz.md`](docs/ADMIN_GUIDE_uz.md) | Administrator guide (Uzbek) |
| [`docs/EDITOR_GUIDE_en.md`](docs/EDITOR_GUIDE_en.md) | Editorial workflow guide (English) |
| [`docs/EDITOR_GUIDE_uz.md`](docs/EDITOR_GUIDE_uz.md) | Editorial workflow guide (Uzbek) |
| [`docs/PERFORMANCE.md`](docs/PERFORMANCE.md) | Measured query counts, bundle sizes and axe-core results |
| [`HANDOFF.md`](HANDOFF.md) | Hand-over notes in Uzbek: what is done, what needs real credentials |

## Before going live

The platform runs with placeholders. Replace them in **Admin → Site settings**
and `.env`:

* e-ISSN and the registration certificate number and date
* founder / publisher name and postal address
* the real editorial board (the seeded members are marked "DEMO — replace")
* `DOI_PREFIX`, `CROSSREF_USER`, `CROSSREF_PASSWORD`, `CROSSREF_TEST=false`
* `ORCID_CLIENT_ID` / `ORCID_CLIENT_SECRET` and `ORCID_BASE=production`
* `RESEND_API_KEY` (or SMTP credentials) with SPF and DKIM on the domain
* `SITE_DOMAIN`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_SECRET_KEY`

`docs/INTEGRATIONS.md` explains where each value comes from and what happens
until it is set.

## Licence

Platform code: MIT. Published articles: CC BY 4.0, copyright retained by the
authors.
