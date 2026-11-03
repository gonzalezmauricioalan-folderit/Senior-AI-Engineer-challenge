*Need to talk more in dept with claude code
# Check data integrity (Since it is real messy data)
- Spin up a Postgres database using Docker Compose. Implement the schema and run the seed to complete the data. 
- Check this (answer with the query used and the result). Create a Data_integrity.md with different sections (add a PASS or FAIL when possible)
	- Start of the data? range of data
	- Number of accounts? 
	- Accounts with no events?
	- Events with no accounts? 
	- select distinct for industry, timezone; event_type, outcome
	- There are events in the weekends? 
	- Locations with most events?
	- Events before account creation?
	- Events outside of the 7 am - 19 pm (use timezone)?
	- Suggest and run others checks (the init already found some data inconsitency) *
- *Act on bad data: The options that I see are:
1. To use a medallion approach with bronze, silver, and golden tables, but that seems like overengeniering
2. To use a view to fix or exclude some data.
- Check basic metrics 
# Define what is normal in this context
- Calculate values to help decide
	- Number of events in total?
	- average/median/standard deviation per account/location?
- What to use as baselaine
	- * 7 Previous days (without sunday or saturdays) or the previous 7 days (eg previous 7 mondays) or previous week in previous year. (do we have to take into account seasonality? ); Tell me pros an cons
- *How to identify if the week or day was a normal or require some attention (because it was higher or lower than the normal week)
- Average?
- Median?
- Standard Deviations?
- Other approachs? Pros and cons of each of them
---- From here lets use spec driven development ---- 
# Backend
- Select stack: fast api
- Migrations of the database
- Define the Open Api implementation
	- /get-insigth (account id, location, current week/day  | day/week)
	- /health
- Out of scope
	- Auth
	- rate limit
# Frontend
- Stack: React 
- Define wire frame of how the ui will look like:
	- select account, location. select previous week starting from now or a different day
	- total of the previous week
	- 

# Outside of scope
- A calendar input to enter days that will move the "normal" of an account/location like holidays or marketing campaigns


------

# Integration tests agains the API using sqlite and test_seed.py

- Add a temporary fake accounts
	- With no events
	- With normal week
	- With a week that had lower events

# Assumptions
- This dashboard will use complete days and not half a day or quarter of days
- The accounts use normal working days and hours

# Use of an LLM
- In this ticket in particular, we won't use an LLM because it won't add relevant value to explain why this day is not normal, for example, because it won't have the data to explain why the number is lower than expected
------

# Results of first iteration discussion

## 1. Additional data integrity checks (line 14) — DECIDED
Add to Data_integrity.md, on top of the original list:
- **Duplicates**: exact duplicates (same account + location + event_type + occurred_at, different id; the init profile found ~12 groups) and near-duplicates (same key within a few seconds).
- **Field consistency**: outcome valid for its event_type, NULL outcome rate per type, duration only on calls, NULL/zero/negative/outlier durations, casing/whitespace in location and enum values.
- **Coverage gaps & spikes**: per account/location, days or weeks with zero events, locations starting or stopping mid-range, sudden spikes (account 6 around 2026-06-03), partial first/last week.
- **Time & timezone sanity**: valid IANA timezones, no future timestamps, events near DST switches, how many events change day/week after UTC → local conversion.

## 2. Act on bad data (line 15) — PARTIALLY DECIDED
- **Mechanism: DECIDED.** Raw tables (`accounts`, `activity_events`) stay untouched (the seed is used as-is). A plain, portable SQL view (`clean_activity_events`) applies the cleaning rules, so it behaves the same on Postgres and on SQLite in tests. UTC → account-local day/week bucketing is done in Python (`zoneinfo`), because SQLite has no IANA timezone support.
  - Pros: cleaning rules readable in one place, portable, easy to unit-test (DST, America/Phoenix, UTC).
  - Cons: re-aggregates per request (fine for ~12.6k rows); logic split between SQL and Python.
  - **Production note for write-up:** a medallion-style approach (or a daily rollup per account/location/local date, refreshed incrementally) would be preferred at real volume; it's overengineering for this challenge.
- **Policy: DEFERRED to next iteration**, after running the integrity queries. De-duplication is certain (production note: prevent at ingestion with an idempotency key / unique constraint). Other rules will be defined on the view based on the check results.

## 3. Baseline (line 24) — PARTIALLY DECIDED
- **Year-over-year / seasonality: NOT POSSIBLE.** Events only span 2026-02-01 → 2026-07-27 (~26 weeks), so seasonality isn't handled. Document it as a limitation (would need ≥ 1 year of history).
- **Comparison type: DEFERRED to next iteration** (depends on weekend/business-hours checks; some accounts may work Saturdays). Candidates:
  - A. Trailing N complete local weeks (Mon–Sun): answers "was last week normal?", smooths noise, includes weekends naturally; can't answer per-day questions, slow to adapt to level shifts.
  - B. Same weekday over previous N weeks: right for a daily view, handles weekends; noisy for small accounts, sensitive to holidays.
  - C. Previous N weekdays excluding Sat/Sun: simple, but assumes Mon–Fri businesses and mixes weekdays.
- **Window length N: DEFERRED**; decide after looking at weekly variance (candidates 4 / 8 / 12 weeks).
- **Minimum history: DECIDED, 4 complete weeks.** Below that, show totals with "not enough history yet" instead of a verdict (covers account 20 with no events and new locations).
- Default period (proposal): the last complete week in the account's local time, not the current partial week.

## 4. How to flag normal vs needs attention (lines 25–29) — PARTIALLY DECIDED
- **Method: DEFERRED.** In the next iteration, run 2–3 methods on the seed and pick the one with the most sensible flags. Candidates:
  - Mean ± k·std: familiar, but one spike week inflates mean and std.
  - Median ± k·MAD: robust to outlier weeks; MAD can be 0 for sparse/stable series, so it needs a floor.
  - Percent change vs median: easiest for customers to read; ignores natural variability (3 → 2 calls = −33%).
  - Percentile / min–max range: intuitive, but coarse with small N.
  - Poisson/count-based test: statistically right for small counts, hard to explain, close to the out-of-scope ML/forecasting line.
  - Proposal to evaluate: median ± k·MAD **and** a minimum % and absolute difference floor; show customers "% vs usual".
- Output states (proposal): Normal / Higher than usual / Lower than usual / Not enough history.
- **Metric: DECIDED, total events**, for simplicity. Write-up note: in a real project, ask product which metric adds the most value (per event type, or outcome rates like missed-call / no-show / conversion). The data volume per account/location is probably too small to split by event type reliably.
- **Multi-location: DECIDED.** Account-level verdict on top, then a table of locations ranked "needs attention" first, each location compared to its own baseline. This answers support's "which location needs attention?"

## Next iteration
1. Docker Compose Postgres + migrations + seed load.
2. Run all integrity checks → Data_integrity.md (query + result + PASS/FAIL).
3. Decide the cleaning policy for the view.
4. Decide the baseline comparison type and N from weekend/weekly-variance data.
5. Compare detection methods on the seed and pick one.
6. Then write PLAN.md and continue with spec-driven development (backend/frontend).

# Results of second iteration (after Data_integrity.md)

## Baseline comparison type — DECIDED
- **Weekly verdict, Mon–Sun in the account's local time**, vs. the previous N complete weeks, for the account and for each ranked location.
- **Daily context without verdicts:** the UI shows the week's 7 days next to each weekday's usual value (median of that weekday over the same N weeks), with no daily flags.
- Why: per location, an average weekday has 1.32 events (median 1, 31.6% of days with zero) and a weekend day 0.33–0.34 (median 0, ~71% zero). A same-weekday MAD would be 0–1, so daily flags would be noise. Sat ≈ Sun, so excluding only Sunday (Mon–Sat) has no justification. Every week contains exactly one Sat and one Sun, so low weekends don't bias weekly comparisons; they stay included, and the write-up says so.
- Out of scope: daily verdicts. Real-project note: ask product whether daily/weekday views matter once accounts have more volume.
- Questions and assumptions raised by the data checks: see `OPEN_QUESTIONS.md`.

## Cleaning policy — DECIDED
- The `clean_activity_events` view only **removes the 12 exact duplicate events** (same account_id, location, event_type, occurred_at and all other columns; keep the lowest id).
- Everything else is kept: NULL outcome/duration, events before 07:00 / after 19:00, weekend events, and the account 6 spike (2026-06-03). Reasons are in `OPEN_QUESTIONS.md`.
- Production note: prevent duplicates at ingestion (idempotency key / unique constraint).

## API — DECIDED (draft; detection fields filled once the method is chosen)
One aggregate endpoint per screen; location ranking is done on the server.
```yaml
GET /health                      → 200 {status: "ok", db: "ok"}
GET /accounts                    → 200 [AccountSummary]
  AccountSummary: {id, name, industry, timezone, location_count, first_week, latest_complete_week}
GET /accounts/{account_id}/weekly-insight?week_start=YYYY-MM-DD
  week_start: optional, a Monday in account-local time; default = latest complete week (as-of rule TBD)
  200 WeeklyInsight · 404 unknown account · 422 week_start not a Monday / outside data range
WeeklyInsight:
  account:   {id, name, timezone}
  week:      {start, end, is_complete}
  baseline:  {method, weeks_used, from, to}
  summary:   Metric                                  # whole account (its own weekly total)
  days:      [{date, weekday, total, usual}]         # 7 rows, context only, no status
  locations: [Metric & {location, history_weeks}]    # sorted: needs attention first
  data_notes:[string]                                # e.g. duplicates removed, UTC timezone warning
Metric: {total, usual, lower, upper, pct_vs_usual,
         status: normal | lower_than_usual | higher_than_usual | not_enough_history}
```
- Location names (with spaces) stay in the payload, not the URL; no per-location endpoint.

## Wireframe — DECIDED (layout A: verdict + ranked table; numbers illustrative)
```
┌ Relay · Weekly activity ─────────────────────┐
│ Account [Metro Collision Centers ▾]          │
│ Week    [◀ Jul 20 – Jul 26, 2026 ▶]  (ET)    │
├──────────────────────────────────────────────┤
│ ▼ LOWER THAN USUAL                           │
│ 52 events · usual ~76 (range 64–88) · −32%   │
│ vs. previous 8 weeks                         │
├──────────────────────────────────────────────┤
│ This week by day   █ actual  · usual         │
│  █·  █·  ▄·  █·  ▄·  ▁·  ▁·                  │
│  Mo  Tu  We  Th  Fr  Sa  Su                  │
├──────────────────────────────────────────────┤
│ Locations (15)          needs attention first│
│ Location  This wk  Usual  vs usual  Status   │
│ Site C        1      5     −80%    ▼ Lower   │
│ Site K        2      6     −67%    ▼ Lower   │
│ Site N       11      5    +120%    ▲ Higher  │
│ Site A        5      5      0%     Normal    │
│ …                                            │
├──────────────────────────────────────────────┤
│ ⓘ 2 duplicate events removed                 │
└──────────────────────────────────────────────┘
```
- The 7-day chart is account-level only; location rows aren't clickable (no drill-down).
- States still to draw: not enough history (e.g. account 20), account with a single location, timezone warning.

## Detection method — DECIDED (parameters pending tuning)
- **Median ± k·spread** over the previous N complete weeks, with `spread = max(1.4826·MAD, √median)`; the lower bound is clamped at 0.
- Flag only if the week is outside the band **and** differs from the median by at least a minimum number of events and a minimum percent.
- Why MAD: the account 6 spike moves its weekly std from 13 to 162 but its median from 76 to 74. Why the floors: location medians are 4–11/week (21 locations ≤ 5), MAD is often 0–3, and a pure MAD band would flag ordinary noise.
- k, N and the floor values are tuned on the seed (see `Detection_tuning.md`).

## As-of date — DECIDED
- Default week = the **latest complete local week that has data** (Jul 20–26, 2026). `week_start` picks other weeks. An optional `AS_OF_DATE` env var overrides "today" to simulate production behavior. Partial weeks never get a verdict.

## Ranking — DECIDED
- **Only `lower_than_usual` counts as "needs attention"**, ranked first by biggest % drop.
- `higher_than_usual` is still shown with its ▲ status but not prioritized. It sorts with `normal` (by location name); `not_enough_history` goes last.

## Test strategy — DECIDED
- Integration tests run against **SQLite**. This works because the dedupe view is portable and the timezone logic lives in Python. Detection math gets pure unit tests with no DB.
- Write-up note: the tests don't run on the engine we ship (Postgres); in a real project, add a Postgres test run in CI.

## Detection parameters — DECIDED (evidence in `Detection_tuning.md`)
- **k = 2.5, N = 8 weeks, min_abs = 3 events, min_pct = 20%**: one setting for the account and location levels.
- Flag rates on the seed: account 3.0% (0.8% lower, 2.3% higher); location 2.6% (1.5% without account 6's spike week). The spike week is flagged at the account level and at all 15 locations; the weeks after it stay normal.
- The floors don't change any verdict on this seed (√median already covers it); they're kept as a guard for other data.
- **Low-volume warning (plan + UI):** small accounts/locations (usual ≤ ~6 events/week) can get odd results. Their weekly swings are mostly random, they're flagged ~3.5× more often than larger sites, and they can't be flagged lower (the lower bound is 0). The UI shows a "low volume, results may be unreliable" note on those rows, and the account card shows it when the account itself is low-volume.
- Ranking stays as decided: lower_than_usual first, then the rest by location name. With 0.1% of location weeks flagged lower, the ranking usually has nothing to prioritize; that's accepted and stated in the write-up.
