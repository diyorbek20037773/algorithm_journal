#!/usr/bin/env bash
# =============================================================================
# Nightly backup: PostgreSQL dump + media archive, with retention and an
# optional off-site copy.
#
#   bash scripts/backup.sh                 # uses .env / the environment
#   BACKUP_DIR=/mnt/backups bash scripts/backup.sh
#
# Environment:
#   PGHOST PGPORT PGUSER PGPASSWORD PGDATABASE   PostgreSQL connection
#   BACKUP_DIR             where archives are written  (default ./backups)
#   MEDIA_DIR              media root to archive       (default ./media)
#   BACKUP_RETENTION_DAYS  how long to keep archives   (default 30)
#   BACKUP_S3_TARGET       optional rclone/aws destination, e.g. s3://bucket/arer
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load .env when present, without overriding variables already exported.
if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  . "${ROOT_DIR}/.env"
  set +a
fi

BACKUP_DIR="${BACKUP_DIR:-${ROOT_DIR}/backups}"
MEDIA_DIR="${MEDIA_DIR:-${ROOT_DIR}/media}"
RETENTION="${BACKUP_RETENTION_DAYS:-30}"

export PGHOST="${PGHOST:-${POSTGRES_HOST:-localhost}}"
export PGPORT="${PGPORT:-${POSTGRES_PORT:-5432}}"
export PGUSER="${PGUSER:-${POSTGRES_USER:-arer}}"
export PGPASSWORD="${PGPASSWORD:-${POSTGRES_PASSWORD:-}}"
export PGDATABASE="${PGDATABASE:-${POSTGRES_DB:-arer}}"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "${BACKUP_DIR}"

DB_FILE="${BACKUP_DIR}/arer-db-${STAMP}.dump"
MEDIA_FILE="${BACKUP_DIR}/arer-media-${STAMP}.tar.gz"
CHECKSUMS="${BACKUP_DIR}/arer-${STAMP}.sha256"

echo "[backup] database ${PGDATABASE} on ${PGHOST}:${PGPORT} -> ${DB_FILE}"
pg_dump --format=custom --compress=6 --no-owner --no-privileges --file "${DB_FILE}"

if [[ -d "${MEDIA_DIR}" ]]; then
  echo "[backup] media ${MEDIA_DIR} -> ${MEDIA_FILE}"
  tar -czf "${MEDIA_FILE}" -C "$(dirname "${MEDIA_DIR}")" "$(basename "${MEDIA_DIR}")"
else
  echo "[backup] media directory ${MEDIA_DIR} not found, skipping"
fi

echo "[backup] checksums -> ${CHECKSUMS}"
(
  cd "${BACKUP_DIR}"
  sha256sum "$(basename "${DB_FILE}")" > "$(basename "${CHECKSUMS}")"
  [[ -f "${MEDIA_FILE}" ]] && sha256sum "$(basename "${MEDIA_FILE}")" >> "$(basename "${CHECKSUMS}")"
) || true

echo "[backup] pruning archives older than ${RETENTION} days"
find "${BACKUP_DIR}" -maxdepth 1 -name 'arer-*' -type f -mtime "+${RETENTION}" -print -delete || true

if [[ -n "${BACKUP_S3_TARGET:-}" ]]; then
  echo "[backup] copying off-site to ${BACKUP_S3_TARGET}"
  if command -v rclone >/dev/null 2>&1; then
    rclone copy "${BACKUP_DIR}" "${BACKUP_S3_TARGET}" --include 'arer-*' --max-age 24h
  elif command -v aws >/dev/null 2>&1; then
    aws s3 cp "${DB_FILE}" "${BACKUP_S3_TARGET}/"
    [[ -f "${MEDIA_FILE}" ]] && aws s3 cp "${MEDIA_FILE}" "${BACKUP_S3_TARGET}/"
    aws s3 cp "${CHECKSUMS}" "${BACKUP_S3_TARGET}/"
  else
    echo "[backup] neither rclone nor aws is installed; off-site copy skipped" >&2
  fi
fi

echo "[backup] done: $(basename "${DB_FILE}")"
