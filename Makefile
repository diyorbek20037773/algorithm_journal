# =============================================================================
# ALGORITHM: Review of Economic Research — developer commands
# `make help` lists everything.
# =============================================================================

COMPOSE ?= docker compose
PY      ?= python
MANAGE  ?= $(PY) manage.py
DC_EXEC ?= $(COMPOSE) exec -T web

.DEFAULT_GOAL := help
.PHONY: help init dev dev-local up down logs shell dbshell migrate migrations \
        seed seed-demo superuser lint lint-fix fmt test test-fast cov messages \
        translations check-translations compile tailwind static screenshots \
        e2e backup restore secret clean ci-check docker-test

help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# --- environment -------------------------------------------------------------
init: ## Create .env from the template with a fresh SECRET_KEY
	@test -f .env || cp .env.example .env
	@$(PY) -c "import secrets,pathlib,re; p=pathlib.Path('.env'); t=p.read_text(encoding='utf-8'); t=re.sub(r'DJANGO_SECRET_KEY=.*', 'DJANGO_SECRET_KEY='+secrets.token_urlsafe(64), t, count=1); p.write_text(t, encoding='utf-8')"
	@echo ".env ready"

secret: ## Print a new Django SECRET_KEY
	@$(PY) -c "import secrets; print(secrets.token_urlsafe(64))"

# --- docker development ------------------------------------------------------
dev: ## Full dockerised dev stack (build, migrate, compilemessages, seed, up)
	$(COMPOSE) up -d --build db redis mailpit
	$(COMPOSE) run --rm web python manage.py compilemessages --ignore=.venv || true
	$(COMPOSE) run --rm web python manage.py migrate --noinput
	$(COMPOSE) run --rm web python manage.py seed_demo
	$(COMPOSE) up

up: ## Start the dev stack in the background
	$(COMPOSE) up -d --build

down: ## Stop the dev stack
	$(COMPOSE) down

logs: ## Follow web logs
	$(COMPOSE) logs -f web

shell: ## Django shell inside the web container
	$(COMPOSE) exec web python manage.py shell

dbshell: ## psql inside the db container
	$(COMPOSE) exec db psql -U $${POSTGRES_USER:-arer} -d $${POSTGRES_DB:-arer}

# --- native development ------------------------------------------------------
dev-local: ## Run the dev server natively (needs Postgres+Redis from .env)
	$(MANAGE) compilemessages --ignore=.venv || true
	$(MANAGE) migrate --noinput
	$(MANAGE) runserver 0.0.0.0:8000

migrate: ## Apply migrations
	$(MANAGE) migrate --noinput

migrations: ## Create migrations
	$(MANAGE) makemigrations

check-migrations: ## Fail if models drifted from migrations
	$(MANAGE) makemigrations --check --dry-run

seed: seed-demo ## Alias for seed-demo

seed-demo: ## Load the full demo journal (idempotent)
	$(MANAGE) seed_demo

superuser: ## Create a Django superuser
	$(MANAGE) createsuperuser

# --- quality -----------------------------------------------------------------
lint: ## ruff + djlint + django check
	ruff check .
	ruff format --check .
	djlint templates apps --check
	$(MANAGE) check

lint-fix: ## Auto-fix lint problems
	ruff check --fix .
	ruff format .
	djlint templates apps --reformat || true

fmt: lint-fix ## Alias for lint-fix

test: ## Run the test suite
	pytest -q

test-fast: ## Run tests excluding e2e/slow markers
	pytest -q -m "not e2e and not slow"

cov: ## Test suite with coverage report
	pytest --cov=apps --cov-report=term-missing --cov-report=html

ci-check: lint check-migrations test ## Everything CI runs

# --- i18n --------------------------------------------------------------------
messages: ## Extract translatable strings for all four languages
	$(MANAGE) makemessages -l en -l uz -l uz_Cyrl -l ru --ignore=.venv --ignore=node_modules --ignore=design --no-obsolete
	$(MANAGE) makemessages -d djangojs -l en -l uz -l uz_Cyrl -l ru --ignore=.venv --ignore=node_modules --ignore=design --no-obsolete || true

compile: ## Compile .po catalogues into .mo
	$(MANAGE) compilemessages --ignore=.venv

check-translations: ## Fail when any catalogue has untranslated or fuzzy entries
	$(PY) scripts/check_translations.py

translations: messages compile check-translations ## Full i18n cycle

# --- assets ------------------------------------------------------------------
tailwind: ## Build the Tailwind stylesheet once
	$(MANAGE) tailwind build

tailwind-watch: ## Watch and rebuild Tailwind
	$(MANAGE) tailwind watch

static: tailwind ## Collect static files
	$(MANAGE) collectstatic --noinput --ignore=src

# --- screenshots & e2e -------------------------------------------------------
screenshots: ## Capture Playwright screenshots into docs/screenshots/
	$(PY) scripts/screenshots.py

e2e: ## Run the Playwright end-to-end suite
	pytest -q -m e2e

# --- operations --------------------------------------------------------------
backup: ## Database + media backup into ./backups
	bash scripts/backup.sh

restore: ## Restore the newest backup (BACKUP=<file> to choose)
	bash scripts/restore.sh $${BACKUP:-}

export-issue: ## Export a preservation bundle (ISSUE=<id>)
	$(MANAGE) export_issue_bundle $${ISSUE}

clean: ## Remove build and cache artefacts
	@$(PY) -c "import shutil,pathlib;[shutil.rmtree(p,ignore_errors=True) for p in ['.pytest_cache','.ruff_cache','.mypy_cache','htmlcov','staticfiles']]"
	@echo "cleaned"
