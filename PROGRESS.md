# PROGRESS.md

Status log for **ALGORITHM: Review of Economic Research (ARER)**.
Updated at the end of every delivery phase (SPEC §14).

---

## Phase 0 — Repository bootstrap ✅

**Done**

- `uv` project (`pyproject.toml`) pinned to Python 3.12 / Django 5.2 LTS, with a
  `dev` extra covering pytest, Playwright, ruff, djlint and mypy.
- Settings split into `config/settings/{base,dev,prod,test}.py`, everything
  environment-driven through `django-environ`; `.env.example` documents every
  variable with a safe default.
- Custom `uz-cyrl` locale registered in `config/locale_info.py`; date and number
  formats for `en`, `uz`, `uz_Cyrl`, `ru` in `config/formats/`.
- Docker Compose development stack: `db` (Postgres 16), `redis`, `web`,
  `tailwind`, `worker`, `beat`, `mailpit`, plus an optional `analytics` profile
  with Matomo.
- `Dockerfile` (multi-stage, `uv`-built virtualenv, `compilemessages` at build
  time) and `scripts/entrypoint.sh` with a Postgres readiness wait.
- `Makefile` with `dev`, `dev-local`, `lint`, `test`, `seed`, `messages`,
  `screenshots`, `backup`, `restore`.
- `.pre-commit-config.yaml` (ruff, djlint, `manage.py check`, missing-migration
  guard) and `.github/workflows/ci.yml` (lint, translations, migrations,
  deployment check, pytest with a Postgres service, backup/restore drill,
  Playwright job).
- `PROGRESS.md`, `DECISIONS.md`, `README.md`.

**Verified** — `manage.py check` clean; `makemigrations --check` clean.

---

## Phase 1 — Accounts, i18n and the design system ✅

**Done**

- Custom `accounts.User` (e-mail login, Argon2), `Profile` with ORCID,
  affiliation, expertise and reviewer statistics; role groups per SPEC §3 with
  permission mixins in `apps/accounts/permissions.py`.
- django-allauth with mandatory e-mail verification and the ORCID provider
  (sandbox by default); `AccountAdapter` / `SocialAccountAdapter` store the
  authenticated ORCID iD on the profile.
- `StaffTwoFactorMiddleware` forces TOTP enrolment for editorial roles;
  enrolment page with QR code and ten single-use recovery codes.
- `apps/core/translit.py`: deterministic Uzbek Latin ↔ Cyrillic transliterator
  (digraphs, apostrophe variants, word-initial `e`/`ye`, capitalisation,
  exception dictionary) plus a `pre_save` hook that fills empty `*_uz_cyrl`
  fields and records what it generated in `auto_translit`.
- Design system from `DESIGN_BRIEF.md` implemented as Tailwind v4 `@theme`
  tokens and component classes in `static/src/css/input.css`; `base.html` with
  sticky header, four-language switcher, footer, skip link, `hreflang`
  alternates, Open Graph and RSS/Atom discovery.
- Error pages 400/403/404/500 and the django-axes lockout page.

---

## Phase 2 — Journal content and the public site — in progress

Models, admin, public views, templates and the JEL seed are written; the seed
command, tests and screenshots are still outstanding.

---

## Phases 3–8 — not started

Their deliverables are listed in `SPEC.md §14`; this file is updated at the end
of each phase with what is done, what is verified and what is deferred.
