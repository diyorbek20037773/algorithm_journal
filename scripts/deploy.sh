#!/usr/bin/env bash
# =============================================================================
# Deploy or update the production stack on the VPS.
#
#   bash scripts/deploy.sh            # pull, build, migrate, restart
#   bash scripts/deploy.sh --seed     # additionally run seed_demo (first install)
#
# The script takes a database backup before migrating, so a failed deployment
# can always be rolled back with scripts/restore.sh.
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

COMPOSE="docker compose -f docker-compose.prod.yml"
SEED=0
[[ "${1:-}" == "--seed" ]] && SEED=1

if [[ ! -f .env ]]; then
  echo "[deploy] .env is missing. Copy .env.example and fill in the production values." >&2
  exit 1
fi

echo "[deploy] 1/7 fetching the latest code"
git pull --rebase

echo "[deploy] 2/7 backing up the database before migrating"
${COMPOSE} exec -T backup sh /scripts/backup.sh || echo "[deploy] backup skipped (stack not running yet)"

echo "[deploy] 3/7 building images"
${COMPOSE} build

echo "[deploy] 4/7 starting the database and cache"
${COMPOSE} up -d db redis

echo "[deploy] 5/7 applying migrations and collecting static files"
${COMPOSE} run --rm web python manage.py migrate --noinput
${COMPOSE} run --rm web python manage.py compilemessages --ignore=.venv
${COMPOSE} run --rm web python manage.py collectstatic --noinput --ignore=src

if [[ "${SEED}" == "1" ]]; then
  echo "[deploy] running seed_demo (first installation)"
  ${COMPOSE} run --rm web python manage.py seed_demo
fi

echo "[deploy] 6/7 restarting the application"
${COMPOSE} up -d --remove-orphans

echo "[deploy] 7/7 waiting for the health check"
for _ in $(seq 1 30); do
  if ${COMPOSE} exec -T web curl -fsS http://localhost:8000/healthz/ >/dev/null 2>&1; then
    echo "[deploy] healthy"
    ${COMPOSE} ps
    exit 0
  fi
  sleep 5
done

echo "[deploy] the application did not become healthy in time." >&2
${COMPOSE} logs --tail 60 web >&2
exit 1
