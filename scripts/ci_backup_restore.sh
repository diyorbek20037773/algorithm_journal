#!/usr/bin/env bash
# =============================================================================
# CI drill for SPEC §15.14: take a backup, restore it into a fresh database and
# verify that the row counts match.
#
# Expects PostgreSQL to be reachable with the CI credentials, and Django to be
# importable (the CI job installs the project first).
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

export PGHOST="${PGHOST:-localhost}"
export PGPORT="${PGPORT:-5432}"
export PGUSER="${PGUSER:-arer}"
export PGPASSWORD="${PGPASSWORD:-arer}"
SOURCE_DB="${PGDATABASE:-arer_test}"
TARGET_DB="arer_restore_check"
BACKUP_DIR="${ROOT_DIR}/backups"

RUN="uv run"
command -v uv >/dev/null 2>&1 || RUN=""

echo "[drill] 1/6 preparing the source database"
export PGDATABASE="${SOURCE_DB}"
export DATABASE_URL="postgres://${PGUSER}:${PGPASSWORD}@${PGHOST}:${PGPORT}/${SOURCE_DB}"
export DJANGO_SETTINGS_MODULE="config.settings.dev"
export DJANGO_DEBUG="False"
export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"

${RUN} python manage.py migrate --noinput
${RUN} python manage.py seed_demo --minimal

BEFORE="$(psql -tAc 'SELECT count(*) FROM core_page')"
echo "[drill] source has ${BEFORE} CMS pages"
if [[ "${BEFORE}" -eq 0 ]]; then
  echo "[drill] the source database is empty; the drill would prove nothing." >&2
  exit 1
fi

echo "[drill] 2/6 taking a backup"
MEDIA_DIR="${ROOT_DIR}/media" BACKUP_DIR="${BACKUP_DIR}" bash scripts/backup.sh

DUMP="$(ls -1t "${BACKUP_DIR}"/arer-db-*.dump | head -n 1)"
echo "[drill] 3/6 backup file: ${DUMP}"

echo "[drill] 4/6 creating the empty target database ${TARGET_DB}"
psql -d postgres -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS ${TARGET_DB};"
psql -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE ${TARGET_DB} OWNER ${PGUSER};"

echo "[drill] 5/6 restoring into ${TARGET_DB}"
PGDATABASE="${TARGET_DB}" FORCE=1 bash scripts/restore.sh "${DUMP}"

echo "[drill] 6/6 verifying the row counts"
AFTER="$(PGDATABASE="${TARGET_DB}" psql -tAc 'SELECT count(*) FROM core_page')"
echo "[drill] restored database has ${AFTER} CMS pages"

psql -d postgres -c "DROP DATABASE IF EXISTS ${TARGET_DB};" >/dev/null

if [[ "${BEFORE}" != "${AFTER}" ]]; then
  echo "[drill] FAILED: ${BEFORE} rows before, ${AFTER} after." >&2
  exit 1
fi

echo "[drill] PASSED: backup and restore preserved ${AFTER} rows."
