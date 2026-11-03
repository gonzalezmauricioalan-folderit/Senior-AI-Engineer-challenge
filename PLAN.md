# PLAN — DASH-247 "Is this week normal for us?"

Implementation plan split into small tasks. **Every task ends in one or more GitHub PRs.**
Why each decision was made: `PLAN_first_iteration.md` (decision log), `Data_integrity.md`, `Detection_tuning.md`, `OPEN_QUESTIONS.md`. Product context: `relay-analytics-starter/docs/`.

**Agents run on Sonnet. Everything that needs judgment has already been decided in this file.** Agents implement; they don't redesign.

---

## 1. Workflow

Roles:
- **Orchestrator:** the main Claude Code session. It launches agents one at a time, relays results to the human, and after each human review offers concrete options to change or enhance the agent definitions (`.claude/agents/*.md`) based on what the review caught.
- **Builders:** `api-builder`, `frontend-builder`. **Reviewers:** `api-reviewer`, `frontend-reviewer`.
- **Human:** reviews and merges every PR on GitHub.

Per task, strictly sequential:
1. Builder: branch `task/<id>-<slug>` from an up-to-date `main` → implement the task's **Scope** → write its **Tests** → run its **Quickstart** → open the PR.
2. Reviewer: checks the PR against this plan, re-runs the Quickstart, posts a review comment. Blocking findings → the builder fixes them on the same branch → re-review.
3. Human reviews and merges (or requests changes → step 1 on the same branch).
4. Orchestrator offers agent improvements, then starts the next task.

### PR rules
- **< 700 changed lines** (added + removed), excluding generated files and data:
  ```bash
  git diff --numstat main...HEAD -- . ':!**/package-lock.json' ':!data/seed.sql' ':!openapi.json' ':!frontend/src/api/schema.d.ts' \
    | awk '{s+=$1+$2} END {print s}'
  ```
- **Stacked PRs** when a task doesn't fit: split along the task's Scope bullets into `task/<id>a-<slug>` (base `main`), `task/<id>b-<slug>` (base `task/<id>a-<slug>`), and so on. Each PR passes its own tests. The PR title says `[<id>a/2]`, and each description links the others. After the lower PR merges, retarget the next one: `gh pr edit <n> --base main`.
- **PR description:** Goal · Changes · Tests added · Quickstart output (trimmed) · Line count · **Decisions taken** (anything this plan didn't specify) · Deviations · Follow-ups.
- **Commit messages:** `<type>(<area>): <summary>` with type ∈ feat, fix, test, chore, docs; area ∈ api, web, db, infra, docs.

### When something isn't specified
- Pick the **simplest option consistent with this plan** and list it under "Decisions taken" in the PR.
- **Stop and ask the orchestrator** instead if it would change: the API contract, the data/cleaning rules, the detection math or constants, the ranking, or the scope of another task.
- If a test in a test task (6, 7, 11) fails because of an app bug: fix it in the same PR as a separate `fix(...)` commit if the fix is < 50 lines; otherwise stop and report.

---

## 2. Decisions (fixed)

- **Data:** raw tables are never modified, and the seed is used as-is. View `clean_activity_events` removes only the 12 exact duplicates.
- **Metric:** total events per week, all event types together.
- **Weeks:** Mon–Sun in the **account's local time**. UTC → local conversion happens **only in Python (`zoneinfo`)**, never in SQL.
- **As-of:** `as_of_local` = `AS_OF_DATE` (env, `YYYY-MM-DD`) if set, else the local date of the dataset's max `occurred_at` in the clean view. Latest complete week = `monday_of(as_of_local) − 7 days` (Jul 20, 2026 on the seed). Default week = the latest complete week. Partial or future weeks → 422.
- **First complete week of the dataset** (computed per account, in the account's timezone): let `d` = local date of the dataset's min `occurred_at` (whole clean view, not just the account); `first_complete_week = d if d is a Monday else monday_of(d) + 7` (Feb 2, 2026 on the seed). Earlier weeks → 422.
- **Empty dataset** (no events at all): `first_complete_week = None` (no lower-bound check); `as_of_local` needs `AS_OF_DATE`, otherwise 422 `no activity data available` and `latest_complete_week = null` in `/accounts`.
- **Series:** one per account (all its events) and one per account+location. A series starts at the first Monday ≥ `first_complete_week` whose week has ≥ 1 event. Weeks without events inside the series count as 0.
- **History of a week W:** the weeks `max(series_start, W − 8 weeks) … W − 1 week`, zero-filled. **The evaluated week is never in its own history.** No series_start, or series_start ≥ W → empty history.
- **Detection** (constants in `backend/app/domain/detection.py`: `K = 2.5`, `N_WEEKS = 8`, `MIN_HISTORY = 4`, `MIN_ABS = 3`, `MIN_PCT = 0.20`, `LOW_VOLUME_USUAL = 6`):
  ```
  if len(history) < MIN_HISTORY: status = not_enough_history; usual/lower/upper/pct = None; low_volume = False
  usual  = median(history)
  MAD    = median(|x − usual| for x in history)
  spread = max(1.4826 · MAD, √usual)
  lower  = max(0, usual − K · spread)
  upper  = usual + K · spread
  diff   = value − usual
  pct    = diff / usual if usual > 0 else None
  flagged = (value < lower or value > upper) and |diff| ≥ MIN_ABS
            and (|pct| ≥ MIN_PCT if usual > 0 else value > 0)
  status = (higher_than_usual if diff > 0 else lower_than_usual) if flagged else normal
  low_volume = usual ≤ LOW_VOLUME_USUAL
  ```
- **Daily context:** the 7 days of the selected week (account level only). `usual` per day = median of that weekday's count over the account's history weeks; `None` when the account summary is `not_enough_history`. Days never get a status.
- **Ranking of locations:** first `lower_than_usual` by `pct_vs_usual` ascending (biggest drop first, ties by name); then `higher_than_usual` and `normal` together by location name; then `not_enough_history` by name. Only lower counts as "needs attention".
- **Locations listed:** every location with ≥ 1 clean event for the account, at any time.
- **Data notes** (exact strings, in this order, only when they apply):
  - `"1 duplicate event removed from this week."` / `"{n} duplicate events removed from this week."`: n = raw rows not in the clean view whose local date falls in the selected week.
  - `"This account's timezone is set to UTC, which may be a misconfiguration; days and weeks may be shifted."`: when `timezone == "UTC"`.
- **Rounding** (in the service, not the domain): `usual`, `lower`, `upper` to 1 decimal; `pct_vs_usual` to 3 decimals (a fraction: −0.32 means −32%).
- **Out of scope:** auth, rate limiting, alerting, ML/forecasting, holiday/campaign calendar, daily verdicts, per-event-type metrics, location drill-down, persisting UI state in the URL.

---

## 3. Implementation spec (fixed)

### 3.1 Libraries
Pin each to the **latest stable version at implementation time** (check with `pip index versions <pkg>` / `npm view <pkg> version`), exact pins only. Don't add any library that isn't listed. If one seems necessary, stop and ask.
- **Backend runtime:** fastapi, uvicorn[standard], sqlalchemy (already pinned), psycopg[binary] (pinned), alembic (pinned). No ORM models (SQLAlchemy Core + `text()` only), no pydantic-settings.
- **Backend dev** (`backend/requirements-dev.txt`, `-r requirements.txt` first): pytest, httpx, ruff.
- **Frontend:** react, react-dom, recharts. Dev: vite, @vitejs/plugin-react, typescript, eslint, typescript-eslint, eslint-plugin-react-hooks, vitest, jsdom, @testing-library/react, @testing-library/user-event, @testing-library/jest-dom, msw, openapi-typescript. Node 22 LTS (`.nvmrc` = `22`). No UI kit, no CSS framework, no state or data-fetching library, no date library.

### 3.2 Backend layout
```
backend/
  pyproject.toml            # ruff (line-length 110, target py313) + pytest config (testpaths, markers: slow)
  app/
    main.py                 # create_app(settings: Settings | None = None) -> FastAPI; app = create_app()
    config.py               # @dataclass(frozen) Settings: database_url, as_of_date: date | None, cors_origins: list[str]; Settings.from_env()
    db.py                   # make_engine(url); get_connection dependency (yields a Connection)
    routes.py               # APIRouter with the 3 endpoints
    schemas.py              # Pydantic response models (3.4)
    repository.py           # SQL only (3.3)
    service.py              # list_accounts(), build_weekly_insight(): orchestration + rounding + errors
    seed.py                 # load_seed(engine, path) -> bool (False if accounts already has rows)
    domain/
      weeks.py              # pure date/timezone helpers
      detection.py          # constants + evaluate() + weekday_usuals()
      ranking.py            # rank_locations()
  migrations/versions/0002_clean_activity_events.py
  tests/
    conftest.py             # fixtures (3.5)
    factories.py            # data builders (3.5)
    unit/                   # domain only
    integration/            # API through TestClient on SQLite
```
- Env vars: `DATABASE_URL` (default `postgresql+psycopg://relay:relay@localhost:5432/relay`), `AS_OF_DATE` (optional), `CORS_ORIGINS` (comma-separated, default `http://localhost:5173,http://localhost:8080`).
- Datetimes from the DB are naive UTC. SQLite returns strings, so the repository normalizes every timestamp with `datetime.fromisoformat` when it gets a `str`.

### 3.3 SQL
Migration `0002_clean_activity_events` (portable; NULLs fall in the same partition on both engines):
```sql
CREATE VIEW clean_activity_events AS
SELECT id, account_id, location, event_type, occurred_at, duration_seconds, outcome
FROM (
  SELECT e.*, ROW_NUMBER() OVER (
    PARTITION BY account_id, location, event_type, occurred_at, duration_seconds, outcome
    ORDER BY id) AS rn
  FROM activity_events e
) t
WHERE rn = 1;
```
Downgrade: `DROP VIEW clean_activity_events`.

Repository functions (each takes a `Connection`):
- `ping(conn) -> None`: `SELECT 1`.
- `list_accounts(conn)`: id, name, industry, timezone, `COUNT(DISTINCT c.location)` as location_count (LEFT JOIN on the clean view), ordered by name.
- `get_account(conn, account_id)`: one row or None.
- `dataset_bounds(conn) -> tuple[datetime, datetime] | None`: min/max `occurred_at` of the clean view.
- `account_events(conn, account_id) -> list[tuple[str, datetime]]`: (location, occurred_at) of **all** the account's clean events. Volume is ≤ ~2.7k rows per account; the production note (rollup table) goes in the write-up.
- `duplicate_timestamps(conn, account_id) -> list[datetime]`: `occurred_at` of raw rows whose id isn't in the clean view.

### 3.4 Domain signatures and API models
```python
# domain/weeks.py
def local_date(occurred_at_utc: datetime, tz: ZoneInfo) -> date
def monday_of(d: date) -> date
def first_complete_week(min_local: date) -> date
def latest_complete_week(as_of_local: date) -> date
def weekly_counts(timestamps_utc: Iterable[datetime], tz: ZoneInfo) -> Counter[date]   # key = local Monday
def daily_counts(timestamps_utc: Iterable[datetime], tz: ZoneInfo) -> Counter[date]    # key = local date
def series_start(counts: Mapping[date, int], first_week: date) -> date | None
def history(counts: Mapping[date, int], start: date | None, week: date, n_weeks: int) -> list[tuple[date, int]]

# domain/detection.py
class Status(StrEnum): NORMAL = "normal"; LOWER = "lower_than_usual"; HIGHER = "higher_than_usual"; NOT_ENOUGH = "not_enough_history"
@dataclass(frozen=True)
class Evaluation: total: int; usual: float | None; lower: float | None; upper: float | None
                  pct_vs_usual: float | None; status: Status; low_volume: bool; history_weeks: int
def evaluate(value: int, history: Sequence[int]) -> Evaluation
def weekday_usuals(history_weeks: Sequence[date], daily: Mapping[date, int]) -> list[float | None]  # 7 items, Mon..Sun

# domain/ranking.py
def rank_locations(items: Sequence[tuple[str, Evaluation]]) -> list[tuple[str, Evaluation]]
```
Pydantic models (`schemas.py`). Field names are the contract. Use `import datetime as dt` and annotate dates as `dt.date`, because a field named `date` typed `date` shadows the type and breaks Pydantic:
```python
class Health(BaseModel): status: Literal["ok", "error"]; db: Literal["ok", "error"]
class AccountSummary(BaseModel): id: int; name: str; industry: str; timezone: str; location_count: int; latest_complete_week: date | None
class AccountRef(BaseModel): id: int; name: str; timezone: str
class Week(BaseModel): start: date; end: date                      # Monday, Sunday
class Baseline(BaseModel): method: Literal["median_mad"]; weeks_used: int; start: date | None; end: date | None
class Metric(BaseModel): total: int; usual: float | None; lower: float | None; upper: float | None
                         pct_vs_usual: float | None; status: Status; low_volume: bool
class LocationMetric(Metric): location: str; history_weeks: int
class Day(BaseModel): date: date; weekday: Literal["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]; total: int; usual: float | None
class WeeklyInsight(BaseModel): account: AccountRef; week: Week; baseline: Baseline; summary: Metric
                                days: list[Day]; locations: list[LocationMetric]; data_notes: list[str]
```
`Baseline.start` = the Monday of the oldest history week; `Baseline.end` = the Sunday of the newest; both None when there's no history.

### 3.5 Endpoints and errors
| Endpoint | Success | Errors (`{"detail": "<exact message>"}`) |
|---|---|---|
| `GET /health` | 200 `{"status":"ok","db":"ok"}` | 503 `{"status":"error","db":"error"}` when `ping` raises |
| `GET /accounts` | 200 `list[AccountSummary]` | — |
| `GET /accounts/{account_id}/weekly-insight?week_start=YYYY-MM-DD` | 200 `WeeklyInsight` | 404 `Account {id} not found` · 422 `week_start must be a Monday` · 422 `week_start is before the first complete week ({date})` · 422 `week_start is not complete yet; the latest complete week is {date}` |

Account without events: 200 with `summary.total = 0`, status `not_enough_history`, `locations = []`, 7 days with `total = 0` and `usual = null`, `baseline.weeks_used = 0`.

### 3.6 Test harness (built in Task 1, used by every backend test)
- `conftest.py`:
  - `db_url(tmp_path)` → `sqlite:///{tmp_path}/test.db`
  - `engine` runs `alembic.command.upgrade(Config("alembic.ini"), "head")` with `DATABASE_URL` monkeypatched, then yields `make_engine(db_url)`
  - `conn` is a connection whose writes are committed
  - `client` is `TestClient(create_app(Settings(database_url=db_url, as_of_date=date(2026, 7, 28), cors_origins=[])))`

  With that `as_of_date`, the latest complete week is **2026-07-20** and the 8 baseline weeks are **2026-05-25 … 2026-07-13**.
- `factories.py`:
  - `add_account(conn, id, name="Test Co", tz="America/Chicago", industry="Test")`
  - `add_weekly(conn, account_id, location, tz, counts: dict[date, int])` places `count` events in each local week, on **Monday** from 12:00 local, one minute apart. Monday matters: the earliest fake event sets the test dataset's `first_complete_week`, so a non-Monday first event would silently drop the oldest history week
  - `add_event(conn, account_id, location, local_dt: datetime, tz, event_type="call_received", outcome=None, duration=None)`
  - `weeks_before(week: date, values: list[int]) -> dict[date, int]` maps `values` to the consecutive weeks ending the week before `week`

  Ids come from a module-level counter starting at 1_000_000.
- Fake account ids: 101+. Tests never use the seed except the `slow` seed tests, which call `load_seed(engine, Path("../data/seed.sql"))`.

### 3.7 Frontend layout and UI rules
```
frontend/
  .nvmrc  package.json  vite.config.ts  tsconfig.json  eslint.config.js  index.html
  src/
    main.tsx  App.tsx  styles.css
    api/schema.d.ts         # generated: npm run gen:api (openapi-typescript ../openapi.json)
    api/types.ts            # aliases: Account, WeeklyInsight, Metric, LocationMetric, Day, Status
    api/client.ts           # getAccounts(), getWeeklyInsight(accountId, weekStart?) with fetch + AbortSignal; throws ApiError(status, detail)
    hooks/useAccounts.ts  hooks/useWeeklyInsight.ts   # {data, error, loading, reload}
    format.ts               # formatPct, formatNumber, weekLabel, tzAbbreviation, addDays
    components/AccountPicker.tsx  WeekPicker.tsx  VerdictCard.tsx  DailyChart.tsx
               LocationsTable.tsx  DataNotes.tsx  StatusBadge.tsx  StateMessage.tsx
    test/setup.ts  test/server.ts (MSW)  test/fixtures.ts
```
- API base URL: `import.meta.env.VITE_API_URL ?? "http://localhost:8000"`.
- **State lives only in React state:** the selected account (default = the first account from `/accounts`) and `weekStart` (default = that account's `latest_complete_week`). Changing account resets the week. ◀ = −7 days; ▶ = +7 days, disabled at `latest_complete_week`.
- **Formats:**
  - `formatPct(-0.32)` → `"−32%"` (U+2212), `formatPct(0.05)` → `"+5%"`, `null` → `"—"`
  - usual shown as `~76`; range `64–88` (rounded integers)
  - week label `"Jul 20 – Jul 26, 2026"` via `Intl.DateTimeFormat("en-US")`
  - timezone abbreviation via `Intl.DateTimeFormat("en-US", {timeZone, timeZoneName: "short"})`

  API dates are `YYYY-MM-DD` strings, so the date math uses UTC to avoid local-time shifts.
- **StatusBadge** (icon + text, never colour alone): lower `▼ Lower than usual` (`--color-lower: #b42318`), higher `▲ Higher than usual` (`--color-higher: #1d4ed8`), normal `● Normal` (`--color-normal: #15803d`), not_enough_history `○ Not enough history` (`--color-muted: #6b7280`).
- **Copy (exact):**
  - not enough history: `Not enough history yet — at least 4 complete weeks are needed to tell what's normal.`
  - account low volume: `This account has low weekly volume, so results may be unreliable.`
  - row low volume: a `Low volume` tag with `title="Low weekly volume: results may be unreliable."`
  - no locations: `No locations with activity yet.`
  - error: `Couldn't load data.` + a `Retry` button
  - loading: `Loading…`
- Single-location accounts show the table with one row. The table keeps the API order (no client-side sorting).
- DailyChart: Recharts `ComposedChart` with a `Bar` for `total` and a `Line` with dots only (no stroke) for `usual`. X labels Mon…Sun.
- Plain CSS in `styles.css` with CSS variables, a single column with max-width 960px.

---

## 4. Test scenarios (expected values)

Backend scenarios run through the API (`client`) on SQLite with fake accounts. All of them use location `Main` and timezone `America/Chicago` unless stated otherwise, and evaluate week **2026-07-20** with history `weeks_before(2026-07-20, [...])` (8 weeks, oldest first).

**Required (from the first-iteration plan):**
| Id | Setup | Expected |
|---|---|---|
| S1 | Account 101 with no events | 200; `summary.status = not_enough_history`, `total = 0`, `locations = []`, 7 days with `total = 0` and `usual = null`, `baseline.weeks_used = 0` |
| S2 | Account 102: history `[20,22,18,21,19,20,23,17]`, week = 21 | usual 20.0, lower 8.8, upper 31.2, pct 0.05, `normal`, `low_volume = false` |
| S3a | Account 103: the same history, week = 5 | `lower_than_usual`, pct −0.75 |
| S3b | Account 104: the same history, week = 40 | `higher_than_usual`, pct 1.0 |
| S4 | Account 105: locations North, South, East, West, each with history `[20]*8`; week: North 20, South 8, East 4, West 35 | Locations ordered **East (lower, −0.8), South (lower, −0.6), North (normal), West (higher)**; account total 67 vs usual 80 → summary **`normal`** (lower bound 57.6). The account looks fine, but two locations need attention. |

**Boundaries and math edges:**
| Id | Setup | Expected |
|---|---|---|
| B1 | 3 weeks of history `[20,20,20]` (series starts 3 weeks before), week = 5 | `not_enough_history`, `history_weeks = 3`, usual null |
| B2 | 5 weeks of history `[20]*5`, week = 5 | evaluated: `lower_than_usual`, `baseline.weeks_used = 5` |
| B3 | 1 event 9 weeks before, history 8 × 0; week = 3 | usual 0.0, `pct_vs_usual = null`, `higher_than_usual` |
| B4 | Same as B3, week = 2 | `normal` (outside the band [0, 0] but diff < 3) |
| B5 | history `[5]*8`, week = 0 | `normal`, lower 0.0, `low_volume = true` |
| B6 | history `[200]*8`, week = 236 | `normal` (above upper 235.4 but +18% < 20%) |
| B7 | history `[200]*8`, week = 241 | `higher_than_usual` |
| B8 | history `[1,1,1,1,0,0,0,0]`, week = 3 | `normal` (usual 0.5, upper 2.4, diff 2.5 < 3) |

**Robustness and data quirks:**
| Id | Setup | Expected |
|---|---|---|
| R1 | history `[20,20,20,300,20,20,20,20]`, week = 20; and a second account with the same history and week = 5 | `normal` (usual 20, the band isn't inflated); the second → `lower_than_usual` |
| R2 | history `[20]*8`, week = 20 plus 1 exact duplicate of one of the week's events | `total = 20`; data note `"1 duplicate event removed from this week."` |
| R3 | Location Old with history `[20]*8` and week = 20; location New with only the last 2 weeks of history `[5,5]` and week = 5 | New: `not_enough_history`, `history_weeks = 2`, ranked last; summary is evaluated (not `not_enough_history`) |
| R4 | Chicago account, events at local Mon 2026-07-13 12:00 (anchor), Sun 2026-07-19 23:59, Mon 2026-07-20 00:30, Sun 2026-07-26 23:30 (= Mon UTC) | Week 2026-07-20: `days[0].total = 1`, `days[6].total = 1`, `summary.total = 2`; the 07-19 event is in week 2026-07-13 |
| R5 | DST: an event at local Mon 2026-03-02 12:00 and one at local Sun 2026-03-08 23:30 (America/Chicago), `week_start=2026-03-02` | Both count in week 2026-03-02: `days[0].total = 1`, `days[6].total = 1` |
| R6 | `America/Phoenix` account, events at local Mon 2026-07-20 12:00 and Sun 2026-07-26 23:30 | Both in week 2026-07-20; `days[6].total = 1` (UTC −7 all year) |
| R7 | `UTC` account with any history | The UTC data note is present; a Chicago account doesn't have it |

**API validation and errors:**
| Id | Request | Expected |
|---|---|---|
| V1 | `week_start=2026-07-21` | 422 `week_start must be a Monday` |
| V2 | `week_start=2026-07-27` | 422 `week_start is not complete yet; the latest complete week is 2026-07-20` |
| V3 | S2-style data (first complete week 2026-05-25), `week_start=2026-05-18` | 422 `week_start is before the first complete week (2026-05-25)` |
| V4 | Account 999 | 404 `Account 999 not found` |
| V5 | No `week_start` | `week.start = 2026-07-20`, `week.end = 2026-07-26` |
| V6 | Any account | `days` has 7 items, Mon…Sun, zero-filled |
| V7 | `/health` with a broken DB (dependency override that raises) | 503 `{"status":"error","db":"error"}` |
| V8 | `/accounts` | Ordered by name; `location_count` and `latest_complete_week` correct; an account with no events has `location_count = 0` |

**Seed golden tests** (`@pytest.mark.slow`, real seed on SQLite, `as_of_date = None`):
| Id | Expected |
|---|---|
| G1 | The clean view has 12,614 rows; the raw table has 12,626 |
| G2 | Account 6, default week → `week.start = 2026-07-20` |
| G3 | Account 6, week 2026-06-01: total 880, usual 66.0, band 27.1–104.9, `higher_than_usual`; all 15 locations `higher_than_usual`; Site A total 49, usual 4.5 |
| G4 | Account 6, week 2026-06-08: total 102, `normal` (the weeks after the spike aren't distorted) |
| G5 | Account 2, week 2026-07-06: total 18, usual 32.5, `lower_than_usual` |
| G6 | Account 15, week 2026-06-01: `higher_than_usual` |
| G7 | Account 20: `not_enough_history`, `locations = []` |
| G8 | Account 18: has the UTC note. Account 1, week 2026-02-02: `not_enough_history` |

**Frontend scenarios** (Vitest + Testing Library rendering `<App />`; HTTP mocked with MSW; fixtures in `src/test/fixtures.ts` typed with `satisfies` against `api/types.ts`, mirroring S1–S4 and the states below):
| Id | Expected |
|---|---|
| F1 (S1) | Account without events: the not-enough-history copy, `No locations with activity yet.`, a chart with 7 zero bars |
| F2 (S2) | `● Normal`, `21 events · usual ~20 (range 9–31) · +5%` |
| F3 (S3) | `▼ Lower than usual` with −75%; `▲ Higher than usual` with +100% |
| F4 (S4) | Account `● Normal`; table rows in API order East, South, North, West with their badges |
| F5 | Low volume: the account warning and a row `Low volume` tag |
| F6 | Data notes: the duplicate and UTC notes rendered as given |
| F7 | Single-location account: a table with one row |
| F8 | Week navigation: ◀ requests `week_start` −7 days; ▶ disabled at the latest week; changing account resets the week |
| F9 | API error → `Couldn't load data.`; `Retry` refetches; `Loading…` while pending |
| F10 | A `not_enough_history` location row shows `—` for usual and % |

---

## 5. Tasks

### Task 0 — Foundation (orchestrator + human) → PR
**Goal:** get the existing foundation onto GitHub through a PR.
**Scope:**
- Human: create an empty GitHub repo with your own name (not a fork, not `relay-analytics-starter`) and add it as `origin`.
- Orchestrator: commit `.gitignore` alone on `main` and push. Then, on branch `task/0-foundation`, commit the rest (compose, migration 0001, seed, scripts, analysis, docs, `.claude/agents/`, CLAUDE.md pointing to this plan) and open a PR. The seed is excluded from the line count. If the docs push the PR over 700 lines, stack them: infra in `0a`, docs in `0b`.

**Tests:** none (no app code).
**Quickstart:**
```bash
docker compose down -v && docker compose up -d --wait && ./scripts/load_seed.sh   # accounts=20, activity_events=12626
```

### Task 1 — API skeleton, clean view, health, test harness (`api-builder`) · ~400 lines
**Goal:** a runnable FastAPI app and the test harness every later task uses.
**Scope:** `pyproject.toml`, `config.py`, `db.py`, `main.py` (with CORS), `routes.py` with `/health` only, migration 0002 (3.3), `requirements-dev.txt`, `tests/conftest.py` + `tests/factories.py` exactly as in 3.6. Update the CLAUDE.md commands: run, lint, test, single test, fast tests (`-m "not slow"`).
**Tests (integration):**
- `/health` → 200 ok
- the view on SQLite: 2 identical rows + 1 different → the view returns 2, keeping the lowest id
- the same, with a NULL outcome in the identical pair
- the factories create the expected local weeks (one check)

**Quickstart:**
```bash
cd backend && .venv/bin/pip install -r requirements-dev.txt     # or: uv pip install --python .venv/bin/python -r requirements-dev.txt
.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/pytest -q
.venv/bin/alembic upgrade head
docker compose exec -T db psql -U relay -d relay -tAc "select count(*) from clean_activity_events"   # 12614
.venv/bin/uvicorn app.main:app --port 8000 & sleep 2; curl -s localhost:8000/health; kill %1         # {"status":"ok","db":"ok"}
```

### Task 2 — Domain logic (`api-builder`) · ~450 lines
**Goal:** all the "is it normal?" logic as pure functions (3.4, section 2 rules). No DB, no FastAPI.
**Scope:** `domain/weeks.py`, `domain/detection.py`, `domain/ranking.py`.
**Tests (unit, `tests/unit/`, kept small, since the scenario tasks cover behavior end to end):**
- `evaluate` on S2's numbers (usual 20, lower 8.82, upper 31.18)
- history < 4 / = 4
- usual = 0
- `first_complete_week` / `latest_complete_week` on a Monday and a Sunday
- `local_date` across the 2026-03-08 DST switch
- ranking order with ties

**Quickstart:**
```bash
cd backend && .venv/bin/ruff check . && .venv/bin/pytest -q tests/unit
```

### Task 3 — Repository, schemas, seed loader, `GET /accounts` (`api-builder`) · ~400 lines
**Goal:** read from the clean view and serve the account picker.
**Scope:** `repository.py` (3.3), `schemas.py` (all models, 3.4), `seed.py` (SQLite: `sqlite3` `executescript`; Postgres: the raw psycopg cursor executes the whole file; one transaction; returns False if `accounts` has rows), `service.list_accounts`, the `/accounts` route.
**Tests (integration):**
- V8
- `load_seed` on SQLite → 20 accounts and 12,626 events, and a second call returns False (`slow`)

**Quickstart:**
```bash
cd backend && .venv/bin/ruff check . && .venv/bin/pytest -q
.venv/bin/uvicorn app.main:app --port 8000 & sleep 2
curl -s localhost:8000/accounts | python3 -m json.tool | head -12; kill %1    # 20 accounts by name; Quiet Harbor Spa location_count 0
```

### Task 4 — `GET /accounts/{id}/weekly-insight` (`api-builder`) · ~450 lines
**Goal:** the dashboard endpoint, exactly as in 3.4/3.5.
**Scope:** `service.build_weekly_insight` (bounds → as-of → validation → bucketing → evaluate the account and each location → weekday usuals → ranking → notes → rounding), the route.
**Tests (integration, only the minimum here; tasks 6–7 cover the catalog):** S2, V4, V5.
**Quickstart:**
```bash
cd backend && .venv/bin/ruff check . && .venv/bin/pytest -q
.venv/bin/uvicorn app.main:app --port 8000 & sleep 2
curl -s "localhost:8000/accounts/6/weekly-insight?week_start=2026-06-01" | python3 -m json.tool | head -30   # total 880, higher_than_usual
curl -s -o /dev/null -w "%{http_code}\n" "localhost:8000/accounts/6/weekly-insight?week_start=2026-06-02"     # 422
kill %1
```

### Task 5 — API container + exported contract (`api-builder`) · ~200 lines
**Goal:** `docker compose up` starts db + api, and the frontend gets a committed contract.
**Scope:**
- `backend/Dockerfile`: `python:3.13-slim` pinned to an exact patch tag; build context = repo root so `data/seed.sql` is copied in.
- `backend/docker-entrypoint.sh`: `alembic upgrade head` → `python -m app.seed` (loads if empty) → `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- Compose service `api`: depends on `db` being healthy, `DATABASE_URL` pointing at `db:5432`, port 8000, and a healthcheck on `/health` (python urllib, not curl).
- `scripts/export_openapi.py` → `openapi.json` at the repo root (sorted keys, 2-space indent).
- Update the CLAUDE.md commands.

**Tests:** a test that compares the committed `openapi.json` with `create_app().openapi()` and fails if it's stale.
**Quickstart:**
```bash
docker compose down -v && docker compose up -d --build --wait
curl -s localhost:8000/health && curl -s localhost:8000/accounts | head -c 200
backend/.venv/bin/python scripts/export_openapi.py && git diff --exit-code openapi.json && echo "contract up to date"
```

### Task 6 — API scenario tests, part 1: S1–S4 + boundaries (`api-builder`) · ~450 lines
**Goal:** prove the required scenarios and the math edges through the API.
**Scope:** `tests/integration/test_scenarios_core.py` (S1–S4), `tests/integration/test_boundaries.py` (B1–B8). One test function per scenario id, named `test_<id>_<short_description>`, each asserting every expected value in section 4. App fixes only under the rule in section 1.
**Tests:** this task *is* tests.
**Quickstart:**
```bash
cd backend && .venv/bin/ruff check . && .venv/bin/pytest -q tests/integration/test_scenarios_core.py tests/integration/test_boundaries.py
.venv/bin/pytest -q tests/integration/test_scenarios_core.py::test_s4_locations_need_review     # single test
```

### Task 7 — API scenario tests, part 2: robustness, validation, seed golden (`api-builder`) · ~450 lines
**Goal:** prove the data-quirk handling, the errors, and parity with `Detection_tuning.md` on the real seed.
**Scope:** `tests/integration/test_robustness.py` (R1–R7), `tests/integration/test_validation.py` (V1–V7), `tests/integration/test_seed_golden.py` (G1–G8, `slow`; one module-scoped seeded engine). Same naming and fix rules as Task 6.
**Quickstart:**
```bash
cd backend && .venv/bin/ruff check . && .venv/bin/pytest -q                  # everything, including slow
.venv/bin/pytest -q -m "not slow"                                           # fast loop
```

### Task 8 — Frontend skeleton, API client, pickers (`frontend-builder`) · ~450 lines
**Goal:** the app loads accounts and a weekly insight, and account/week selection works.
**Scope:** the `frontend/` scaffold (3.7), `npm run gen:api` → `schema.d.ts`, `types.ts`, `client.ts`, both hooks, `format.ts`, `AccountPicker`, `WeekPicker`, `StateMessage`, `App.tsx` (pickers + loading/error; the insight body shows the total and status as plain text for now), `test/setup.ts`, `test/server.ts`, `test/fixtures.ts` (an accounts list + an S2-shaped insight). Scripts: `dev`, `build`, `lint`, `test`, `gen:api`. Update the CLAUDE.md frontend commands.
**Tests (integration with MSW):**
- F8, F9
- `format.ts` unit cases: the pct sign and U+2212, null, week label, tz abbreviation

**Quickstart:**
```bash
cd frontend && npm ci && npm run gen:api && git diff --exit-code src/api/schema.d.ts
npm run lint && npm test -- --run && npm run build
```

### Task 9 — Verdict card, daily chart, data notes (`frontend-builder`) · ~400 lines
**Goal:** the top half of the wireframe.
**Scope:** `StatusBadge`, `VerdictCard` (status, `N events · usual ~X (range a–b) · ±P%`, `vs. previous {weeks_used} weeks`, the not-enough-history copy, the account low-volume warning), `DailyChart`, `DataNotes`; wire them into `App.tsx`. Fixtures for S1, S3a, S3b, low volume, and the notes.
**Tests (integration with MSW):** F1 (card and chart part), F2, F3, F5 (account part), F6.
**Quickstart:**
```bash
cd frontend && npm run lint && npm test -- --run && npm run build
```

### Task 10 — Ranked locations table (`frontend-builder`) · ~300 lines
**Goal:** the bottom half: which location needs attention.
**Scope:** `LocationsTable` (Location · This week · Usual · vs usual · Status; the `Low volume` tag; `—` for nulls; the empty state), the `Locations ({n})  needs attention first` header, wired into `App.tsx`. Fixtures for S4, single location, and a not-enough-history row.
**Tests (integration with MSW):** F4, F5 (row part), F7, F10, F1 (empty table part).
**Quickstart:**
```bash
cd frontend && npm run lint && npm test -- --run && npm run build
```

### Task 11 — Frontend scenario pass + live check (`frontend-builder`) · ~250 lines
**Goal:** one end-to-end pass over F1–F10 against the full app, plus a manual check against the real API.
**Scope:** `src/test/scenarios.test.tsx`: one test per F id, rendering `<App />` and checking the full screen per scenario (tasks 8–10 tested pieces). Fix gaps under the rule in section 1. Manual check with `docker compose up` and `npm run dev`: account 6 week 2026-06-01 (▲ higher), account 20 (not enough history), account 18 (UTC note), account 8 (single location). Describe what you saw in the PR.
**Quickstart:**
```bash
cd frontend && npm run lint && npm test -- --run && npm run build
```

### Task 12 — Web container + one-command run (`frontend-builder`) · ~150 lines
**Goal:** a reviewer runs `docker compose up` and opens the dashboard.
**Scope:**
- `frontend/Dockerfile`: multi-stage, `node:22-alpine` (pinned patch tag) to build, then `nginx:1.27-alpine` (pinned) to serve; build arg `VITE_API_URL=http://localhost:8000`.
- Compose service `web` on port **8080**, depending on `api`.
- A root `README.md` "Run it" section: one command, the URLs, and a reset command.

**Tests:** none new; the Quickstart is the check.
**Quickstart:**
```bash
docker compose down -v && docker compose up -d --build --wait
curl -s -o /dev/null -w "%{http_code}\n" localhost:8080        # 200
curl -s localhost:8000/accounts | head -c 100
```

### Task 13 — Write-up (orchestrator + human) → PR
**Goal:** the submission README.
**Content:**
- problem and approach
- the definition of "normal" and why median + MAD (`Detection_tuning.md`)
- the data quirks and how each is handled (`Data_integrity.md`, `OPEN_QUESTIONS.md`)
- limitations: no seasonality, ~25 weeks of data, small counts, low-volume locations are rarely flagged lower, an empty "needs attention" list is common, SQLite tests vs Postgres
- production notes: rollup tables / medallion, dedupe at ingestion, Postgres tests in CI, auth, all-events-per-request
- out of scope
- how the work was done: spec-driven, Sonnet builder/reviewer agents, the Docker sandbox in bypass mode

**Quickstart:** the human reads the README on the PR.

---

## 6. Order

```
0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13
```
Backend tasks first: the frontend builds against the `openapi.json` produced in Task 5, and the backend scenario tests (6–7) run before any frontend work, so contract bugs are caught early.
