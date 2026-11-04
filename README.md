# Relay: "is this week's activity normal for us?" (DASH-247)

A dashboard that tells a customer admin, on Monday morning, whether last week's activity (calls, leads,
appointments) was normal for their account, and which of their locations dropped. The ticket is
`DASH-247`. "Normal" means the account's own recent history: the median of the previous 8 complete weeks, with a
band that one-off spikes can't distort.

## Run it

Prerequisites: Docker with compose v2, and free host ports 5432 (db), 8000 (api) and 8080 (web).

```bash
docker compose up -d --build --wait    # db + api + web; the api migrates and seeds itself
```

- Dashboard: http://localhost:8080
- API: http://localhost:8000 (health check: http://localhost:8000/health, docs: http://localhost:8000/docs)

Reset to a clean database:

```bash
docker compose down -v && docker compose up -d --build --wait
```

**Fresh-clone check (budget: 15 minutes):** from `git clone` in a temporary directory, `docker compose build
--no-cache` followed by `docker compose up -d --wait` took **2 min 20 s** until db, api and web were healthy, the
dashboard returned 200, and `/health` returned `{"status":"ok","db":"ok"}`. The base images (`postgres`, `python`,
`node`, `nginx`) were already pulled; the pip and npm installs ran from scratch. On that host port 5432 was taken,
so it ran with `POSTGRES_PORT=5434` (see below).

**Ports and env vars.** The defaults work without a `.env`. `.env.example` lists the variables; copy it to `.env`
to change them.

| Variable | Default | What it does |
|---|---|---|
| `POSTGRES_PORT` | `5432` | Host port of the db. Set it if 5432 is taken, e.g. `POSTGRES_PORT=5434 docker compose up -d --build --wait`. The api is not affected: inside compose it reaches the db at `db:5432`. |
| `API_PORT` | `8000` | Host port of the api. The web image bakes `http://localhost:${API_PORT}` in at build time, so rebuild after changing it. |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | `relay` | Database credentials. |
| `DATABASE_URL` | `postgresql+psycopg://relay:relay@localhost:5432/relay` | Used by Alembic and the api when they run on the host. |
| `AS_OF_DATE` | unset | `YYYY-MM-DD`. Pins "today". Unset, it's the local date of the newest event, so the seed's latest complete week is the week of 2026-07-20. |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:8080` | Origins the api allows. |

The web port is fixed at **8080** because it's in the api's default CORS list.

**What to look at.** The default week (2026-07-20) is normal for every account. To see verdicts that need
attention, pick:

| Account | Week | What it shows |
|---|---|---|
| 6 Metro Collision Centers | 2026-06-01 | Higher (880 vs ~66). All 15 sites are higher. This is the one-day spike on 2026-06-03. |
| 2 Harbor Dental Partners | 2026-07-06 | Lower (18 vs ~32.5, −45%). |
| 1 Summit Auto Group | 2026-06-01 | The account is normal, but Site F is lower (2 vs ~10) and is ranked first. |
| 20 Quiet Harbor Spa | any | Not enough history (no events). |
| 18 Capital City Storage | any | The UTC-timezone data note. |

### Local development (without the api and web containers)

```bash
cp .env.example .env                                        # optional; the defaults match
docker compose up -d --wait db                              # db only
uv venv backend/.venv && uv pip install --python backend/.venv/bin/python -r backend/requirements-dev.txt
./scripts/load_seed.sh                                      # migrate + load data/seed.sql (skips if already loaded)
(cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000)
(cd frontend && nvm use && npm ci && npm run dev)           # Node 22; http://localhost:5173
```

## Tests

```bash
cd backend && .venv/bin/pytest -q             # 88 tests on SQLite, no Docker needed (~8 min; -m "not slow" skips the full-seed ones)
cd frontend && npm test -- --run              # 46 tests, Vitest + MSW, no live api
```

Lint: `cd backend && .venv/bin/ruff check . && .venv/bin/ruff format --check .` and `cd frontend && npm run lint`.
The committed `openapi.json` is the contract between the two sides. A backend test fails if it's stale
(`backend/.venv/bin/python scripts/export_openapi.py` regenerates it), and the frontend types are generated from it
(`npm run gen:api`).

## Stack and why

- **FastAPI + React (TypeScript, Vite).** The stack we're strongest in. FastAPI gives typed models and an OpenAPI
  contract for free, and the frontend types are generated from that contract.
- **Postgres 16, SQLAlchemy Core with raw SQL, no ORM.** There are only three queries, all reads. Plain SQL in
  `text()` is easier to review than ORM mappings and runs unchanged on SQLite.
- **Alembic migrations.** The starter `schema.sql` is wired in as migration `0001`, plus an index on
  `(account_id, occurred_at)` and the `clean_activity_events` view. The schema exists only in migrations.
- **Aggregation in Python, not SQL.** Weeks and days have to be bucketed in each account's IANA timezone, DST
  included, and the tests run on SQLite, which has no timezone support. SQL does the cleaning (the dedupe view)
  and the filter by account. Python (`zoneinfo`) does the bucketing, baselines and verdicts. One account is at most
  ~2.7k rows, so this is cheap. In production we'd pre-aggregate into a daily rollup table per
  account/location/local date and read only that.
- **React state + `localStorage`, no state or data-fetching library.** The state is one selection (account and
  week). It survives a reload through `localStorage`, and a stored value that is invalid or blocked falls back to
  the default.
- **SQLite for tests.** Fast and hermetic. Every test builds its own data through factories, and the "golden"
  tests load the real seed. The cost: Postgres-specific behavior isn't tested in CI (see "With another day").

## Interpretation of the ticket

- **The question** is asked by a customer admin on Monday morning, about the week that just ended (Mon–Sun in the
  account's local time).
- **"Normal for us"** is the account's own history, not a comparison with other customers.
- **What the screen shows:** one verdict for the account (normal / higher / lower / not enough history), the 7
  days of the week next to their usual values as context, and every location with its own verdict, ranked so that
  the locations that dropped come first.
- **Metric:** total events (calls + leads + appointments), deduplicated.

### How "normal" is defined

For a week with total `value` and the totals of the previous 8 complete weeks as `history`
(`backend/app/domain/detection.py`):

```
fewer than 4 history weeks          -> not_enough_history
usual  = median(history)
MAD    = median(|x − usual|)
spread = max(1.4826 · MAD, √usual)                   # never narrower than Poisson noise
band   = [max(0, usual − 2.5·spread), usual + 2.5·spread]
flag if value is outside the band AND |value − usual| ≥ 3 AND |pct| ≥ 20%
```

**Why median + MAD.** `Detection_tuning.md` ran a grid over k, N and the floors against the seed and a
Poisson-noise baseline:

- **Robust to spikes.** Account 6's spike week (880 events vs ~66) is flagged higher, and the weeks after it keep
  a band like the one before it. With mean ± std, "usual" jumps to ~170 and the band to 0–888 for 8 weeks: even
  zero events would read normal.
- **k = 2.5.** At k = 2 the flag rate (6.0%) is barely above pure noise (5.2%). At k = 3 no account week is ever
  lower, so a real −45% drop (account 2, week of 2026-07-06) is missed. k = 2.5 flags 3% of account-weeks, at
  1.7× the noise rate.
- **N = 8 weeks.** About as stable as 12 weeks, adapts to level changes within two months, and matches the
  wireframe's "vs. previous 8 weeks".
- **The floors (3 events, 20%)** never change a verdict on this seed. The `√usual` term already implies them.
  They're cheap insurance for volumes outside the seed's range.

## Assumptions

On a real ticket these would go to product or the data owners. Evidence: `OPEN_QUESTIONS.md` and
`Data_integrity.md`.

| Question | Working assumption |
|---|---|
| Why does account 20 have no events? | Not onboarded yet → "not enough history". |
| Why is account 18's timezone `UTC`? | Probably a misconfiguration. We use it as stored and show a data note. |
| Why are ~20% of events before 07:00 local? | Automated processes. No business-hours filter; everything counts. |
| Why account 6's one-day spike (2026-06-03) and +94% for account 15 the same week? | A marketing campaign. Kept, flagged higher, and the median keeps it out of later baselines. |
| Why are `duration_seconds` and `outcome` sometimes NULL? | Not captured yet. Irrelevant to an event count; the rows still count. |
| Which metric matters most? | Total events, for volume and simplicity. |
| Do businesses work weekends? | Every account has some weekend activity (2–12%) → full Mon–Sun weeks. |

### Data quirks and how each is handled

The seed is used as-is and the raw tables are never modified (`Data_integrity.md` has the full profile).

| Quirk | Handling |
|---|---|
| 12 exact duplicate pairs (every column except `id`) | Removed by the `clean_activity_events` view (lowest `id` kept). The week's data notes say how many were removed. |
| 27 near-duplicates (1–60 s apart) | Kept. They differ in duration or outcome, so they look like distinct events. |
| Account 6's one-day spike | Kept and flagged higher. The median/MAD baseline absorbs it for later weeks. |
| Account 20 has no events | "Not enough history" card and an empty locations table. |
| Account 18 has timezone `UTC` | Used as stored, with a warning note that days and weeks may be shifted. |
| `America/Phoenix` (no DST) and DST switches | All bucketing goes through `zoneinfo`, so each account's offsets are correct. |
| First and last weeks have one day each | Never offered or evaluated. The first complete week is 2026-02-02 and the last is 2026-07-20. Earlier, partial or future weeks → 422. |
| Data ends months before today | "Today" is the date of the newest event (or `AS_OF_DATE`), not the wall clock. |
| NULL `outcome` / `duration_seconds` | Irrelevant to the count; the rows still count. |
| Location names repeat across accounts (`Site A`…) | Locations are always scoped by account. |

## Design decisions and trade-offs

- **Dedupe-only cleaning.** Only exact duplicates are removed. Anything else would mean guessing which real-looking
  events are wrong.
- **Weekly verdicts, daily context.** At ~1 event per location per weekday, daily verdicts would be noise. The
  days are shown next to their usual values without a status.
- **Mon–Sun weeks.** We first proposed Mon–Sat. The data showed Saturday ≈ Sunday and weekend activity on every
  account, so weeks include Sunday.
- **8-week window, k = 2.5, floors (3, 20%).** See "Why median + MAD" above.
- **Ranking is "lower only".** Only `lower_than_usual` locations count as "needs attention" and come first,
  biggest drop first. Higher and normal follow together by name. On this data the needs-attention list is usually
  empty: the default week has no flagged location on any account.
- **Low-volume warnings.** When usual ≤ 6, percentages are noisy and the UI says so, on the account and on each
  location row. **Known limit:** below usual ≈ 6.25 (= k²) the lower bound is 0, so a small site can't be flagged
  lower even at zero events. Just above that, it can only be flagged lower at 0 events. Example: account 14,
  Site B, week of 2026-07-20 reads normal at 2 events vs usual 6.5 (−69%): its band is 0.1–12.9, and the
  low-volume warning doesn't show because 6.5 > 6. If product cares about sites "going dark", that needs its own
  rule (`Detection_tuning.md` §7).

## Deliberately deferred

- **An LLM feature.** The numbers already answer the question exactly, for free, instantly and testably. An LLM
  could only restate them, and it couldn't explain *why* a week was unusual, because the data has no causes in it
  (no campaigns, holidays or staffing). An invented explanation is worse than none on a dashboard customers act
  on. It would fit once the product captures context, such as notes, transcripts or campaign records, behind a
  trust boundary that never changes the numbers (PLAN.md 0.2).
- **Daily verdicts:** too little volume per day.
- **Per-event-type and outcome metrics:** too little volume per series, and we'd ask product which one matters.
- **Seasonality:** 25 weeks of data can't show annual patterns.
- **Holiday and campaign annotations, alerting, ML forecasting:** out of scope by the ticket or by volume.
- **Auth:** the account picker is a demo convenience. In production the account comes from the session.
- **Postgres tests in CI:** the tests run on SQLite. The Postgres path is checked by running the stack.

## With another day

- A daily rollup table per account/location/local date (Postgres `AT TIME ZONE`), so the api reads aggregates
  instead of events.
- Per-event-type and outcome metrics (for example, missed-call rate), after asking product which one matters.
- Postgres integration tests in CI.
- An annotations calendar, so a campaign week can be marked as expected.
- A "went dark" rule for small sites (see the known limit above).

## How it was built

Spec-driven and AI-first. `PLAN.md` was written and frozen before any code; the decision log is
`PLAN_first_iteration.md`. Each task was implemented by a builder agent on its own branch, checked by a reviewer
agent (`.claude/agents/`), and reviewed and merged by a human as a GitHub PR. The AI interaction log is in `ai-log/`.

### Changes from the plan

`PLAN.md` stays frozen. `PLAN_CHANGES.md` records every change after Task 1:

1. **Health test with a broken db (Task 7).** The test points the app at an unreachable database instead of a
   dependency override, because `/health` no longer goes through that dependency.
2. **Frontend dependencies (Task 8a).** Four required companion packages were added (`@types/react`,
   `@types/react-dom`, `@testing-library/dom`, `@eslint/js`). TypeScript is pinned to 5.9.3, the newest version
   that `openapi-typescript` and `typescript-eslint` both accept.
3. **Task 11 skipped (Task 12).** The consolidated F1–F13 full-screen tests and the manual browser check were
   skipped for time. Every F scenario is still covered by a Task 8–10 test; `PLAN_CHANGES.md` maps them and says
   what was lost.
