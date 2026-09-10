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

case "${ROLE}" in
  web)
    wait_for_postgres
    python manage.py compilemessages --ignore=.venv >/dev/null 2>&1 || true
    python manage.py migrate --noinput
    python manage.py tailwind build || true
    python manage.py collectstatic --noinput --ignore=src || true
    exec python manage.py runserver 0.0.0.0:8000
    ;;
  prod)
    wait_for_postgres
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput --ignore=src
    exec gunicorn config.wsgi:application \
      --bind 0.0.0.0:8000 \
      --workers "${GUNICORN_WORKERS:-3}" \
      --threads "${GUNICORN_THREADS:-2}" \
      --timeout 120 \
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
