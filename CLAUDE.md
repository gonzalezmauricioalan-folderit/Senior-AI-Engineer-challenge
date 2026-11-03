# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## IMPORTANT

You are running inside a docker sandbox. You have access to some MCP (eg Github, Jira.) But There is no need to use in this session

## What this repo is

A take-home exercise for "Relay", a fictional B2B SaaS that tracks inbound customer activity (calls, leads, appointments) across a customer's locations. The task is ticket **DASH-247** (`relay-analytics-starter/docs/TICKET.md`): help a customer answer *"is this week's activity normal for us?"* on their dashboard.

- Product hints: compare against some baseline; multi-location customers matter; a customer admin should be able to look at it on Monday morning and act on it.
- **Out of scope:** alerting/notifications, ML/forecasting.
- The team works spec-driven and AI-first. Planning, spec interpretation and hardening agent output carry the weight, so record the important decisions and assumptions in the repo.

## Stack

- **DB:** Postgres 16.4 in Docker Compose (`docker-compose.yml`, service `db`). Credentials come from env vars (`.env.example`), defaulting to `relay`/`relay`/`relay`.
- **Migrations:** Alembic in `backend/` (`backend/migrations/versions/`). The schema lives only in migrations. Never hand-run DDL.
- **Backend:** FastAPI (planned) in `backend/`, Python venv at `backend/.venv`, deps pinned in `backend/requirements.txt`.
- No app code, lint or test tooling yet. Add those commands here once they exist, including how to run a single test.

## Local database

```bash
cp .env.example .env                                   # optional; defaults match
uv venv backend/.venv && uv pip install --python backend/.venv/bin/python -r backend/requirements.txt
                                                       # or: python3 -m venv backend/.venv && backend/.venv/bin/pip install -r backend/requirements.txt
docker compose up -d --wait                            # start db, wait for healthy
(cd backend && .venv/bin/alembic upgrade head)         # migrate only
./scripts/load_seed.sh                                 # migrate + load data/seed.sql (skips if data already present)
docker compose exec db psql -U relay -d relay          # psql shell
docker compose down -v && docker compose up -d --wait && ./scripts/load_seed.sh   # reset
```

- URL: `postgresql+psycopg://relay:relay@localhost:5432/relay` (`DATABASE_URL`, read by `backend/migrations/env.py`).
- `data/seed.sql` is a byte-identical copy of the starter seed (sha256 `40e60ee8…eaea2`). Never edit it.
- Timestamps are `timestamp without time zone` holding UTC. Convert per account timezone in queries.
- Migration `0001_initial_schema` also adds index `ix_activity_events_account_id_occurred_at` (it covers the FK and the per-account time-range access).
- Expected after seed: 20 accounts, 12626 events, `occurred_at` from 2026-02-01 10:57:44 to 2026-07-27 22:20:34.

## Starter material (`relay-analytics-starter/`)

This directory is **gitignored** and kept only as local reference (its nested `.git` was removed). Copy `schema.sql` and `seed.sql` into the real project. `docs/` is context only and doesn't need to ship.

Rules from the starter README:
- Wire `schema.sql` into **the project's own migrations**. Don't hand-run the DDL. The SQL is portable, so adapt the types to the chosen database.
- Use the seed data **as-is**. Don't regenerate, extend or "fix" it. Treat it like messy production data and handle its quirks in code.
- Don't name anything `relay-analytics-starter`.

## Data model

- `accounts(id, name, industry, timezone, created_at)`: 20 customers. `timezone` is an IANA name.
- `activity_events(id, account_id, location, event_type, occurred_at, duration_seconds, outcome)`: about 12.6k rows.
  - `event_type`: `call_received` | `lead_created` | `appointment_set`
  - `outcome` by type: calls → `connected`/`missed`/`voicemail`; leads → `open`/`converted`; appointments → `completed`/`no_show`
  - `occurred_at` is **UTC**. Any "week" or "day" a customer sees must be bucketed in the account's own timezone. Monday-morning views depend on this.

## Known data quirks (from profiling the seed; re-verify before relying on them)

- Events run 2026-02-01 → 2026-07-27, about 26 weeks. The last week may be partial.
- Account 20 (Quiet Harbor Spa) has **no events at all**, so the baseline has to handle an empty history.
- Accounts range from 1 location to 15. Location names follow the pattern `Site A`…`Site O` and are unique only *within* an account.
- Account 6 (Metro Collision Centers, 15 sites) has a large spike across many sites starting around 2026-06-03, so a naive mean baseline would be skewed by it.
- About 12 groups of exact duplicate events have the same account, location, type and timestamp but different `id`s.
- `outcome` is NULL on about 400 rows across all types. `duration_seconds` applies only to calls (20–1500s) and is NULL on about 313 calls.
- Account timezones include `America/Phoenix`, which has no DST, and plain `UTC`.

To profile the data quickly, load `schema.sql` and then `seed.sql` into SQLite. Both run unmodified.
