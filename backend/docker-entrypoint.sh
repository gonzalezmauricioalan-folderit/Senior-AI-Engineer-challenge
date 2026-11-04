#!/bin/sh
# Container start-up (PLAN.md Task 5): schema -> data -> server.
# `set -e` so a failed migration or seed stops the container instead of serving an empty db.
set -e

# Idempotent: no-op when the db is already at head.
alembic upgrade head

# Loads data/seed.sql only when `accounts` is empty, so restarts never duplicate data.
python -m app.seed

# exec so uvicorn is PID 1 and receives SIGTERM from `docker compose stop`.
# 0.0.0.0 because the published port is reached through the container's eth0, not loopback.
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
