#!/usr/bin/env bash
# =============================================================================
# Restore the journal from a backup produced by scripts/backup.sh.
#
#   bash scripts/restore.sh                          # newest dump in ./backups
#   bash scripts/restore.sh backups/arer-db-….dump   # a specific dump
#   RESTORE_MEDIA=1 bash scripts/restore.sh          # also unpack the media archive
#
# The script refuses to run against a database that already has data unless
# FORCE=1 is set, so that it cannot silently destroy a live installation.
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  . "${ROOT_DIR}/.env"
  set +a
fi

BACKUP_DIR="${BACKUP_DIR:-${ROOT_DIR}/backups}"
MEDIA_DIR="${MEDIA_DIR:-${ROOT_DIR}/media}"

export PGHOST="${PGHOST:-${POSTGRES_HOST:-localhost}}"
export PGPORT="${PGPORT:-${POSTGRES_PORT:-5432}}"
export PGUSER="${PGUSER:-${POSTGRES_USER:-arer}}"
export PGPASSWORD="${PGPASSWORD:-${POSTGRES_PASSWORD:-}}"
export PGDATABASE="${PGDATABASE:-${POSTGRES_DB:-arer}}"

DUMP="${1:-}"
if [[ -z "${DUMP}" ]]; then
  DUMP="$(ls -1t "${BACKUP_DIR}"/arer-db-*.dump 2>/dev/null | head -n 1 || true)"
fi
if [[ -z "${DUMP}" || ! -f "${DUMP}" ]]; then
  echo "[restore] no dump found. Pass one explicitly: bash scripts/restore.sh <file>" >&2
  exit 1
fi

echo "[restore] source: ${DUMP}"

CHECKSUMS="${DUMP%.dump}"
CHECKSUMS="${BACKUP_DIR}/arer-${CHECKSUMS##*arer-db-}.sha256"
if [[ -f "${CHECKSUMS}" ]]; then
  echo "[restore] verifying checksum"
  (cd "${BACKUP_DIR}" && sha256sum -c "$(basename "${CHECKSUMS}")" --ignore-missing)
fi

EXISTING="$(psql -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'" 2>/dev/null || echo 0)"
if [[ "${EXISTING}" -gt 0 && "${FORCE:-0}" != "1" ]]; then
  echo "[restore] the target database already contains ${EXISTING} tables." >&2
  echo "[restore] re-run with FORCE=1 to drop and recreate the public schema." >&2
  exit 2
fi

echo "[restore] recreating the public schema in ${PGDATABASE}"
psql -v ON_ERROR_STOP=1 -c "DROP SCHEMA IF EXISTS public CASCADE;" -c "CREATE SCHEMA public;"

echo "[restore] loading the dump"
pg_restore --no-owner --no-privileges --dbname "${PGDATABASE}" "${DUMP}"

if [[ "${RESTORE_MEDIA:-0}" == "1" ]]; then
  MEDIA_ARCHIVE="${BACKUP_DIR}/arer-media-${CHECKSUMS##*arer-}"
  MEDIA_ARCHIVE="${MEDIA_ARCHIVE%.sha256}.tar.gz"
  if [[ -f "${MEDIA_ARCHIVE}" ]]; then
    echo "[restore] unpacking ${MEDIA_ARCHIVE}"
    mkdir -p "$(dirname "${MEDIA_DIR}")"
    tar -xzf "${MEDIA_ARCHIVE}" -C "$(dirname "${MEDIA_DIR}")"
  else
    echo "[restore] media archive ${MEDIA_ARCHIVE} not found; skipping"
  fi
fi

ROWS="$(psql -tAc "SELECT count(*) FROM journal_article" 2>/dev/null || echo 0)"
echo "[restore] done. journal_article rows: ${ROWS}"
echo "[restore] run 'python manage.py migrate' to apply any newer migrations."
