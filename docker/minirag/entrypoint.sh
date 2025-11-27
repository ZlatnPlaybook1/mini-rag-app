#!/bin/bash
set -euo pipefail

echo "Waiting up to 30s for DB to accept connections (best-effort)..."

if [ -n "${DATABASE_URL:-}" ]; then
  # parse host and port from DATABASE_URL like postgresql://user:pass@host:5432/db
  host=$(echo "$DATABASE_URL" | sed -E 's#.*@([^:/]+).*#\1#' || echo "")
  port=$(echo "$DATABASE_URL" | sed -E 's#.*:([0-9]+)/.*#\1#' || echo "")
  if command -v nc >/dev/null 2>&1 && [ -n "$host" ] && [ -n "$port" ]; then
    tries=30
    until nc -z "$host" "$port" >/dev/null 2>&1 || [ $tries -le 0 ]; do
      printf '.'
      tries=$((tries-1))
      sleep 1
    done
    echo
    if [ $tries -le 0 ]; then
      echo "Warning: DB did not become reachable at ${host}:${port} after 30s — continuing anyway."
    else
      echo "DB reachable at ${host}:${port}"
    fi
  fi
fi

echo "Running database migrations..."
# use explicit alembic config path to be deterministic
if command -v alembic >/dev/null 2>&1; then
  cd /app/models/db_schemas/minirag/
  alembic -c ./alembic.ini upgrade head || {
    echo "alembic upgrade failed (see logs). Continuing to start the app."
  }
  cd /app
else
  echo "alembic not found; skipping migrations"
fi

# Finally replace the shell with the main command from CMD (uvicorn)
# This lets Dockerfile's CMD run uvicorn and be PID 1.
exec "$@"
