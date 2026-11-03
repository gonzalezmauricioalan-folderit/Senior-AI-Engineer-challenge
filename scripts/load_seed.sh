#!/usr/bin/env bash
# Migrate the compose db to head, then load data/seed.sql (unmodified) via psql in the db container.
# Idempotent: if accounts or activity_events already has rows, the seed is skipped.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

[ -f .env ] && set -a && . ./.env && set +a
DB="${POSTGRES_DB:-relay}"
USER_="${POSTGRES_USER:-relay}"
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://${USER_}:${POSTGRES_PASSWORD:-relay}@localhost:${POSTGRES_PORT:-5432}/${DB}}"

ALEMBIC="$ROOT/backend/.venv/bin/alembic"
[ -x "$ALEMBIC" ] || { echo "error: $ALEMBIC not found; create the venv first (see CLAUDE.md)" >&2; exit 1; }

psql_db() { docker compose exec -T db psql -v ON_ERROR_STOP=1 -U "$USER_" -d "$DB" "$@"; }

echo "==> waiting for db"
for _ in $(seq 1 60); do
  docker compose exec -T db pg_isready -U "$USER_" -d "$DB" >/dev/null 2>&1 && break
  sleep 1
done
docker compose exec -T db pg_isready -U "$USER_" -d "$DB" >/dev/null || { echo "error: db not ready (is 'docker compose up -d' running?)" >&2; exit 1; }

echo "==> alembic upgrade head"
(cd backend && "$ALEMBIC" upgrade head)

existing="$(psql_db -tA -c "SELECT (SELECT count(*) FROM accounts) + (SELECT count(*) FROM activity_events)")"
if [ "$existing" != "0" ]; then
  echo "==> seed skipped: tables already contain $existing rows (reset with: docker compose down -v)"
  exit 0
fi

echo "==> loading data/seed.sql"
psql_db -q --single-transaction < data/seed.sql
psql_db -tA -c "SELECT 'accounts=' || count(*) FROM accounts" -c "SELECT 'activity_events=' || count(*) FROM activity_events"
echo "==> done"
