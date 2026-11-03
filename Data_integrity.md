# Data integrity report

Integrity checks on the seed data (`accounts`, `activity_events`) for DASH-247 ("is this week's activity normal for us?"). The report is descriptive only. The cleaning policy will be decided in the next iteration. The last section lists the candidate rules, with no decision taken.

**How it was produced**
- Database: the Postgres 16 container from `docker-compose.yml`, loaded through the project's migrations plus `data/seed.sql`, unmodified.
- Every query ran read-only (`default_transaction_read_only=on`). The SQL shown is the exact SQL that ran. To reproduce a query, run `docker compose exec -T db psql -U relay -d relay` and paste it in.
- Run date: 2026-11-03.

**Conventions**
- `occurred_at` and `created_at` are UTC, stored as `timestamp without time zone`. Local time is `(occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone`.
- A week runs Monday to Sunday in the account's local time (`date_trunc('week', local_ts)`).
- A "complete week" is one of the 25 local weeks starting 2026-02-02 through 2026-07-20 (see check 1). Weekly statistics use only complete weeks.
- Status: **PASS** means the data meets the expectation. **FAIL** means it doesn't, and some rule or handling is needed. **INFO** means there is no right or wrong answer; the result feeds a design decision.

## Summary

| # | Check | Status | Finding |
|---|---|---|---|
| 1 | Data range | INFO | 2026-02-01 10:57 UTC to 2026-07-27 22:20 UTC. Every timezone has **25 complete local weeks** (weeks of 2026-02-02 to 2026-07-20). The first and last weeks have one day each. |
| 2 | Number of accounts | PASS | 20 accounts, with unique ids and names. |
| 3 | Accounts with no events | INFO | 1 account: #20 Quiet Harbor Spa. It needs an empty-history state. |
| 4 | Orphan events | PASS | 0 events without an account. |
| 5 | Distinct values | PASS | 8 industries, 6 timezones, 3 event types, 7 outcomes. All are in the expected domains. NULL outcome is the only extra value. |
| 6 | Weekend events | INFO | 9.2% of events fall on local Sat/Sun (account range 2.4% to 11.5%). Saturday and Sunday are about equal. No account has zero weekend activity. |
| 7 | Locations | INFO | 69 locations (1 to 15 per account), with 106 to 261 events each. Volume per location is small and fairly even. |
| 8 | Events before account `created_at` | PASS | 0. The earliest event comes 60 days after its account was created. |
| 9 | Outside 07:00–19:00 local | INFO | 20.5% overall, almost all before 07:00. Western timezones are at 29–31%. The local-hour profile shifts with the timezone (seed artefact). |
| 10a | Exact duplicates | FAIL | 12 pairs (24 rows, 12 surplus). Every column except `id` matches, and the ids are consecutive. |
| 10b | Near-duplicates | INFO | 2 pairs within 1–5 s and 25 within 6–60 s. None of the ≤5 s pairs match on duration and outcome. Most are inside account 6's spike. |
| 11a | Outcome valid for event type | PASS | 0 invalid combinations and 0 unknown event types. |
| 11b | NULL outcome | FAIL | 398 rows (3.1–3.3% of each type). |
| 11c | Duration only on calls | PASS | Leads and appointments never have a duration. |
| 11d | Call duration values | FAIL | 313 calls (4.0%) have NULL duration. None are zero, negative or extreme (range 20–1500 s). |
| 11e | Missed calls with duration | INFO | `missed` calls have durations similar to `connected` ones (median 711 s). This is semantically odd, but the dashboard metric doesn't use it. |
| 11f | Casing, whitespace, empty strings | PASS | 0 issues. Every location matches `^Site [A-Z]$`. |
| 12a | Zero-event weeks | PASS / INFO | 0 zero weeks at account level (except #20). At location level: 4 zero weeks across 3 locations out of 1,725 location-weeks. |
| 12b | Locations starting or stopping mid-range | PASS | None. Every location is active from the first week to the last. |
| 12c | Spikes | FAIL | Account 6, **Wed 2026-06-03: 805 events in one day** (normal is about 13/day). It covers all 15 sites and all 3 types. Its week is 11.6× the median. No other account goes above 1.65× its weekly median. |
| 12d | Partial first and last week | INFO | Week of 2026-01-26: 18 events (Sun 02-01 only). Week of 2026-07-27: 79 events (Mon 07-27 only). |
| 13a | Valid IANA timezones | PASS | All 6 are in `pg_timezone_names`. Offsets are as expected, and Phoenix stays at −07:00. |
| 13b | Future timestamps | PASS / INFO | 0 after `now()`. The last event is **99 days** before today, so "this week" by the wall clock has no data. |
| 13c | Events near DST switches | INFO | 131 events within ±1 day of 2026-03-08 and 0 in the skipped 02:00–03:00 hour. 2026-11-01 is outside the data range. |
| 13d | UTC vs local day and week | INFO | 67 events (0.53%) move to a different date and 8 (0.06%) to a different week after conversion. |
| 14 | Inputs for baseline decisions | INFO | Weekly CV is 0.16–0.32 per account. Location medians are only 4–11 events/week, so noise there is about Poisson. The spike inflates account 6's mean and std (std 162 → 13). No meaningful trend. |

---

## 1. Data range

**Overall**

```sql
SELECT min(occurred_at) AS min_utc, max(occurred_at) AS max_utc, count(*) AS events
FROM activity_events;
```

| min_utc | max_utc | events |
|---|---|---|
| 2026-02-01 10:57:44 | 2026-07-27 22:20:34 | 12626 |

**Per account (UTC and local)**

```sql
SELECT a.id, a.name, a.timezone, count(e.id) AS events,
       min(e.occurred_at) AS first_utc, max(e.occurred_at) AS last_utc,
       min((e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone) AS first_local,
       max((e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone) AS last_local
FROM accounts a
LEFT JOIN activity_events e ON e.account_id = a.id
GROUP BY a.id ORDER BY a.id;
```

| id | name | timezone | events | first_utc | last_utc | first_local | last_local |
|---|---|---|---|---|---|---|---|
| 1 | Summit Auto Group | America/Chicago | 1223 | 2026-02-01 16:39:22 | 2026-07-27 20:27:47 | 2026-02-01 10:39:22 | 2026-07-27 15:27:47 |
| 2 | Harbor Dental Partners | America/New_York | 730 | 2026-02-02 07:57:45 | 2026-07-26 20:04:27 | 2026-02-02 02:57:45 | 2026-07-26 16:04:27 |
| 3 | Bluebird HVAC | America/Denver | 477 | 2026-02-02 10:42:23 | 2026-07-27 20:23:21 | 2026-02-02 03:42:23 | 2026-07-27 14:23:21 |
| 4 | Cornerstone Vet Clinics | America/Chicago | 797 | 2026-02-01 17:30:53 | 2026-07-27 19:07:29 | 2026-02-01 11:30:53 | 2026-07-27 14:07:29 |
| 5 | Pacific Smiles | America/Los_Angeles | 884 | 2026-02-01 10:57:44 | 2026-07-27 20:18:43 | 2026-02-01 02:57:44 | 2026-07-27 13:18:43 |
| 6 | Metro Collision Centers | America/New_York | 2641 | 2026-02-01 12:06:40 | 2026-07-27 19:15:33 | 2026-02-01 07:06:40 | 2026-07-27 15:15:33 |
| 7 | Desert Springs Plumbing | America/Phoenix | 437 | 2026-02-01 11:42:04 | 2026-07-27 14:58:39 | 2026-02-01 04:42:04 | 2026-07-27 07:58:39 |
| 8 | Lakeside Physio | America/Chicago | 261 | 2026-02-02 13:24:27 | 2026-07-24 17:30:25 | 2026-02-02 07:24:27 | 2026-07-24 12:30:25 |
| 9 | Ironwood Fitness | America/Denver | 546 | 2026-02-02 09:56:42 | 2026-07-27 21:34:36 | 2026-02-02 02:56:42 | 2026-07-27 15:34:36 |
| 10 | Gulf Coast Roofing | America/Chicago | 342 | 2026-02-02 14:20:35 | 2026-07-27 22:20:34 | 2026-02-02 08:20:35 | 2026-07-27 17:20:34 |
| 11 | Northgate Optical | America/New_York | 354 | 2026-02-02 17:32:43 | 2026-07-27 15:04:06 | 2026-02-02 12:32:43 | 2026-07-27 11:04:06 |
| 12 | Redline Tire & Service | America/Los_Angeles | 1304 | 2026-02-01 12:18:24 | 2026-07-27 21:09:18 | 2026-02-01 04:18:24 | 2026-07-27 14:09:18 |
| 13 | Willow Creek Counseling | America/Chicago | 205 | 2026-02-02 10:40:44 | 2026-07-27 17:33:26 | 2026-02-02 04:40:44 | 2026-07-27 12:33:26 |
| 14 | Beacon Home Security | America/New_York | 638 | 2026-02-01 16:26:34 | 2026-07-27 20:50:26 | 2026-02-01 11:26:34 | 2026-07-27 16:50:26 |
| 15 | Sierra Pest Solutions | America/Phoenix | 499 | 2026-02-02 08:54:26 | 2026-07-27 17:42:39 | 2026-02-02 01:54:26 | 2026-07-27 10:42:39 |
| 16 | Old Town Barbers | America/Chicago | 167 | 2026-02-03 20:08:08 | 2026-07-27 16:28:51 | 2026-02-03 14:08:08 | 2026-07-27 11:28:51 |
| 17 | Evergreen Landscaping | America/Los_Angeles | 323 | 2026-02-03 12:34:28 | 2026-07-27 22:00:29 | 2026-02-03 04:34:28 | 2026-07-27 15:00:29 |
| 18 | Capital City Storage | UTC | 588 | 2026-02-01 13:55:16 | 2026-07-27 15:13:35 | 2026-02-01 13:55:16 | 2026-07-27 15:13:35 |
| 19 | Riverbend Chiropractic | America/New_York | 210 | 2026-02-02 17:17:48 | 2026-07-27 15:16:44 | 2026-02-02 12:17:48 | 2026-07-27 11:16:44 |
| 20 | Quiet Harbor Spa | America/Los_Angeles | 0 | NULL | NULL | NULL | NULL |

**Complete local weeks per timezone.** A week is complete when the whole Mon–Sun local week falls inside the dataset window.

```sql
-- Dataset window = [global min, global max] of occurred_at, seen in each account's local time.
-- A local Mon-Sun week is complete if it lies entirely inside that window.
WITH g AS (SELECT min(occurred_at) AS lo, max(occurred_at) AS hi FROM activity_events),
w AS (
  SELECT a.timezone,
         (g.lo AT TIME ZONE 'UTC') AT TIME ZONE a.timezone AS lo_local,
         (g.hi AT TIME ZONE 'UTC') AT TIME ZONE a.timezone AS hi_local
  FROM accounts a CROSS JOIN g GROUP BY a.timezone, g.lo, g.hi)
SELECT timezone, lo_local, hi_local,
       (date_trunc('week', lo_local) + interval '7 days')::date AS first_complete_wk,
       (date_trunc('week', hi_local) - interval '7 days')::date AS last_complete_wk,
       ((date_trunc('week', hi_local)::date - date_trunc('week', lo_local)::date) / 7 - 1) AS complete_weeks
FROM w ORDER BY timezone;
```

| timezone | lo_local | hi_local | first_complete_wk | last_complete_wk | complete_weeks |
|---|---|---|---|---|---|
| America/Chicago | 2026-02-01 04:57:44 | 2026-07-27 17:20:34 | 2026-02-02 | 2026-07-20 | 25 |
| America/Denver | 2026-02-01 03:57:44 | 2026-07-27 16:20:34 | 2026-02-02 | 2026-07-20 | 25 |
| America/Los_Angeles | 2026-02-01 02:57:44 | 2026-07-27 15:20:34 | 2026-02-02 | 2026-07-20 | 25 |
| America/New_York | 2026-02-01 05:57:44 | 2026-07-27 18:20:34 | 2026-02-02 | 2026-07-20 | 25 |
| America/Phoenix | 2026-02-01 03:57:44 | 2026-07-27 15:20:34 | 2026-02-02 | 2026-07-20 | 25 |
| UTC | 2026-02-01 10:57:44 | 2026-07-27 22:20:34 | 2026-02-02 | 2026-07-20 | 25 |

**Weekly totals across all accounts (local weeks)**

```sql
SELECT date_trunc('week', (e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone)::date AS local_week,
       count(*) AS events, count(DISTINCT e.account_id) AS accounts,
       count(DISTINCT ((e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone)::date) AS local_days
FROM activity_events e JOIN accounts a ON a.id = e.account_id
GROUP BY 1 ORDER BY 1;
```

| local_week | events | accounts | local_days |
|---|---|---|---|
| 2026-01-26 | 18 | 8 | 1 |
| 2026-02-02 | 458 | 19 | 7 |
| 2026-02-09 | 456 | 19 | 7 |
| 2026-02-16 | 463 | 19 | 7 |
| 2026-02-23 | 476 | 19 | 7 |
| 2026-03-02 | 477 | 19 | 7 |
| 2026-03-09 | 486 | 19 | 7 |
| 2026-03-16 | 440 | 19 | 7 |
| 2026-03-23 | 468 | 19 | 7 |
| 2026-03-30 | 482 | 19 | 7 |
| 2026-04-06 | 465 | 19 | 7 |
| 2026-04-13 | 421 | 19 | 7 |
| 2026-04-20 | 489 | 19 | 7 |
| 2026-04-27 | 466 | 19 | 7 |
| 2026-05-04 | 443 | 19 | 7 |
| 2026-05-11 | 480 | 19 | 7 |
| 2026-05-18 | 490 | 19 | 7 |
| 2026-05-25 | 457 | 19 | 7 |
| 2026-06-01 | 1270 | 19 | 7 |
| 2026-06-08 | 485 | 19 | 7 |
| 2026-06-15 | 455 | 19 | 7 |
| 2026-06-22 | 458 | 19 | 7 |
| 2026-06-29 | 491 | 19 | 7 |
| 2026-07-06 | 483 | 19 | 7 |
| 2026-07-13 | 467 | 19 | 7 |
| 2026-07-20 | 503 | 19 | 7 |
| 2026-07-27 | 79 | 17 | 1 |

**Status: INFO.** Every account with data covers the same window: local 2026-02-01 (a Sunday) to 2026-07-27 (a Monday). That gives 25 complete Mon–Sun weeks in every timezone, with a one-day stub at each end. Week 2026-06-01 stands out at 1,270 events. That is account 6's spike (check 12c).

## 2. Number of accounts

```sql
SELECT count(*) AS accounts, count(DISTINCT id) AS distinct_ids, count(DISTINCT name) AS distinct_names
FROM accounts;
```

| accounts | distinct_ids | distinct_names |
|---|---|---|
| 20 | 20 | 20 |

**Status: PASS.** 20 accounts, as the brief expects. There are no duplicate ids or names.

## 3. Accounts with no events

```sql
SELECT a.id, a.name, a.industry, a.timezone, a.created_at
FROM accounts a
WHERE NOT EXISTS (SELECT 1 FROM activity_events e WHERE e.account_id = a.id);
```

| id | name | industry | timezone | created_at |
|---|---|---|---|---|
| 20 | Quiet Harbor Spa | Personal Care | America/Los_Angeles | 2025-12-04 12:00:00 |

**Status: INFO.** Account 20 has never had an event, even though it was created 2025-12-04. That isn't invalid data, but the dashboard and the baseline must handle an empty history (the planned "not enough history" state).

## 4. Events with no account (orphans)

```sql
SELECT count(*) AS orphan_events
FROM activity_events e
LEFT JOIN accounts a ON a.id = e.account_id
WHERE a.id IS NULL;
```

| orphan_events |
|---|
| 0 |

**Status: PASS.** The FK holds, and every event joins to an account.

## 5. Distinct values

**`accounts.industry`**

```sql
SELECT industry, count(*) AS accounts FROM accounts GROUP BY 1 ORDER BY 2 DESC, 1;
```

| industry | accounts |
|---|---|
| Home Services | 6 |
| Healthcare | 4 |
| Automotive Services | 3 |
| Dental | 2 |
| Personal Care | 2 |
| Fitness | 1 |
| Storage | 1 |
| Veterinary | 1 |

**`accounts.timezone`**

```sql
SELECT timezone, count(*) AS accounts FROM accounts GROUP BY 1 ORDER BY 2 DESC, 1;
```

| timezone | accounts |
|---|---|
| America/Chicago | 6 |
| America/New_York | 5 |
| America/Los_Angeles | 4 |
| America/Denver | 2 |
| America/Phoenix | 2 |
| UTC | 1 |

**`activity_events.event_type`**

```sql
SELECT event_type, count(*) AS events FROM activity_events GROUP BY 1 ORDER BY 2 DESC;
```

| event_type | events |
|---|---|
| call_received | 7780 |
| lead_created | 3044 |
| appointment_set | 1802 |

**`activity_events.outcome` by `event_type`**

```sql
SELECT event_type, outcome, count(*) AS events
FROM activity_events GROUP BY 1, 2 ORDER BY 1, 2 NULLS LAST;
```

| event_type | outcome | events |
|---|---|---|
| appointment_set | completed | 1439 |
| appointment_set | no_show | 305 |
| appointment_set | NULL | 58 |
| call_received | connected | 4669 |
| call_received | missed | 1937 |
| call_received | voicemail | 934 |
| call_received | NULL | 240 |
| lead_created | converted | 1073 |
| lead_created | open | 1871 |
| lead_created | NULL | 100 |

**Status: PASS.** Every value is in the documented domain, and casing is consistent (see 11f). The only value outside the domain is NULL outcome (398 rows, check 11b). Calls are 62% of events, leads 24% and appointments 14%.

## 6. Weekend events (local Sat/Sun)

**Per account.** The last row is the total.

```sql
WITH l AS (
  SELECT a.id, a.name, a.industry,
         extract(isodow FROM (e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone) AS dow
  FROM activity_events e JOIN accounts a ON a.id = e.account_id)
SELECT id, name, industry, count(*) AS events,
       sum((dow = 6)::int) AS sat, sum((dow = 7)::int) AS sun,
       round(100.0 * avg((dow IN (6, 7))::int), 1) AS weekend_pct,
       round(100.0 * avg((dow = 6)::int), 1) AS sat_pct,
       round(100.0 * avg((dow = 7)::int), 1) AS sun_pct
FROM l GROUP BY ROLLUP ((id, name, industry))
ORDER BY id NULLS LAST;
```

| id | name | industry | events | sat | sun | weekend_pct | sat_pct | sun_pct |
|---|---|---|---|---|---|---|---|---|
| 1 | Summit Auto Group | Automotive Services | 1223 | 66 | 62 | 10.5 | 5.4 | 5.1 |
| 2 | Harbor Dental Partners | Dental | 730 | 40 | 35 | 10.3 | 5.5 | 4.8 |
| 3 | Bluebird HVAC | Home Services | 477 | 24 | 22 | 9.6 | 5.0 | 4.6 |
| 4 | Cornerstone Vet Clinics | Veterinary | 797 | 44 | 40 | 10.5 | 5.5 | 5.0 |
| 5 | Pacific Smiles | Dental | 884 | 49 | 53 | 11.5 | 5.5 | 6.0 |
| 6 | Metro Collision Centers | Automotive Services | 2641 | 118 | 120 | 9.0 | 4.5 | 4.5 |
| 7 | Desert Springs Plumbing | Home Services | 437 | 16 | 18 | 7.8 | 3.7 | 4.1 |
| 8 | Lakeside Physio | Healthcare | 261 | 9 | 9 | 6.9 | 3.4 | 3.4 |
| 9 | Ironwood Fitness | Fitness | 546 | 26 | 25 | 9.3 | 4.8 | 4.6 |
| 10 | Gulf Coast Roofing | Home Services | 342 | 14 | 9 | 6.7 | 4.1 | 2.6 |
| 11 | Northgate Optical | Healthcare | 354 | 15 | 14 | 8.2 | 4.2 | 4.0 |
| 12 | Redline Tire & Service | Automotive Services | 1304 | 67 | 71 | 10.6 | 5.1 | 5.4 |
| 13 | Willow Creek Counseling | Healthcare | 205 | 1 | 4 | 2.4 | 0.5 | 2.0 |
| 14 | Beacon Home Security | Home Services | 638 | 32 | 33 | 10.2 | 5.0 | 5.2 |
| 15 | Sierra Pest Solutions | Home Services | 499 | 20 | 19 | 7.8 | 4.0 | 3.8 |
| 16 | Old Town Barbers | Personal Care | 167 | 2 | 3 | 3.0 | 1.2 | 1.8 |
| 17 | Evergreen Landscaping | Home Services | 323 | 10 | 10 | 6.2 | 3.1 | 3.1 |
| 18 | Capital City Storage | Storage | 588 | 25 | 30 | 9.4 | 4.3 | 5.1 |
| 19 | Riverbend Chiropractic | Healthcare | 210 | 6 | 6 | 5.7 | 2.9 | 2.9 |
| NULL | NULL | NULL | 12626 | 584 | 583 | 9.2 | 4.6 | 4.6 |

**Day-of-week distribution (all accounts)**

```sql
SELECT extract(isodow FROM (e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone)::int AS isodow,
       to_char((e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone, 'Dy') AS day,
       count(*) AS events, round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct
FROM activity_events e JOIN accounts a ON a.id = e.account_id
GROUP BY 1, 2 ORDER BY 1;
```

| isodow | day | events | pct |
|---|---|---|---|
| 1 | Mon | 2223 | 17.6 |
| 2 | Tue | 2126 | 16.8 |
| 3 | Wed | 2893 | 22.9 |
| 4 | Thu | 2115 | 16.8 |
| 5 | Fri | 2102 | 16.6 |
| 6 | Sat | 584 | 4.6 |
| 7 | Sun | 583 | 4.6 |

**Status: INFO.** Every account has some weekend activity, so none is strictly Mon–Fri. Weekends are still light: 9.2% of events overall, against 28.6% if days were uniform. The lowest are #13 Willow Creek Counseling (2.4%) and #16 Old Town Barbers (3.0%). The highest is #5 Pacific Smiles (11.5%). Saturday and Sunday are almost the same for every account (584 vs 583 overall), which is unusual for real businesses such as barbers. It is probably a seed-generation artefact. Wednesday's 22.9% is account 6's spike day. Without it, Wednesday is about 16.6%, in line with the other weekdays. **Implications:** a weekday-only baseline would drop about 9% of events and would never judge weekend activity. A weekly Mon–Sun total includes weekends at no extra cost. Per-day weekend counts are tiny (see 14d).

## 7. Locations

**Top 10 locations by events**

```sql
SELECT e.account_id, a.name, e.location, count(*) AS events
FROM activity_events e JOIN accounts a ON a.id = e.account_id
GROUP BY 1, 2, 3 ORDER BY 4 DESC LIMIT 10;
```

| account_id | name | location | events |
|---|---|---|---|
| 2 | Harbor Dental Partners | Site A | 261 |
| 8 | Lakeside Physio | Site A | 261 |
| 3 | Bluebird HVAC | Site B | 243 |
| 2 | Harbor Dental Partners | Site C | 241 |
| 3 | Bluebird HVAC | Site A | 234 |
| 2 | Harbor Dental Partners | Site B | 228 |
| 7 | Desert Springs Plumbing | Site A | 220 |
| 7 | Desert Springs Plumbing | Site B | 217 |
| 12 | Redline Tire & Service | Site E | 215 |
| 19 | Riverbend Chiropractic | Site A | 210 |

**Bottom 5 locations by events**

```sql
SELECT e.account_id, a.name, e.location, count(*) AS events
FROM activity_events e JOIN accounts a ON a.id = e.account_id
GROUP BY 1, 2, 3 ORDER BY 4 ASC LIMIT 5;
```

| account_id | name | location | events |
|---|---|---|---|
| 18 | Capital City Storage | Site C | 106 |
| 18 | Capital City Storage | Site A | 110 |
| 18 | Capital City Storage | Site B | 121 |
| 18 | Capital City Storage | Site D | 125 |
| 18 | Capital City Storage | Site E | 126 |

**Locations per account**

```sql
SELECT a.id, a.name, count(DISTINCT e.location) AS locations, count(e.id) AS events,
       min(lc.n) AS min_events_per_loc, max(lc.n) AS max_events_per_loc
FROM accounts a
LEFT JOIN activity_events e ON e.account_id = a.id
LEFT JOIN (SELECT account_id, location, count(*) AS n FROM activity_events GROUP BY 1, 2) lc
       ON lc.account_id = a.id AND lc.location = e.location
GROUP BY a.id ORDER BY a.id;
```

| id | name | locations | events | min_events_per_loc | max_events_per_loc |
|---|---|---|---|---|---|
| 1 | Summit Auto Group | 6 | 1223 | 192 | 209 |
| 2 | Harbor Dental Partners | 3 | 730 | 228 | 261 |
| 3 | Bluebird HVAC | 2 | 477 | 234 | 243 |
| 4 | Cornerstone Vet Clinics | 4 | 797 | 185 | 208 |
| 5 | Pacific Smiles | 5 | 884 | 158 | 205 |
| 6 | Metro Collision Centers | 15 | 2641 | 148 | 195 |
| 7 | Desert Springs Plumbing | 2 | 437 | 217 | 220 |
| 8 | Lakeside Physio | 1 | 261 | 261 | 261 |
| 9 | Ironwood Fitness | 3 | 546 | 166 | 206 |
| 10 | Gulf Coast Roofing | 2 | 342 | 169 | 173 |
| 11 | Northgate Optical | 2 | 354 | 175 | 179 |
| 12 | Redline Tire & Service | 7 | 1304 | 156 | 215 |
| 13 | Willow Creek Counseling | 1 | 205 | 205 | 205 |
| 14 | Beacon Home Security | 4 | 638 | 140 | 170 |
| 15 | Sierra Pest Solutions | 3 | 499 | 146 | 188 |
| 16 | Old Town Barbers | 1 | 167 | 167 | 167 |
| 17 | Evergreen Landscaping | 2 | 323 | 157 | 166 |
| 18 | Capital City Storage | 5 | 588 | 106 | 126 |
| 19 | Riverbend Chiropractic | 1 | 210 | 210 | 210 |
| 20 | Quiet Harbor Spa | 0 | 0 | NULL | NULL |

**Status: INFO.** There are 69 account-location pairs. Location names repeat across accounts (`Site A` exists in 19 accounts), so a location is identified by `(account_id, location)`. Volume is spread evenly within each account: max/min per location is at most 1.38× (account 12). The biggest location has only 261 events in 26 weeks, about 10 per week. Account 6's 15 sites have only 148–195 events each, about 5 per week (excluding the spike).

## 8. Events before account `created_at`

```sql
SELECT count(*) FILTER (WHERE e.occurred_at < a.created_at) AS events_before_created,
       min(e.occurred_at - a.created_at) AS smallest_gap_event_minus_created
FROM activity_events e JOIN accounts a ON a.id = e.account_id;
```

| events_before_created | smallest_gap_event_minus_created |
|---|---|
| 0 | 60 days 22:40:44 |

**Status: PASS.** No event predates its account. All accounts were created between 2025-01-04 and 2025-12-04, before the data starts.

## 9. Events outside 07:00–19:00 local time

**Overall**

```sql
WITH l AS (
  SELECT extract(hour FROM (e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone) AS h
  FROM activity_events e JOIN accounts a ON a.id = e.account_id)
SELECT count(*) AS events,
       count(*) FILTER (WHERE h < 7)   AS before_07,
       count(*) FILTER (WHERE h >= 19) AS from_19,
       round(100.0 * avg((h < 7 OR h >= 19)::int), 1) AS outside_07_19_pct
FROM l;
```

| events | before_07 | from_19 | outside_07_19_pct |
|---|---|---|---|
| 12626 | 2249 | 344 | 20.5 |

**Per account**

```sql
WITH l AS (
  SELECT a.id, a.timezone,
         extract(hour FROM (e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone) AS h
  FROM activity_events e JOIN accounts a ON a.id = e.account_id)
SELECT id, timezone, count(*) AS events,
       count(*) FILTER (WHERE h < 7 OR h >= 19) AS outside,
       round(100.0 * avg((h < 7 OR h >= 19)::int), 1) AS outside_pct,
       round(100.0 * avg((h < 7)::int), 1) AS before_07_pct,
       round(100.0 * avg((h >= 19)::int), 1) AS from_19_pct
FROM l GROUP BY 1, 2 ORDER BY 1;
```

| id | timezone | events | outside | outside_pct | before_07_pct | from_19_pct |
|---|---|---|---|---|---|---|
| 1 | America/Chicago | 1223 | 207 | 16.9 | 16.4 | 0.5 |
| 2 | America/New_York | 730 | 125 | 17.1 | 12.6 | 4.5 |
| 3 | America/Denver | 477 | 100 | 21.0 | 19.9 | 1.0 |
| 4 | America/Chicago | 797 | 131 | 16.4 | 16.1 | 0.4 |
| 5 | America/Los_Angeles | 884 | 272 | 30.8 | 29.6 | 1.1 |
| 6 | America/New_York | 2641 | 391 | 14.8 | 11.6 | 3.2 |
| 7 | America/Phoenix | 437 | 130 | 29.7 | 28.6 | 1.1 |
| 8 | America/Chicago | 261 | 36 | 13.8 | 13.8 | 0.0 |
| 9 | America/Denver | 546 | 131 | 24.0 | 23.4 | 0.5 |
| 10 | America/Chicago | 342 | 47 | 13.7 | 13.7 | 0.0 |
| 11 | America/New_York | 354 | 49 | 13.8 | 11.6 | 2.3 |
| 12 | America/Los_Angeles | 1304 | 403 | 30.9 | 29.6 | 1.3 |
| 13 | America/Chicago | 205 | 36 | 17.6 | 17.6 | 0.0 |
| 14 | America/New_York | 638 | 98 | 15.4 | 11.8 | 3.6 |
| 15 | America/Phoenix | 499 | 146 | 29.3 | 28.1 | 1.2 |
| 16 | America/Chicago | 167 | 37 | 22.2 | 22.2 | 0.0 |
| 17 | America/Los_Angeles | 323 | 98 | 30.3 | 28.5 | 1.9 |
| 18 | UTC | 588 | 130 | 22.1 | 1.0 | 21.1 |
| 19 | America/New_York | 210 | 26 | 12.4 | 7.1 | 5.2 |

**Hour-of-day distribution (local hour), by timezone**

```sql
WITH l AS (
  SELECT a.timezone, extract(hour FROM (e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone)::int AS h
  FROM activity_events e JOIN accounts a ON a.id = e.account_id)
SELECT h AS local_hour, count(*) AS all_tz,
       sum((timezone = 'America/New_York')::int)    AS new_york,
       sum((timezone = 'America/Chicago')::int)     AS chicago,
       sum((timezone = 'America/Denver')::int)      AS denver,
       sum((timezone = 'America/Phoenix')::int)     AS phoenix,
       sum((timezone = 'America/Los_Angeles')::int) AS los_angeles,
       sum((timezone = 'UTC')::int)                 AS utc
FROM l GROUP BY 1 ORDER BY 1;
```

| local_hour | all_tz | new_york | chicago | denver | phoenix | los_angeles | utc |
|---|---|---|---|---|---|---|---|
| 0 | 62 | 11 | 6 | 7 | 5 | 33 | 0 |
| 1 | 102 | 16 | 15 | 15 | 19 | 37 | 0 |
| 2 | 164 | 28 | 37 | 17 | 13 | 69 | 0 |
| 3 | 274 | 49 | 57 | 36 | 36 | 96 | 0 |
| 4 | 412 | 93 | 76 | 38 | 53 | 150 | 2 |
| 5 | 542 | 131 | 139 | 45 | 67 | 159 | 1 |
| 6 | 693 | 202 | 155 | 65 | 72 | 196 | 3 |
| 7 | 901 | 254 | 210 | 102 | 86 | 241 | 8 |
| 8 | 1002 | 315 | 230 | 96 | 93 | 257 | 11 |
| 9 | 1123 | 383 | 295 | 94 | 88 | 247 | 16 |
| 10 | 1209 | 444 | 308 | 104 | 92 | 240 | 21 |
| 11 | 1114 | 434 | 310 | 84 | 79 | 179 | 28 |
| 12 | 1112 | 450 | 289 | 78 | 69 | 180 | 46 |
| 13 | 933 | 417 | 215 | 67 | 52 | 135 | 47 |
| 14 | 827 | 383 | 198 | 52 | 36 | 100 | 58 |
| 15 | 651 | 290 | 160 | 40 | 23 | 70 | 68 |
| 16 | 575 | 232 | 114 | 47 | 41 | 89 | 52 |
| 17 | 335 | 156 | 91 | 28 | 0 | 0 | 60 |
| 18 | 251 | 126 | 81 | 0 | 1 | 0 | 43 |
| 19 | 199 | 154 | 2 | 0 | 0 | 1 | 42 |
| 20 | 33 | 0 | 0 | 2 | 0 | 3 | 28 |
| 21 | 34 | 2 | 2 | 2 | 3 | 5 | 20 |
| 22 | 31 | 2 | 2 | 1 | 5 | 7 | 14 |
| 23 | 47 | 1 | 3 | 3 | 3 | 17 | 20 |

**For reference: hour-of-day in UTC**

```sql
SELECT extract(hour FROM occurred_at)::int AS utc_hour, count(*) AS events
FROM activity_events GROUP BY 1 ORDER BY 1;
```

| utc_hour | events |
|---|---|
| 0 | 1 |
| 1 | 2 |
| 2 | 9 |
| 3 | 5 |
| 4 | 18 |
| 5 | 39 |
| 6 | 69 |
| 7 | 131 |
| 8 | 224 |
| 9 | 293 |
| 10 | 504 |
| 11 | 667 |
| 12 | 840 |
| 13 | 1012 |
| 14 | 1192 |
| 15 | 1256 |
| 16 | 1265 |
| 17 | 1199 |
| 18 | 1019 |
| 19 | 849 |
| 20 | 690 |
| 21 | 495 |
| 22 | 346 |
| 23 | 501 |

**Status: INFO.** 20.5% of events fall outside 07:00–19:00 local, and almost all of them are *before* 07:00. In UTC the activity has a single peak around 14–17 UTC for every timezone. Local hours therefore shift with the offset: New York peaks around 10–12 local, Los Angeles and Phoenix around 07–10 local, with 28–30% of their events before 07:00. Each timezone also cuts off sharply at the local hour that matches 00:00 UTC (for example, Los Angeles has 0 events at 17–18 local). UTC hour 23 also shows a bump (501 vs 346 at 22). This pattern suggests the seed timestamps were generated on a UTC clock and are not business-hours-aware. We treat it as a property of the data, not something to fix. **Implications:** a "business hours only" filter would remove up to 31% of west-coast activity, so it is not a safe cleaning rule. Bucketing by local *day* and *week* is barely affected (check 13d).

## 10. Duplicates

### 10a. Exact duplicates

Exact duplicates share account, location, event type and `occurred_at`, but have a different `id`.

```sql
SELECT count(*) AS groups, sum(n) AS rows_in_groups, sum(n - 1) AS surplus_rows, max(n) AS max_group_size
FROM (SELECT count(*) AS n FROM activity_events
      GROUP BY account_id, location, event_type, occurred_at HAVING count(*) > 1) d;
```

| groups | rows_in_groups | surplus_rows | max_group_size |
|---|---|---|---|
| 12 | 24 | 12 | 2 |

```sql
SELECT account_id, location, event_type, occurred_at, count(*) AS n,
       string_agg(id::text, ',' ORDER BY id) AS ids,
       string_agg(coalesce(duration_seconds::text, 'NULL'), ',' ORDER BY id) AS durations,
       string_agg(coalesce(outcome, 'NULL'), ',' ORDER BY id) AS outcomes,
       count(DISTINCT coalesce(duration_seconds::text, '-')) = 1
         AND count(DISTINCT coalesce(outcome, '-')) = 1 AS all_columns_match
FROM activity_events
GROUP BY account_id, location, event_type, occurred_at
HAVING count(*) > 1
ORDER BY occurred_at;
```

| account_id | location | event_type | occurred_at | n | ids | durations | outcomes | all_columns_match |
|---|---|---|---|---|---|---|---|---|
| 6 | Site E | call_received | 2026-02-24 15:27:21 | 2 | 1523,1524 | 719,719 | connected,connected | t |
| 4 | Site B | call_received | 2026-02-24 17:08:10 | 2 | 1538,1539 | 461,461 | NULL,NULL | t |
| 8 | Site A | call_received | 2026-03-06 12:50:34 | 2 | 2236,2237 | 1251,1251 | connected,connected | t |
| 6 | Site L | call_received | 2026-04-29 17:06:25 | 2 | 5851,5852 | 244,244 | connected,connected | t |
| 1 | Site F | appointment_set | 2026-04-29 17:33:31 | 2 | 5856,5857 | NULL,NULL | completed,completed | t |
| 18 | Site C | lead_created | 2026-05-07 14:26:28 | 2 | 6325,6326 | NULL,NULL | converted,converted | t |
| 6 | Site A | call_received | 2026-05-17 14:18:12 | 2 | 6966,6967 | 763,763 | missed,missed | t |
| 12 | Site A | lead_created | 2026-05-25 17:45:32 | 2 | 7524,7525 | NULL,NULL | open,open | t |
| 6 | Site L | call_received | 2026-06-03 18:34:15 | 2 | 8738,8739 | 611,611 | voicemail,voicemail | t |
| 18 | Site D | call_received | 2026-06-12 12:18:45 | 2 | 9595,9596 | 1238,1238 | missed,missed | t |
| 2 | Site A | call_received | 2026-06-12 13:46:10 | 2 | 9603,9604 | 1128,1128 | missed,missed | t |
| 1 | Site C | call_received | 2026-07-07 20:26:04 | 2 | 11266,11267 | 497,497 | voicemail,voicemail | t |

**Status: FAIL.** 12 groups, each a pair, so there are 12 surplus rows. In every pair `duration_seconds` and `outcome` also match and the ids are consecutive. These look like double-ingested rows, not real coincidences. They are spread over 7 accounts, and one (ids 8738/8739) falls on account 6's spike day.

### 10b. Near-duplicates

Near-duplicates share account, location and event type, with timestamps 1–60 s apart.

```sql
-- Pairs of events with the same account/location/type, b after a by <= 60 s (or same second, a.id < b.id).
WITH p AS (
  SELECT extract(epoch FROM b.occurred_at - a.occurred_at) AS gap_s,
         (a.duration_seconds IS NOT DISTINCT FROM b.duration_seconds
          AND a.outcome IS NOT DISTINCT FROM b.outcome) AS same_attrs,
         a.account_id
  FROM activity_events a
  JOIN activity_events b
    ON  b.account_id = a.account_id AND b.location = a.location AND b.event_type = a.event_type
    AND b.occurred_at BETWEEN a.occurred_at AND a.occurred_at + interval '60 seconds'
    AND (b.occurred_at > a.occurred_at OR a.id < b.id))
SELECT CASE WHEN gap_s = 0 THEN 'a: 0 s (exact)' WHEN gap_s <= 5 THEN 'b: 1-5 s' ELSE 'c: 6-60 s' END AS gap,
       count(*) AS pairs,
       sum(same_attrs::int) AS pairs_same_duration_and_outcome,
       sum((account_id = 6)::int) AS pairs_in_account_6
FROM p GROUP BY 1 ORDER BY 1;
```

| gap | pairs | pairs_same_duration_and_outcome | pairs_in_account_6 |
|---|---|---|---|
| a: 0 s (exact) | 12 | 12 | 4 |
| b: 1-5 s | 2 | 0 | 2 |
| c: 6-60 s | 25 | 4 | 17 |

**Pairs within 1–5 s**

```sql
SELECT a.id AS id1, b.id AS id2, a.account_id, a.location, a.event_type, a.occurred_at,
       extract(epoch FROM b.occurred_at - a.occurred_at)::int AS gap_s,
       a.duration_seconds AS dur1, b.duration_seconds AS dur2, a.outcome AS out1, b.outcome AS out2
FROM activity_events a
JOIN activity_events b
  ON  b.account_id = a.account_id AND b.location = a.location AND b.event_type = a.event_type
  AND b.occurred_at > a.occurred_at AND b.occurred_at <= a.occurred_at + interval '5 seconds'
ORDER BY a.occurred_at;
```

| id1 | id2 | account_id | location | event_type | occurred_at | gap_s | dur1 | dur2 | out1 | out2 |
|---|---|---|---|---|---|---|---|---|---|---|
| 8527 | 8528 | 6 | Site O | call_received | 2026-06-03 15:53:04 | 5 | 810 | 478 | NULL | connected |
| 8972 | 8973 | 6 | Site D | call_received | 2026-06-03 23:19:21 | 4 | 644 | 312 | connected | missed |

**Status: INFO.** Only 2 pairs fall within 5 s. Both are on account 6's spike day and both have different durations and outcomes, so they look like separate events. Of the 25 pairs at 6–60 s, 17 are in account 6 (mostly on 2026-06-03, when the density is about 60× normal) and only 4 match on duration and outcome. That is the kind of collision you'd expect by chance at this density. There is no evidence of near-duplicate re-ingestion apart from the exact pairs.

## 11. Field consistency

### 11a. Outcome valid for its event type

**Invalid (event_type, outcome) combinations**

```sql
SELECT event_type, outcome, count(*) AS events
FROM activity_events
WHERE outcome IS NOT NULL
  AND NOT ( (event_type = 'call_received'   AND outcome IN ('connected', 'missed', 'voicemail'))
         OR (event_type = 'lead_created'    AND outcome IN ('open', 'converted'))
         OR (event_type = 'appointment_set' AND outcome IN ('completed', 'no_show')) )
GROUP BY 1, 2;
```

| event_type | outcome | events |
|---|---|---|
| — | — | — |

_0 rows._

**Unknown event types**

```sql
SELECT count(*) AS unknown_event_type
FROM activity_events
WHERE event_type NOT IN ('call_received', 'lead_created', 'appointment_set');
```

| unknown_event_type |
|---|
| 0 |

**Status: PASS.** Every non-NULL outcome is valid for its type.

### 11b–11d. NULL rates and duration presence

```sql
SELECT event_type, count(*) AS events,
       sum((outcome IS NULL)::int) AS null_outcome,
       round(100.0 * avg((outcome IS NULL)::int), 2) AS null_outcome_pct,
       sum((duration_seconds IS NOT NULL)::int) AS with_duration,
       sum((duration_seconds IS NULL)::int) AS null_duration,
       round(100.0 * avg((duration_seconds IS NULL)::int), 2) AS null_duration_pct
FROM activity_events GROUP BY 1 ORDER BY 1;
```

| event_type | events | null_outcome | null_outcome_pct | with_duration | null_duration | null_duration_pct |
|---|---|---|---|---|---|---|
| appointment_set | 1802 | 58 | 3.22 | 0 | 1802 | 100.00 |
| call_received | 7780 | 240 | 3.08 | 7467 | 313 | 4.02 |
| lead_created | 3044 | 100 | 3.29 | 0 | 3044 | 100.00 |

**Calls with both outcome and duration NULL**

```sql
SELECT count(*) AS calls_null_outcome_and_duration
FROM activity_events
WHERE event_type = 'call_received' AND outcome IS NULL AND duration_seconds IS NULL;
```

| calls_null_outcome_and_duration |
|---|
| 6 |

**Status: 11b FAIL, 11c PASS.**
- **11b:** `outcome` is NULL on 398 rows (58 appointments, 240 calls, 100 leads), about 3.1–3.3% of every type. The rate is uniform, so it looks random rather than systematic. It doesn't affect a total-events metric, but it would affect outcome rates (missed-call, no-show, conversion) if those are added later.
- **11c:** `duration_seconds` appears only on calls. It is 100% NULL for leads and appointments, as expected.
- **11d:** 313 calls (4.0%) have no duration. 6 calls have neither outcome nor duration.

### 11d. Call duration values

```sql
SELECT count(*) AS calls_with_duration,
       min(duration_seconds) AS min_s,
       percentile_cont(0.01) WITHIN GROUP (ORDER BY duration_seconds) AS p01,
       percentile_cont(0.25) WITHIN GROUP (ORDER BY duration_seconds) AS p25,
       percentile_cont(0.50) WITHIN GROUP (ORDER BY duration_seconds) AS p50,
       percentile_cont(0.75) WITHIN GROUP (ORDER BY duration_seconds) AS p75,
       percentile_cont(0.99) WITHIN GROUP (ORDER BY duration_seconds) AS p99,
       max(duration_seconds) AS max_s,
       sum((duration_seconds = 0)::int) AS zero,
       sum((duration_seconds < 0)::int) AS negative,
       sum((duration_seconds > 4 * 3600)::int) AS over_4h
FROM activity_events
WHERE event_type = 'call_received' AND duration_seconds IS NOT NULL;
```

| calls_with_duration | min_s | p01 | p25 | p50 | p75 | p99 | max_s | zero | negative | over_4h |
|---|---|---|---|---|---|---|---|---|---|---|
| 7467 | 20 | 36.66 | 399.5 | 754 | 1124.5 | 1484 | 1500 | 0 | 0 | 0 |

**Duration by call outcome**

```sql
SELECT outcome, count(*) AS calls, min(duration_seconds) AS min_s,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY duration_seconds) AS median_s,
       max(duration_seconds) AS max_s
FROM activity_events WHERE event_type = 'call_received'
GROUP BY 1 ORDER BY 1 NULLS LAST;
```

| outcome | calls | min_s | median_s | max_s |
|---|---|---|---|---|
| connected | 4669 | 20 | 769.5 | 1500 |
| missed | 1937 | 20 | 711 | 1500 |
| voicemail | 934 | 21 | 778.5 | 1499 |
| NULL | 240 | 26 | 733.5 | 1495 |

**Status: 11d FAIL (NULLs only), 11e INFO.** No duration is zero, negative or extreme. The range is 20–1500 s and the quartiles are evenly spaced (about 400 / 754 / 1125), which looks like a uniform distribution. The only defect is the 313 NULLs. **11e:** `missed` calls carry durations as long as `connected` ones (median 711 s vs 770 s). That doesn't make sense for a missed call, so duration would need care if it is ever used for a metric. It isn't needed for total events.

### 11f. Casing, whitespace and empty strings

```sql
SELECT 'activity_events.location' AS col,
       count(*) FILTER (WHERE location <> btrim(location)) AS lead_trail_ws,
       count(*) FILTER (WHERE btrim(location) = '') AS empty,
       count(DISTINCT location) AS distinct_raw,
       count(DISTINCT lower(btrim(location))) AS distinct_normalised,
       count(*) FILTER (WHERE location !~ '^Site [A-Z]$') AS off_pattern
FROM activity_events
UNION ALL
SELECT 'activity_events.event_type', count(*) FILTER (WHERE event_type <> btrim(event_type)),
       count(*) FILTER (WHERE btrim(event_type) = ''), count(DISTINCT event_type),
       count(DISTINCT lower(btrim(event_type))), count(*) FILTER (WHERE event_type <> lower(event_type))
FROM activity_events
UNION ALL
SELECT 'activity_events.outcome', count(*) FILTER (WHERE outcome <> btrim(outcome)),
       count(*) FILTER (WHERE btrim(outcome) = ''), count(DISTINCT outcome),
       count(DISTINCT lower(btrim(outcome))), count(*) FILTER (WHERE outcome <> lower(outcome))
FROM activity_events
UNION ALL
SELECT 'accounts.name', count(*) FILTER (WHERE name <> btrim(name)), count(*) FILTER (WHERE btrim(name) = ''),
       count(DISTINCT name), count(DISTINCT lower(btrim(name))), NULL FROM accounts
UNION ALL
SELECT 'accounts.industry', count(*) FILTER (WHERE industry <> btrim(industry)), count(*) FILTER (WHERE btrim(industry) = ''),
       count(DISTINCT industry), count(DISTINCT lower(btrim(industry))), NULL FROM accounts
UNION ALL
SELECT 'accounts.timezone', count(*) FILTER (WHERE timezone <> btrim(timezone)), count(*) FILTER (WHERE btrim(timezone) = ''),
       count(DISTINCT timezone), count(DISTINCT lower(btrim(timezone))), NULL FROM accounts;
```

| col | lead_trail_ws | empty | distinct_raw | distinct_normalised | off_pattern |
|---|---|---|---|---|---|
| accounts.timezone | 0 | 0 | 6 | 6 | NULL |
| accounts.industry | 0 | 0 | 8 | 8 | NULL |
| accounts.name | 0 | 0 | 20 | 20 | NULL |
| activity_events.location | 0 | 0 | 15 | 15 | 0 |
| activity_events.outcome | 0 | 0 | 7 | 7 | 0 |
| activity_events.event_type | 0 | 0 | 3 | 3 | 0 |

**Status: PASS.** There is no leading or trailing whitespace and no empty strings. Lower-casing or trimming merges no distinct values. All `location` values match `^Site [A-Z]$`, and all enums are lower-case.

## 12. Coverage gaps and spikes

### 12a. Weekly totals per account and zero-event weeks (25 complete weeks)

```sql
-- Complete local weeks only (2026-02-02 .. 2026-07-20 week starts; see check 1).
WITH weeks AS (SELECT generate_series('2026-02-02'::date, '2026-07-20'::date, '7 days')::date AS wk),
l AS (SELECT e.account_id,
             date_trunc('week', (e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone)::date AS wk
      FROM activity_events e JOIN accounts a ON a.id = e.account_id),
c AS (SELECT a.id AS account_id, w.wk, count(l.wk) AS n
      FROM accounts a CROSS JOIN weeks w
      LEFT JOIN l ON l.account_id = a.id AND l.wk = w.wk
      GROUP BY 1, 2)
SELECT account_id, sum(n) AS events, min(n) AS min_wk,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY n) AS median_wk,
       max(n) AS max_wk,
       round((max(n) / nullif(percentile_cont(0.5) WITHIN GROUP (ORDER BY n), 0))::numeric, 2) AS max_over_median,
       (array_agg(wk ORDER BY n DESC, wk))[1] AS max_week,
       sum((n = 0)::int) AS zero_weeks
FROM c GROUP BY 1 ORDER BY 1;
```

| account_id | events | min_wk | median_wk | max_wk | max_over_median | max_week | zero_weeks |
|---|---|---|---|---|---|---|---|
| 1 | 1212 | 36 | 50 | 62 | 1.24 | 2026-06-29 | 0 |
| 2 | 730 | 18 | 31 | 37 | 1.19 | 2026-05-25 | 0 |
| 3 | 475 | 10 | 19 | 29 | 1.53 | 2026-03-09 | 0 |
| 4 | 790 | 21 | 32 | 42 | 1.31 | 2026-04-06 | 0 |
| 5 | 870 | 23 | 34 | 53 | 1.56 | 2026-07-06 | 0 |
| 6 | 2628 | 50 | 76 | 881 | 11.59 | 2026-06-01 | 0 |
| 7 | 433 | 11 | 17 | 22 | 1.29 | 2026-02-23 | 0 |
| 8 | 261 | 7 | 11 | 14 | 1.27 | 2026-04-06 | 0 |
| 9 | 541 | 12 | 22 | 31 | 1.41 | 2026-04-20 | 0 |
| 10 | 338 | 10 | 13 | 18 | 1.38 | 2026-02-09 | 0 |
| 11 | 352 | 8 | 14 | 20 | 1.43 | 2026-05-18 | 0 |
| 12 | 1290 | 32 | 53 | 68 | 1.28 | 2026-06-29 | 0 |
| 13 | 204 | 4 | 9 | 11 | 1.22 | 2026-02-09 | 0 |
| 14 | 634 | 16 | 25 | 40 | 1.60 | 2026-03-02 | 0 |
| 15 | 495 | 12 | 20 | 33 | 1.65 | 2026-06-01 | 0 |
| 16 | 165 | 2 | 7 | 9 | 1.29 | 2026-02-09 | 0 |
| 17 | 320 | 6 | 13 | 18 | 1.38 | 2026-02-16 | 0 |
| 18 | 584 | 17 | 24 | 30 | 1.25 | 2026-05-25 | 0 |
| 19 | 207 | 5 | 8 | 13 | 1.63 | 2026-07-20 | 0 |
| 20 | 0 | 0 | 0 | 0 | NULL | 2026-02-02 | 25 |

**Zero-event weeks at location level**

```sql
WITH weeks AS (SELECT generate_series('2026-02-02'::date, '2026-07-20'::date, '7 days')::date AS wk),
l AS (SELECT e.account_id, e.location,
             date_trunc('week', (e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone)::date AS wk
      FROM activity_events e JOIN accounts a ON a.id = e.account_id),
loc AS (SELECT DISTINCT account_id, location FROM l),
c AS (SELECT lo.account_id, lo.location, w.wk, count(l.wk) AS n
      FROM loc lo CROSS JOIN weeks w
      LEFT JOIN l ON l.account_id = lo.account_id AND l.location = lo.location AND l.wk = w.wk
      GROUP BY 1, 2, 3)
SELECT count(DISTINCT (account_id, location)) AS locations,
       count(*) AS location_weeks,
       sum((n = 0)::int) AS zero_weeks,
       count(DISTINCT (account_id, location)) FILTER (WHERE n = 0) AS locations_with_a_zero_week,
       sum((n <= 2)::int) AS weeks_with_le_2_events
FROM c;
```

| locations | location_weeks | zero_weeks | locations_with_a_zero_week | weeks_with_le_2_events |
|---|---|---|---|---|
| 69 | 1725 | 4 | 3 | 106 |

```sql
WITH weeks AS (SELECT generate_series('2026-02-02'::date, '2026-07-20'::date, '7 days')::date AS wk),
l AS (SELECT e.account_id, e.location,
             date_trunc('week', (e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone)::date AS wk
      FROM activity_events e JOIN accounts a ON a.id = e.account_id),
loc AS (SELECT DISTINCT account_id, location FROM l),
c AS (SELECT lo.account_id, lo.location, w.wk, count(l.wk) AS n
      FROM loc lo CROSS JOIN weeks w
      LEFT JOIN l ON l.account_id = lo.account_id AND l.location = lo.location AND l.wk = w.wk
      GROUP BY 1, 2, 3)
SELECT account_id, location, string_agg(wk::text, ', ' ORDER BY wk) FILTER (WHERE n = 0) AS zero_event_weeks,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY n) AS median_wk
FROM c GROUP BY 1, 2
HAVING min(n) = 0
ORDER BY 1, 2;
```

| account_id | location | zero_event_weeks | median_wk |
|---|---|---|---|
| 6 | Site G | 2026-04-13, 2026-06-29 | 5 |
| 6 | Site N | 2026-02-23 | 5 |
| 18 | Site C | 2026-03-23 | 4 |

**Status: PASS (account) / INFO (location).** No active account has an empty complete week, and the lowest is 2 events (#16 Old Town Barbers). At location level only 4 of 1,725 location-weeks are empty, but 106 location-weeks (6%) have 2 events or fewer. A location can drop to 0 or 1 in a normal week, so location verdicts will be noisy (see 14b).

### 12b. Locations that start or stop mid-range

```sql
-- Locations whose first/last local event is more than 7 days inside the dataset window
-- (window in local time: 2026-02-01 .. 2026-07-27).
WITH l AS (SELECT e.account_id, e.location,
                  ((e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone)::date AS d
           FROM activity_events e JOIN accounts a ON a.id = e.account_id),
s AS (SELECT account_id, location, min(d) AS first_day, max(d) AS last_day, count(*) AS events
      FROM l GROUP BY 1, 2)
SELECT count(*) AS locations,
       max(first_day) AS latest_first_day,
       min(last_day) AS earliest_last_day,
       count(*) FILTER (WHERE first_day > '2026-02-08') AS starts_mid_range,
       count(*) FILTER (WHERE last_day < '2026-07-20') AS stops_mid_range
FROM s;
```

| locations | latest_first_day | earliest_last_day | starts_mid_range | stops_mid_range |
|---|---|---|---|---|
| 69 | 2026-02-05 | 2026-07-22 | 0 | 0 |

**Status: PASS.** Every location's first event is on or before 2026-02-05 and its last on or after 2026-07-22. No location opens or closes inside the window, so a per-location baseline never starts mid-series in this data. The minimum-history rule still matters for production.

### 12c. Spikes

The max/median column in 12a is 1.19–1.65 for every account except #6, which is 11.59.

**Account 6, daily counts around the spike (local New York time)**

```sql
SELECT ((e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone)::date AS local_day,
       to_char((e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone, 'Dy') AS dow,
       count(*) AS events, count(DISTINCT e.location) AS sites,
       sum((e.event_type = 'call_received')::int) AS calls,
       sum((e.event_type = 'lead_created')::int) AS leads,
       sum((e.event_type = 'appointment_set')::int) AS appts
FROM activity_events e JOIN accounts a ON a.id = e.account_id
WHERE a.id = 6
  AND ((e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone)::date BETWEEN '2026-05-27' AND '2026-06-10'
GROUP BY 1, 2 ORDER BY 1;
```

| local_day | dow | events | sites | calls | leads | appts |
|---|---|---|---|---|---|---|
| 2026-05-27 | Wed | 11 | 9 | 6 | 2 | 3 |
| 2026-05-28 | Thu | 12 | 10 | 7 | 2 | 3 |
| 2026-05-29 | Fri | 10 | 10 | 7 | 2 | 1 |
| 2026-05-30 | Sat | 3 | 3 | 0 | 3 | 0 |
| 2026-05-31 | Sun | 2 | 2 | 2 | 0 | 0 |
| 2026-06-01 | Mon | 16 | 12 | 11 | 4 | 1 |
| 2026-06-02 | Tue | 16 | 10 | 8 | 4 | 4 |
| 2026-06-03 | Wed | 805 | 15 | 485 | 210 | 110 |
| 2026-06-04 | Thu | 18 | 12 | 7 | 6 | 5 |
| 2026-06-05 | Fri | 14 | 9 | 9 | 3 | 2 |
| 2026-06-06 | Sat | 4 | 3 | 3 | 1 | 0 |
| 2026-06-07 | Sun | 8 | 6 | 6 | 2 | 0 |
| 2026-06-08 | Mon | 17 | 11 | 10 | 5 | 2 |
| 2026-06-09 | Tue | 16 | 9 | 11 | 1 | 4 |
| 2026-06-10 | Wed | 16 | 10 | 11 | 2 | 3 |

**Account 6 spike by site**

```sql
WITH l AS (SELECT e.location, ((e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone)::date AS d
           FROM activity_events e JOIN accounts a ON a.id = e.account_id WHERE a.id = 6)
SELECT location,
       count(*) FILTER (WHERE d = '2026-06-03') AS on_2026_06_03,
       round(count(*) FILTER (WHERE d <> '2026-06-03') / 176.0 * 7, 1) AS avg_per_week_other_days,
       round(100.0 * count(*) FILTER (WHERE d = '2026-06-03')
             / sum(count(*) FILTER (WHERE d = '2026-06-03')) OVER (), 1) AS share_of_spike_pct
FROM l GROUP BY 1 ORDER BY 1;
```

| location | on_2026_06_03 | avg_per_week_other_days | share_of_spike_pct |
|---|---|---|---|
| Site A | 43 | 5.6 | 5.3 |
| Site B | 64 | 4.7 | 8.0 |
| Site C | 62 | 5.1 | 7.7 |
| Site D | 64 | 5.2 | 8.0 |
| Site E | 52 | 5.4 | 6.5 |
| Site F | 58 | 4.5 | 7.2 |
| Site G | 51 | 4.5 | 6.3 |
| Site H | 48 | 4.4 | 6.0 |
| Site I | 43 | 4.5 | 5.3 |
| Site J | 52 | 4.8 | 6.5 |
| Site K | 52 | 4.8 | 6.5 |
| Site L | 61 | 5.3 | 7.6 |
| Site M | 44 | 4.1 | 5.5 |
| Site N | 69 | 4.8 | 8.6 |
| Site O | 42 | 5.3 | 5.2 |

**Largest single days vs that account's median weekday (all accounts)**

```sql
-- Daily counts per account vs that account's median daily count (weekdays, local time).
WITH d AS (SELECT e.account_id, ((e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone)::date AS day, count(*) AS n
           FROM activity_events e JOIN accounts a ON a.id = e.account_id GROUP BY 1, 2),
m AS (SELECT account_id, percentile_cont(0.5) WITHIN GROUP (ORDER BY n) AS med FROM d
      WHERE extract(isodow FROM day) < 6 GROUP BY 1)
SELECT d.account_id, d.day, d.n AS events, m.med AS median_weekday, round((d.n / m.med)::numeric, 1) AS ratio
FROM d JOIN m USING (account_id)
ORDER BY ratio DESC LIMIT 10;
```

| account_id | day | events | median_weekday | ratio |
|---|---|---|---|---|
| 6 | 2026-06-03 | 805 | 13 | 61.9 |
| 3 | 2026-04-22 | 10 | 3 | 3.3 |
| 16 | 2026-06-02 | 3 | 1 | 3.0 |
| 16 | 2026-03-17 | 3 | 1 | 3.0 |
| 16 | 2026-07-22 | 3 | 1 | 3.0 |
| 16 | 2026-03-31 | 3 | 1 | 3.0 |
| 16 | 2026-05-26 | 3 | 1 | 3.0 |
| 16 | 2026-03-11 | 3 | 1 | 3.0 |
| 16 | 2026-02-10 | 3 | 1 | 3.0 |
| 18 | 2026-02-20 | 11 | 4 | 2.8 |

**Status: FAIL.** The spike is a **single local day**, Wed 2026-06-03, with 805 events against a normal weekday of about 13. It is **spread across all 15 sites** (5–9% each, 42–69 events per site against about 5 per site per week). It covers all three event types in their usual mix (485 calls, 210 leads, 110 appointments), and the missed-call rate is unchanged at about 24.5%. The days on either side are normal, so this is a one-day event, not a level shift. It could be a real incident such as a hail storm (this is a collision-repair business) or a bulk import. The data can't tell which. No other account has a day above 3.3× its median weekday, and those are small counts (3 vs 1, 10 vs 3). It is the only real spike in the dataset.

### 12d. Partial first and last week

```sql
WITH l AS (SELECT e.account_id, a.timezone, (e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone AS ts
           FROM activity_events e JOIN accounts a ON a.id = e.account_id)
SELECT date_trunc('week', ts)::date AS local_week, count(*) AS events, count(DISTINCT account_id) AS accounts,
       min(ts::date) AS first_local_day, max(ts::date) AS last_local_day, max(ts) AS last_local_ts
FROM l
WHERE date_trunc('week', ts)::date IN ('2026-01-26', '2026-07-27')
GROUP BY 1 ORDER BY 1;
```

| local_week | events | accounts | first_local_day | last_local_day | last_local_ts |
|---|---|---|---|---|---|
| 2026-01-26 | 18 | 8 | 2026-02-01 | 2026-02-01 | 2026-02-01 13:55:16 |
| 2026-07-27 | 79 | 17 | 2026-07-27 | 2026-07-27 | 2026-07-27 17:20:34 |

**Status: INFO.** Both edge weeks contain a single local day: 18 and 79 events. They must not be compared against full weeks. Under the plan's default ("the last complete local week"), the "current" week would be the week of 2026-07-20.

## 13. Time and timezone sanity

### 13a. Valid IANA timezones and observed offsets

```sql
SELECT a.timezone, count(*) AS accounts, (z.name IS NOT NULL) AS in_pg_timezone_names
FROM accounts a LEFT JOIN pg_timezone_names z ON z.name = a.timezone
GROUP BY a.timezone, z.name ORDER BY 1;
```

| timezone | accounts | in_pg_timezone_names |
|---|---|---|
| America/Chicago | 6 | t |
| America/Denver | 2 | t |
| America/Los_Angeles | 4 | t |
| America/New_York | 5 | t |
| America/Phoenix | 2 | t |
| UTC | 1 | t |

**UTC → local offsets actually applied to events**

```sql
SELECT a.timezone,
       min(((e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone) - e.occurred_at) AS min_offset,
       max(((e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone) - e.occurred_at) AS max_offset
FROM activity_events e JOIN accounts a ON a.id = e.account_id
GROUP BY 1 ORDER BY 1;
```

| timezone | min_offset | max_offset |
|---|---|---|
| America/Chicago | -06:00:00 | -05:00:00 |
| America/Denver | -07:00:00 | -06:00:00 |
| America/Los_Angeles | -08:00:00 | -07:00:00 |
| America/New_York | -05:00:00 | -04:00:00 |
| America/Phoenix | -07:00:00 | -07:00:00 |
| UTC | 00:00:00 | 00:00:00 |

**Status: PASS.** All timezones resolve. The DST zones show both their standard and daylight offsets. `America/Phoenix` stays at −07:00 and `UTC` at 00:00, as expected.

### 13b. Future timestamps

```sql
SELECT (now() AT TIME ZONE 'UTC')::timestamp(0) AS now_utc,
       max(occurred_at) AS dataset_max,
       count(*) FILTER (WHERE occurred_at > now() AT TIME ZONE 'UTC') AS events_after_now,
       (SELECT count(*) FROM accounts WHERE created_at > now() AT TIME ZONE 'UTC') AS accounts_created_after_now,
       ((now() AT TIME ZONE 'UTC')::date - max(occurred_at)::date) AS days_since_last_event
FROM activity_events;
```

| now_utc | dataset_max | events_after_now | accounts_created_after_now | days_since_last_event |
|---|---|---|---|---|
| 2026-11-03 16:54:44 | 2026-07-27 22:20:34 | 0 | 0 | 99 |

**Status: PASS / INFO.** No event or account is in the future. But the data ends 99 days before today (2026-11-03). A dashboard that defines "this week" from the wall clock would show empty weeks for every account. The app needs an "as-of" reference date, for example the latest event in the data or a configurable date. That is a design decision, not a data fix.

### 13c. Events near the 2026 US DST switches

```sql
-- US DST 2026: starts Sun 2026-03-08 02:00 local, ends Sun 2026-11-01 02:00 local.
WITH l AS (SELECT a.timezone, (e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone AS ts
           FROM activity_events e JOIN accounts a ON a.id = e.account_id)
SELECT timezone,
       count(*) FILTER (WHERE ts::date BETWEEN '2026-03-07' AND '2026-03-09') AS within_1d_of_mar_08,
       count(*) FILTER (WHERE ts >= '2026-03-08 00:00' AND ts < '2026-03-08 04:00') AS mar_08_00_to_04_local,
       count(*) FILTER (WHERE ts::date BETWEEN '2026-10-31' AND '2026-11-02') AS within_1d_of_nov_01
FROM l GROUP BY 1 ORDER BY 1;
```

| timezone | within_1d_of_mar_08 | mar_08_00_to_04_local | within_1d_of_nov_01 |
|---|---|---|---|
| America/Chicago | 31 | 1 | 0 |
| America/Denver | 10 | 0 | 0 |
| America/Los_Angeles | 24 | 0 | 0 |
| America/New_York | 54 | 0 | 0 |
| America/Phoenix | 8 | 0 | 0 |
| UTC | 4 | 0 | 0 |

**Status: INFO.** 131 events fall within ±1 local day of the 2026-03-08 spring-forward. Only 1 falls between 00:00 and 04:00 local that day, and none falls in the non-existent 02:00–03:00 hour. The 2026-11-01 fall-back is outside the data. Local weeks that contain a DST switch are 167 or 169 hours long. The impact is negligible but worth a unit test (DST zones, Phoenix and UTC).

### 13d. Events whose local date or week differs from UTC

```sql
WITH l AS (SELECT a.timezone, e.occurred_at AS u,
                  (e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone AS ts
           FROM activity_events e JOIN accounts a ON a.id = e.account_id)
SELECT coalesce(timezone, 'ALL') AS timezone, count(*) AS events,
       count(*) FILTER (WHERE ts::date <> u::date) AS different_date,
       round(100.0 * avg((ts::date <> u::date)::int), 2) AS different_date_pct,
       count(*) FILTER (WHERE date_trunc('week', ts) <> date_trunc('week', u)) AS different_week,
       round(100.0 * avg((date_trunc('week', ts) <> date_trunc('week', u))::int), 2) AS different_week_pct,
       count(*) FILTER (WHERE extract(isodow FROM ts) IN (6,7) <> extract(isodow FROM u) IN (6,7)) AS weekend_flag_changes
FROM l GROUP BY ROLLUP (timezone) ORDER BY timezone NULLS LAST;
```

| timezone | events | different_date | different_date_pct | different_week | different_week_pct | weekend_flag_changes |
|---|---|---|---|---|---|---|
| ALL | 12626 | 67 | 0.53 | 8 | 0.06 | 11 |
| America/Chicago | 2995 | 9 | 0.30 | 2 | 0.07 | 2 |
| America/Denver | 1023 | 8 | 0.78 | 3 | 0.29 | 3 |
| America/Los_Angeles | 2511 | 33 | 1.31 | 2 | 0.08 | 5 |
| America/New_York | 4573 | 5 | 0.11 | 1 | 0.02 | 1 |
| America/Phoenix | 936 | 12 | 1.28 | 0 | 0.00 | 0 |
| UTC | 588 | 0 | 0.00 | 0 | 0.00 | 0 |

**Status: INFO.** Only 67 events (0.53%) change calendar date, 8 (0.06%) change week and 11 move between weekday and weekend after conversion. The effect is small because almost no activity happens between 00:00 and 07:00 UTC (check 9). Correct local bucketing is still required. For Los Angeles and Phoenix, about 1.3% of events would land on the wrong day without it.

---

## 14. Inputs for baseline decisions

### 14a. Weekly volume per account

25 complete weeks; account 6's spike week 2026-06-01 is excluded. `dispersion` is variance/mean, where about 1 is Poisson-like. `mad` is the median absolute deviation.

```sql
-- Weekly totals per account over the 25 complete local weeks, with and without
-- account 6's spike week (2026-06-01). Dispersion = variance / mean (1 = Poisson-like).
WITH weeks AS (SELECT generate_series('2026-02-02'::date, '2026-07-20'::date, '7 days')::date AS wk),
l AS (SELECT e.account_id,
             date_trunc('week', (e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone)::date AS wk
      FROM activity_events e JOIN accounts a ON a.id = e.account_id),
c AS (SELECT a.id AS account_id, w.wk, count(l.wk) AS n
      FROM accounts a CROSS JOIN weeks w
      LEFT JOIN l ON l.account_id = a.id AND l.wk = w.wk
      GROUP BY 1, 2),
x AS (SELECT * FROM c WHERE NOT (account_id = 6 AND wk = '2026-06-01'))
SELECT account_id, count(*) AS weeks, min(n) AS min,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY n) AS median,
       round(avg(n), 1) AS mean, round(stddev_samp(n), 1) AS std,
       round(stddev_samp(n) / nullif(avg(n), 0), 2) AS cv,
       round(var_samp(n) / nullif(avg(n), 0), 2) AS dispersion,
       max(n) AS max,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY abs(n - m.med)) AS mad
FROM x JOIN (SELECT account_id, percentile_cont(0.5) WITHIN GROUP (ORDER BY n) AS med FROM x GROUP BY 1) m
     USING (account_id)
GROUP BY account_id ORDER BY account_id;
```

| account_id | weeks | min | median | mean | std | cv | dispersion | max | mad |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 36 | 50 | 48.5 | 7.7 | 0.16 | 1.22 | 62 | 6 |
| 2 | 25 | 18 | 31 | 29.2 | 5.9 | 0.20 | 1.19 | 37 | 3 |
| 3 | 25 | 10 | 19 | 19.0 | 5.1 | 0.27 | 1.36 | 29 | 3 |
| 4 | 25 | 21 | 32 | 31.6 | 5.7 | 0.18 | 1.02 | 42 | 4 |
| 5 | 25 | 23 | 34 | 34.8 | 7.8 | 0.22 | 1.75 | 53 | 6 |
| 6 | 24 | 50 | 76 | 72.8 | 13.2 | 0.18 | 2.38 | 102 | 9.5 |
| 7 | 25 | 11 | 17 | 17.3 | 2.9 | 0.17 | 0.48 | 22 | 2 |
| 8 | 25 | 7 | 11 | 10.4 | 1.9 | 0.18 | 0.35 | 14 | 1 |
| 9 | 25 | 12 | 22 | 21.6 | 4.6 | 0.21 | 0.96 | 31 | 3 |
| 10 | 25 | 10 | 13 | 13.5 | 2.2 | 0.16 | 0.35 | 18 | 2 |
| 11 | 25 | 8 | 14 | 14.1 | 2.7 | 0.19 | 0.51 | 20 | 2 |
| 12 | 25 | 32 | 53 | 51.6 | 9.9 | 0.19 | 1.89 | 68 | 8 |
| 13 | 25 | 4 | 9 | 8.2 | 2.0 | 0.25 | 0.51 | 11 | 2 |
| 14 | 25 | 16 | 25 | 25.4 | 4.9 | 0.19 | 0.96 | 40 | 3 |
| 15 | 25 | 12 | 20 | 19.8 | 4.6 | 0.23 | 1.07 | 33 | 3 |
| 16 | 25 | 2 | 7 | 6.6 | 2.1 | 0.32 | 0.66 | 9 | 2 |
| 17 | 25 | 6 | 13 | 12.8 | 3.1 | 0.25 | 0.77 | 18 | 2 |
| 18 | 25 | 17 | 24 | 23.4 | 4.0 | 0.17 | 0.70 | 30 | 3 |
| 19 | 25 | 5 | 8 | 8.3 | 2.2 | 0.27 | 0.60 | 13 | 2 |
| 20 | 25 | 0 | 0 | 0.0 | 0.0 | NULL | NULL | 0 | 0 |

**Account 6, with and without the spike week**

```sql
WITH weeks AS (SELECT generate_series('2026-02-02'::date, '2026-07-20'::date, '7 days')::date AS wk),
c AS (SELECT w.wk, count(e.id) AS n
      FROM weeks w
      LEFT JOIN activity_events e
        ON e.account_id = 6
       AND date_trunc('week', (e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE 'America/New_York')::date = w.wk
      GROUP BY 1)
SELECT 'with spike week' AS series, percentile_cont(0.5) WITHIN GROUP (ORDER BY n) AS median,
       round(avg(n), 1) AS mean, round(stddev_samp(n), 1) AS std FROM c
UNION ALL
SELECT 'without spike week', percentile_cont(0.5) WITHIN GROUP (ORDER BY n),
       round(avg(n), 1), round(stddev_samp(n), 1) FROM c WHERE wk <> '2026-06-01';
```

| series | median | mean | std |
|---|---|---|---|
| with spike week | 76 | 105.1 | 162.2 |
| without spike week | 76 | 72.8 | 13.2 |

**Status: INFO.**
- Account weekly CV ranges from 0.16 to 0.32. Most accounts are close to Poisson noise (dispersion 0.35–1.9). Account 6 is somewhat over-dispersed (2.4) even without the spike.
- The spike week raises account 6's mean from 72.8 to 105.1 and its std from 13.2 to 162.2. A mean ± k·std band would be useless for about N weeks after the spike. The median (76) doesn't move.
- MAD is small: 1–3 for most accounts. For #8 it is 1, so a pure median ± k·MAD band would flag ±2–3 events. That supports the plan's idea of a minimum % or absolute floor.
- The smallest accounts (#13, #16, #19) have a median of 7–9 events per week, with lows of 2–5.

### 14b. Weekly volume per location

Locations are grouped by their weekly median; account 6's spike week is excluded.

```sql
-- Distribution of per-location weekly medians (25 complete weeks; account 6 spike week excluded).
WITH weeks AS (SELECT generate_series('2026-02-02'::date, '2026-07-20'::date, '7 days')::date AS wk),
l AS (SELECT e.account_id, e.location,
             date_trunc('week', (e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone)::date AS wk
      FROM activity_events e JOIN accounts a ON a.id = e.account_id),
loc AS (SELECT DISTINCT account_id, location FROM l),
c AS (SELECT lo.account_id, lo.location, w.wk, count(l.wk) AS n
      FROM loc lo CROSS JOIN weeks w
      LEFT JOIN l ON l.account_id = lo.account_id AND l.location = lo.location AND l.wk = w.wk
      WHERE NOT (lo.account_id = 6 AND w.wk = '2026-06-01')
      GROUP BY 1, 2, 3),
s AS (SELECT account_id, location, percentile_cont(0.5) WITHIN GROUP (ORDER BY n) AS med,
             avg(n) AS mean, stddev_samp(n) / nullif(avg(n), 0) AS cv, min(n) AS mn
      FROM c GROUP BY 1, 2)
SELECT CASE WHEN med <= 5 THEN 'a: 4-5' WHEN med <= 7 THEN 'b: 6-7' WHEN med <= 9 THEN 'c: 8-9' ELSE 'd: 10-11' END
         AS weekly_median_bucket,
       count(*) AS locations, round(avg(cv), 2) AS avg_cv, min(mn) AS lowest_week,
       round(avg(1 / sqrt(mean)), 2) AS avg_poisson_cv
FROM s GROUP BY 1 ORDER BY 1;
```

| weekly_median_bucket | locations | avg_cv | lowest_week | avg_poisson_cv |
|---|---|---|---|---|
| a: 4-5 | 21 | 0.47 | 0 | 0.45 |
| b: 6-7 | 24 | 0.38 | 1 | 0.39 |
| c: 8-9 | 19 | 0.34 | 1 | 0.35 |
| d: 10-11 | 5 | 0.28 | 2 | 0.32 |

**Status: INFO.** Every location has a weekly median between 4 and 11. The observed CV (0.28–0.47) matches the Poisson expectation 1/√mean almost exactly, so location-level week-to-week variation is pure count noise. For a location with a median of 5, a ±50% swing is a normal week. 21 locations have a median of 5 or below: 14 of account 6's 15 sites, all 5 of account 18's, and one site each in accounts 12 and 15.

### 14c. Trend and level shift

Median weekly count, first 8 vs last 8 complete weeks.

```sql
-- Level shift check: median weekly count, first 8 vs last 8 complete weeks.
WITH weeks AS (SELECT generate_series('2026-02-02'::date, '2026-07-20'::date, '7 days')::date AS wk),
l AS (SELECT e.account_id,
             date_trunc('week', (e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone)::date AS wk
      FROM activity_events e JOIN accounts a ON a.id = e.account_id),
c AS (SELECT a.id AS account_id, w.wk, count(l.wk) AS n
      FROM accounts a CROSS JOIN weeks w LEFT JOIN l ON l.account_id = a.id AND l.wk = w.wk
      WHERE a.id <> 20 GROUP BY 1, 2)
SELECT account_id,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY n) FILTER (WHERE wk <  '2026-03-30') AS median_first_8,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY n) FILTER (WHERE wk >= '2026-06-01') AS median_last_8,
       round(((percentile_cont(0.5) WITHIN GROUP (ORDER BY n) FILTER (WHERE wk >= '2026-06-01'))
         / (percentile_cont(0.5) WITHIN GROUP (ORDER BY n) FILTER (WHERE wk < '2026-03-30')))::numeric, 2) AS ratio
FROM c GROUP BY 1 ORDER BY ratio DESC;
```

| account_id | median_first_8 | median_last_8 | ratio |
|---|---|---|---|
| 12 | 47.5 | 56 | 1.18 |
| 18 | 22.5 | 25 | 1.11 |
| 3 | 18.5 | 20.5 | 1.11 |
| 14 | 25 | 27 | 1.08 |
| 5 | 31.5 | 34 | 1.08 |
| 2 | 31 | 33 | 1.06 |
| 17 | 12 | 12.5 | 1.04 |
| 4 | 30.5 | 31.5 | 1.03 |
| 6 | 77 | 77.5 | 1.01 |
| 19 | 7 | 7 | 1.00 |
| 16 | 6.5 | 6.5 | 1.00 |
| 1 | 47.5 | 47 | 0.99 |
| 11 | 15.5 | 15 | 0.97 |
| 10 | 13.5 | 12.5 | 0.93 |
| 7 | 18 | 16.5 | 0.92 |
| 15 | 21.5 | 19.5 | 0.91 |
| 8 | 11 | 10 | 0.91 |
| 9 | 21 | 19 | 0.90 |
| 13 | 9 | 8 | 0.89 |

**Status: INFO.** Ratios run from 0.89 to 1.18, with no strong trend or level shift in any account. A shorter window (4 weeks) would gain little in adaptivity, and a longer one (8–12 weeks) gives more stable medians. Seasonality can't be assessed with 26 weeks (already noted in the plan).

### 14d. Daily volume: weekday vs weekend days

Complete weeks only; account 6's spike day is excluded.

```sql
-- Daily volume per account on local weekdays vs weekends (complete weeks, account 6 spike day excluded).
WITH days AS (SELECT generate_series('2026-02-02'::date, '2026-07-26'::date, '1 day')::date AS d),
l AS (SELECT e.account_id, ((e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE a.timezone)::date AS d
      FROM activity_events e JOIN accounts a ON a.id = e.account_id),
c AS (SELECT a.id AS account_id, days.d, count(l.d) AS n
      FROM accounts a CROSS JOIN days LEFT JOIN l ON l.account_id = a.id AND l.d = days.d
      WHERE a.id <> 20 AND NOT (a.id = 6 AND days.d = '2026-06-03')
      GROUP BY 1, 2)
SELECT account_id,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY n) FILTER (WHERE extract(isodow FROM d) < 6) AS median_weekday,
       round(avg(n) FILTER (WHERE extract(isodow FROM d) < 6), 1) AS mean_weekday,
       round(100.0 * avg((n = 0)::int) FILTER (WHERE extract(isodow FROM d) < 6), 1) AS zero_weekday_pct,
       round(avg(n) FILTER (WHERE extract(isodow FROM d) >= 6), 1) AS mean_weekend_day,
       round(100.0 * avg((n = 0)::int) FILTER (WHERE extract(isodow FROM d) >= 6), 1) AS zero_weekend_day_pct
FROM c GROUP BY 1 ORDER BY 1;
```

| account_id | median_weekday | mean_weekday | zero_weekday_pct | mean_weekend_day | zero_weekend_day_pct |
|---|---|---|---|---|---|
| 1 | 9 | 8.7 | 1.6 | 2.5 | 2.0 |
| 2 | 6 | 5.2 | 3.2 | 1.5 | 10.0 |
| 3 | 3 | 3.4 | 5.6 | 0.9 | 26.0 |
| 4 | 6 | 5.7 | 4.0 | 1.7 | 12.0 |
| 5 | 6 | 6.2 | 2.4 | 2.0 | 4.0 |
| 6 | 13 | 12.8 | 3.2 | 4.7 | 6.0 |
| 7 | 3 | 3.2 | 1.6 | 0.7 | 40.0 |
| 8 | 2 | 1.9 | 9.6 | 0.4 | 64.0 |
| 9 | 4 | 3.9 | 3.2 | 1.0 | 18.0 |
| 10 | 2 | 2.5 | 7.2 | 0.5 | 54.0 |
| 11 | 3 | 2.6 | 4.8 | 0.6 | 42.0 |
| 12 | 9 | 9.2 | 1.6 | 2.7 | 6.0 |
| 13 | 2 | 1.6 | 11.2 | 0.1 | 90.0 |
| 14 | 4 | 4.6 | 4.0 | 1.3 | 20.0 |
| 15 | 4 | 3.6 | 5.6 | 0.8 | 34.0 |
| 16 | 1 | 1.3 | 16.0 | 0.1 | 90.0 |
| 17 | 2 | 2.4 | 9.6 | 0.4 | 60.0 |
| 18 | 4 | 4.2 | 2.4 | 1.1 | 22.0 |
| 19 | 2 | 1.6 | 15.2 | 0.2 | 76.0 |

**Status: INFO.** Median weekday counts are 1–13 per account. Mean weekend-day counts are 0.1–4.7, and for 6 accounts most weekend days have zero events (#13 and #16: 90% of weekend days are empty). Comparing the same weekday (option B) or individual days would be dominated by count noise for most accounts. Weekly totals (option A) have far more stable counts.

---

## Candidate cleaning rules

These are options only. The policy will be decided in the next iteration and applied in the `clean_activity_events` view. The raw tables stay untouched.

| # | Issue | Rows affected | Options |
|---|---|---|---|
| R1 | Exact duplicates: same account, location, type and `occurred_at`; all other columns equal (10a) | 12 surplus rows in 12 pairs (24 rows involved) | **Exclude** surplus: keep one row per group, e.g. `min(id)`. **Keep** all: inflates counts by 12. **Flag** with an `is_duplicate` column. |
| R2 | Near-duplicates within 1–60 s (10b) | 2 pairs ≤ 5 s, 25 pairs at 6–60 s; none match on all attributes at ≤ 5 s | **Keep**: they look like distinct events. **Exclude** pairs under a gap threshold. **Flag** for review. |
| R3 | Account 6 one-day spike, 2026-06-03 (12c) | 805 events (30% of account 6's total), all 15 sites | **Keep** in the raw counts but make the baseline robust (median/MAD, or exclude outlier weeks from the baseline window only). **Exclude** the day from the baseline. **Flag** the day or week as anomalous. Excluding it from the *reported* totals would hide a possibly real event. |
| R4 | NULL `outcome` (11b) | 398 rows (240 calls, 100 leads, 58 appointments) | **Keep**: irrelevant to a total-events metric. **Exclude** only from outcome-rate metrics. **Flag** or map to `unknown`. |
| R5 | NULL `duration_seconds` on calls (11d) | 313 calls (6 also have NULL outcome) | **Keep**: irrelevant to a total-events metric. **Exclude** from any duration metric. **Flag**. |
| R6 | `missed` calls with a long duration (11e) | 1,937 missed calls, all with plausible-looking durations except 76 NULLs | **Keep** as is. **Treat** duration as unreliable for missed calls. **Flag**. |
| R7 | Partial edge weeks (12d) | 18 events (week of 2026-01-26), 79 events (week of 2026-07-27) | **Exclude** from baselines and verdicts. **Keep** but label as partial. **Flag** the week as incomplete. |
| R8 | Activity outside 07:00–19:00 local (9) | 2,593 events (20.5%) | **Keep**: probably a timestamp-generation artefact, not bad rows. **Exclude**: would remove up to 31% of west-coast data. **Flag** only for display. |
| R9 | Weekend activity (6) | 1,167 events (9.2%) | **Keep** within weekly Mon–Sun totals. **Exclude** in a weekday-only baseline: loses 9% of the data. **Flag** weekend days separately in daily views. |
| R10 | Account with no events (3) | 1 account (#20), 0 rows | **Keep** the account and show a "not enough history" state. **Exclude** it from the dashboard list. |
| R11 | Data ends 99 days before `now()` (13b) | All rows | Not a row rule. **Anchor** "current week" to the latest event or a configured as-of date, **or** use the wall clock and show empty weeks. |
