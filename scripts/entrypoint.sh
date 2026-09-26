#!/usr/bin/env bash
# Container entrypoint: wait for Postgres, then run the requested process.
set -euo pipefail

ROLE="${1:-web}"

wait_for_postgres() {
  # DATABASE_URL is what Django itself connects with, so it is the only
  # trustworthy target here.  POSTGRES_PORT in .env is a *host-side* publishing
  # choice: inside the compose network the database always listens on 5432, and
  # waiting on the published port hangs the container forever.
  local host port user
  if [ -n "${DATABASE_URL:-}" ]; then
    read -r host port user <<EOF
$(python - <<'PY'
import os
from urllib.parse import urlparse

url = urlparse(os.environ["DATABASE_URL"])
print(url.hostname or "db", url.port or 5432, url.username or "arer")
PY
)
EOF
  else
    host="${POSTGRES_HOST:-db}"
    port="5432"
    user="${POSTGRES_USER:-arer}"
  fi
  echo "[entrypoint] waiting for postgres at ${host}:${port} ..."
  for _ in $(seq 1 60); do
    if pg_isready -h "${host}" -p "${port}" -U "${user}" >/dev/null 2>&1; then
      echo "[entrypoint] postgres is ready"
      return 0
    fi
    sleep 1
  done
  echo "[entrypoint] postgres did not become ready in time" >&2
  return 1
}

prepare_database() {
  python manage.py migrate --noinput
  # Only used when no REDIS_URL is configured (database-backed cache); a no-op otherwise.
  python manage.py createcachetable
  # Optional first administrator for platforms without a shell. Django reads
  # DJANGO_SUPERUSER_EMAIL / DJANGO_SUPERUSER_PASSWORD; an existing account is left alone.
  if [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    python manage.py createsuperuser --noinput >/dev/null 2>&1 \
      && echo "[entrypoint] created superuser ${DJANGO_SUPERUSER_EMAIL}" \
      || echo "[entrypoint] superuser ${DJANGO_SUPERUSER_EMAIL} already exists"
  fi
  # A freshly created database has no policy pages, sections or JEL codes,
  # so every footer link would 404. Seed that content once; it is flagged
  # "needs editorial review" and carries no accounts. SEED_DEMO_ON_START=true
  # (staging only) additionally loads the demo users, articles and
  # submissions the first time.
  if [ "${SEED_DEMO_ON_START:-false}" = "true" ]; then
    python manage.py seed_demo --if-empty || true
  else
    python manage.py seed_demo --content-only --if-empty || true
  fi
}

case "${ROLE}" in
  web)
    wait_for_postgres
    python manage.py compilemessages --ignore=.venv >/dev/null 2>&1 || true
    python manage.py migrate --noinput
    python manage.py tailwind build || true
    python manage.py collectstatic --noinput --ignore=src || true
    exec python manage.py runserver 0.0.0.0:8000
    ;;
  migrate)
    # One-shot schema + first-start content job (Kubernetes PreSync hook).
    wait_for_postgres
    prepare_database
    ;;
  prod)
    wait_for_postgres
    python manage.py collectstatic --noinput --ignore=src
    # Kubernetes runs this once in a hook Job (role `migrate`) and sets
    # MIGRATE_ON_START=false, so replicas never race each other on the schema.
    if [ "${MIGRATE_ON_START:-true}" = "true" ]; then
      prepare_database
    fi
    # Workers follow the CPU count (the usual 2n+1, capped so a large host does
    # not open more database connections than Postgres allows); threads let
    # each worker overlap the I/O-bound parts of a request. 200 concurrent
    # readers on 3×2 slots queued for seconds; on 9×4 they do not.
    cpus="$(nproc 2>/dev/null || echo 2)"
    default_workers=$(( 2 * cpus + 1 ))
    if [ "${default_workers}" -gt 12 ]; then default_workers=12; fi
    exec gunicorn config.wsgi:application \
      --bind "0.0.0.0:${PORT:-8000}" \
      --workers "${GUNICORN_WORKERS:-${default_workers}}" \
      --threads "${GUNICORN_THREADS:-4}" \
      --worker-tmp-dir /dev/shm \
      --max-requests 1000 \
      --max-requests-jitter 100 \
      --keep-alive 5 \
      --timeout 60 \
      --graceful-timeout 30 \
      --access-logfile - \
      --error-logfile -
    ;;
  worker)
    wait_for_postgres
    exec celery -A config worker -l info --concurrency "${CELERY_CONCURRENCY:-2}"
    ;;
  beat)
    wait_for_postgres
    exec celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    ;;
  tailwind)
    exec python manage.py tailwind watch
    ;;
  *)
    exec "$@"
    ;;
esac
