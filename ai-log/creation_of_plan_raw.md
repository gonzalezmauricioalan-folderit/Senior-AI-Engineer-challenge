 ▐▛███▛█   Claude Code v2.1.317
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   /home/admin123/projects/qualitra_challenge

  Get to finished work sooner with Opus 5.5. Switch anytime with /model.
  1 more notice hidden

! git status                                                                    
  ⎿  On branch main

     No commits yet
     … +7 lines (ctrl+o to expand)

● The repo has no commits yet, and the only thing in it is the untracked
  relay-analytics-starter/ directory.

  What would you like to do next? I could make an initial commit, look through
  the starter project, or work on something specific in it.

✻ Churned for 2s · done 2:20 PM

❯ create gitignore and add relay-analytics-starter/                             

  Listed 1 directory, ran 1 shell command (ctrl+o to expand)

● Write(.gitignore)
  ⎿  Wrote 27 lines to .gitignore
       1 # OS
       2 .DS_Store
       3 Thumbs.db
       4 
       5 # Editors
       6 .vscode/
       7 .idea/
       8 *.swp
       9 
      10 # Environment / secrets
     … +17 lines (ctrl+o to expand)

● User answered Claude's questions:
  ⎿  · relay-analytics-starter/ is its own git repo (1 commit, origin 
     github.com/Qualitara/relay-analytics-starter). A plain `git add` would only
     record a commit pointer, not the files. How should it be added? → remove 
     that .git of that folder for now and add the folder to gitignore

  Ran 1 shell command (ctrl+o to expand)

● I added a .gitignore at the repo root and staged it. Git now ignores
  relay-analytics-starter/ instead of tracking it. Nothing is committed yet.

  - .gitignore: covers the usual noise: OS and editor files, .env* (but not
    .env.example), dependency and build folders, Python caches, logs and local
    database files. relay-analytics-starter/ is listed at the end.
  - relay-analytics-starter/.git: deleted, as you asked. That repo had a single
    commit, and it's still on GitHub at
    github.com/Qualitara/relay-analytics-starter. The folder's files are
    untouched.

  git status now shows only .gitignore, staged and ready to commit.

✻ Churned for 22s · done 2:23 PM

❯ /init                                                                         

  Listed 1 directory, ran 2 shell commands (ctrl+o to expand)

● Write(CLAUDE.md)
  ⎿  Wrote 42 lines to CLAUDE.md
       1 # CLAUDE.md
       2 
       3 This file provides guidance to Claude Code (claude.ai/code) when
          working with code in this repository.
       4 
       5 ## What this repo is
       6 
       7 A take-home exercise for "Relay", a fictional B2B SaaS that trac
         ks inbound customer activity (calls, leads, appointments) across
          a customer's locations. The task is ticket **DASH-247** (`relay
     … +36 lines (~3 KB) (ctrl+o to expand)

● I've created CLAUDE.md at the repo root. There's no application code yet, so
  it has no build, lint or test commands. It has a note to add them once you
  pick a stack.

  What it covers:
  - The task: ticket DASH-247, help a customer see whether this week's activity
    is normal for them. It lists product's hints and what's out of scope
    (alerting and ML/forecasting).
  - Starter README rules:
    - Load the schema through your own migrations, not by hand.
    - Use the seed data as-is.
    - Don't keep the relay-analytics-starter name.

    It also notes that the starter folder is gitignored and kept only for
    reference.
  - Data model: the two tables, which outcomes go with which event type, and the
    fact that timestamps are UTC. "This week" has to be worked out in each
    account's own timezone.
  - Data quirks: I loaded the seed into a throwaway SQLite database and checked
    it. It loads unmodified, and these are worth knowing before designing a
    baseline:
    - Account 20 has no events at all.
    - Account 6 has a big spike across many of its 15 sites starting around
      2026-06-03.
    - There are about 12 groups of exact duplicate events with different IDs.
    - About 400 rows have no outcome, and some calls have no duration.
    - Location names like "Site A" repeat across accounts, so they're only
      unique within one account.
    - Timezones include Phoenix (no daylight saving) and plain UTC.

  CLAUDE.md is not staged or committed yet.

✻ Worked for 53s · done 2:24 PM

! code .                                                                        
  ⎿  /bin/bash: line 1: code: command not found

● code isn't available in this sandbox. VS Code runs on your host, not in here.
  If you're on direct-mount mode, open the folder from a host terminal instead:

  code /path/to/qualitra_challenge

  If you're not sure which mode you're in, run ! [ -d /run/sandbox/source ] && 
  echo clone || echo direct. In clone mode, your files only reach the host once
  you fetch them: git fetch sandbox-<name>.

✻ Crunched for 2s · done 2:25 PM

❯ i just write the @PLAN_first_iteration.md check it. lets create PLAN.MD do    
  not write code yet or the PLAN.MD, lets talk to clear up the items with * .   
  lets go one item at the time (write at the end of the first iteration the     
  resutls). (if possible give me the option to select different questions or to 
  clarify something). Remember that the goal is to complete the challenge       
  ⎿  Read PLAN_first_iteration.md (65 lines)
  ⎿  1 skill available

● Your plan has 4 items marked with *. We'll go through them one at a time, and
  I'll collect the decisions so they can go into PLAN.md once this round is
  done:

  1. Extra integrity checks (line 14)
  2. How to act on bad data (line 15)
  3. Which baseline window to use (line 24)
  4. How to flag a week or day that needs attention (lines 25–29)

  Item 1: extra integrity checks. Your list already covers range, orphans,
  distinct values, weekends, top locations, events before account creation, and
  events outside business hours. Here's what I'd add, grouped by what each group
  protects:

● User answered Claude's questions:
  ⎿  · Item 1/4 — Which additional integrity checks should go into 
     Data_integrity.md? (pick any; use Other to propose your own or ask about 
     one) → Duplicates, Field consistency, Coverage gaps & spikes, Time & 
     timezone sanity

● Item 1 is settled with all four groups included. For item 2, the README
  requires the seed to stay as-is, so raw tables can't be modified, and any
  cleanup or bucketing must work identically on SQLite (integration tests) and
  Postgres (dev), since SQLite lacks materialized views and IANA timezone
  conversion.

● User declined to answer questions
  ⎿  · Item 2/4 — Where should bad data be handled? (View + Python bucketing 
     (Rec.) / Medallion (bronze/silver/gold) / Only in application code)
     · Item 2/4 — For questionable rows, exclude them or keep and count them? 
     (Dedupe only, keep the rest (Rec.) / Exclude anything suspicious / Keep 
     everything, flag it)

● What would you like to clarify about item 2? It could be the options
  themselves, the SQLite vs. Postgres limitation, what counts as "bad data", or
  something else. Once I know, I'll rework the questions.

✻ Brewed for 33s · done 4:26 PM

❯ Talk to me about the different pros and cons. Remember that this is a         
  challenge. We can clarify that the approach is not ideal and that in the real 
  world, in a production database, we will suggest something else.              

● Here's how they compare, with the fact that this is a challenge in mind.

  Where to handle bad data

  A. Raw tables + a cleaning SQL view, timezone bucketing in Python
  - ✅ Follows the README: the seed stays untouched, and the cleaning rules are
    visible SQL a reviewer can read in one place.
  - ✅ A plain view works the same on Postgres and SQLite, so your integration
    tests exercise the real rules.
  - ✅ Doing the UTC → local-day conversion in Python (zoneinfo) avoids SQLite's
    lack of timezone support and is easy to unit-test, including DST and
    Phoenix.
  - ❌ It re-aggregates on every request. That's fine for about 12.6k rows but
    wouldn't scale to millions.
  - ❌ It splits the logic in two: cleaning in SQL, bucketing in Python.

  B. Medallion (bronze → silver → gold)
  - ✅ It's the "real" data-engineering answer: auditable layers, fast reads
    from pre-aggregated daily counts, and room for late-arriving data.
  - ❌ It needs a refresh job or triggers plus a way to orchestrate it, which is
    a lot of moving parts for 20 accounts.
  - ❌ The gold table has to be keyed by local date, so the timezone logic moves
    into the ETL anyway.
  - ❌ Reviewers may read it as overengineering for the size of the ticket,
    which is your own instinct too.

  C. Only in application code
  - ✅ Simplest database, and everything is in one language.
  - ❌ The cleaning rules are buried in code. A reviewer or analyst can't just
    SELECT from the cleaned data, and the integrity report and the API could
    drift apart.

  My take: use A for the challenge. In the write-up, say that in production
  you'd move toward B: a daily rollup per account, location and local date,
  refreshed incrementally. That would be a stored table or a Postgres
  materialized view, not a SQLite-compatible one. Reviewers get to see that you
  weighed the tradeoff without you paying the cost of building B.

  What to do with questionable rows

  1. Remove exact duplicates, keep everything else
  - ✅ Duplicates are the only quirk that clearly inflates the thing we measure,
    which is activity volume. A call with a NULL outcome is still a call.
  - ✅ It's easy to defend, and each rule has a count you can show in
    Data_integrity.md.
  - ❌ It assumes the duplicates are ingestion double-writes. Two genuinely
    separate calls in the same second are possible but unlikely.

  2. Exclude anything suspicious (NULLs, events outside business hours, the
  spike…)
  - ✅ The numbers look clean.
  - ❌ It undercounts real activity, and it hides exactly the signal the ticket
    is about. The account 6 spike might be the "not normal" week the customer
    needs to see.
  - ❌ It goes against the spirit of "treat it like messy production data and
    handle it."

  3. Keep everything and flag it
  - ✅ The most transparent option: the API can say how many duplicate rows a
    number includes.
  - ❌ It adds flag columns or extra counts that the UI has to explain. That's
    extra scope for little value at this size.

  My take: use 1, and treat events outside business hours and on weekends as
  reported, not excluded. The account 6 spike is a question for the baseline
  (item 3), not a cleaning rule. For production, you'd note that duplicates
  should be fixed at ingestion with an idempotency key or a unique constraint.

● User answered Claude's questions:
  ⎿  · Item 2/4 — Where should bad data be handled? → A: View + Python 
     (Recommended)
     · Item 2/4 — Policy for questionable rows? → This decision will be in the 
     next iteration. First let's clear up the plan a bit. In the next iteration 
     we will run the different queries to detect the data integrity and we will 
     define what to do on that view. We for sure will de-duplicate data but 
     probably something else 
● Item 2 is decided:
  - Mechanism: option A. The raw tables stay untouched, a portable SQL view does
    the cleaning, and Python handles the timezone bucketing. The write-up will
    name a medallion-style rollup as the production path.
  - Policy: you're deferring it to the next iteration, after the integrity
    queries have run. Deduplication is certain, and other rules may follow.

  Item 3: which baseline window

  First, a fact that settles one of your options: year-over-year isn't possible.
  Events only cover 2026-02-01 → 2026-07-27, about 26 weeks. The accounts were
  created in 2025, but there's no 2025 activity. So we can't measure
  seasonality, and the honest answer is to say so: "not handled; it would need
  ≥1 year of history."

  That leaves your other two ideas. Here's how I read them:

  A. Trailing N complete weeks (this week vs. the previous N weeks, Mon–Sun in
  local time)
  - ✅ Matches the Monday-morning question directly: "was last week normal?"
  - ✅ Weekly totals smooth out day-to-day noise and handle weekends
    automatically, because every week includes them.
  - ✅ Simple to explain: "your average over the last 8 weeks was X."
  - ❌ It can't answer "was Tuesday odd?"
  - ❌ It reacts slowly to a level shift. After account 6's spike starts, the
    baseline climbs for weeks.

  B. Same weekday over the previous N weeks (this Monday vs. the last 8 Mondays)
  - ✅ The right baseline for a daily view, because Mondays and Saturdays really
    do differ for service businesses.
  - ✅ It handles weekends naturally. There's no need to drop Sat/Sun, since
    each day is compared to its own weekday.
  - ❌ Only N data points per weekday, so small single-site accounts get very
    noisy baselines (zero vs. one event).
  - ❌ A single holiday distorts one weekday's baseline.

  C. Previous N weekdays, skipping Sat/Sun
  - ✅ Simple, and fine if the businesses are closed on weekends.
  - ❌ It assumes everyone works Mon–Fri. Barbers, gyms and spas are often
    busiest on weekends, and the integrity check will show whether weekend
    events exist. It also mixes Mondays with Fridays.

  Window length (N): 4 weeks reacts quickly but is noisy. 8 weeks is a common
  middle ground. 12+ weeks is stable, but with 26 weeks of data it leaves little
  to evaluate. Whatever N we pick, we also need a minimum-history rule: below
  it the UI says "not enough history" instead of a verdict. That covers account
  20 and new locations.

  My take: use A with N = 8 as the primary weekly view, since it answers the
  Monday question, and B for the daily drill-down if the day view stays in
  scope. Default to the last complete local week. Monday morning shouldn't show
  a two-hour-old partial week.

● User answered Claude's questions:
  ⎿  · Item 3/4 — Which baseline comparison(s)? → Let's skip this decision to 
     the next iteration too because maybe there are some accounts that work on 
     Saturday for example. 
     · Item 3/4 — Baseline window length N (weeks)? → Decide after data checks
     · Item 3/4 — Minimum history before showing a verdict? → 4 weeks 
     (Recommended)

● Item 3 is decided:
  - Comparison type (week vs. day vs. weekdays only): deferred to the next
    iteration, because the weekend and business-hours checks will show which
    accounts work Saturdays.
  - Window length N: decided after the data checks.
  - Minimum history: 4 complete weeks. Below that, the UI shows the totals with
    "not enough history yet."

  Item 4: how to flag "needs attention"

  Each method needs a center (what's typical) and a spread (how far from typical
  counts as unusual).

  1. Mean ± k·standard deviation (z-score)
  - ✅ Widely known and easy to compute in SQL or Python.
  - ❌ It isn't robust: one spike week, like account 6's in June, inflates both
    the mean and the std. Later spikes then look "normal," and real dips get
    missed.
  - ❌ With 8 points and small counts, the std is unstable.

  2. Median ± k·MAD (median absolute deviation)
  - ✅ Robust: a few abnormal weeks barely move the baseline. That's exactly the
    messy-data case.
  - ✅ Still simple to explain: "a typical week is about 45 calls; this week
    was 22."
  - ❌ MAD can be 0 for very stable or very sparse series, so a ±1 change gets
    flagged. That needs a floor.
  - ❌ Slightly less familiar to non-technical reviewers.

  3. Percent change vs. median (e.g. ±25%)
  - ✅ The easiest for a customer to read: "30% below your usual."
  - ❌ It ignores natural variability. ±25% is huge for a stable 15-site group
    and tiny for a shop doing 3 calls a week (3 → 2 is −33%).

  4. Percentile / historical range (e.g. outside the min–max or the 10th–90th
  percentile of the last N weeks)
  - ✅ Intuitive: "lowest week in 8 weeks."
  - ❌ With N = 8, percentiles are coarse, and min/max is set by a single
    outlier.

  5. Poisson / count-based test
  - ✅ Statistically right for small event counts, and it handles the
    3-calls-a-week shop well.
  - ❌ Hard to explain on a dashboard, and close to the "ML/forecasting" line
    that's out of scope.

  My take: use 2 + 3 combined. Flag only when the value is beyond median ± k·MAD
  and the absolute or percent difference passes a small floor (e.g. ≥ 20% and ≥
  3 events). That suppresses noise on small accounts. Show the customer the
  percent difference ("38% below your usual week"), not the statistics. Three
  states: Normal / Higher than usual / Lower than usual, plus Not enough 
  history.

  Two related questions are worth deciding too: what gets measured, and how 
  multi-location is shown. Product called out multi-location explicitly.

● User answered Claude's questions:
  ⎿  · Item 4/4 — Which detection method? → Compare on data first
     · Item 4/4 — What gets evaluated as normal or not? → "total events for the 
     sake of simplicity, we have to add a note that in a real project, we should
     ask about what option add more value and probably we don't have a good 
     volume of data to split in event types"
     · Item 4/4 — How should multi-location accounts be shown? → Account + 
     ranked locations (Rec.)

● Bash(cat >> PLAN_first_iteration.md <<'EOF'…)
  ⎿  Updated PLAN_first_iteration.md (+48 -1)
       62  - The accounts use normal working days and hours
       63  
       64  # Use of an LLM
       65 -- In this ticket in particular, we won't use an LLM because it
          - won't add relevant value to explain why this day is not norma
          -l, for example, because it won't have the data to explain why 
          -the number is lower than expected                             
       65 +- In this ticket in particular, we won't use an LLM because it
          + won't add relevant value to explain why this day is not norma
          +l, for example, because it won't have the data to explain why 
          +the number is lower than expected                             
       66 +------                                                        
       67 +                                                              
       68 +# Results of first iteration discussion                       
       69 +                                                              
       70 +## 1. Additional data integrity checks (line 14) — DECIDED    
       71 +Add to Data_integrity.md, on top of the original list:        
       72 +- **Duplicates**: exact duplicates (same account + location + 
          +event_type + occurred_at, different id; the init profile found
          + ~12 groups) and near-duplicates (same key within a few second
          +s).                                                           
       73 +- **Field consistency**: outcome valid for its event_type, NUL
          +L outcome rate per type, duration only on calls, NULL/zero/neg
          +ative/outlier durations, casing/whitespace in location and enu
          +m values.                                                     
       74 +- **Coverage gaps & spikes**: per account/location, days or we
          +eks with zero events, locations starting or stopping mid-range
          +, sudden spikes (account 6 around 2026-06-03), partial first/l
          +ast week.                                                     
       75 +- **Time & timezone sanity**: valid IANA timezones, no future 
          +timestamps, events near DST switches, how many events change d
          +ay/week after UTC → local conversion.                         
       76 +                                                              
       77 +## 2. Act on bad data (line 15) — PARTIALLY DECIDED           
       78 +- **Mechanism: DECIDED.** Raw tables (`accounts`, `activity_ev
          +ents`) stay untouched (the seed is used as-is). A plain, porta
          +ble SQL view (`clean_activity_events`) applies the cleaning ru
          +les, so it behaves the same on Postgres and on SQLite in tests
          +. UTC → account-local day/week bucketing is done in Python (`z
          +oneinfo`), because SQLite has no IANA timezone support.       
       79 +  - Pros: cleaning rules readable in one place, portable, easy
          + to unit-test (DST, America/Phoenix, UTC).                    
       80 +  - Cons: re-aggregates per request (fine for ~12.6k rows); lo
          +gic split between SQL and Python.                             
       81 +  - **Production note for write-up:** a medallion-style approa
          +ch (or a daily rollup per account/location/local date, refresh
          +ed incrementally) would be preferred at real volume; it's over
          +engineering for this challenge.                               
       82 +- **Policy: DEFERRED to next iteration**, after running the in
          +tegrity queries. De-duplication is certain (production note: p
          +revent at ingestion with an idempotency key / unique constrain
          +t). Other rules will be defined on the view based on the check
          + results.                                                     
       83 +                                                              
       84 +## 3. Baseline (line 24) — PARTIALLY DECIDED                  
       85 +- **Year-over-year / seasonality: NOT POSSIBLE.** Events only 
          +span 2026-02-01 → 2026-07-27 (~26 weeks), so seasonality isn't
          + handled. Document it as a limitation (would need ≥ 1 year of 
          +history).                                                     
       86 +- **Comparison type: DEFERRED to next iteration** (depends on 
          +weekend/business-hours checks; some accounts may work Saturday
          +s). Candidates:                                               
       87 +  - A. Trailing N complete local weeks (Mon–Sun): answers "was
          + last week normal?", smooths noise, includes weekends naturall
          +y; can't answer per-day questions, slow to adapt to level shif
          +ts.                                                           
       88 +  - B. Same weekday over previous N weeks: right for a daily v
          +iew, handles weekends; noisy for small accounts, sensitive to 
          +holidays.                                                     
       89 +  - C. Previous N weekdays excluding Sat/Sun: simple, but assu
          +mes Mon–Fri businesses and mixes weekdays.                    
       90 +- **Window length N: DEFERRED**; decide after looking at weekl
          +y variance (candidates 4 / 8 / 12 weeks).                     
       91 +- **Minimum history: DECIDED, 4 complete weeks.** Below that, 
          +show totals with "not enough history yet" instead of a verdict
          + (covers account 20 with no events and new locations).        
       92 +- Default period (proposal): the last complete week in the acc
          +ount's local time, not the current partial week.              
       93 +                                                              
       94 +## 4. How to flag normal vs needs attention (lines 25–29) — PA
          +RTIALLY DECIDED                                               
       95 +- **Method: DEFERRED.** In the next iteration, run 2–3 methods
          + on the seed and pick the one with the most sensible flags. Ca
          +ndidates:                                                     
       96 +  - Mean ± k·std: familiar, but one spike week inflates mean a
          +nd std.                                                       
       97 +  - Median ± k·MAD: robust to outlier weeks; MAD can be 0 for 
          +sparse/stable series, so it needs a floor.                    
       98 +  - Percent change vs median: easiest for customers to read; i
          +gnores natural variability (3 → 2 calls = −33%).              
       99 +  - Percentile / min–max range: intuitive, but coarse with sma
          +ll N.                                                         
      100 +  - Poisson/count-based test: statistically right for small co
          +unts, hard to explain, close to the out-of-scope ML/forecastin
          +g line.                                                       
     … 12 more lines (ctrl+o to expand)

● We've been through all four starred items. I've added the results as a new
  section at the end of PLAN_first_iteration.md, as you asked. PLAN.md and code
  are untouched.

  ┌───────────┬─────────────────────────────────────┬───────────────────────┐
  │   Item    │               Decided               │   Deferred to next    │
  │           │                                     │       iteration       │
  ├───────────┼─────────────────────────────────────┼───────────────────────┤
  │ 1. Extra  │ All four groups: duplicates, field  │                       │
  │ checks    │ consistency, coverage gaps &        │ —                     │
  │           │ spikes, time & timezone sanity      │                       │
  ├───────────┼─────────────────────────────────────┼───────────────────────┤
  │           │ Raw tables untouched, a portable    │                       │
  │ 2. Bad    │ SQL view does the cleaning, Python  │ Cleaning rules beyond │
  │ data      │ handles timezones; medallion noted  │  deduplication        │
  │           │ as the production path              │                       │
  ├───────────┼─────────────────────────────────────┼───────────────────────┤
  │           │ No year-over-year possible (only    │ Week vs. weekday vs.  │
  │ 3.        │ ~26 weeks of data); 4 weeks of      │ weekdays-only; window │
  │ Baseline  │ history required before showing a   │  length N             │
  │           │ verdict                             │                       │
  ├───────────┼─────────────────────────────────────┼───────────────────────┤
  │           │ Measure total events, with a note   │ Method, picked after  │
  │ 4.        │ to ask product about other metrics; │ comparing a few on    │
  │ Flagging  │  account verdict on top plus ranked │ the seed              │
  │           │  locations                          │                       │
  └───────────┴─────────────────────────────────────┴───────────────────────┘

  The new section ends with a 6-step list for the next iteration, starting with
  the Docker Postgres setup and the integrity queries.

  Two things in the original plan conflict with these decisions, so you may want
  to change them:
  - Wireframe: "select account, location" doesn't fit the new ranked-locations
    view. Account becomes the main selection, and a location can be a
    drill-down.
  - API naming: /get-insigth has a typo. A resource-style path would read
    better, e.g. GET /accounts/{id}/insights?period=week&date=….

✻ Cooked for 1m 31s · done 4:39 PM

❯ start the next iteration with the docker compose postgres (Use subagents to   
  spin up the database and to create a Docker Compose, and use a different      
  agent to write the file of data integrity so we can save some context here)   

● I'll run this in two steps, because the integrity agent needs a running,
  seeded database. First, an agent that sets up Docker Compose, the migration
  and the seed load. When it reports back, I'll start the integrity agent.

● Agent(Docker Compose Postgres + seed)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

● The database agent is running in the background. It's setting up:
  - docker-compose.yml with Postgres 16
  - an Alembic migration for the two tables, inside backend/ (the schema goes in
    through a real migration, not raw DDL)
  - an unmodified copy of the seed at data/seed.sql, plus a load script
  - a full start-and-load run, checked against the expected 20 accounts and
    12,626 events
  - a "Local database" section in CLAUDE.md

  When it reports back, I'll start the second agent to run every integrity check
  against Postgres and write Data_integrity.md, with each query, its result,
  and PASS/FAIL.

✻ Cogitated for 25s · done 4:44 PM

● Agent "Docker Compose Postgres + seed" finished · 4m 0s

● The database is up and verified: 20 accounts, 12,626 events, and the expected
  date range. Next I'll start the integrity agent.

● Agent(Write Data_integrity.md)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

● The local Postgres is running and seeded. The database agent checked the
  counts: 20 accounts and 12,626 events from 2026-02-01 10:57:44 to 2026-07-27
  22:20:34. Nothing is committed.

  - Docker: docker-compose.yml runs postgres:16.4.
  - Migration: the schema goes in through an Alembic migration in backend/, not
    raw DDL. It also adds one index, on account + event time.
  - Seed: data/seed.sql is a byte-identical copy of the starter file.
    scripts/load_seed.sh runs the migration and loads it, and skips the load if
    the data is already there.
  - Docs: CLAUDE.md now has the commands to start, migrate, seed, open psql and
    reset.

  The agent hit two snags:
  - Virtual environment: Python's built-in venv doesn't work in this sandbox, so
    uv was used instead. CLAUDE.md lists both.
  - ID columns: they're plain integers with no auto-increment, to match the
    starter schema. If the backend ever creates rows, that needs changing.

  A second agent is now running every check from the plan and writing
  Data_integrity.md. Each check gets its SQL, its result and a PASS/FAIL/INFO
  status. The report also covers:
  - weekend share per account
  - duplicates
  - spikes
  - weekly volume spread per account and location

  That's the data we need for the open decisions on cleaning rules, baseline
  window and detection method. I'll pass you its key findings when it finishes.

✻ Crunched for 26s · done 4:49 PM

● Agent "Write Data_integrity.md" finished · 8m 28s

● Data_integrity.md is at the repo root. It covers 13 checks plus a section of
  inputs for the baseline decisions. Each check has its exact SQL, the real
  output, PASS/FAIL/INFO and a short reading. All queries were read-only, and
  nothing is committed.

  ┌───────────────────────────┬────────┬────────────────────────────────────┐
  │           Check           │ Status │              Finding               │
  ├───────────────────────────┼────────┼────────────────────────────────────┤
  │                           │        │ 2026-02-01 → 07-27; 25 complete    │
  │ Range                     │ INFO   │ local weeks; the first and last    │
  │                           │        │ weeks contain only one day each    │
  ├───────────────────────────┼────────┼────────────────────────────────────┤
  │ Accounts, orphans, events │ PASS   │ 20 accounts, 0 orphan events, 0    │
  │  before account creation  │        │ events before the account existed  │
  ├───────────────────────────┼────────┼────────────────────────────────────┤
  │ Accounts with no events   │ INFO   │ Only #20 Quiet Harbor Spa          │
  ├───────────────────────────┼────────┼────────────────────────────────────┤
  │ Valid values, duration    │        │                                    │
  │ only on calls,            │ PASS   │ No problems                        │
  │ casing/whitespace         │        │                                    │
  ├───────────────────────────┼────────┼────────────────────────────────────┤
  │ Weekend activity          │ INFO   │ 9.2% of events; every account has  │
  │                           │        │ some (2.4%–11.5%)                  │
  ├───────────────────────────┼────────┼────────────────────────────────────┤
  │ Outside 07:00–19:00 local │ INFO   │ 20.5%, mostly before 07:00         │
  ├───────────────────────────┼────────┼────────────────────────────────────┤
  │                           │        │ 12 pairs; every column matches and │
  │ Exact duplicates          │ FAIL   │  the ids are consecutive, so       │
  │                           │        │ they're double-ingested            │
  ├───────────────────────────┼────────┼────────────────────────────────────┤
  │                           │        │ A few within seconds of each       │
  │ Near-duplicates           │ INFO   │ other, but they look like separate │
  │                           │        │  real events                       │
  ├───────────────────────────┼────────┼────────────────────────────────────┤
  │                           │        │ 398 events with no outcome (~3% of │
  │ NULL outcome / duration   │ FAIL   │  each type); 313 calls with no     │
  │                           │        │ duration                           │
  ├───────────────────────────┼────────┼────────────────────────────────────┤
  │ Coverage gaps             │ PASS   │ No empty account-weeks; only 4 of  │
  │                           │        │ 1,725 location-weeks are empty     │
  ├───────────────────────────┼────────┼────────────────────────────────────┤
  │                           │        │ Account 6 on Wed 2026-06-03: 805   │
  │ Spike                     │ FAIL   │ events vs. ~13 on a normal day,    │
  │                           │        │ across all 15 sites, for that one  │
  │                           │        │ day only                           │
  ├───────────────────────────┼────────┼────────────────────────────────────┤
  │                           │        │ All timezones valid; only 0.06% of │
  │ Time & timezone           │ PASS   │  events move to a different week   │
  │                           │        │ after converting to local time     │
  └───────────────────────────┴────────┴────────────────────────────────────┘

  What this means for the open decisions:
  1. Weekends: every account has weekend activity, so a weekdays-only baseline
     is out. Weekend days are too sparse for same-weekday comparisons, which
     points to Mon–Sun weekly totals.
  2. Duplicates: safe to dedupe. There's no sign that near-duplicates are
     re-ingestion.
  3. The spike is a single day. For account 6, it pushes the weekly standard
     deviation from 13 to 162, while the median only moves from 76 to 74. That's
     strong evidence for median-based detection over mean ± std.
  4. Small locations: a typical location has 4–11 events a week, and 21
     locations have 5 or fewer. A ±50% swing is normal at that size, so
     detection needs a minimum % / absolute floor.
  5. Two surprises:
     - Timestamps look generated on a UTC clock, not local business hours.
       Filtering to business hours would delete real data, so that's not a safe
       cleaning rule.
     - The data ends 99 days before today. "Last week" for the dashboard has to
       come from an as-of date, not today's date.

  The deferred decisions are next. As before, we can take them one at a time, in
  this order:
  - cleaning policy
  - baseline type and window length N
  - detection method, with a comparison run on the seed
  - as-of date handling

  Shall I start with the cleaning policy?

✻ Cogitated for 13m 25s · done 4:57 PM

❯ I will do some checks on the database. Remember that this is a sandbox. Give  
  me the port that I have to open and the command to open this in Docker        
  sandboxes so I can connect my pgAdmin to this database.                       

  Ran 1 shell command (ctrl+o to expand)

● Postgres is on port 5432 inside the sandbox, listening on all interfaces, so
  it can be published as is. Run this on your host:

  sbx ports claude-qualitra-challenge --publish 5432:5432

  If something on your host already uses 5432, such as a local Postgres, map a
  different host port instead, like --publish 15432:5432, and use 15432 in
  pgAdmin.

  pgAdmin connection:

  ┌──────────┬───────────────────────────────────┐
  │  Field   │               Value               │
  ├──────────┼───────────────────────────────────┤
  │ Host     │ localhost                         │
  ├──────────┼───────────────────────────────────┤
  │ Port     │ 5432 (or the host port you chose) │
  ├──────────┼───────────────────────────────────┤
  │ Database │ relay                             │
  ├──────────┼───────────────────────────────────┤
  │ Username │ relay                             │
  ├──────────┼───────────────────────────────────┤
  │ Password │ relay                             │
  └──────────┴───────────────────────────────────┘

  To check the mapping: sbx ports claude-qualitra-challenge. To remove it when
  you're done: sbx ports claude-qualitra-challenge --unpublish 5432:5432.

✻ Baked for 13s · done 5:09 PM

❯ These are some questions that I will ask. If this was a real ticket we have   
  to add this somewhere.                                                        
  1. Why are there allocations with no events?. Assumption for the challenge:   
  No onboarding of the account yet                                              
  2. Why does the 'Capital City Storage' have UTC as the time zone? Assumption  
  for the challenge: That's weird. That's probably a misconfiguration           
     3 Why are some events before 7 a.m? Assumption for the challenge: Some     
  automated process creates a few events                                        
     4 why the spike on  single local day, Wed 2026-06-03, with 805 events?     
  Assumption for the challenge: Marketing campaign                              
     5 why the calls with null duration?                                        
     6 why is this value allowed to be null? (it has 398 rows affected):        
  activity_events:   outcome           VARCHAR(40)  NULL                        
     4 important note: I am using Claude Code in bypass mode because I am using 
  Claude Code inside Docker sandboxes. That restricts a lot of the damage that  
  Claude Code can do and lets me focus on high-level tasks instead of manually  
  reviewing each command. It also isolates my instances.                        
                                                                                
  Questions for you                                                             
  we have fewer events on Saturday and Sunday. that will affect the decision of 
  using mon-sat as the baseline (also we are excluding Sundays; we have to be   
  upfront about this). Maybe we can choose two baselines: an entire week and    
  also the previous days, like the previous 7 days, the previous 7 Mondays, for 
  example? Pros and cons? Is it not a problem to have fewer events on those     
  days (if we use median absolute deviation)?                                   

● Write(OPEN_QUESTIONS.md)
  ⎿  Wrote 16 lines to OPEN_QUESTIONS.md
      1 # Open questions & assumptions
      2 
      3 Questions that, on a real ticket, would go to product / data owne
        rs before building. For the challenge, each has a working assumpt
        ion so work can proceed. Evidence is in `Data_integrity.md`.
      4 
      5 | # | Question | Assumption for the challenge | Impact on the sol
        ution |
      6 |---|---|---|---|
      7 | 1 | Why are there accounts with no events (#20 Quiet Harbor Spa
     … +10 lines (~2 KB) (ctrl+o to expand)

● I've logged your questions in OPEN_QUESTIONS.md with their assumptions, and
  proposed answers for 5 and 6 marked as Proposed. Next I'm checking a typical
  day at the location level for your baseline question.

  Ran 2 shell commands (ctrl+o to expand)

● ┌───────────────────────┬────────────────┬────────┬────────────────────┐
  │ Per location, per day │ Average events │ Median │ Days with 0 events │
  ├───────────────────────┼────────────────┼────────┼────────────────────┤
  │ Mon–Fri               │ 1.32           │ 1      │ 31.6%              │
  ├───────────────────────┼────────────────┼────────┼────────────────────┤
  │ Sat                   │ 0.34           │ 0      │ 70.5%              │
  ├───────────────────────┼────────────────┼────────┼────────────────────┤
  │ Sun                   │ 0.33           │ 0      │ 71.3%              │
  └───────────────────────┴────────────────┴────────┴────────────────────┘

  Saturday and Sunday look the same, so there's no reason to keep Saturday and
  drop Sunday. And a typical location gets about one event per weekday, which is
  the bigger issue.

  Does fewer weekend events matter for a weekly baseline?

  No. Every Mon–Sun week contains exactly one Saturday and one Sunday, so the
  mix of days is the same in every week we compare. Low weekends make the weekly
  total a bit smaller, not less comparable. Dropping Sunday (or both weekend
  days) wouldn't make the comparison any fairer. It would just discard about
  5–9% of real events, and we'd have to justify that. My recommendation: keep 
  Mon–Sun and say plainly in the write-up that weekends are low-volume but
  included.

  Is it a problem for the median absolute deviation (MAD)?

  Yes, at the daily level. With a median of 0 on weekends (and 1 on weekdays)
  per location:
  - Over the previous 8 Saturdays, most values are 0, so the median is 0 and the
    MAD is 0. A single event on Saturday is then "infinitely" unusual.
  - Even on weekdays, the MAD is 0–1, so a change of 1 or 2 events gets flagged.
    That's noise, not something worth acting on.

  The minimum-difference floor would hide those flags. But then nearly every
  daily verdict at the location level would be "normal (low volume)". That
  doesn't help anyone and makes the feature look broken.

  Two baselines: whole week + daily

  ┌─────────────┬────────────────┬───────────────────────┬────────────────┐
  │             │    Weekly      │                       │  Daily: same   │
  │             │ (Mon–Sun vs.   │  Daily: previous 7    │   weekday,     │
  │             │  previous N    │         days          │  previous N    │
  │             │     weeks)     │                       │     weeks      │
  ├─────────────┼────────────────┼───────────────────────┼────────────────┤
  │             │ "Was last week │                       │ "Was this      │
  │ Answers     │  normal?", the │ "Was yesterday normal │ Monday normal  │
  │             │  Monday        │  vs. the last week?"  │ for a Monday?" │
  │             │ question       │                       │                │
  ├─────────────┼────────────────┼───────────────────────┼────────────────┤
  │             │ ~7× a day;     │                       │                │
  │ Volume per  │ workable even  │ 1 day                 │ 1 day          │
  │ data point  │ for small      │                       │                │
  │             │ locations      │                       │                │
  ├─────────────┼────────────────┼───────────────────────┼────────────────┤
  │             │                │ ❌ Mixes Mon with     │                │
  │ Weekday     │ Built in       │ Sat/Sun, so every     │ ✅ Like with   │
  │ effect      │                │ Monday looks high and │ like           │
  │             │                │  every Sunday low     │                │
  ├─────────────┼────────────────┼───────────────────────┼────────────────┤
  │ Noise for   │                │                       │ Very high      │
  │ small       │ Moderate       │ High                  │ (weekends:     │
  │ locations   │                │                       │ median 0)      │
  ├─────────────┼────────────────┼───────────────────────┼────────────────┤
  │             │                │                       │ Secondary,     │
  │ Verdict     │ Primary        │ Not recommended       │ only where     │
  │             │                │                       │ volume allows  │
  └─────────────┴────────────────┴───────────────────────┴────────────────┘

  Pros of having both:
  - A customer can see which day caused an unusual week ("the week was low,
    mostly Tuesday").
  - For large accounts, a daily view adds real information.

  Cons of having both:
  - Double the scope: two baselines, two sets of tests, more UI.
  - Conflicting verdicts: "the week is normal, but Tuesday is low" confuses
    people.
  - Mostly noise at location level: most location-days don't have the volume for
    a meaningful verdict.
  - A different question: a daily view leans toward monitoring, which is close
    to the out-of-scope alerting. The ticket's question is Monday-morning weekly
    review.

  My recommendation:
  - Weekly Mon–Sun is the only verdict. It covers the account and each ranked
    location.
  - Daily is context, not a verdict. Show a simple bar chart of the week's 7
    days next to each day's usual value (the median for that weekday). Daily
    verdicts are left out of scope because the volume is too low, and the
    write-up backs that with the numbers above.

  That keeps the drill-down without producing misleading daily flags. In a real
  project, you'd ask product whether daily or weekday views matter once accounts
  have more volume.

● User answered Claude's questions:
  ⎿  · Which baseline setup should we go with? → Weekly verdict + daily context

● Bash(cat >> PLAN_first_iteration.md <<'EOF'…)
  ⎿  Updated PLAN_first_iteration.md (+57 -1)
       62  - The accounts use normal working days and hours
       63  
       64  # Use of an LLM
       65 -- In this ticket in particular, we won't use an LLM because it
          - won't add relevant value to explain why this day is not norma
          -l, for example, because it won't have the data to explain why 
          -the number is lower than expected                             
       65   No newline at end of file
       66 +- In this ticket in particular, we won't use an LLM because it
          + won't add relevant value to explain why this day is not norma
          +l, for example, because it won't have the data to explain why 
          +the number is lower than expected                             
       67 +------                                                        
       68 +                                                              
       69 +# Results of first iteration discussion                       
       70 +                                                              
       71 +## 1. Additional data integrity checks (line 14) — DECIDED    
       72 +Add to Data_integrity.md, on top of the original list:        
       73 +- **Duplicates**: exact duplicates (same account + location + 
          +event_type + occurred_at, different id; the init profile found
          + ~12 groups) and near-duplicates (same key within a few second
          +s).                                                           
       74 +- **Field consistency**: outcome valid for its event_type, NUL
          +L outcome rate per type, duration only on calls, NULL/zero/neg
          +ative/outlier durations, casing/whitespace in location and enu
          +m values.                                                     
       75 +- **Coverage gaps & spikes**: per account/location, days or we
          +eks with zero events, locations starting or stopping mid-range
          +, sudden spikes (account 6 around 2026-06-03), partial first/l
          +ast week.                                                     
       76 +- **Time & timezone sanity**: valid IANA timezones, no future 
          +timestamps, events near DST switches, how many events change d
          +ay/week after UTC → local conversion.                         
       77 +                                                              
       78 +## 2. Act on bad data (line 15) — PARTIALLY DECIDED           
       79 +- **Mechanism: DECIDED.** Raw tables (`accounts`, `activity_ev
          +ents`) stay untouched (the seed is used as-is). A plain, porta
          +ble SQL view (`clean_activity_events`) applies the cleaning ru
          +les, so it behaves the same on Postgres and on SQLite in tests
          +. UTC → account-local day/week bucketing is done in Python (`z
          +oneinfo`), because SQLite has no IANA timezone support.       
       80 +  - Pros: cleaning rules readable in one place, portable, easy
          + to unit-test (DST, America/Phoenix, UTC).                    
       81 +  - Cons: re-aggregates per request (fine for ~12.6k rows); lo
          +gic split between SQL and Python.                             
       82 +  - **Production note for write-up:** a medallion-style approa
          +ch (or a daily rollup per account/location/local date, refresh
          +ed incrementally) would be preferred at real volume; it's over
          +engineering for this challenge.                               
       83 +- **Policy: DEFERRED to next iteration**, after running the in
          +tegrity queries. De-duplication is certain (production note: p
          +revent at ingestion with an idempotency key / unique constrain
          +t). Other rules will be defined on the view based on the check
          + results.                                                     
       84 +                                                              
       85 +## 3. Baseline (line 24) — PARTIALLY DECIDED                  
       86 +- **Year-over-year / seasonality: NOT POSSIBLE.** Events only 
          +span 2026-02-01 → 2026-07-27 (~26 weeks), so seasonality isn't
          + handled. Document it as a limitation (would need ≥ 1 year of 
          +history).                                                     
       87 +- **Comparison type: DEFERRED to next iteration** (depends on 
          +weekend/business-hours checks; some accounts may work Saturday
          +s). Candidates:                                               
       88 +  - A. Trailing N complete local weeks (Mon–Sun): answers "was
          + last week normal?", smooths noise, includes weekends naturall
          +y; can't answer per-day questions, slow to adapt to level shif
          +ts.                                                           
       89 +  - B. Same weekday over previous N weeks: right for a daily v
          +iew, handles weekends; noisy for small accounts, sensitive to 
          +holidays.                                                     
       90 +  - C. Previous N weekdays excluding Sat/Sun: simple, but assu
          +mes Mon–Fri businesses and mixes weekdays.                    
       91 +- **Window length N: DEFERRED**; decide after looking at weekl
          +y variance (candidates 4 / 8 / 12 weeks).                     
       92 +- **Minimum history: DECIDED, 4 complete weeks.** Below that, 
          +show totals with "not enough history yet" instead of a verdict
          + (covers account 20 with no events and new locations).        
       93 +- Default period (proposal): the last complete week in the acc
          +ount's local time, not the current partial week.              
       94 +                                                              
       95 +## 4. How to flag normal vs needs attention (lines 25–29) — PA
          +RTIALLY DECIDED                                               
       96 +- **Method: DEFERRED.** In the next iteration, run 2–3 methods
          + on the seed and pick the one with the most sensible flags. Ca
          +ndidates:                                                     
       97 +  - Mean ± k·std: familiar, but one spike week inflates mean a
          +nd std.                                                       
       98 +  - Median ± k·MAD: robust to outlier weeks; MAD can be 0 for 
          +sparse/stable series, so it needs a floor.                    
       99 +  - Percent change vs median: easiest for customers to read; i
          +gnores natural variability (3 → 2 calls = −33%).              
      100 +  - Percentile / min–max range: intuitive, but coarse with sma
          +ll N.                                                         
     … 22 more lines (ctrl+o to expand)

● I've recorded the decision in PLAN_first_iteration.md, in a new "second
  iteration" section:
  - The verdict comes from the week: each Mon–Sun week, in the account's local
    time, is compared with the previous N weeks.
  - Daily numbers are context only: the UI shows each day next to that weekday's
    usual value, with no flag.

  The section includes the numbers behind the choice.

  Three items are still open: the cleaning policy, the window length N combined
  with the detection method (one comparison run on the seed covers both), and
  how to set the as-of date. Shall I go on with the cleaning policy?
✻ Brewed for 1m 6s · done 5:35 PM

❯ On the Postgres view the only action that we will take will be to deduplicate 
  the 12 events. what else do we need to addres before creating the final       
  PLAN.md? wireframes? and what else?                                           

● Bash(cat >> PLAN_first_iteration.md <<'EOF'…)
  ⎿  Updated PLAN_first_iteration.md (+5 -0)
      119  - Why: per location, an average weekday has 1.32 events (media
           n 1, 31.6% of days with zero) and a weekend day 0.33–0.34 (med
           ian 0, ~71% zero). A same-weekday MAD would be 0–1, so daily f
           lags would be noise. Sat ≈ Sun, so excluding only Sunday (Mon–
           Sat) has no justification. Every week contains exactly one Sat
            and one Sun, so low weekends don't bias weekly comparisons; t
           hey stay included, and the write-up says so.
      120  - Out of scope: daily verdicts. Real-project note: ask product
            whether daily/weekday views matter once accounts have more vo
           lume.
      121  - Questions and assumptions raised by the data checks: see `OP
           EN_QUESTIONS.md`.
      122 +                                                              
      123 +## Cleaning policy — DECIDED                                  
      124 +- The `clean_activity_events` view only **removes the 12 exact
          + duplicate events** (same account_id, location, event_type, oc
          +curred_at and all other columns; keep the lowest id).         
      125 +- Everything else is kept: NULL outcome/duration, events befor
          +e 07:00 / after 19:00, weekend events, and the account 6 spike
          + (2026-06-03). Reasons are in `OPEN_QUESTIONS.md`.            
      126 +- Production note: prevent duplicates at ingestion (idempotenc
          +y key / unique constraint).                                   

● I've recorded the cleaning decision in PLAN_first_iteration.md: the view only
  removes the 12 duplicates, and everything else stays.

  Here's what's still open before PLAN.md. Wireframes are on the list, but some
  items come before them because they decide what the screen shows.

  Must decide (they change the spec)

  1. The take-home prompt from the email. I've only seen the starter repo. The
     email may set deliverables (README, write-up, tests, a time limit, how to
     run it), and PLAN.md should be checked against it. Can you paste its
     requirements?
  2. Detection method, window N and thresholds. One comparison run on the seed
     covers median+MAD vs. mean±std vs. percent change, N = 4/8/12, and the
     floor values. It also decides whether the account-level verdict uses the
     account's own weekly total (my suggestion) or is derived from its
     locations.
  3. As-of date and current week. The data ends 2026-07-27, 99 days before
     today, so "last week" by the real clock is empty. Options:
     - the latest complete week in the data
     - a configurable AS_OF_DATE
     - a week parameter on the API with that as the default

     I'd go with the parameter plus the default. Also: never show the current
     partial week as a verdict.
  4. Ranking and what "needs attention" means. Is higher than usual also
     something to flag, or only lower? For Monday action, a drop usually matters
     more. Options:
     - sort locations by size of deviation, with lows first
     - show both directions, but put lows first
  5. API contract. Endpoints, parameters and the response shape, as an OpenAPI
     spec. This is the core of the spec-driven step. Draft:
     - GET /accounts
     - GET /accounts/{id}/weekly-insight?week=
     - GET /health
  6. Wireframe. The account picker, the week picker, the account verdict card,
     the ranked locations table, and the 7-day context chart. Empty and
     low-history states have to be shown too.
  7. Test strategy. Your plan says SQLite for integration tests, but the app
     runs on Postgres. The dedupe view (ROW_NUMBER) works on both, and the
     timezone logic lives in Python, so SQLite is workable. The risk is testing
     a database you don't ship on. The alternative is running tests against a
     test Postgres in Docker.

  Can take a sensible default (tell me if you disagree)

  - Frontend tooling: Vite + React + TypeScript, with a small chart library such
    as Recharts.
  - How a reviewer runs it: docker compose up brings up the db, the API (which
    migrates and seeds on start) and the frontend.
  - Write-up: decisions, tradeoffs, production notes, AI-usage notes. Most of
    this is already collected across the plan and OPEN_QUESTIONS.md.
  - Out of scope (already noted): auth, rate limits, alerting, ML,
    holiday/campaign calendar, daily verdicts, per-event-type metrics.

● User answered Claude's questions:
  ⎿  · Which item do we take next? → API + wireframe

● I'll draft both here, as you asked: no PLAN.md yet. Two things still undecided
  are left as placeholders, and the shape works whichever way they go:
  - the detection method, which fills usual, lower and upper
  - the as-of default, which decides which week the API returns when none is
    given

  API draft (OpenAPI, condensed)

  GET /health                      → 200 {status: "ok", db: "ok"}

  GET /accounts                    → 200 [AccountSummary]
    AccountSummary: {id, name, industry, timezone, location_count,
                     first_week, latest_complete_week}      # for the pickers

  GET /accounts/{account_id}/weekly-insight?week_start=YYYY-MM-DD
    week_start: optional, a Monday in the account's local time;
                default = latest complete week (as-of rule TBD)
    200 WeeklyInsight
    404 account not found · 422 week_start not a Monday / outside data range

  WeeklyInsight:
    account:  {id, name, timezone}
    week:     {start, end, is_complete}
    baseline: {method, weeks_used, from, to}        # e.g. "median_mad", 8
    summary:  Metric                                # whole account
    days:     [{date, weekday, total, usual}]       # 7 rows, context only, no 
  status
    locations:[Metric & {location, history_weeks}]  # sorted: needs attention 
  first
    data_notes: [string]                            # "2 duplicate events 
  removed",
                                                    # "timezone is UTC — may be 
  misconfigured"
  Metric:
    total, usual, lower, upper, pct_vs_usual,
    status: normal | lower_than_usual | higher_than_usual | not_enough_history

  Design choices worth your review:
  - One aggregate endpoint per screen: the dashboard makes a single request, and
    the location ranking happens on the server, so the UI stays simple.
  - The location goes inside the payload, not the URL: location names contain
    spaces ("Site A"). A per-location URL like /locations/{name} only becomes
    necessary if we add a drill-down.
  - data_notes keeps the messy-data handling visible to the customer. That's
    cheap credibility with reviewers.
  - No day granularity: that follows the weekly-verdict decision.

  Wireframes

  Two layouts are in the question below; select an option to see its preview.

● User answered Claude's questions:
  ⎿  · Which dashboard layout? → A: Verdict + ranked table
     · How should the API be shaped? → One aggregate endpoint
     · Should a location row be clickable to show that location's 7-day context?
     → No, account-level days only

● Bash(cat >> PLAN_first_iteration.md <<'EOF'…)
  ⎿  Updated PLAN_first_iteration.md (+50 -0)
      124  - The `clean_activity_events` view only **removes the 12 exact
            duplicate events** (same account_id, location, event_type, oc
           curred_at and all other columns; keep the lowest id).
      125  - Everything else is kept: NULL outcome/duration, events befor
           e 07:00 / after 19:00, weekend events, and the account 6 spike
            (2026-06-03). Reasons are in `OPEN_QUESTIONS.md`.
      126  - Production note: prevent duplicates at ingestion (idempotenc
           y key / unique constraint).
      127 +                                                              
      128 +## API — DECIDED (draft; detection fields filled once the meth
          +od is chosen)                                                 
      129 +One aggregate endpoint per screen; location ranking is done on
          + the server.                                                  
      130 +```yaml                                                       
      131 +GET /health                      → 200 {status: "ok", db: "ok"
          +}                                                             
      132 +GET /accounts                    → 200 [AccountSummary]       
      133 +  AccountSummary: {id, name, industry, timezone, location_coun
          +t, first_week, latest_complete_week}                          
      134 +GET /accounts/{account_id}/weekly-insight?week_start=YYYY-MM-D
          +D                                                             
      135 +  week_start: optional, a Monday in account-local time; defaul
          +t = latest complete week (as-of rule TBD)                     
      136 +  200 WeeklyInsight · 404 unknown account · 422 week_start not
          + a Monday / outside data range                                
      137 +WeeklyInsight:                                                
      138 +  account:   {id, name, timezone}                             
      139 +  week:      {start, end, is_complete}                        
      140 +  baseline:  {method, weeks_used, from, to}                   
      141 +  summary:   Metric                                  # whole a
          +ccount (its own weekly total)                                 
      142 +  days:      [{date, weekday, total, usual}]         # 7 rows,
          + context only, no status                                      
      143 +  locations: [Metric & {location, history_weeks}]    # sorted:
          + needs attention first                                        
      144 +  data_notes:[string]                                # e.g. du
          +plicates removed, UTC timezone warning                        
      145 +Metric: {total, usual, lower, upper, pct_vs_usual,            
      146 +         status: normal | lower_than_usual | higher_than_usual
          + | not_enough_history}                                        
      147 +```                                                           
      148 +- Location names (with spaces) stay in the payload, not the UR
          +L; no per-location endpoint.                                  
      149 +                                                              
      150 +## Wireframe — DECIDED (layout A: verdict + ranked table; numb
          +ers illustrative)                                             
      151 +```                                                           
      152 +┌ Relay · Weekly activity ─────────────────────┐              
      153 +│ Account [Metro Collision Centers ▾]          │              
      154 +│ Week    [◀ Jul 20 – Jul 26, 2026 ▶]  (ET)    │              
      155 +├──────────────────────────────────────────────┤              
      156 +│ ▼ LOWER THAN USUAL                           │              
      157 +│ 52 events · usual ~76 (range 64–88) · −32%   │              
      158 +│ vs. previous 8 weeks                         │              
      159 +├──────────────────────────────────────────────┤              
      160 +│ This week by day   █ actual  · usual         │              
      161 +│  █·  █·  ▄·  █·  ▄·  ▁·  ▁·                  │              
      162 +│  Mo  Tu  We  Th  Fr  Sa  Su                  │              
      163 +├──────────────────────────────────────────────┤              
     … 13 more lines (ctrl+o to expand)

● I've added both to the second-iteration section of PLAN_first_iteration.md:
  - API: one aggregate weekly-insight endpoint, plus /accounts and /health.
  - Wireframe: layout A, with an account-level 7-day chart and no location
    drill-down. The numbers in it are illustrative, and three states still need
    drawing: not enough history, an account with a single location, and the
    timezone warning.

  These items are still open before PLAN.md:
  1. Take-home prompt requirements: please paste them so PLAN.md can be checked
     against them.
  2. Detection method run: this decides the method, window length N and floors,
     which then fill usual, lower and upper.
  3. As-of date and ranking: the default week, and whether "higher than usual"
     counts as needing attention.
  4. Test strategy: SQLite vs. a test Postgres.

  Which one next? I'd do the detection run in a subagent while we settle 3 and 4
  here.

✻ Baked for 1m 29s · done 5:41 PM

❯ for 2 we will use: median absolute deviation what was the concern that you    
  had?                                                                          

● The median absolute deviation (MAD) is the right choice here: the account 6
  spike pushes the weekly std from 13 to 162, while the median barely moves. My
  concern isn't the spike. It's small counts:

  1. The MAD collapses to 0 or 1 on sparse or very stable series. For an 8-week
     history like 5,5,4,5,6,5,5,4, the median is 5 and the MAD is 0. Any week
     that isn't exactly 5 then falls outside the band, so 6 events would be
     flagged "higher than usual". The integrity report found a MAD of 1–3 for
     most accounts, and location medians of only 4–11 events a week. 21
     locations have a median of 5 or less.
  2. Random variation in small counts is large compared with the numbers. A
     location that normally gets 5 events a week will see weeks of 2 or 9 just
     by chance. A pure MAD band treats those as unusual, and the Monday view
     becomes a list of false alarms, especially for account 6's 14 small sites.
  3. The lower bound can go below 0. With a median of 3, a band like 3 ± 4 makes
     "lower than usual" impossible to reach even at zero events. The bound has
     to be capped at 0, and very small locations may never get a "lower" flag at
     all.
  4. Few data points. With the 4-week minimum history, the median and MAD of 4
     numbers are unstable. That's acceptable, but it's a reason to settle N with
     the data.
  5. Calibration. We need k (how many MADs count as unusual) and the 1.4826
     scaling, so that "k = 3" means roughly the same as 3 standard deviations.
     The customer sees none of this, just "−38% vs your usual week".

  The fix is a floor, in one of these forms:
  - Floor on the spread: spread = max(1.4826·MAD, √median). The √median term is
    the natural random variation for counts, so a quiet location gets a wider,
    more realistic band. It's still simple and explainable.
  - Floor on the difference: flag only if the value is outside median ± k·spread
    and the difference is at least a minimum number of events (e.g. ≥ 3) and
    percent (e.g. ≥ 20%).
  - Both: the most robust option, with more parameters to justify.

● User answered Claude's questions:
  ⎿  · How should MAD be protected against small counts? → Both floors 
     (Recommended)
     · Tune k, N and the floors with a run on the seed? → Yes, via a subagent

● Bash(cat >> PLAN_first_iteration.md <<'EOF'…)
  ⎿  Updated PLAN_first_iteration.md (+6 -0)
      174  ```
      175  - The 7-day chart is account-level only; location rows aren't 
           clickable (no drill-down).
      176  - States still to draw: not enough history (e.g. account 20), 
           account with a single location, timezone warning.
      177 +                                                              
      178 +## Detection method — DECIDED (parameters pending tuning)     
      179 +- **Median ± k·spread** over the previous N complete weeks, wi
          +th `spread = max(1.4826·MAD, √median)`; the lower bound is cla
          +mped at 0.                                                    
      180 +- Flag only if the week is outside the band **and** differs fr
          +om the median by at least a minimum number of events and a min
          +imum percent.                                                 
      181 +- Why MAD: the account 6 spike moves its weekly std from 13 to
          + 162 but its median from 76 to 74. Why the floors: location me
          +dians are 4–11/week (21 locations ≤ 5), MAD is often 0–3, and 
          +a pure MAD band would flag ordinary noise.                    
      182 +- k, N and the floor values are tuned on the seed (see `Detect
          +ion_tuning.md`).                                              

● Agent(Tune MAD detection parameters)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

● I've set the detection method in the plan, and a subagent is now tuning its
  parameters on the seed, producing a results doc and a reproduction script.
  While that runs, I'll settle the remaining open questions.

● User answered Claude's questions:
  ⎿  · Which week does the dashboard show by default? (The data ends 2026-07-27,
     99 days ago.) → Latest complete week in data
     · What counts as 'needs attention' for ranking locations? → Lower only
     · Which database do the integration tests run against? → SQLite (your plan)

● Bash(cat >> PLAN_first_iteration.md <<'EOF'…)
  ⎿  Updated PLAN_first_iteration.md (+11 -0)
      180  - Flag only if the week is outside the band **and** differs fr
           om the median by at least a minimum number of events and a min
           imum percent.
      181  - Why MAD: the account 6 spike moves its weekly std from 13 to
            162 but its median from 76 to 74. Why the floors: location me
           dians are 4–11/week (21 locations ≤ 5), MAD is often 0–3, and 
           a pure MAD band would flag ordinary noise.
      182  - k, N and the floor values are tuned on the seed (see `Detect
           ion_tuning.md`).
      183 +                                                              
      184 +## As-of date — DECIDED                                       
      185 +- Default week = the **latest complete local week that has dat
          +a** (Jul 20–26, 2026). `week_start` picks other weeks. An opti
          +onal `AS_OF_DATE` env var overrides "today" to simulate produc
          +tion behavior. Partial weeks never get a verdict.             
      186 +                                                              
      187 +## Ranking — DECIDED                                          
      188 +- **Only `lower_than_usual` counts as "needs attention"**, ran
          +ked first by biggest % drop.                                  
      189 +- `higher_than_usual` is still shown with its ▲ status but not
          + prioritized. It sorts with `normal` (by location name); `not_
          +enough_history` goes last.                                    
      190 +                                                              
      191 +## Test strategy — DECIDED                                    
      192 +- Integration tests run against **SQLite**. This works because
          + the dedupe view is portable and the timezone logic lives in P
          +ython. Detection math gets pure unit tests with no DB.        
      193 +- Write-up note: the tests don't run on the engine we ship (Po
          +stgres); in a real project, add a Postgres test run in CI.    

● I've added three more decisions to PLAN_first_iteration.md:
  - Default week: the latest complete week in the data, Jul 20–26, 2026. Other
    weeks can be picked with week_start, and AS_OF_DATE can override "today".
  - Ranking: only lower than usual counts as needing attention, biggest drop
    first. Higher weeks still show ▲ but sort alphabetically with the normal
    ones, and locations with not enough history go last.
  - Tests: SQLite for integration tests, with pure unit tests for the detection
    math. The write-up will note that a Postgres test run in CI would be the
    production choice.

  The tuning agent is still running. When it finishes, I'll pass you the
  recommended k, N and floors. After that, the only thing left before PLAN.md is
  the take-home prompt requirements from the email. If you paste them now, I
  can check the plan against them while we wait.

✻ Cogitated for 1m 5s · done 5:46 PM

● Agent "Tune MAD detection parameters" finished · 5m 1s

● The tuning run is done. The recommendation is k = 2.5, N = 8, minimum 
  difference 3 events and 20%, one setting for both the account and its
  locations. Details are in Detection_tuning.md, and the run can be reproduced
  with analysis/tune_detection.py.

  ┌──────────┬───────────────┬─────────────┬───────────────────────────────┐
  │  Level   │    Weeks      │  Flagged    │        Flagged higher         │
  │          │   evaluated   │    lower    │                               │
  ├──────────┼───────────────┼─────────────┼───────────────────────────────┤
  │ Account  │ 399           │ 0.8%        │ 2.3%                          │
  ├──────────┼───────────────┼─────────────┼───────────────────────────────┤
  │ Location │ 1,449         │ 0.1%        │ 2.5% (1.5% without the spike  │
  │          │               │             │ week)                         │
  └──────────┴───────────────┴─────────────┴───────────────────────────────┘

  Checks:
  - Account 6's spike week is flagged higher, for the account and all 15 of its
    locations, under every setting tested.
  - The weeks after the spike stay normal. With mean ± std, the band would be
    0–888 for 8 weeks, so even a week with zero events would read normal.
  - Account 20 and every series' first 4 weeks show "not enough history".

  Why the agent recommends 3% flagged rather than 5–10%: it ran the same method
  on pure random data. At k = 2, random noise alone gets flagged 5.2% of the
  time, so most flags would be false alarms. At k = 3, no account week is ever
  flagged lower, which misses a real −45% drop for account 2. k = 2.5 is the
  balance.

  Two findings affect earlier decisions:

  1. The "needs attention" list will almost always be empty, which clashes with 
     "lower only" ranking. Only 0.1% of location weeks are flagged lower. When a
     site's usual is about 6 events or fewer, the lower bound is 0, so even a
     drop to zero reads normal. Location flags are also mostly noise: small
     sites get flagged about 3.5× more often than larger ones.
  2. The 3-event / 20% minimums never changed a single verdict on this data. The
     √median floor already covers them. The agent kept them as a guard for
     other data.

  It also found that account 15 (Phoenix) is up 94% in the same week as account
  6's spike. That could be a second planted anomaly, so I'd add it to
  OPEN_QUESTIONS.md.

● User answered Claude's questions:
  ⎿  · Accept k=2.5, N=8, floors (3 events, 20%)? → 1 and add a warning on the 
     plan an UI that small accounts will get sometis odd results 
     · Location flags almost never say 'lower' (0.1%), so a 'lower only' ranking
     would usually be empty. How should the locations table rank? → Keep as 
     decided
     · Add account 15's +94% in the spike week to OPEN_QUESTIONS.md? → Yes

● Bash(cat >> PLAN_first_iteration.md <<'EOF'…)
  ⎿  13:| 7 | Why does Sierra Pest Solutions (#15, Phoenix) jump +94% in th
     e same week as account 6's spike (week of 2026-06-01)? | The same kind
      of campaign as #4. | Kept as-is; flagged higher like account 6. If it
     … +2 lines (ctrl+o to expand)
  ⎿  Updated PLAN_first_iteration.md (+7 -0)
      191  ## Test strategy — DECIDED
      192  - Integration tests run against **SQLite**. This works because
            the dedupe view is portable and the timezone logic lives in P
           ython. Detection math gets pure unit tests with no DB.
      193  - Write-up note: the tests don't run on the engine we ship (Po
           stgres); in a real project, add a Postgres test run in CI.
      194 +                                                              
      195 +## Detection parameters — DECIDED (evidence in `Detection_tuni
          +ng.md`)                                                       
      196 +- **k = 2.5, N = 8 weeks, min_abs = 3 events, min_pct = 20%**:
          + one setting for the account and location levels.             
      197 +- Flag rates on the seed: account 3.0% (0.8% lower, 2.3% highe
          +r); location 2.6% (1.5% without account 6's spike week). The s
          +pike week is flagged at the account level and at all 15 locati
          +ons; the weeks after it stay normal.                          
      198 +- The floors don't change any verdict on this seed (√median al
          +ready covers it); they're kept as a guard for other data.     
      199 +- **Low-volume warning (plan + UI):** small accounts/locations
          + (usual ≤ ~6 events/week) can get odd results. Their weekly sw
          +ings are mostly random, they're flagged ~3.5× more often than 
          +larger sites, and they can't be flagged lower (the lower bound
          + is 0). The UI shows a "low volume, results may be unreliable"
          + note on those rows, and the account card shows it when the ac
          +count itself is low-volume.                                   
      200 +- Ranking stays as decided: lower_than_usual first, then the r
          +est by location name. With 0.1% of location weeks flagged lowe
          +r, the ranking usually has nothing to prioritize; that's accep
          +ted and stated in the write-up.                               
  ⎿  Updated OPEN_QUESTIONS.md (+1 -0)
      10  | 4 | Why the spike on Wed 2026-06-03 for Metro Collision Cente
          rs (#6): 805 events across all 15 sites vs ~13 on a normal day?
           | A marketing campaign. | Keep the data. It's a real "not norm
          al" week the customer should see; use a robust (median-based) b
          aseline so it doesn't distort later weeks. Annotating campaigns
          /holidays is out of scope (see plan). |
      11  | 5 | Why do some calls (313) have a NULL `duration_seconds`? |
           *Proposed:* the duration wasn't captured (e.g. missed calls or
           a telephony integration gap). | Doesn't affect the metric (tot
          al event count); calls still count. |
      12  | 6 | Why is `outcome` nullable (398 rows, ~3% of each event ty
          pe)? | *Proposed:* the outcome isn't known yet or wasn't record
          ed (e.g. a lead still being worked). | Doesn't affect the metri
          c (total event count); rows still count. |
      13 +| 7 | Why does Sierra Pest Solutions (#15, Phoenix) jump +94% i
         +n the same week as account 6's spike (week of 2026-06-01)? | Th
         +e same kind of campaign as #4. | Kept as-is; flagged higher lik
         +e account 6. If it's a data issue (e.g. a bulk import affecting
         + several accounts), the cleaning view would need a rule. |     
      14  
      15  ## Process note (for the write-up)
      16  

● All decisions are recorded:
  - Parameters: k = 2.5, N = 8, minimum difference 3 events and 20%. The plan
    has them, with the evidence.
  - Low-volume warning: in both the plan and the UI spec. The threshold is a
    usual of about 6 events a week or fewer. Below that, the lower bound of the
    band is 0, so a drop can't be flagged. The UI warns on those location rows,
    and on the account card when the whole account is that small.
  - Ranking: kept as you decided. The plan notes that the "needs attention" list
    will usually be empty, and the write-up will say so.
  - Account 15: added to OPEN_QUESTIONS.md as question 7, with the assumption
    that it's the same kind of campaign as account 6's spike.

  Every open item from the plan is now decided except one: the requirements from
  the take-home email. If you paste them, I'll check the decisions against them
  and then write PLAN.md. If you'd rather skip that, I can write PLAN.md now
  from what we have.

✻ Cogitated for 18m 44s · done 6:01 PM

❯ all the necesary information is on the ./relay-analytics-starter folder;      
  start creating the PLAN.MD. separate in different tasks, each task will have  
  a section that explain the goal, the quickstart (instructions for the agent   
  to check the task). There will be an API builder, an API reviewer, a frontend 
  builder, and a frontend reviewer. Those are agents (create the basic          
  definitions of those) the task must be short enough so the human can review   
  the results. The cration will be secuential builder -> reviewer -> human      
  review of the Pull request in github (claude code return options to           
  change/enhance some agents). Ideally a pull request should have less than 700 
  lines to review                                                               

  Ran 2 shell commands (ctrl+o to expand)

● The repo has no commits and no GitHub remote, so I need a Task 0 before any
  PRs. I'm writing PLAN.md and the four agent definitions next.
● Write(PLAN.md)
  ⎿  Wrote 296 lines to PLAN.md
       1 # PLAN — DASH-247 "Is this week normal for us?"
       2 
       3 Implementation plan, split into small tasks that each end in one
          reviewable pull request.
       4 Why each decision was made: `PLAN_first_iteration.md` (decision 
         log), `Data_integrity.md`, `Detection_tuning.md`, `OPEN_QUESTION
         S.md`.
       5 
       6 ## Workflow
       7 
     … +289 lines (ctrl+o to expand)

● Now the four agent definitions:

● Bash(mkdir -p /home/admin123/projects/qualitra_challenge/.claude/agents && cd
      /home/admin123/projects/qualitra_challenge/.claude/agents && cat >
      api-builder.md <<'EO…)
  ⎿  api-builder.md
     api-reviewer.md
     frontend-builder.md
     frontend-reviewer.md
  ⎿  Created .claude/agents/api-builder.md (+25 -0)
       1 +---                                                            
       2 +name: api-builder                                              
       3 +description: Implements one backend task (FastAPI, Alembic, Pyt
         +hon domain logic, pytest) from PLAN.md and opens a PR. Use when
         + a PLAN.md task is assigned to api-builder.                    
       4 +---                                                            
       5 +                                                               
       6 +You implement exactly ONE task from `PLAN.md` in the backend (`
         +backend/`, `scripts/`, compose services for the API). The task 
         +id is given in your prompt.                                    
       7 +                                                               
       8 +Before coding:                                                 
       9 +- Read `CLAUDE.md`, the "Workflow", "Decisions" and "API contra
         +ct" sections of `PLAN.md`, and your task. Read `Detection_tunin
         +g.md` when the task touches detection.                         
      10 +- If the task contradicts a decision, or can't fit in < 700 cha
         +nged lines, stop and report back with a proposed fix or split. 
         +Don't improvise.                                               
      11 +                                                               
      12 +While coding:                                                  
      13 +- Branch `task/<id>-<slug>` from an up-to-date `main`.         
      14 +- Stay inside the task's scope. Note anything else as a follow-
         +up in the PR.                                                  
      15 +- Python: type hints, small pure functions, match the existing 
         +code. Domain logic (`app/domain/`) has no DB or FastAPI imports
         +. Timezone conversion only in Python (`zoneinfo`), never in SQL
         +. SQL must run on Postgres and SQLite.                         
      16 +- Never edit `data/seed.sql`, never change the raw tables' data
         +, never hand-run DDL (migrations only).                        
      17 +- Pin every new dependency to an exact version.                
      18 +- Write the tests the task lists; add ones you find necessary. 
      19 +                                                               
      20 +Before opening the PR:                                         
      21 +- Run the task's **Quickstart** exactly; everything must pass. 
         +Run `ruff check` and the full `pytest`.                        
      22 +- Check the line count with the command in PLAN.md (< 700).    
      23 +- Commit with a clear message, push, and open the PR with `gh p
         +r create` (base `main`). Description: Goal · Changes · Quicksta
         +rt output (trimmed) · Line count · Deviations from PLAN.md · Op
         +en questions · Follow-ups.                                     
      24 +                                                               
      25 +Final report: PR URL, line count, quickstart result, deviations
         + and open questions (≤ 15 lines).                              
  ⎿  Created .claude/agents/api-reviewer.md (+22 -0)
       1 +---                                                            
       2 +name: api-reviewer                                             
       3 +description: Reviews a backend PR from api-builder against PLAN
         +.md, re-runs the task's quickstart and posts a review on the PR
         +. Use after api-builder opens a PR.                            
       4 +tools: Bash, Read, Grep, Glob                                  
       5 +---                                                            
       6 +                                                               
       7 +You review ONE backend PR (number and task id given in your pro
         +mpt). You don't change code: you report findings, and the build
         +er fixes them.                                                 
       8 +                                                               
       9 +Steps:                                                         
      10 +1. Read `CLAUDE.md`, the "Workflow", "Decisions" and "API contr
         +act" sections of `PLAN.md`, and the task. Read `Detection_tunin
         +g.md` if detection is touched.                                 
      11 +2. `gh pr checkout <n>`; read the full diff (`git diff main...H
         +EAD`) and the PR description.                                  
      12 +3. Re-run the task's **Quickstart** and the full test suite. Re
         +cord the actual output.                                        
      13 +4. Check, at least:                                            
      14 +   - **Scope:** only this task; < 700 changed lines (command in
         + PLAN.md).                                                     
      15 +   - **Contract:** response shapes, status codes, nulls and ord
         +ering exactly as in PLAN.md.                                   
      16 +   - **Decisions:** dedupe-only view; Mon–Sun local weeks via `
         +zoneinfo`; no timezone math in SQL; N = 8, min history 4, k = 2
         +.5, floors 3 / 20%, low_volume ≤ 6; ranking rule; partial weeks
         + never get a verdict.                                          
      17 +   - **Correctness:** off-by-one in week ranges and baseline wi
         +ndows (the evaluated week must never be in its own history), DS
         +T/Phoenix/UTC handling, `usual = 0`, empty accounts, duplicate 
         +counting.                                                      
      18 +   - **Portability:** SQL and migrations work on both Postgres 
         +and SQLite; seed and raw tables untouched; dependencies pinned.
      19 +   - **Tests:** they cover the cases the task lists and would f
         +ail if the logic were wrong (no tautological tests).           
      20 +5. Post the review with `gh pr review <n> --comment --body-file
         + <file>` (use `--request-changes` if there are blocking finding
         +s). Format: Verdict (APPROVE / CHANGES REQUESTED) · Quickstart 
         +result · Findings, each with severity (blocking / should-fix / 
         +nit), `file:line`, problem and suggested fix · What was verifie
         +d.                                                             
      21 +                                                               
      22 +Only report findings you verified (by reading the code or runni
         +ng it). Final report: verdict, blocking findings, PR URL (≤ 15 
         +lines).                                                        
  ⎿  Created .claude/agents/frontend-builder.md (+25 -0)
       1 +---                                                            
       2 +name: frontend-builder                                         
       3 +description: Implements one frontend task (React + TypeScript +
         + Vite, Vitest) from PLAN.md and opens a PR. Use when a PLAN.md 
         +task is assigned to frontend-builder.                          
       4 +---                                                            
       5 +                                                               
       6 +You implement exactly ONE task from `PLAN.md` in `frontend/` (a
         +nd its compose service). The task id is given in your prompt.  
       7 +                                                               
       8 +Before coding:                                                 
       9 +- Read `CLAUDE.md`, the "Workflow", "Decisions", "API contract"
         + and "Wireframe" sections of `PLAN.md`, and your task. The cont
         +ract source of truth is `openapi.json` at the repo root.       
      10 +- If the task contradicts a decision, needs an API change, or c
         +an't fit in < 700 changed lines, stop and report back with a pr
         +oposed fix or split. Don't change the backend.                 
      11 +                                                               
      12 +While coding:                                                  
      13 +- Branch `task/<id>-<slug>` from an up-to-date `main`.         
      14 +- Stay inside the task's scope. Note anything else as a follow-
         +up in the PR.                                                  
      15 +- TypeScript strict, function components, small components, mat
         +ch the existing code. Types come from the contract. The fronten
         +d displays what the API returns: no re-ranking, no re-computing
         + verdicts.                                                     
      16 +- Accessibility: status is never shown by colour alone (icon + 
         +text), labelled controls, keyboard-usable pickers.             
      17 +- Pin every new dependency to an exact version; commit the lock
         +file.                                                          
      18 +- Tests use fixture JSON shaped exactly like the contract, neve
         +r a live API.                                                  
      19 +                                                               
      20 +Before opening the PR:                                         
      21 +- Run the task's **Quickstart** exactly; lint, tests and build 
         +must pass. Check the manual steps in a running app when the tas
         +k lists them, and describe what you saw.                       
      22 +- Check the line count with the command in PLAN.md (< 700).    
      23 +- Commit, push, and open the PR with `gh pr create` (base `main
         +`). Description: Goal · Changes · Quickstart output (trimmed) ·
         + Manual check · Line count · Deviations from PLAN.md · Open que
         +stions · Follow-ups.                                           
      24 +                                                               
      25 +Final report: PR URL, line count, quickstart result, deviations
         + and open questions (≤ 15 lines).                              
  ⎿  Created .claude/agents/frontend-reviewer.md (+22 -0)
       1 +---                                                            
       2 +name: frontend-reviewer                                        
       3 +description: Reviews a frontend PR from frontend-builder agains
         +t PLAN.md and the wireframe, re-runs the task's quickstart and 
         +posts a review on the PR. Use after frontend-builder opens a PR
         +.                                                              
       4 +tools: Bash, Read, Grep, Glob                                  
       5 +---                                                            
       6 +                                                               
       7 +You review ONE frontend PR (number and task id given in your pr
         +ompt). You don't change code: you report findings, and the buil
         +der fixes them.                                                
       8 +                                                               
       9 +Steps:                                                         
      10 +1. Read `CLAUDE.md`, the "Workflow", "Decisions", "API contract
         +" and "Wireframe" sections of `PLAN.md`, the task, and `openapi
         +.json`.                                                        
      11 +2. `gh pr checkout <n>`; read the full diff (`git diff main...H
         +EAD`) and the PR description.                                  
      12 +3. Re-run the task's **Quickstart** (lint, tests, build). Recor
         +d the actual output. If the task lists manual checks and the AP
         +I is available, verify them against the running app.           
      13 +4. Check, at least:                                            
      14 +   - **Scope:** only this task; < 700 changed lines (command in
         + PLAN.md, lockfiles and generated files excluded).             
      15 +   - **Contract:** types match `openapi.json`; nulls handled (`
         +usual`, `pct_vs_usual` when not_enough_history); no re-sorting 
         +or re-computing of what the API decides.                       
      16 +   - **Wireframe and states:** layout as in PLAN.md; loading, e
         +rror, not enough history, single location, low volume and UTC n
         +ote handled where the task requires them.                      
      17 +   - **UX/accessibility:** status shown with icon + text, not c
         +olour alone; labelled, keyboard-usable controls; readable numbe
         +rs (percent signs, rounding).                                  
      18 +   - **Quality:** strict TypeScript without `any` escapes; depe
         +ndencies pinned; no dead code or leftover debug output.        
      19 +   - **Tests:** cover the task's cases with contract-shaped fix
         +tures and would fail if the UI were wrong.                     
      20 +5. Post the review with `gh pr review <n> --comment --body-file
         + <file>` (use `--request-changes` if there are blocking finding
         +s). Format: Verdict (APPROVE / CHANGES REQUESTED) · Quickstart 
         +result · Findings, each with severity (blocking / should-fix / 
         +nit), `file:line`, problem and suggested fix · What was verifie
         +d.                                                             
      21 +                                                               
      22 +Only report findings you verified. Final report: verdict, block
         +ing findings, PR URL (≤ 15 lines).                             

● Bash(sed -i 's/ (use `--request-changes` if there are blocking findings)/.
      Always use `--comment`: the PRs are opened from the same GitHub account,
      and GitHub reject…)
  ⎿  frontend-reviewer.md:20:5. Post the review with `gh pr review <n> --co
     mment --body-file <file>`. Always use `--comment`: the PRs are opened
     from the same GitHub account, and GitHub rejects approve or request-ch
     … +10 lines (ctrl+o to expand)
  ⎿  Updated .claude/agents/api-reviewer.md (+1 -1)
      17     - **Correctness:** off-by-one in week ranges and baseline wi
          ndows (the evaluated week must never be in its own history), DS
          T/Phoenix/UTC handling, `usual = 0`, empty accounts, duplicate 
          counting.
      18     - **Portability:** SQL and migrations work on both Postgres 
          and SQLite; seed and raw tables untouched; dependencies pinned.
      19     - **Tests:** they cover the cases the task lists and would f
          ail if the logic were wrong (no tautological tests).
      20 -5. Post the review with `gh pr review <n> --comment --body-file
         - <file>` (use `--request-changes` if there are blocking finding
         -s). Format: Verdict (APPROVE / CHANGES REQUESTED) · Quickstart 
         -result · Findings, each with severity (blocking / should-fix / 
         -nit), `file:line`, problem and suggested fix · What was verifie
         -d.                                                             
      20 +5. Post the review with `gh pr review <n> --comment --body-file
         + <file>`. Always use `--comment`: the PRs are opened from the s
         +ame GitHub account, and GitHub rejects approve or request-chang
         +es on your own PR, so the verdict goes in the body. Format: Ver
         +dict (APPROVE / CHANGES REQUESTED) · Quickstart result · Findin
         +gs, each with severity (blocking / should-fix / nit), `file:lin
         +e`, problem and suggested fix · What was verified.             
      21  
      22  Only report findings you verified (by reading the code or runni
          ng it). Final report: verdict, blocking findings, PR URL (≤ 15 
          lines).
  ⎿  Updated .claude/agents/frontend-reviewer.md (+1 -1)
      17     - **UX/accessibility:** status shown with icon + text, not c
          olour alone; labelled, keyboard-usable controls; readable numbe
          rs (percent signs, rounding).
      18     - **Quality:** strict TypeScript without `any` escapes; depe
          ndencies pinned; no dead code or leftover debug output.
      19     - **Tests:** cover the task's cases with contract-shaped fix
          tures and would fail if the UI were wrong.
      20 -5. Post the review with `gh pr review <n> --comment --body-file
         - <file>` (use `--request-changes` if there are blocking finding
         -s). Format: Verdict (APPROVE / CHANGES REQUESTED) · Quickstart 
         -result · Findings, each with severity (blocking / should-fix / 
         -nit), `file:line`, problem and suggested fix · What was verifie
         -d.                                                             
      20 +5. Post the review with `gh pr review <n> --comment --body-file
         + <file>`. Always use `--comment`: the PRs are opened from the s
         +ame GitHub account, and GitHub rejects approve or request-chang
         +es on your own PR, so the verdict goes in the body. Format: Ver
         +dict (APPROVE / CHANGES REQUESTED) · Quickstart result · Findin
         +gs, each with severity (blocking / should-fix / nit), `file:lin
         +e`, problem and suggested fix · What was verified.             
      21  
      22  Only report findings you verified. Final report: verdict, block
          ing findings, PR URL (≤ 15 lines).

● PLAN.md and the four agent definitions are written. Nothing is committed yet:
  the repo has no commits and no GitHub remote, so PRs can't be opened until
  Task 0 is done.

  PLAN.md starts with the workflow and the rules every task shares, then the 11
  tasks:
  - Workflow: builder → reviewer → your PR review → I offer changes to the agent
    definitions based on what your review caught.
  - PR rule: under 700 changed lines, with the command to check it (lockfiles,
    the seed and the generated openapi.json don't count). A builder that can't
    fit stops and proposes a split.
  - Shared reference: a short summary of every decision, the target API contract
    and the wireframe, so the agents don't have to dig through the decision
    log.
  - Each task has a goal, scope, a quickstart the agents and you can run to
    check it, and an estimated size.

  ┌─────┬───────────────────────────────────────┬──────────────────┬────────┐
  │  #  │                 Task                  │      Agent       │ Est.   │
  │     │                                       │                  │ lines  │
  ├─────┼───────────────────────────────────────┼──────────────────┼────────┤
  │ 0   │ Initial commit + GitHub repo          │ you + me         │ —      │
  ├─────┼───────────────────────────────────────┼──────────────────┼────────┤
  │ 1   │ API skeleton, dedupe view migration,  │ api-builder      │ ~350   │
  │     │ /health, test harness                 │                  │        │
  ├─────┼───────────────────────────────────────┼──────────────────┼────────┤
  │ 2   │ Weeks, detection and ranking logic,   │ api-builder      │ ~550   │
  │     │ unit tests only                       │                  │        │
  ├─────┼───────────────────────────────────────┼──────────────────┼────────┤
  │ 3   │ Database queries + GET /accounts      │ api-builder      │ ~350   │
  ├─────┼───────────────────────────────────────┼──────────────────┼────────┤
  │ 4   │ GET /accounts/{id}/weekly-insight +   │ api-builder      │ ~500   │
  │     │ seed test                             │                  │        │
  ├─────┼───────────────────────────────────────┼──────────────────┼────────┤
  │ 5   │ API container + exported openapi.json │ api-builder      │ ~200   │
  ├─────┼───────────────────────────────────────┼──────────────────┼────────┤
  │ 6   │ Frontend skeleton, API client,        │ frontend-builder │ ~450   │
  │     │ account/week pickers                  │                  │        │
  ├─────┼───────────────────────────────────────┼──────────────────┼────────┤
  │ 7   │ Verdict card + 7-day chart            │ frontend-builder │ ~450   │
  ├─────┼───────────────────────────────────────┼──────────────────┼────────┤
  │ 8   │ Ranked locations table                │ frontend-builder │ ~350   │
  ├─────┼───────────────────────────────────────┼──────────────────┼────────┤
  │ 9   │ Frontend container, docker compose up │ frontend-builder │ ~150   │
  │     │  runs everything                      │                  │        │
  ├─────┼───────────────────────────────────────┼──────────────────┼────────┤
  │ 10  │ Write-up                              │ you + me         │ —      │
  └─────┴───────────────────────────────────────┴──────────────────┴────────┘

  The agents are in .claude/agents/. Builders work on a task/<id>-<slug> branch,
  run the quickstart and open the PR. Reviewers can read and run things but not
  edit; they re-run the quickstart and post findings by severity, with
  file:line. Reviewers post a comment with the verdict in the body, because
  GitHub won't let you approve or request changes on your own PR. Claude Code
  may only pick up new agent definitions after a session restart.

  A few details weren't discussed, so I chose them. Change any you disagree
  with:
  - Partial or future weeks: asking for one returns a 422 error instead of a
    verdict.
  - Low volume: a row counts as low-volume when its usual is 6 events a week or
    fewer. That's where the lower bound of the band reaches 0.
  - Ranking: lower-than-usual locations are sorted by biggest % drop first.
  - /accounts: I dropped the first_week field. The week picker only needs
    latest_complete_week.
  - Single-location accounts: whether to show a one-row table is left to the
    Task 8 builder, who has to note the choice in the PR.

  For Task 0: create an empty GitHub repo under a name of your own (not a fork,
  not relay-analytics-starter) and give me its URL. I'll then add it as origin,
  update CLAUDE.md to point at the plan, make the initial commit and push main.

✻ Baked for 2m 40s · done 6:21 PM

❯ These agents will run using Sonnet. What other information can we provide to  
  them so they don't have to take high-level decisions because we already took  
  those? also if task wont fit use stacked PRs. Test must be a different        
  section. Ideally integration tests. all tasks should submit one or more PR to 
  github.                                                                       
  Also check the first iteration plan because I had some tests that must be a   
  different task where you will check those results, those cases. Also suggest  
  more cases. The only ones that I wrote were related to checking that:         
  - allocation with no value                                                    
  - allocation with values                                                      
  - abnormal values                                                             
  - allocation with values, with locations that require review                  

● Before I rewrite the plan, here's how I'll handle each point:

  1. Sonnet: all four agents get model: sonnet. To keep them from making design
     decisions, PLAN.md gets a fixed implementation spec:
     - file layout and module names
     - function signatures
     - exact Pydantic/TypeScript models
     - the view SQL
     - pinned library versions
     - error body format, rounding and labels
     - the component tree, plus fixture and seed-loading approach

     Plus one rule: anything not in the spec gets the simplest option, listed in
     the PR as a "decision taken".
  2. Stacked PRs: a task that won't fit under 700 lines is split into stacked
     PRs. Each one targets the previous branch.
  3. Tests: every task gets its own Tests section, separate from scope and
     quickstart, preferring integration tests. On top of that there are
     dedicated test tasks built around the scenarios from your first iteration
     plan.
  4. Every task ends in a PR: Task 0 becomes a minimal commit on main plus a
     foundation PR, and the write-up becomes a PR too.

  Your first-iteration tests used SQLite with fake accounts, plus test_seed.py.
  "Allocation" read as account here, which fits those fake accounts. Your 4
  cases become required scenarios:
  - S1: an account with no events
  - S2: an account with normal values
  - S3: abnormal values, both higher and lower
  - S4: an account with values where some locations need review, which also
    covers the ranking order

  Here are my suggested additions:

● User answered Claude's questions:
  ⎿  · Which suggested test scenarios should be added to your 4 required ones? →
     Boundaries & math edges, Robustness & data quirks, API validation & 
     errors, Seed golden tests
     · How should the frontend be tested? → MSW only

  Ran 2 shell commands (ctrl+o to expand)

● I'm writing the expanded PLAN.md with a fixed implementation spec, separate
  Tests sections, scenario-test tasks, stacked PRs, and one PR per task.

● Write(PLAN.md)
  ⎿  Added 400 lines, removed 199 lines
        1  # PLAN — DASH-247 "Is this week normal for us?"
        2  
        3 -Implementation plan, split into small tasks that each end in o
          -ne reviewable pull request.                                   
        4 -Why each decision was made: `PLAN_first_iteration.md` (decisio
          -n log), `Data_integrity.md`, `Detection_tuning.md`, `OPEN_QUES
          -TIONS.md`.                                                    
        3 +Implementation plan split into small tasks. **Every task ends 
          +in one or more GitHub PRs.**                                  
        4 +Why each decision was made: `PLAN_first_iteration.md` (decisio
          +n log), `Data_integrity.md`, `Detection_tuning.md`, `OPEN_QUES
          +TIONS.md`. Product context: `relay-analytics-starter/docs/`.  
        5  
        6 -## Workflow                                                   
        6 +**Agents run on Sonnet. Everything that needs judgment has alr
          +eady been decided in this file.** Agents implement; they don't
          + redesign.                                                    
        7  
        8 -Each task runs sequentially:                                  
        8 +---                                                           
        9  
       10 -1. **Builder agent** (`api-builder` or `frontend-builder`) cre
          -ates branch `task/<id>-<slug>` from `main`, implements **only*
          -* that task, runs the task's quickstart, and opens a PR.      
       11 -2. **Reviewer agent** (`api-reviewer` or `frontend-reviewer`) 
          -checks the PR against this plan, re-runs the quickstart, and p
          -osts a review on the PR. Blocking findings go back to the buil
          -der (same branch) until the reviewer approves.                
       12 -3. **Human review** on GitHub. Merge, or request changes (back
          - to step 1 on the same branch).                               
       13 -4. After each human review, Claude Code offers options to chan
          -ge or enhance the agent definitions (`.claude/agents/*.md`) ba
          -sed on what the review caught, so the next task benefits.     
       10 +## 1. Workflow                                                
       11  
       15 -Rules for every PR:                                           
       16 -- **< 700 changed lines** (added + removed), excluding lockfil
          -es, `data/seed.sql` and the generated `openapi.json`. Check wi
          -th:                                                           
       12 +Roles:                                                        
       13 +- **Orchestrator:** the main Claude Code session. It launches 
          +agents one at a time, relays results to the human, and after e
          +ach human review offers concrete options to change or enhance 
          +the agent definitions (`.claude/agents/*.md`) based on what th
          +e review caught.                                              
       14 +- **Builders:** `api-builder`, `frontend-builder`. **Reviewers
          +:** `api-reviewer`, `frontend-reviewer`.                      
       15 +- **Human:** reviews and merges every PR on GitHub.           
       16 +                                                              
       17 +Per task, strictly sequential:                                
       18 +1. Builder: branch `task/<id>-<slug>` from an up-to-date `main
          +` → implement the task's **Scope** → write its **Tests** → run
          + its **Quickstart** → open the PR.                            
       19 +2. Reviewer: checks the PR against this plan, re-runs the Quic
          +kstart, posts a review comment. Blocking findings → the builde
          +r fixes them on the same branch → re-review.                  
       20 +3. Human reviews and merges (or requests changes → step 1 on t
          +he same branch).                                              
       21 +4. Orchestrator offers agent improvements, then starts the nex
          +t task.                                                       
       22 +                                                              
       23 +### PR rules                                                  
       24 +- **< 700 changed lines** (added + removed), excluding generat
          +ed files and data:                                            
       25    ```bash
       18 -  git diff --numstat main...HEAD -- . ':!**/package-lock.json'
          - ':!data/seed.sql' ':!**/openapi.json' | awk '{s+=$1+$2} END {
          -print s}'                                                     
       26 +  git diff --numstat main...HEAD -- . ':!**/package-lock.json'
          + ':!data/seed.sql' ':!openapi.json' ':!frontend/src/api/schema
          +.d.ts' \                                                      
       27 +    | awk '{s+=$1+$2} END {print s}'                          
       28    ```
       20 -  If a task won't fit, the builder stops and proposes a split 
          -instead of opening an oversized PR.                           
       21 -- PR description: goal, what changed, quickstart output, line 
          -count, deviations from the plan, and open questions.          
       22 -- No scope creep: anything not in the task goes in the PR's "f
          -ollow-ups" list.                                              
       29 +- **Stacked PRs** when a task doesn't fit: split along the tas
          +k's Scope bullets into `task/<id>a-<slug>` (base `main`), `tas
          +k/<id>b-<slug>` (base `task/<id>a-<slug>`), and so on. Each PR
          + passes its own tests. The PR title says `[<id>a/2]`, and each
          + description links the others. After the lower PR merges, reta
          +rget the next one: `gh pr edit <n> --base main`.              
       30 +- **PR description:** Goal · Changes · Tests added · Quickstar
          +t output (trimmed) · Line count · **Decisions taken** (anythin
          +g this plan didn't specify) · Deviations · Follow-ups.        
       31 +- **Commit messages:** `<type>(<area>): <summary>` with type ∈
          + feat, fix, test, chore, docs; area ∈ api, web, db, infra, doc
          +s.                                                            
       32  
       24 -## Decisions every task must respect (summary)                
       33 +### When something isn't specified                            
       34 +- Pick the **simplest option consistent with this plan** and l
          +ist it under "Decisions taken" in the PR.                     
       35 +- **Stop and ask the orchestrator** instead if it would change
          +: the API contract, the data/cleaning rules, the detection mat
          +h or constants, the ranking, or the scope of another task.    
       36 +- If a test in a test task (6, 7, 11) fails because of an app 
          +bug: fix it in the same PR as a separate `fix(...)` commit if 
          +the fix is < 50 lines; otherwise stop and report.             
       37  
       26 -- **Data:** raw tables are never modified; the seed is used as
          --is. View `clean_activity_events` removes only the 12 exact du
          -plicates (same account_id, location, event_type, occurred_at, 
          -duration_seconds, outcome; keep the lowest id).               
       27 -- **Metric:** total events per week. Weeks are **Mon–Sun in th
          -e account's local time**. UTC → local conversion happens in **
          -Python (`zoneinfo`)**, never in SQL (SQLite has no timezones).
       28 -- **As-of:** `as_of` = `AS_OF_DATE` env var if set, else the m
          -ax `occurred_at` in the dataset. A week is complete when its S
          -unday is before `as_of`'s local date. Default week = the lates
          -t complete week (Jul 20–26, 2026). Partial weeks never get a v
          -erdict.                                                       
       29 -- **Baseline:** the previous **N = 8** complete weeks of the s
          -ame series (account total, or account+location), never includi
          -ng the evaluated week. A series starts at its first complete w
          -eek with an event; weeks without events inside its range count
          - as 0. **Fewer than 4 prior weeks → `not_enough_history`**; 4–
          -7 → use what's available.                                     
       30 -- **Detection** (from `Detection_tuning.md`):                 
       38 +---                                                           
       39 +                                                              
       40 +## 2. Decisions (fixed)                                       
       41 +                                                              
       42 +- **Data:** raw tables are never modified, and the seed is use
          +d as-is. View `clean_activity_events` removes only the 12 exac
          +t duplicates.                                                 
       43 +- **Metric:** total events per week, all event types together.
       44 +- **Weeks:** Mon–Sun in the **account's local time**. UTC → lo
          +cal conversion happens **only in Python (`zoneinfo`)**, never 
          +in SQL.                                                       
       45 +- **As-of:** `as_of_local` = `AS_OF_DATE` (env, `YYYY-MM-DD`) 
          +if set, else the local date of the dataset's max `occurred_at`
          + in the clean view. Latest complete week = `monday_of(as_of_lo
          +cal) − 7 days` (Jul 20, 2026 on the seed). Default week = the 
          +latest complete week. Partial or future weeks → 422.          
       46 +- **First complete week of the dataset:** let `d` = local date
          + of the dataset's min `occurred_at`; `first_complete_week = d 
          +if d is a Monday else monday_of(d) + 7` (Feb 2, 2026 on the se
          +ed). Earlier weeks → 422.                                     
       47 +- **Series:** one per account (all its events) and one per acc
          +ount+location. A series starts at the first Monday ≥ `first_co
          +mplete_week` whose week has ≥ 1 event. Weeks without events in
          +side the series count as 0.                                   
       48 +- **History of a week W:** the weeks `max(series_start, W − 8 
          +weeks) … W − 1 week`, zero-filled. **The evaluated week is nev
          +er in its own history.** No series_start, or series_start ≥ W 
          +→ empty history.                                              
       49 +- **Detection** (constants in `backend/app/domain/detection.py
          +`: `K = 2.5`, `N_WEEKS = 8`, `MIN_HISTORY = 4`, `MIN_ABS = 3`,
          + `MIN_PCT = 0.20`, `LOW_VOLUME_USUAL = 6`):                   
       50    ```
       51 +  if len(history) < MIN_HISTORY: status = not_enough_history; 
          +usual/lower/upper/pct = None; low_volume = False              
       52    usual  = median(history)
       33 -  MAD    = median(|x − usual|)                                
       53 +  MAD    = median(|x − usual| for x in history)               
       54    spread = max(1.4826 · MAD, √usual)
       35 -  lower  = max(0, usual − 2.5 · spread)                       
       36 -  upper  = usual + 2.5 · spread                               
       37 -  diff   = value − usual;  pct = diff / usual (null when usual
          - = 0)                                                         
       38 -  flagged if (value < lower or value > upper) and |diff| ≥ 3  
       39 -             and (|pct| ≥ 0.20 if usual > 0 else value > 0)   
       40 -  status = higher_than_usual | lower_than_usual if flagged, el
          -se normal                                                     
       55 +  lower  = max(0, usual − K · spread)                         
       56 +  upper  = usual + K · spread                                 
       57 +  diff   = value − usual                                      
       58 +  pct    = diff / usual if usual > 0 else None                
       59 +  flagged = (value < lower or value > upper) and |diff| ≥ MIN_
          +ABS                                                           
       60 +            and (|pct| ≥ MIN_PCT if usual > 0 else value > 0) 
       61 +  status = (higher_than_usual if diff > 0 else lower_than_usua
          +l) if flagged else normal                                     
       62 +  low_volume = usual ≤ LOW_VOLUME_USUAL                       
       63    ```
       42 -- **Low volume:** `low_volume = usual ≤ 6` (below that, `lower
          -` is 0 and drops can't be flagged). The UI warns that results 
          -may be odd for these rows/accounts.                           
       43 -- **Ranking of locations:** `lower_than_usual` first (biggest 
          -% drop first), then `higher_than_usual` and `normal` together 
          -by location name, then `not_enough_history`.                  
       44 -- **Daily context:** 7 days of the selected week, each with `u
          -sual` = median of that weekday over the same baseline weeks. A
          -ccount level only, no daily status.                           
       45 -- **Data notes:** "N duplicate events removed" (raw minus clea
          -n rows in the selected week for that account, only if > 0); "T
          -imezone is UTC — it may be misconfigured" when the account's t
          -imezone is `UTC`.                                             
       46 -- **Out of scope:** auth, rate limiting, alerting, ML/forecast
          -ing, holiday/campaign calendar, daily verdicts, per-event-type
          - metrics, location drill-down.                                
       47 -- **Tests:** pure unit tests for the domain logic; integration
          - tests run against **SQLite** (migrated with Alembic, so the v
          -iew is tested too).                                           
       64 +- **Daily context:** the 7 days of the selected week (account 
          +level only). `usual` per day = median of that weekday's count 
          +over the account's history weeks; `None` when the account summ
          +ary is `not_enough_history`. Days never get a status.         
       65 +- **Ranking of locations:** first `lower_than_usual` by `pct_v
          +s_usual` ascending (biggest drop first, ties by name); then `h
          +igher_than_usual` and `normal` together by location name; then
          + `not_enough_history` by name. Only lower counts as "needs att
          +ention".                                                      
       66 +- **Locations listed:** every location with ≥ 1 clean event fo
          +r the account, at any time.                                   
       67 +- **Data notes** (exact strings, in this order, only when they
          + apply):                                                      
       68 +  - `"1 duplicate event removed from this week."` / `"{n} dupl
          +icate events removed from this week."`: n = raw rows not in th
          +e clean view whose local date falls in the selected week.     
       69 +  - `"This account's timezone is set to UTC, which may be a mi
          +sconfiguration; days and weeks may be shifted."`: when `timezo
          +ne == "UTC"`.                                                 
       70 +- **Rounding** (in the service, not the domain): `usual`, `low
          +er`, `upper` to 1 decimal; `pct_vs_usual` to 3 decimals (a fra
          +ction: −0.32 means −32%).                                     
       71 +- **Out of scope:** auth, rate limiting, alerting, ML/forecast
          +ing, holiday/campaign calendar, daily verdicts, per-event-type
          + metrics, location drill-down, persisting UI state in the URL.
       72  
       49 -## API contract (target)                                      
       73 +---                                                           
       74  
       51 -```yaml                                                       
       52 -GET /health                      → 200 {status: "ok", db: "ok"
          -}   (503 with db: "error" if the DB is unreachable)           
       53 -GET /accounts                    → 200 [AccountSummary]       
          -    (ordered by name)                                         
       54 -  AccountSummary: {id, name, industry, timezone, location_coun
          -t, latest_complete_week}                                      
       55 -GET /accounts/{account_id}/weekly-insight?week_start=YYYY-MM-D
          -D                                                             
       56 -  week_start: optional Monday (account-local); default = lates
          -t complete week                                               
       57 -  200 WeeklyInsight                                           
       58 -  404 unknown account                                         
       59 -  422 week_start not a Monday, before the dataset's first comp
          -lete week, or not complete yet                                
       60 -WeeklyInsight:                                                
       61 -  account:    {id, name, timezone}                            
       62 -  week:       {start, end}                                  # 
          -Monday, Sunday                                                
       63 -  baseline:   {method: "median_mad", weeks_used, from, to}  # 
          -from/to null when no history                                  
       64 -  summary:    Metric                                        # 
          -the account's own weekly total                                
       65 -  days:       [{date, weekday, total, usual}]               # 
          -7 rows; usual null without history                            
       66 -  locations:  [Metric & {location, history_weeks}]          # 
          -ranked as above                                               
       67 -  data_notes: [string]                                        
       68 -Metric: {total, usual, lower, upper, pct_vs_usual, status, low
          -_volume}                                                      
       69 -  status: normal | lower_than_usual | higher_than_usual | not_
          -enough_history                                                
       70 -  usual/lower/upper/pct_vs_usual: null when not_enough_history
       71 -```                                                           
       75 +## 3. Implementation spec (fixed)                             
       76  
       73 -Account 20 (no events): 200, `summary.total = 0`, `status = no
          -t_enough_history`, `locations = []`, `days` all 0.            
       77 +### 3.1 Libraries                                             
       78 +Pin each to the **latest stable version at implementation time
          +** (check with `pip index versions <pkg>` / `npm view <pkg> ve
          +rsion`), exact pins only. Don't add any library that isn't lis
          +ted. If one seems necessary, stop and ask.                    
       79 +- **Backend runtime:** fastapi, uvicorn[standard], sqlalchemy 
          +(already pinned), psycopg[binary] (pinned), alembic (pinned). 
          +No ORM models (SQLAlchemy Core + `text()` only), no pydantic-s
          +ettings.                                                      
       80 +- **Backend dev** (`backend/requirements-dev.txt`, `-r require
          +ments.txt` first): pytest, httpx, ruff.                       
       81 +- **Frontend:** react, react-dom, recharts. Dev: vite, @vitejs
          +/plugin-react, typescript, eslint, typescript-eslint, eslint-p
          +lugin-react-hooks, vitest, jsdom, @testing-library/react, @tes
          +ting-library/user-event, @testing-library/jest-dom, msw, opena
          +pi-typescript. Node 22 LTS (`.nvmrc` = `22`). No UI kit, no CS
          +S framework, no state or data-fetching library, no date librar
          +y.                                                            
       82  
       75 -## Wireframe (target)                                         
       76 -                                                              
       83 +### 3.2 Backend layout                                        
       84  ```
       78 -┌ Relay · Weekly activity ─────────────────────┐              
       79 -│ Account [Metro Collision Centers ▾]          │              
       80 -│ Week    [◀ Jul 20 – Jul 26, 2026 ▶]  (ET)    │              
       81 -├──────────────────────────────────────────────┤              
       82 -│ ▼ LOWER THAN USUAL                           │              
       83 -│ 52 events · usual ~76 (range 64–88) · −32%   │              
       84 -│ vs. previous 8 weeks                         │              
       85 -├──────────────────────────────────────────────┤              
       86 -│ This week by day   █ actual  · usual         │              
       87 -│  █·  █·  ▄·  █·  ▄·  ▁·  ▁·                  │              
       88 -│  Mo  Tu  We  Th  Fr  Sa  Su                  │              
       89 -├──────────────────────────────────────────────┤              
       90 -│ Locations (15)          needs attention first│              
       91 -│ Location  This wk  Usual  vs usual  Status   │              
       92 -│ Site C        1      5     −80%    ▼ Lower   │              
       93 -│ Site N       11      5    +120%    ▲ Higher  │              
       94 -│ Site A        5      5      0%     Normal    │              
       95 -│ …                                            │              
       96 -├──────────────────────────────────────────────┤              
       97 -│ ⓘ 2 duplicate events removed                 │              
       98 -└──────────────────────────────────────────────┘              
       85 +backend/                                                      
       86 +  pyproject.toml            # ruff (line-length 110, target py
          +313) + pytest config (testpaths, markers: slow)               
       87 +  app/                                                        
       88 +    main.py                 # create_app(settings: Settings | 
          +None = None) -> FastAPI; app = create_app()                   
       89 +    config.py               # @dataclass(frozen) Settings: dat
          +abase_url, as_of_date: date | None, cors_origins: list[str]; S
          +ettings.from_env()                                            
       90 +    db.py                   # make_engine(url); get_connection
          + dependency (yields a Connection)                             
       91 +    routes.py               # APIRouter with the 3 endpoints  
       92 +    schemas.py              # Pydantic response models (3.4)  
       93 +    repository.py           # SQL only (3.3)                  
       94 +    service.py              # list_accounts(), build_weekly_in
          +sight(): orchestration + rounding + errors                    
       95 +    seed.py                 # load_seed(engine, path) -> bool 
          +(False if accounts already has rows)                          
       96 +    domain/                                                   
       97 +      weeks.py              # pure date/timezone helpers      
       98 +      detection.py          # constants + evaluate() + weekday
          +_usuals()                                                     
       99 +      ranking.py            # rank_locations()                
      100 +  migrations/versions/0002_clean_activity_events.py           
      101 +  tests/                                                      
      102 +    conftest.py             # fixtures (3.5)                  
      103 +    factories.py            # data builders (3.5)             
      104 +    unit/                   # domain only                     
      105 +    integration/            # API through TestClient on SQLite
      106  ```
      100 -States: loading, API error, not enough history (account 20), s
          -ingle-location account, low-volume warning, UTC timezone warni
          -ng.                                                           
      107 +- Env vars: `DATABASE_URL` (default `postgresql+psycopg://rela
          +y:relay@localhost:5432/relay`), `AS_OF_DATE` (optional), `CORS
          +_ORIGINS` (comma-separated, default `http://localhost:5173,htt
          +p://localhost:8080`).                                         
      108 +- Datetimes from the DB are naive UTC. SQLite returns strings,
          + so the repository normalizes every timestamp with `datetime.f
          +romisoformat` when it gets a `str`.                           
      109  
      102 ----                                                           
      110 +### 3.3 SQL                                                   
      111 +Migration `0002_clean_activity_events` (portable; NULLs fall i
          +n the same partition on both engines):                        
      112 +```sql                                                        
      113 +CREATE VIEW clean_activity_events AS                          
      114 +SELECT id, account_id, location, event_type, occurred_at, dura
          +tion_seconds, outcome                                         
      115 +FROM (                                                        
      116 +  SELECT e.*, ROW_NUMBER() OVER (                             
      117 +    PARTITION BY account_id, location, event_type, occurred_at
          +, duration_seconds, outcome                                   
      118 +    ORDER BY id) AS rn                                        
      119 +  FROM activity_events e                                      
      120 +) t                                                           
      121 +WHERE rn = 1;                                                 
      122 +```                                                           
      123 +Downgrade: `DROP VIEW clean_activity_events`.                 
      124  
      104 -## Task 0 — Foundation commit and GitHub repo (human + Claude 
          -Code, no agents)                                              
      125 +Repository functions (each takes a `Connection`):             
      126 +- `ping(conn) -> None`: `SELECT 1`.                           
      127 +- `list_accounts(conn)`: id, name, industry, timezone, `COUNT(
          +DISTINCT c.location)` as location_count (LEFT JOIN on the clea
          +n view), ordered by name.                                     
      128 +- `get_account(conn, account_id)`: one row or None.           
      129 +- `dataset_bounds(conn) -> tuple[datetime, datetime] | None`: 
          +min/max `occurred_at` of the clean view.                      
      130 +- `account_events(conn, account_id) -> list[tuple[str, datetim
          +e]]`: (location, occurred_at) of **all** the account's clean e
          +vents. Volume is ≤ ~2.7k rows per account; the production note
          + (rollup table) goes in the write-up.                         
      131 +- `duplicate_timestamps(conn, account_id) -> list[datetime]`: 
          +`occurred_at` of raw rows whose id isn't in the clean view.   
      132  
      106 -**Goal:** put the existing foundation on `main` so every later
          - task is a reviewable PR.                                     
      133 +### 3.4 Domain signatures and API models                      
      134 +```python                                                     
      135 +# domain/weeks.py                                             
      136 +def local_date(occurred_at_utc: datetime, tz: ZoneInfo) -> dat
          +e                                                             
      137 +def monday_of(d: date) -> date                                
      138 +def first_complete_week(min_local: date) -> date              
      139 +def latest_complete_week(as_of_local: date) -> date           
      140 +def weekly_counts(timestamps_utc: Iterable[datetime], tz: Zone
          +Info) -> Counter[date]   # key = local Monday                 
      141 +def daily_counts(timestamps_utc: Iterable[datetime], tz: ZoneI
          +nfo) -> Counter[date]    # key = local date                   
      142 +def series_start(counts: Mapping[date, int], first_week: date)
          + -> date | None                                               
      143 +def history(counts: Mapping[date, int], start: date | None, we
          +ek: date, n_weeks: int) -> list[tuple[date, int]]             
      144  
      108 -- Human: create an **empty GitHub repo with your own name** (n
          -ot a fork, not `relay-analytics-starter`) and add it as `origi
          -n`.                                                           
      109 -- Claude Code: add `.claude/agents/` (already drafted), update
          - `CLAUDE.md` to point at this plan, then make the initial comm
          -it (db, migrations, seed, docs, analysis) and push `main`.    
      145 +# domain/detection.py                                         
      146 +class Status(StrEnum): NORMAL = "normal"; LOWER = "lower_than_
          +usual"; HIGHER = "higher_than_usual"; NOT_ENOUGH = "not_enough
          +_history"                                                     
      147 +@dataclass(frozen=True)                                       
      148 +class Evaluation: total: int; usual: float | None; lower: floa
          +t | None; upper: float | None                                 
      149 +                  pct_vs_usual: float | None; status: Status; 
          +low_volume: bool; history_weeks: int                          
      150 +def evaluate(value: int, history: Sequence[int]) -> Evaluation
      151 +def weekday_usuals(history_weeks: Sequence[date], daily: Mappi
          +ng[date, int]) -> list[float | None]  # 7 items, Mon..Sun     
      152  
      111 -**Quickstart:**                                               
      112 -```bash                                                       
      113 -git log --oneline -1 && git remote -v                         
      114 -docker compose up -d --wait && ./scripts/load_seed.sh   # 20 a
          -ccounts, 12626 events                                         
      153 +# domain/ranking.py                                           
      154 +def rank_locations(items: Sequence[tuple[str, Evaluation]]) ->
          + list[tuple[str, Evaluation]]                                 
      155  ```
      156 +Pydantic models (`schemas.py`). Field names are the contract: 
      157 +```python                                                     
      158 +class Health(BaseModel): status: Literal["ok", "error"]; db: L
          +iteral["ok", "error"]                                         
      159 +class AccountSummary(BaseModel): id: int; name: str; industry:
          + str; timezone: str; location_count: int; latest_complete_week
          +: date | None                                                 
      160 +class AccountRef(BaseModel): id: int; name: str; timezone: str
      161 +class Week(BaseModel): start: date; end: date                 
          +     # Monday, Sunday                                         
      162 +class Baseline(BaseModel): method: Literal["median_mad"]; week
          +s_used: int; start: date | None; end: date | None             
      163 +class Metric(BaseModel): total: int; usual: float | None; lowe
          +r: float | None; upper: float | None                          
      164 +                         pct_vs_usual: float | None; status: S
          +tatus; low_volume: bool                                       
      165 +class LocationMetric(Metric): location: str; history_weeks: in
          +t                                                             
      166 +class Day(BaseModel): date: date; weekday: Literal["Mon","Tue"
          +,"Wed","Thu","Fri","Sat","Sun"]; total: int; usual: float | No
          +ne                                                            
      167 +class WeeklyInsight(BaseModel): account: AccountRef; week: Wee
          +k; baseline: Baseline; summary: Metric                        
      168 +                                days: list[Day]; locations: li
          +st[LocationMetric]; data_notes: list[str]                     
      169 +```                                                           
      170 +`Baseline.start` = the Monday of the oldest history week; `Bas
          +eline.end` = the Sunday of the newest; both None when there's 
          +no history.                                                   
      171  
      117 ----                                                           
      172 +### 3.5 Endpoints and errors                                  
      173 +| Endpoint | Success | Errors (`{"detail": "<exact message>"}`
          +) |                                                           
      174 +|---|---|---|                                                 
      175 +| `GET /health` | 200 `{"status":"ok","db":"ok"}` | 503 `{"sta
          +tus":"error","db":"error"}` when `ping` raises |              
      176 +| `GET /accounts` | 200 `list[AccountSummary]` | — |          
      177 +| `GET /accounts/{account_id}/weekly-insight?week_start=YYYY-M
          +M-DD` | 200 `WeeklyInsight` | 404 `Account {id} not found` · 4
          +22 `week_start must be a Monday` · 422 `week_start is before t
          +he first complete week ({date})` · 422 `week_start is not comp
          +lete yet; the latest complete week is {date}` |               
      178  
      119 -## Task 1 — API skeleton, clean view, health (`api-builder`) ·
          - ~350 lines                                                   
      179 +Account without events: 200 with `summary.total = 0`, status `
          +not_enough_history`, `locations = []`, 7 days with `total = 0`
          + and `usual = null`, `baseline.weeks_used = 0`.               
      180  
      121 -**Goal:** a runnable FastAPI app with the cleaning view and a 
          -test harness that the next tasks build on.                    
      181 +### 3.6 Test harness (built in Task 1, used by every backend t
          +est)                                                          
      182 +- `conftest.py`:                                              
      183 +  - `db_url(tmp_path)` → `sqlite:///{tmp_path}/test.db`       
      184 +  - `engine` runs `alembic.command.upgrade(Config("alembic.ini
          +"), "head")` with `DATABASE_URL` monkeypatched, then yields `m
          +ake_engine(db_url)`                                           
      185 +  - `conn` is a connection whose writes are committed         
      186 +  - `client` is `TestClient(create_app(Settings(database_url=d
          +b_url, as_of_date=date(2026, 7, 28), cors_origins=[])))`      
      187  
      123 -**Scope:**                                                    
      124 -- `backend/app/`: FastAPI app factory, settings (`DATABASE_URL
          -`, `AS_OF_DATE`, `CORS_ORIGINS`), SQLAlchemy engine/session de
          -pendency.                                                     
      125 -- Alembic migration `0002_clean_activity_events`: the dedupe v
          -iew with `ROW_NUMBER()`, portable SQL (it must run on Postgres
          - and SQLite).                                                 
      126 -- `GET /health` (checks the DB with `SELECT 1`).              
      127 -- pytest setup: a fixture that migrates a temporary **SQLite**
          - DB with Alembic and gives a `TestClient`; `ruff` for lint/for
          -mat. Pinned deps in `backend/requirements.txt` (+ `requirement
          -s-dev.txt`).                                                  
      128 -- Tests: health OK; the view removes exactly the duplicates of
          - a small fixture (2 identical rows + 1 different → 2 rows).   
      129 -- Update `CLAUDE.md` with run/lint/test commands, including a 
          -single test.                                                  
      188 +  With that `as_of_date`, the latest complete week is **2026-0
          +7-20** and the 8 baseline weeks are **2026-05-25 … 2026-07-13*
          +*.                                                            
      189 +- `factories.py`:                                             
      190 +  - `add_account(conn, id, name="Test Co", tz="America/Chicago
          +", industry="Test")`                                          
      191 +  - `add_weekly(conn, account_id, location, tz, counts: dict[d
          +ate, int])` places `count` events in each local week, on Tuesd
          +ay from 12:00 local, one minute apart                         
      192 +  - `add_event(conn, account_id, location, local_dt: datetime,
          + tz, event_type="call_received", outcome=None, duration=None)`
      193 +  - `weeks_before(week: date, values: list[int]) -> dict[date,
          + int]` maps `values` to the consecutive weeks ending the week 
          +before `week`                                                 
      194  
      131 -**Quickstart:**                                               
      132 -```bash                                                       
      133 -cd backend && .venv/bin/pip install -r requirements-dev.txt   
          -# or uv pip                                                   
      134 -.venv/bin/ruff check . && .venv/bin/pytest -q                 
      135 -.venv/bin/alembic upgrade head    # against the compose Postgr
          -es                                                            
      136 -docker compose exec -T db psql -U relay -d relay -tAc "select 
          -count(*) from clean_activity_events"   # 12614                
      137 -.venv/bin/uvicorn app.main:app --port 8000 &  curl -s localhos
          -t:8000/health   # {"status":"ok","db":"ok"}                   
      195 +  Ids come from a module-level counter starting at 1_000_000. 
      196 +- Fake account ids: 101+. Tests never use the seed except the 
          +`slow` seed tests, which call `load_seed(engine, Path("../data
          +/seed.sql"))`.                                                
      197 +                                                              
      198 +### 3.7 Frontend layout and UI rules                          
      199  ```
      200 +frontend/                                                     
      201 +  .nvmrc  package.json  vite.config.ts  tsconfig.json  eslint.
          +config.js  index.html                                         
      202 +  src/                                                        
      203 +    main.tsx  App.tsx  styles.css                             
      204 +    api/schema.d.ts         # generated: npm run gen:api (open
          +api-typescript ../openapi.json)                               
      205 +    api/types.ts            # aliases: Account, WeeklyInsight,
          + Metric, LocationMetric, Day, Status                          
      206 +    api/client.ts           # getAccounts(), getWeeklyInsight(
          +accountId, weekStart?) with fetch + AbortSignal; throws ApiErr
          +or(status, detail)                                            
      207 +    hooks/useAccounts.ts  hooks/useWeeklyInsight.ts   # {data,
          + error, loading, reload}                                      
      208 +    format.ts               # formatPct, formatNumber, weekLab
          +el, tzAbbreviation, addDays                                   
      209 +    components/AccountPicker.tsx  WeekPicker.tsx  VerdictCard.
          +tsx  DailyChart.tsx                                           
      210 +               LocationsTable.tsx  DataNotes.tsx  StatusBadge.
          +tsx  StateMessage.tsx                                         
      211 +    test/setup.ts  test/server.ts (MSW)  test/fixtures.ts     
      212 +```                                                           
      213 +- API base URL: `import.meta.env.VITE_API_URL ?? "http://local
          +host:8000"`.                                                  
      214 +- **State lives only in React state:** the selected account (d
          +efault = the first account from `/accounts`) and `weekStart` (
          +default = that account's `latest_complete_week`). Changing acc
          +ount resets the week. ◀ = −7 days; ▶ = +7 days, disabled at `l
          +atest_complete_week`.                                         
      215 +- **Formats:**                                                
      216 +  - `formatPct(-0.32)` → `"−32%"` (U+2212), `formatPct(0.05)` 
          +→ `"+5%"`, `null` → `"—"`                                     
      217 +  - usual shown as `~76`; range `64–88` (rounded integers)    
      218 +  - week label `"Jul 20 – Jul 26, 2026"` via `Intl.DateTimeFor
          +mat("en-US")`                                                 
      219 +  - timezone abbreviation via `Intl.DateTimeFormat("en-US", {t
          +imeZone, timeZoneName: "short"})`                             
      220  
      221 +  API dates are `YYYY-MM-DD` strings, so the date math uses UT
          +C to avoid local-time shifts.                                 
      222 +- **StatusBadge** (icon + text, never colour alone): lower `▼ 
          +Lower than usual` (`--color-lower: #b42318`), higher `▲ Higher
          + than usual` (`--color-higher: #1d4ed8`), normal `● Normal` (`
          +--color-normal: #15803d`), not_enough_history `○ Not enough hi
          +story` (`--color-muted: #6b7280`).                            
      223 +- **Copy (exact):**                                           
      224 +  - not enough history: `Not enough history yet — at least 4 c
          +omplete weeks are needed to tell what's normal.`              
      225 +  - account low volume: `This account has low weekly volume, s
          +o results may be unreliable.`                                 
      226 +  - row low volume: a `Low volume` tag with `title="Low weekly
          + volume: results may be unreliable."`                         
      227 +  - no locations: `No locations with activity yet.`           
      228 +  - error: `Couldn't load data.` + a `Retry` button           
      229 +  - loading: `Loading…`                                       
      230 +- Single-location accounts show the table with one row. The ta
          +ble keeps the API order (no client-side sorting).             
      231 +- DailyChart: Recharts `ComposedChart` with a `Bar` for `total
          +` and a `Line` with dots only (no stroke) for `usual`. X label
          +s Mon…Sun.                                                    
      232 +- Plain CSS in `styles.css` with CSS variables, a single colum
          +n with max-width 960px.                                       
      233 +                                                              
      234  ---
      235  
      142 -## Task 2 — Domain logic: weeks, detection, ranking (`api-buil
          -der`) · ~550 lines                                            
      236 +## 4. Test scenarios (expected values)                        
      237  
      144 -**Goal:** all the "is it normal?" logic as pure, framework-fre
          -e functions with thorough unit tests. No DB, no HTTP.         
      238 +Backend scenarios run through the API (`client`) on SQLite wit
          +h fake accounts. All of them use location `Main` and timezone 
          +`America/Chicago` unless stated otherwise, and evaluate week *
          +*2026-07-20** with history `weeks_before(2026-07-20, [...])` (
          +8 weeks, oldest first).                                       
      239  
      146 -**Scope (`backend/app/domain/`):**                            
      147 -- `weeks.py`: UTC naive → account-local date (`zoneinfo`), loc
          -al Monday of a date, `as_of` resolution, latest complete week,
          - weekly and per-weekday bucketing of event timestamps, zero-fi
          -lling a series from its first complete week.                  
      148 -- `detection.py`: `evaluate(value, history) → Metric` exactly 
          -as in "Decisions" (including `usual = 0`, history < 4, low_vol
          -ume). Constants `K=2.5, N=8, MIN_HISTORY=4, MIN_ABS=3, MIN_PCT
          -=0.20, LOW_VOLUME_USUAL=6` in one place.                      
      149 -- `ranking.py`: location order as in "Decisions".             
      150 -- Unit tests: DST weeks (US 2026-03-08), `America/Phoenix`, `U
          -TC`, an event at 23:30 local on Sunday vs Monday UTC; median/M
          -AD band with a spike in history (stays robust); `usual = 0`; h
          -istory of 3 → not_enough_history; 4–7 weeks of history; floors
          -; low_volume boundary; ranking ties.                          
      151 -- Parity check: one test that reproduces two example rows from
          - `Detection_tuning.md` (e.g. account 6, week of 2026-06-01 → h
          -igher_than_usual) using hard-coded weekly values.             
      240 +**Required (from the first-iteration plan):**                 
      241 +| Id | Setup | Expected |                                     
      242 +|---|---|---|                                                 
      243 +| S1 | Account 101 with no events | 200; `summary.status = not
          +_enough_history`, `total = 0`, `locations = []`, 7 days with `
          +total = 0` and `usual = null`, `baseline.weeks_used = 0` |    
      244 +| S2 | Account 102: history `[20,22,18,21,19,20,23,17]`, week 
          += 21 | usual 20.0, lower 8.8, upper 31.2, pct 0.05, `normal`, 
          +`low_volume = false` |                                        
      245 +| S3a | Account 103: the same history, week = 5 | `lower_than_
          +usual`, pct −0.75 |                                           
      246 +| S3b | Account 104: the same history, week = 40 | `higher_tha
          +n_usual`, pct 1.0 |                                           
      247 +| S4 | Account 105: locations North, South, East, West, each w
          +ith history `[20]*8`; week: North 20, South 8, East 4, West 35
          + | Locations ordered **East (lower, −0.8), South (lower, −0.6)
          +, North (normal), West (higher)**; account total 67 vs usual 8
          +0 → summary **`normal`** (lower bound 57.6). The account looks
          + fine, but two locations need attention. |                    
      248  
      153 -**Quickstart:**                                               
      154 -```bash                                                       
      155 -cd backend && .venv/bin/ruff check . && .venv/bin/pytest -q te
          -sts/domain                                                    
      156 -```                                                           
      249 +**Boundaries and math edges:**                                
      250 +| Id | Setup | Expected |                                     
      251 +|---|---|---|                                                 
      252 +| B1 | 3 weeks of history `[20,20,20]` (series starts 3 weeks 
          +before), week = 5 | `not_enough_history`, `history_weeks = 3`,
          + usual null |                                                 
      253 +| B2 | 5 weeks of history `[20]*5`, week = 5 | evaluated: `low
          +er_than_usual`, `baseline.weeks_used = 5` |                   
      254 +| B3 | 1 event 9 weeks before, history 8 × 0; week = 3 | usual
          + 0.0, `pct_vs_usual = null`, `higher_than_usual` |            
      255 +| B4 | Same as B3, week = 2 | `normal` (outside the band [0, 0
          +] but diff < 3) |                                             
      256 +| B5 | history `[5]*8`, week = 0 | `normal`, lower 0.0, `low_v
          +olume = true` |                                               
      257 +| B6 | history `[200]*8`, week = 236 | `normal` (above upper 2
          +35.4 but +18% < 20%) |                                        
      258 +| B7 | history `[200]*8`, week = 241 | `higher_than_usual` |  
      259 +| B8 | history `[1,1,1,1,0,0,0,0]`, week = 3 | `normal` (usual
          + 0.5, upper 2.4, diff 2.5 < 3) |                              
      260  
      158 ----                                                           
      261 +**Robustness and data quirks:**                               
      262 +| Id | Setup | Expected |                                     
      263 +|---|---|---|                                                 
      264 +| R1 | history `[20,20,20,300,20,20,20,20]`, week = 20; and a 
          +second account with the same history and week = 5 | `normal` (
          +usual 20, the band isn't inflated); the second → `lower_than_u
          +sual` |                                                       
      265 +| R2 | history `[20]*8`, week = 20 plus 1 exact duplicate of o
          +ne of the week's events | `total = 20`; data note `"1 duplicat
          +e event removed from this week."` |                           
      266 +| R3 | Location Old with history `[20]*8` and week = 20; locat
          +ion New with only the last 2 weeks of history `[5,5]` and week
          + = 5 | New: `not_enough_history`, `history_weeks = 2`, ranked 
          +last; summary is evaluated (not `not_enough_history`) |       
      267 +| R4 | Events at local Sun 2026-07-26 23:30 (Mon UTC), Mon 202
          +6-07-20 00:30, and Sun 2026-07-19 23:59 | The first two count 
          +in week 2026-07-20 (Sun / Mon in `days`); the third doesn't | 
      268 +| R5 | DST: an event at local Sun 2026-03-08 23:30 (America/Ch
          +icago) | Counts in week 2026-03-02 (`days[6]`, Sun) |         
      269 +| R6 | `America/Phoenix` account, event at local Sun 23:30 | C
          +ounts on that Sunday (UTC −7 all year) |                      
      270 +| R7 | `UTC` account with any history | The UTC data note is p
          +resent; a Chicago account doesn't have it |                   
      271  
      160 -## Task 3 — Repository + `GET /accounts` (`api-builder`) · ~35
          -0 lines                                                       
      272 +**API validation and errors:**                                
      273 +| Id | Request | Expected |                                   
      274 +|---|---|---|                                                 
      275 +| V1 | `week_start=2026-07-21` | 422 `week_start must be a Mon
          +day` |                                                        
      276 +| V2 | `week_start=2026-07-27` | 422 `week_start is not comple
          +te yet; the latest complete week is 2026-07-20` |             
      277 +| V3 | A week before the dataset's first complete week | 422 `
          +week_start is before the first complete week (…)` |           
      278 +| V4 | Account 999 | 404 `Account 999 not found` |            
      279 +| V5 | No `week_start` | `week.start = 2026-07-20`, `week.end 
          += 2026-07-26` |                                               
      280 +| V6 | Any account | `days` has 7 items, Mon…Sun, zero-filled 
          +|                                                             
      281 +| V7 | `/health` with a broken DB (dependency override that ra
          +ises) | 503 `{"status":"error","db":"error"}` |               
      282 +| V8 | `/accounts` | Ordered by name; `location_count` and `la
          +test_complete_week` correct; an account with no events has `lo
          +cation_count = 0` |                                           
      283  
      162 -**Goal:** read from the clean view and serve the account list 
          -for the picker.                                               
      284 +**Seed golden tests** (`@pytest.mark.slow`, real seed on SQLit
          +e, `as_of_date = None`):                                      
      285 +| Id | Expected |                                             
      286 +|---|---|                                                     
      287 +| G1 | The clean view has 12,614 rows; the raw table has 12,62
          +6 |                                                           
      288 +| G2 | Account 6, default week → `week.start = 2026-07-20` |  
      289 +| G3 | Account 6, week 2026-06-01: total 880, usual 66.0, band
          + 27.1–104.9, `higher_than_usual`; all 15 locations `higher_tha
          +n_usual`; Site A total 49, usual 4.5 |                        
      290 +| G4 | Account 6, week 2026-06-08: total 102, `normal` (the we
          +eks after the spike aren't distorted) |                       
      291 +| G5 | Account 2, week 2026-07-06: total 18, usual 32.5, `lowe
          +r_than_usual` |                                               
      292 +| G6 | Account 15, week 2026-06-01: `higher_than_usual` |     
      293 +| G7 | Account 20: `not_enough_history`, `locations = []` |   
      294 +| G8 | Account 18: has the UTC note. Account 1, week 2026-02-0
          +2: `not_enough_history` |                                     
      295  
      296 +**Frontend scenarios** (Vitest + Testing Library rendering `<A
          +pp />`; HTTP mocked with MSW; fixtures in `src/test/fixtures.t
          +s` typed with `satisfies` against `api/types.ts`, mirroring S1
          +–S4 and the states below):                                    
      297 +| Id | Expected |                                             
      298 +|---|---|                                                     
      299 +| F1 (S1) | Account without events: the not-enough-history cop
          +y, `No locations with activity yet.`, a chart with 7 zero bars
          + |                                                            
      300 +| F2 (S2) | `● Normal`, `21 events · usual ~20 (range 9–31) · 
          ++5%` |                                                        
      301 +| F3 (S3) | `▼ Lower than usual` with −75%; `▲ Higher than usu
          +al` with +100% |                                              
      302 +| F4 (S4) | Account `● Normal`; table rows in API order East, 
          +South, North, West with their badges |                        
      303 +| F5 | Low volume: the account warning and a row `Low volume` 
          +tag |                                                         
      304 +| F6 | Data notes: the duplicate and UTC notes rendered as giv
          +en |                                                          
      305 +| F7 | Single-location account: a table with one row |        
      306 +| F8 | Week navigation: ◀ requests `week_start` −7 days; ▶ dis
          +abled at the latest week; changing account resets the week |  
      307 +| F9 | API error → `Couldn't load data.`; `Retry` refetches; `
          +Loading…` while pending |                                     
      308 +| F10 | A `not_enough_history` location row shows `—` for usua
          +l and % |                                                     
      309 +                                                              
      310 +---                                                           
      311 +                                                              
      312 +## 5. Tasks                                                   
      313 +                                                              
      314 +### Task 0 — Foundation (orchestrator + human) → PR           
      315 +**Goal:** get the existing foundation onto GitHub through a PR
          +.                                                             
      316  **Scope:**
      165 -- `backend/app/repository.py`: queries on `clean_activity_even
          -ts` / `accounts` only (no timezone math in SQL): accounts with
          - location counts; events of one account for a UTC range wide e
          -nough to cover the selected week + 8 prior weeks (in local tim
          -e); raw vs clean counts for the duplicate note; the dataset's 
          -min/max `occurred_at`.                                        
      166 -- Pydantic response models for the whole contract (`backend/ap
          -p/schemas.py`), so the OpenAPI is complete from here on.      
      167 -- `GET /accounts` with `latest_complete_week` from the domain 
          -logic.                                                        
      168 -- Integration tests (SQLite) with fake accounts: one with no e
          -vents, one with a normal history, one with a low week.        
      317 +- Human: create an empty GitHub repo with your own name (not a
          + fork, not `relay-analytics-starter`) and add it as `origin`. 
      318 +- Orchestrator: commit `.gitignore` alone on `main` and push. 
          +Then, on branch `task/0-foundation`, commit the rest (compose,
          + migration 0001, seed, scripts, analysis, docs, `.claude/agent
          +s/`, CLAUDE.md pointing to this plan) and open a PR. The seed 
          +is excluded from the line count. If the docs push the PR over 
          +700 lines, stack them: infra in `0a`, docs in `0b`.           
      319  
      320 +**Tests:** none (no app code).                                
      321  **Quickstart:**
      322  ```bash
      172 -cd backend && .venv/bin/ruff check . && .venv/bin/pytest -q   
      173 -curl -s localhost:8000/accounts | python3 -m json.tool | head 
          --20   # 20 accounts, Quiet Harbor Spa location_count 0        
      323 +docker compose down -v && docker compose up -d --wait && ./scr
          +ipts/load_seed.sh   # accounts=20, activity_events=12626      
      324  ```
      325  
      176 ----                                                           
      326 +### Task 1 — API skeleton, clean view, health, test harness (`
          +api-builder`) · ~400 lines                                    
      327 +**Goal:** a runnable FastAPI app and the test harness every la
          +ter task uses.                                                
      328 +**Scope:** `pyproject.toml`, `config.py`, `db.py`, `main.py` (
          +with CORS), `routes.py` with `/health` only, migration 0002 (3
          +.3), `requirements-dev.txt`, `tests/conftest.py` + `tests/fact
          +ories.py` exactly as in 3.6. Update the CLAUDE.md commands: ru
          +n, lint, test, single test, fast tests (`-m "not slow"`).     
      329 +**Tests (integration):**                                      
      330 +- `/health` → 200 ok                                          
      331 +- the view on SQLite: 2 identical rows + 1 different → the vie
          +w returns 2, keeping the lowest id                            
      332 +- the same, with a NULL outcome in the identical pair         
      333 +- the factories create the expected local weeks (one check)   
      334  
      178 -## Task 4 — `GET /accounts/{id}/weekly-insight` (`api-builder`
          -) · ~500 lines                                                
      335 +**Quickstart:**                                               
      336 +```bash                                                       
      337 +cd backend && .venv/bin/pip install -r requirements-dev.txt   
          +  # or: uv pip install --python .venv/bin/python -r requiremen
          +ts-dev.txt                                                    
      338 +.venv/bin/ruff check . && .venv/bin/ruff format --check . && .
          +venv/bin/pytest -q                                            
      339 +.venv/bin/alembic upgrade head                                
      340 +docker compose exec -T db psql -U relay -d relay -tAc "select 
          +count(*) from clean_activity_events"   # 12614                
      341 +.venv/bin/uvicorn app.main:app --port 8000 & sleep 2; curl -s 
          +localhost:8000/health; kill %1         # {"status":"ok","db":"
          +ok"}                                                          
      342 +```                                                           
      343  
      180 -**Goal:** the endpoint the dashboard uses, matching the contra
          -ct.                                                           
      344 +### Task 2 — Domain logic (`api-builder`) · ~450 lines        
      345 +**Goal:** all the "is it normal?" logic as pure functions (3.4
          +, section 2 rules). No DB, no FastAPI.                        
      346 +**Scope:** `domain/weeks.py`, `domain/detection.py`, `domain/r
          +anking.py`.                                                   
      347 +**Tests (unit, `tests/unit/`, kept small, since the scenario t
          +asks cover behavior end to end):**                            
      348 +- `evaluate` on S2's numbers (usual 20, lower 8.82, upper 31.1
          +8)                                                            
      349 +- history < 4 / = 4                                           
      350 +- usual = 0                                                   
      351 +- `first_complete_week` / `latest_complete_week` on a Monday a
          +nd a Sunday                                                   
      352 +- `local_date` across the 2026-03-08 DST switch               
      353 +- ranking order with ties                                     
      354  
      182 -**Scope:**                                                    
      183 -- Service that assembles `WeeklyInsight`: summary, 7 days with
          - weekday usuals, ranked locations with `history_weeks`, data n
          -otes, baseline metadata.                                      
      184 -- Validation and errors: 404 / 422 as in the contract.        
      185 -- Integration tests (SQLite fake accounts): normal week → norm
          -al; low week → lower_than_usual and ranked first; no events → 
          -not_enough_history and `locations = []`; 3 weeks of history → 
          -not_enough_history; non-Monday → 422; future/partial week → 42
          -2; unknown account → 404; duplicate note appears.             
      186 -- Seed test (`tests/test_seed.py`, loads `data/seed.sql` into 
          -SQLite; mark it `slow`): account 6, week 2026-06-01 → summary 
          -higher_than_usual and all 15 locations higher; default week fo
          -r account 6 is 2026-07-20; account 18 has the UTC note.       
      187 -                                                              
      355  **Quickstart:**
      356  ```bash
      190 -cd backend && .venv/bin/ruff check . && .venv/bin/pytest -q   
          -         # all, incl. slow seed test                          
      191 -curl -s "localhost:8000/accounts/6/weekly-insight?week_start=2
          -026-06-01" | python3 -m json.tool | head -40                  
      192 -curl -s -o /dev/null -w "%{http_code}\n" "localhost:8000/accou
          -nts/6/weekly-insight?week_start=2026-06-02"   # 422           
      193 -curl -s -o /dev/null -w "%{http_code}\n" "localhost:8000/accou
          -nts/999/weekly-insight"                       # 404           
      357 +cd backend && .venv/bin/ruff check . && .venv/bin/pytest -q te
          +sts/unit                                                      
      358  ```
      359  
      196 ----                                                           
      360 +### Task 3 — Repository, schemas, seed loader, `GET /accounts`
          + (`api-builder`) · ~400 lines                                 
      361 +**Goal:** read from the clean view and serve the account picke
          +r.                                                            
      362 +**Scope:** `repository.py` (3.3), `schemas.py` (all models, 3.
          +4), `seed.py` (SQLite: `sqlite3` `executescript`; Postgres: th
          +e raw psycopg cursor executes the whole file; one transaction;
          + returns False if `accounts` has rows), `service.list_accounts
          +`, the `/accounts` route.                                     
      363 +**Tests (integration):**                                      
      364 +- V8                                                          
      365 +- `load_seed` on SQLite → 20 accounts and 12,626 events, and a
          + second call returns False (`slow`)                           
      366  
      198 -## Task 5 — API container + exported contract (`api-builder`) 
          -· ~200 lines                                                  
      367 +**Quickstart:**                                               
      368 +```bash                                                       
      369 +cd backend && .venv/bin/ruff check . && .venv/bin/pytest -q   
      370 +.venv/bin/uvicorn app.main:app --port 8000 & sleep 2          
      371 +curl -s localhost:8000/accounts | python3 -m json.tool | head 
          +-12; kill %1    # 20 accounts by name; Quiet Harbor Spa locati
          +on_count 0                                                    
      372 +```                                                           
      373  
      200 -**Goal:** a reviewer can start the API with Docker, and the fr
          -ontend has a committed contract to build against.             
      374 +### Task 4 — `GET /accounts/{id}/weekly-insight` (`api-builder
          +`) · ~450 lines                                               
      375 +**Goal:** the dashboard endpoint, exactly as in 3.4/3.5.      
      376 +**Scope:** `service.build_weekly_insight` (bounds → as-of → va
          +lidation → bucketing → evaluate the account and each location 
          +→ weekday usuals → ranking → notes → rounding), the route.    
      377 +**Tests (integration, only the minimum here; tasks 6–7 cover t
          +he catalog):** S2, V4, V5.                                    
      378 +**Quickstart:**                                               
      379 +```bash                                                       
      380 +cd backend && .venv/bin/ruff check . && .venv/bin/pytest -q   
      381 +.venv/bin/uvicorn app.main:app --port 8000 & sleep 2          
      382 +curl -s "localhost:8000/accounts/6/weekly-insight?week_start=2
          +026-06-01" | python3 -m json.tool | head -30   # total 880, hi
          +gher_than_usual                                               
      383 +curl -s -o /dev/null -w "%{http_code}\n" "localhost:8000/accou
          +nts/6/weekly-insight?week_start=2026-06-02"     # 422         
      384 +kill %1                                                       
      385 +```                                                           
      386  
      387 +### Task 5 — API container + exported contract (`api-builder`)
          + · ~200 lines                                                 
      388 +**Goal:** `docker compose up` starts db + api, and the fronten
          +d gets a committed contract.                                  
      389  **Scope:**
      203 -- `backend/Dockerfile` (pinned Python slim image); compose ser
          -vice `api` that waits for `db`, runs `alembic upgrade head`, l
          -oads the seed if empty (reuse the logic of `scripts/load_seed.
          -sh`), then starts uvicorn on port 8000. CORS for the frontend 
          -origin.                                                       
      204 -- `scripts/export_openapi.py` → `openapi.json` at the repo roo
          -t (generated, excluded from the line count); a test that fails
          - if the committed file is stale.                              
      390 +- `backend/Dockerfile`: `python:3.13-slim` pinned to an exact 
          +patch tag; build context = repo root so `data/seed.sql` is cop
          +ied in.                                                       
      391 +- `backend/docker-entrypoint.sh`: `alembic upgrade head` → `py
          +thon -m app.seed` (loads if empty) → `uvicorn app.main:app --h
          +ost 0.0.0.0 --port 8000`.                                     
      392 +- Compose service `api`: depends on `db` being healthy, `DATAB
          +ASE_URL` pointing at `db:5432`, port 8000, and a healthcheck o
          +n `/health` (python urllib, not curl).                        
      393 +- `scripts/export_openapi.py` → `openapi.json` at the repo roo
          +t (sorted keys, 2-space indent).                              
      394 +- Update the CLAUDE.md commands.                              
      395  
      396 +**Tests:** a test that compares the committed `openapi.json` w
          +ith `create_app().openapi()` and fails if it's stale.         
      397  **Quickstart:**
      398  ```bash
      399  docker compose down -v && docker compose up -d --build --wait
      209 -curl -s localhost:8000/health && curl -s localhost:8000/accoun
          -ts | head -c 300                                              
      210 -backend/.venv/bin/python scripts/export_openapi.py && git diff
          - --exit-code openapi.json                                     
      400 +curl -s localhost:8000/health && curl -s localhost:8000/accoun
          +ts | head -c 200                                              
      401 +backend/.venv/bin/python scripts/export_openapi.py && git diff
          + --exit-code openapi.json && echo "contract up to date"       
      402  ```
      403  
      213 ----                                                           
      404 +### Task 6 — API scenario tests, part 1: S1–S4 + boundaries (`
          +api-builder`) · ~450 lines                                    
      405 +**Goal:** prove the required scenarios and the math edges thro
          +ugh the API.                                                  
      406 +**Scope:** `tests/integration/test_scenarios_core.py` (S1–S4),
          + `tests/integration/test_boundaries.py` (B1–B8). One test func
          +tion per scenario id, named `test_<id>_<short_description>`, e
          +ach asserting every expected value in section 4. App fixes onl
          +y under the rule in section 1.                                
      407 +**Tests:** this task *is* tests.                              
      408 +**Quickstart:**                                               
      409 +```bash                                                       
      410 +cd backend && .venv/bin/ruff check . && .venv/bin/pytest -q te
          +sts/integration/test_scenarios_core.py tests/integration/test_
          +boundaries.py                                                 
      411 +.venv/bin/pytest -q tests/integration/test_scenarios_core.py::
          +test_s4_locations_need_review     # single test               
      412 +```                                                           
      413  
      215 -## Task 6 — Frontend skeleton, API client, pickers (`frontend-
          -builder`) · ~450 lines                                        
      414 +### Task 7 — API scenario tests, part 2: robustness, validatio
          +n, seed golden (`api-builder`) · ~450 lines                   
      415 +**Goal:** prove the data-quirk handling, the errors, and parit
          +y with `Detection_tuning.md` on the real seed.                
      416 +**Scope:** `tests/integration/test_robustness.py` (R1–R7), `te
          +sts/integration/test_validation.py` (V1–V7), `tests/integratio
          +n/test_seed_golden.py` (G1–G8, `slow`; one module-scoped seede
          +d engine). Same naming and fix rules as Task 6.               
      417 +**Quickstart:**                                               
      418 +```bash                                                       
      419 +cd backend && .venv/bin/ruff check . && .venv/bin/pytest -q   
          +               # everything, including slow                   
      420 +.venv/bin/pytest -q -m "not slow"                             
          +              # fast loop                                     
      421 +```                                                           
      422  
      217 -**Goal:** a React app that loads accounts and a weekly insight
          -, with working account/week selection.                        
      423 +### Task 8 — Frontend skeleton, API client, pickers (`frontend
          +-builder`) · ~450 lines                                       
      424 +**Goal:** the app loads accounts and a weekly insight, and acc
          +ount/week selection works.                                    
      425 +**Scope:** the `frontend/` scaffold (3.7), `npm run gen:api` →
          + `schema.d.ts`, `types.ts`, `client.ts`, both hooks, `format.t
          +s`, `AccountPicker`, `WeekPicker`, `StateMessage`, `App.tsx` (
          +pickers + loading/error; the insight body shows the total and 
          +status as plain text for now), `test/setup.ts`, `test/server.t
          +s`, `test/fixtures.ts` (an accounts list + an S2-shaped insigh
          +t). Scripts: `dev`, `build`, `lint`, `test`, `gen:api`. Update
          + the CLAUDE.md frontend commands.                             
      426 +**Tests (integration with MSW):**                             
      427 +- F8, F9                                                      
      428 +- `format.ts` unit cases: the pct sign and U+2212, null, week 
          +label, tz abbreviation                                        
      429  
      219 -**Scope:**                                                    
      220 -- `frontend/`: Vite + React + TypeScript (pinned versions), ES
          -Lint, Vitest + Testing Library.                               
      221 -- Typed API client from `openapi.json` (hand-written types or 
          -`openapi-typescript`; generated files are excluded from the li
          -ne count). Base URL from `VITE_API_URL`, default `http://local
          -host:8000`.                                                   
      222 -- Layout shell; account picker (from `/accounts`); week picker
          - with ◀ ▶ that moves by 7 days, defaults to the account's `lat
          -est_complete_week`, disables ▶ past it, and shows the account'
          -s timezone abbreviation.                                      
      223 -- Loading and API-error states. Tests with fixture JSON shaped
          - exactly like the contract (no live API in tests).            
      224 -                                                              
      430  **Quickstart:**
      431  ```bash
      227 -cd frontend && npm ci && npm run lint && npm test -- --run && 
          -npm run build                                                 
      228 -npm run dev   # with the API running: pick an account, move we
          -eks, see raw JSON / placeholders                              
      432 +cd frontend && npm ci && npm run gen:api && git diff --exit-co
          +de src/api/schema.d.ts                                        
      433 +npm run lint && npm test -- --run && npm run build            
      434  ```
      435  
      231 ----                                                           
      232 -                                                              
      233 -## Task 7 — Verdict card + 7-day chart (`frontend-builder`) · 
          -~450 lines                                                    
      234 -                                                              
      235 -**Goal:** the top half of the wireframe: the account's answer 
          -to "is this week normal?".                                    
      236 -                                                              
      237 -**Scope:**                                                    
      238 -- Verdict card: status with icon (▼ lower, ▲ higher, ● normal)
          -, total, "usual ~X (range lower–upper)", % vs usual, "vs. prev
          -ious N weeks". `not_enough_history` state ("Not enough history
          - yet — needs 4 complete weeks"). Low-volume warning when `summ
          -ary.low_volume`.                                              
      239 -- 7-day chart (Recharts, pinned): bars for actual, a marker fo
          -r usual per weekday; no status per day.                       
      240 -- Data notes area (duplicates, UTC timezone warning).         
      241 -- Colour is never the only signal (icon + text). Tests for eac
          -h status, not_enough_history, low volume, notes.              
      242 -                                                              
      436 +### Task 9 — Verdict card, daily chart, data notes (`frontend-
          +builder`) · ~400 lines                                        
      437 +**Goal:** the top half of the wireframe.                      
      438 +**Scope:** `StatusBadge`, `VerdictCard` (status, `N events · u
          +sual ~X (range a–b) · ±P%`, `vs. previous {weeks_used} weeks`,
          + the not-enough-history copy, the account low-volume warning),
          + `DailyChart`, `DataNotes`; wire them into `App.tsx`. Fixtures
          + for S1, S3a, S3b, low volume, and the notes.                 
      439 +**Tests (integration with MSW):** F1 (card and chart part), F2
          +, F3, F5 (account part), F6.                                  
      440  **Quickstart:**
      441  ```bash
      442  cd frontend && npm run lint && npm test -- --run && npm run bu
           ild
      246 -# manual: account 6 week 2026-06-01 → ▲ higher; account 20 → n
          -ot enough history; account 18 → UTC note                      
      443  ```
      444  
      249 ----                                                           
      250 -                                                              
      251 -## Task 8 — Ranked locations table (`frontend-builder`) · ~350
          - lines                                                        
      252 -                                                              
      445 +### Task 10 — Ranked locations table (`frontend-builder`) · ~3
          +00 lines                                                      
      446  **Goal:** the bottom half: which location needs attention.
      447 +**Scope:** `LocationsTable` (Location · This week · Usual · vs
          + usual · Status; the `Low volume` tag; `—` for nulls; the empt
          +y state), the `Locations ({n})  needs attention first` header,
          + wired into `App.tsx`. Fixtures for S4, single location, and a
          + not-enough-history row.                                      
      448 +**Tests (integration with MSW):** F4, F5 (row part), F7, F10, 
          +F1 (empty table part).                                        
      449 +**Quickstart:**                                               
      450 +```bash                                                       
      451 +cd frontend && npm run lint && npm test -- --run && npm run bu
          +ild                                                           
      452 +```                                                           
      453  
      255 -**Scope:**                                                    
      256 -- Table in the API's order (the frontend doesn't re-sort): loc
          -ation, this week, usual, % vs usual, status; `not_enough_histo
          -ry` rows show "—"; low-volume rows show a small "low volume" h
          -int with a tooltip explaining that results may be unreliable. 
      257 -- Single-location accounts: show the table anyway (one row) or
          - hide it if it duplicates the card; choose and note it in the 
          -PR.                                                           
      258 -- Empty state for accounts without locations (account 20).    
      259 -- Tests: order preserved, each status, low-volume hint, empty 
          -state.                                                        
      260 -                                                              
      454 +### Task 11 — Frontend scenario pass + live check (`frontend-b
          +uilder`) · ~250 lines                                         
      455 +**Goal:** one end-to-end pass over F1–F10 against the full app
          +, plus a manual check against the real API.                   
      456 +**Scope:** `src/test/scenarios.test.tsx`: one test per F id, r
          +endering `<App />` and checking the full screen per scenario (
          +tasks 8–10 tested pieces). Fix gaps under the rule in section 
          +1. Manual check with `docker compose up` and `npm run dev`: ac
          +count 6 week 2026-06-01 (▲ higher), account 20 (not enough his
          +tory), account 18 (UTC note), account 8 (single location). Des
          +cribe what you saw in the PR.                                 
      457  **Quickstart:**
      458  ```bash
      459  cd frontend && npm run lint && npm test -- --run && npm run bu
           ild
      264 -# manual: account 6 → 15 rows; account 8 (single site) → chose
          -n behavior; account 20 → empty state                          
      460  ```
      461  
      267 ----                                                           
      462 +### Task 12 — Web container + one-command run (`frontend-build
          +er`) · ~150 lines                                             
      463 +**Goal:** a reviewer runs `docker compose up` and opens the da
          +shboard.                                                      
      464 +**Scope:**                                                    
      465 +- `frontend/Dockerfile`: multi-stage, `node:22-alpine` (pinned
          + patch tag) to build, then `nginx:1.27-alpine` (pinned) to ser
          +ve; build arg `VITE_API_URL=http://localhost:8000`.           
      466 +- Compose service `web` on port **8080**, depending on `api`. 
      467 +- A root `README.md` "Run it" section: one command, the URLs, 
          +and a reset command.                                          
      468  
      269 -## Task 9 — Frontend container + one-command run (`frontend-bu
          -ilder`) · ~150 lines                                          
      270 -                                                              
      271 -**Goal:** `docker compose up` starts db + api + frontend for a
          - reviewer.                                                    
      272 -                                                              
      273 -**Scope:** `frontend/Dockerfile` (build + serve static with a 
          -pinned image), compose service `web` on port 5173 (or 8080) wi
          -th `VITE_API_URL` set at build time; root `README.md` "Run it"
          - section (one command, URLs).                                 
      274 -                                                              
      469 +**Tests:** none new; the Quickstart is the check.             
      470  **Quickstart:**
      471  ```bash
      472  docker compose down -v && docker compose up -d --build --wait
      278 -curl -s -o /dev/null -w "%{http_code}\n" localhost:5173   # 20
          -0; open it in a browser                                       
      473 +curl -s -o /dev/null -w "%{http_code}\n" localhost:8080       
          + # 200                                                        
      474 +curl -s localhost:8000/accounts | head -c 100                 
      475  ```
      476  
      281 ----                                                           
      477 +### Task 13 — Write-up (orchestrator + human) → PR            
      478 +**Goal:** the submission README.                              
      479 +**Content:**                                                  
      480 +- problem and approach                                        
      481 +- the definition of "normal" and why median + MAD (`Detection_
          +tuning.md`)                                                   
      482 +- the data quirks and how each is handled (`Data_integrity.md`
          +, `OPEN_QUESTIONS.md`)                                        
      483 +- limitations: no seasonality, ~25 weeks of data, small counts
          +, low-volume locations are rarely flagged lower, an empty "nee
          +ds attention" list is common, SQLite tests vs Postgres        
      484 +- production notes: rollup tables / medallion, dedupe at inges
          +tion, Postgres tests in CI, auth, all-events-per-request      
      485 +- out of scope                                                
      486 +- how the work was done: spec-driven, Sonnet builder/reviewer 
          +agents, the Docker sandbox in bypass mode                     
      487  
      283 -## Task 10 — Write-up (Claude Code + human, no agents)        
      488 +**Quickstart:** the human reads the README on the PR.         
      489  
      285 -**Goal:** the submission's README: what was built, decisions a
          -nd trade-offs, production notes, AI-usage notes.              
      286 -                                                              
      287 -**Content (sources in brackets):** problem and approach; defin
          -ition of "normal" and why median+MAD (`Detection_tuning.md`); 
          -data quirks and how each is handled (`Data_integrity.md`, `OPE
          -N_QUESTIONS.md`); limitations (no seasonality, ~25 weeks, smal
          -l counts, low-volume locations rarely flagged lower, SQLite te
          -sts vs Postgres); production notes (rollup tables / medallion,
          - dedupe at ingestion, Postgres tests in CI, auth); out of scop
          -e; how the work was done (spec-driven, builder/reviewer agents
          -, Docker sandbox in bypass mode).                             
      288 -                                                              
      490  ---
      491  
      291 -## Task order and dependencies                                
      492 +## 6. Order                                                   
      493  
      494  ```
      294 -0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10                    
      495 +0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13     
      496  ```
      296 -Task 2 only depends on Task 1's test setup; tasks 6–9 build ag
          -ainst the `openapi.json` from Task 5.                         
      497 +Backend tasks first: the frontend builds against the `openapi.
          +json` produced in Task 5, and the backend scenario tests (6–7)
          + run before any frontend work, so contract bugs are caught ear
          +ly.                                                           

● Before finishing, I'm checking the expected values in the scenario table
  against the detection rule:

  Ran 1 shell command (ctrl+o to expand)

● The figures check out, but I found a trap: in a test database, Tuesday-dated
  fake events would silently cut the oldest history week. I'm moving the events
  to Mondays and spelling out the edge cases.

● Bash(python3 - <<'EOF'
      p='PLAN.md'; s=open(p).read()…)
  ⎿  ==> api-builder.md <==
     ---
     name: api-builder
     … +14 lines (ctrl+o to expand)
  ⎿  Updated PLAN.md (+7 -6)
      43  - **Metric:** total events per week, all event types together.
      44  - **Weeks:** Mon–Sun in the **account's local time**. UTC → loc
          al conversion happens **only in Python (`zoneinfo`)**, never in
           SQL.
      45  - **As-of:** `as_of_local` = `AS_OF_DATE` (env, `YYYY-MM-DD`) i
          f set, else the local date of the dataset's max `occurred_at` i
          n the clean view. Latest complete week = `monday_of(as_of_local
          ) − 7 days` (Jul 20, 2026 on the seed). Default week = the late
          st complete week. Partial or future weeks → 422.
      46 -- **First complete week of the dataset:** let `d` = local date 
         -of the dataset's min `occurred_at`; `first_complete_week = d if
         - d is a Monday else monday_of(d) + 7` (Feb 2, 2026 on the seed)
         -. Earlier weeks → 422.                                         
      46 +- **First complete week of the dataset** (computed per account,
         + in the account's timezone): let `d` = local date of the datase
         +t's min `occurred_at` (whole clean view, not just the account);
         + `first_complete_week = d if d is a Monday else monday_of(d) + 
         +7` (Feb 2, 2026 on the seed). Earlier weeks → 422.             
      47 +- **Empty dataset** (no events at all): `first_complete_week = 
         +None` (no lower-bound check); `as_of_local` needs `AS_OF_DATE`,
         + otherwise 422 `no activity data available` and `latest_complet
         +e_week = null` in `/accounts`.                                 
      48  - **Series:** one per account (all its events) and one per acco
          unt+location. A series starts at the first Monday ≥ `first_comp
          lete_week` whose week has ≥ 1 event. Weeks without events insid
          e the series count as 0.
      49  - **History of a week W:** the weeks `max(series_start, W − 8 w
          eeks) … W − 1 week`, zero-filled. **The evaluated week is never
           in its own history.** No series_start, or series_start ≥ W → e
          mpty history.
      50  - **Detection** (constants in `backend/app/domain/detection.py`
          : `K = 2.5`, `N_WEEKS = 8`, `MIN_HISTORY = 4`, `MIN_ABS = 3`, `
          MIN_PCT = 0.20`, `LOW_VOLUME_USUAL = 6`):
     ...
      189    With that `as_of_date`, the latest complete week is **2026-0
           7-20** and the 8 baseline weeks are **2026-05-25 … 2026-07-13*
           *.
      190  - `factories.py`:
      191    - `add_account(conn, id, name="Test Co", tz="America/Chicago
           ", industry="Test")`
      191 -  - `add_weekly(conn, account_id, location, tz, counts: dict[d
          -ate, int])` places `count` events in each local week, on Tuesd
          -ay from 12:00 local, one minute apart                         
      192 +  - `add_weekly(conn, account_id, location, tz, counts: dict[d
          +ate, int])` places `count` events in each local week, on **Mon
          +day** from 12:00 local, one minute apart. Monday matters: the 
          +earliest fake event sets the test dataset's `first_complete_we
          +ek`, so a non-Monday first event would silently drop the oldes
          +t history week                                                
      193    - `add_event(conn, account_id, location, local_dt: datetime,
            tz, event_type="call_received", outcome=None, duration=None)`
      194    - `weeks_before(week: date, values: list[int]) -> dict[date,
            int]` maps `values` to the consecutive weeks ending the week 
           before `week`
      195  
     ...
      265  | R1 | history `[20,20,20,300,20,20,20,20]`, week = 20; and a 
           second account with the same history and week = 5 | `normal` (
           usual 20, the band isn't inflated); the second → `lower_than_u
           sual` |
      266  | R2 | history `[20]*8`, week = 20 plus 1 exact duplicate of o
           ne of the week's events | `total = 20`; data note `"1 duplicat
           e event removed from this week."` |
      267  | R3 | Location Old with history `[20]*8` and week = 20; locat
           ion New with only the last 2 weeks of history `[5,5]` and week
            = 5 | New: `not_enough_history`, `history_weeks = 2`, ranked 
           last; summary is evaluated (not `not_enough_history`) |
      267 -| R4 | Events at local Sun 2026-07-26 23:30 (Mon UTC), Mon 202
          -6-07-20 00:30, and Sun 2026-07-19 23:59 | The first two count 
          -in week 2026-07-20 (Sun / Mon in `days`); the third doesn't | 
      268 -| R5 | DST: an event at local Sun 2026-03-08 23:30 (America/Ch
          -icago) | Counts in week 2026-03-02 (`days[6]`, Sun) |         
      269 -| R6 | `America/Phoenix` account, event at local Sun 23:30 | C
          -ounts on that Sunday (UTC −7 all year) |                      
      268 +| R4 | Chicago account, events at local Mon 2026-07-13 12:00 (
          +anchor), Sun 2026-07-19 23:59, Mon 2026-07-20 00:30, Sun 2026-
          +07-26 23:30 (= Mon UTC) | Week 2026-07-20: `days[0].total = 1`
          +, `days[6].total = 1`, `summary.total = 2`; the 07-19 event is
          + in week 2026-07-13 |                                         
      269 +| R5 | DST: an event at local Mon 2026-03-02 12:00 and one at 
          +local Sun 2026-03-08 23:30 (America/Chicago), `week_start=2026
          +-03-02` | Both count in week 2026-03-02: `days[0].total = 1`, 
          +`days[6].total = 1` |                                         
      270 +| R6 | `America/Phoenix` account, events at local Mon 2026-07-
          +20 12:00 and Sun 2026-07-26 23:30 | Both in week 2026-07-20; `
          +days[6].total = 1` (UTC −7 all year) |                        
      271  | R7 | `UTC` account with any history | The UTC data note is p
           resent; a Chicago account doesn't have it |
      272  
      273  **API validation and errors:**
     ...
      275  |---|---|---|
      276  | V1 | `week_start=2026-07-21` | 422 `week_start must be a Mon
           day` |
      277  | V2 | `week_start=2026-07-27` | 422 `week_start is not comple
           te yet; the latest complete week is 2026-07-20` |
      277 -| V3 | A week before the dataset's first complete week | 422 `
          -week_start is before the first complete week (…)` |           
      278 +| V3 | S2-style data (first complete week 2026-05-25), `week_s
          +tart=2026-05-18` | 422 `week_start is before the first complet
          +e week (2026-05-25)` |                                        
      279  | V4 | Account 999 | 404 `Account 999 not found` |
      280  | V5 | No `week_start` | `week.start = 2026-07-20`, `week.end 
           = 2026-07-26` |
      281  | V6 | Any account | `days` has 7 items, Mon…Sun, zero-filled 
           |
  ⎿  Updated .claude/agents/api-builder.md (+1 -0)
      1  ---
      2  name: api-builder
      3  description: Implements one backend task (FastAPI, Alembic, Pyth
         on domain logic, pytest) from PLAN.md and opens a PR. Use when a
          PLAN.md task is assigned to api-builder.
      4 +model: sonnet                                                   
      5  ---
      6  
      7  You implement exactly ONE task from `PLAN.md` in the backend (`b
         ackend/`, `scripts/`, compose services for the API). The task id
          is given in your prompt.
  ⎿  Updated .claude/agents/api-reviewer.md (+1 -0)
      1  ---
      2  name: api-reviewer
      3  description: Reviews a backend PR from api-builder against PLAN.
         md, re-runs the task's quickstart and posts a review on the PR. 
         Use after api-builder opens a PR.
      4 +model: sonnet                                                   
      5  tools: Bash, Read, Grep, Glob
      6  ---
      7  
  ⎿  Updated .claude/agents/frontend-builder.md (+1 -0)
      1  ---
      2  name: frontend-builder
      3  description: Implements one frontend task (React + TypeScript + 
         Vite, Vitest) from PLAN.md and opens a PR. Use when a PLAN.md ta
         sk is assigned to frontend-builder.
      4 +model: sonnet                                                   
      5  ---
      6  
      7  You implement exactly ONE task from `PLAN.md` in `frontend/` (an
         d its compose service). The task id is given in your prompt.
  ⎿  Updated .claude/agents/frontend-reviewer.md (+1 -0)
      1  ---
      2  name: frontend-reviewer
      3  description: Reviews a frontend PR from frontend-builder against
          PLAN.md and the wireframe, re-runs the task's quickstart and po
         sts a review on the PR. Use after frontend-builder opens a PR.
      4 +model: sonnet                                                   
      5  tools: Bash, Read, Grep, Glob
      6  ---
      7  

● Now updating the agent bodies for stacked PRs, the Tests sections, the fixed
  spec, and the "Decisions taken" rule:

● Bash(python3 - <<'EOF'
      import re…)
  ⎿     27 api-builder.md
        27 api-reviewer.md
        27 frontend-builder.md
     … +38 lines (ctrl+o to expand)
  ⎿  Updated .claude/agents/api-builder.md (+16 -15)
       1  ---
       2  name: api-builder
       3 -description: Implements one backend task (FastAPI, Alembic, Pyt
         -hon domain logic, pytest) from PLAN.md and opens a PR. Use when
         - a PLAN.md task is assigned to api-builder.                    
       3 +description: Implements one backend task (FastAPI, Alembic, Pyt
         +hon domain logic, pytest) from PLAN.md and opens one or more PR
         +s. Use when a PLAN.md task is assigned to api-builder.         
       4  model: sonnet
       5  ---
       6  
       7 -You implement exactly ONE task from `PLAN.md` in the backend (`
         -backend/`, `scripts/`, compose services for the API). The task 
         -id is given in your prompt.                                    
       7 +You implement exactly ONE task from `PLAN.md` in the backend (`
         +backend/`, `scripts/`, the compose `api` service). The task id 
         +is given in your prompt.                                       
       8  
       9  Before coding:
      10 -- Read `CLAUDE.md`, the "Workflow", "Decisions" and "API contra
         -ct" sections of `PLAN.md`, and your task. Read `Detection_tunin
         -g.md` when the task touches detection.                         
      11 -- If the task contradicts a decision, or can't fit in < 700 cha
         -nged lines, stop and report back with a proposed fix or split. 
         -Don't improvise.                                               
      10 +- Read `CLAUDE.md` and in `PLAN.md`: section 1 (Workflow, PR ru
         +les, "When something isn't specified"), section 2 (Decisions), 
         +section 3 (Implementation spec), section 4 (Test scenarios) and
         + your task in section 5.                                       
      11 +- Everything that needs judgment is already decided in PLAN.md.
         + Follow the spec literally: file names, signatures, field names
         +, constants, exact strings, libraries. Don't redesign, rename o
         +r "improve" it.                                                
      12 +- Not specified → choose the simplest option consistent with th
         +e plan and list it under "Decisions taken" in the PR. If it wou
         +ld touch the API contract, the data/cleaning rules, the detecti
         +on math/constants, the ranking, or another task's scope → stop 
         +and report back instead.                                       
      13  
      14  While coding:
      14 -- Branch `task/<id>-<slug>` from an up-to-date `main`.         
      15 -- Stay inside the task's scope. Note anything else as a follow-
         -up in the PR.                                                  
      16 -- Python: type hints, small pure functions, match the existing 
         -code. Domain logic (`app/domain/`) has no DB or FastAPI imports
         -. Timezone conversion only in Python (`zoneinfo`), never in SQL
         -. SQL must run on Postgres and SQLite.                         
      17 -- Never edit `data/seed.sql`, never change the raw tables' data
         -, never hand-run DDL (migrations only).                        
      18 -- Pin every new dependency to an exact version.                
      19 -- Write the tests the task lists; add ones you find necessary. 
      15 +- Branch `task/<id>-<slug>` from an up-to-date `main`. Implemen
         +t only the task's **Scope**, then write everything in its **Tes
         +ts** section (prefer integration tests through the public inter
         +face).                                                         
      16 +- If the diff will exceed 700 lines (command in PLAN.md section
         + 1), use **stacked PRs** exactly as PLAN.md describes: split al
         +ong the Scope bullets, each PR with its own passing tests.     
      17 +- Pin every new dependency to an exact version (latest stable a
         +t implementation time). Only libraries listed in PLAN.md 3.1.  
      18 +- Python: type hints everywhere, small pure functions. `app/dom
         +ain/` imports nothing from FastAPI, SQLAlchemy or `app.reposito
         +ry`.                                                           
      19 +- Timezone conversion only in Python (`zoneinfo`), never in SQL
         +. All SQL must run on both Postgres and SQLite.                
      20 +- Never edit `data/seed.sql`, never modify raw table data, neve
         +r hand-run DDL (migrations only).                              
      21  
      21 -Before opening the PR:                                         
      22 -- Run the task's **Quickstart** exactly; everything must pass. 
         -Run `ruff check` and the full `pytest`.                        
      23 -- Check the line count with the command in PLAN.md (< 700).    
      24 -- Commit with a clear message, push, and open the PR with `gh p
         -r create` (base `main`). Description: Goal · Changes · Quicksta
         -rt output (trimmed) · Line count · Deviations from PLAN.md · Op
         -en questions · Follow-ups.                                     
      22 +Before opening each PR:                                        
      23 +- Run the task's **Quickstart** exactly as written; every comma
         +nd must pass. Paste the trimmed output in the PR.              
      24 +- Check the line count (< 700).                                
      25 +- Commit (`<type>(<area>): <summary>`), push, and open the PR w
         +ith `gh pr create` (base `main`, or the previous branch for a s
         +tacked PR). Description: Goal · Changes · Tests added · Quickst
         +art output · Line count · Decisions taken · Deviations · Follow
         +-ups.                                                          
      26  
     … 2 more lines (ctrl+o to expand)
  ⎿  Updated .claude/agents/frontend-builder.md (+16 -15)
       1  ---
       2  name: frontend-builder
       3 -description: Implements one frontend task (React + TypeScript +
         - Vite, Vitest) from PLAN.md and opens a PR. Use when a PLAN.md 
         -task is assigned to frontend-builder.                          
       3 +description: Implements one frontend task (React + TypeScript +
         + Vite, Vitest + MSW) from PLAN.md and opens one or more PRs. Us
         +e when a PLAN.md task is assigned to frontend-builder.         
       4  model: sonnet
       5  ---
       6  
       7 -You implement exactly ONE task from `PLAN.md` in `frontend/` (a
         -nd its compose service). The task id is given in your prompt.  
       7 +You implement exactly ONE task from `PLAN.md` in `frontend/` (a
         +nd the compose `web` service). The task id is given in your pro
         +mpt.                                                           
       8  
       9  Before coding:
      10 -- Read `CLAUDE.md`, the "Workflow", "Decisions", "API contract"
         - and "Wireframe" sections of `PLAN.md`, and your task. The cont
         -ract source of truth is `openapi.json` at the repo root.       
      11 -- If the task contradicts a decision, needs an API change, or c
         -an't fit in < 700 changed lines, stop and report back with a pr
         -oposed fix or split. Don't change the backend.                 
      10 +- Read `CLAUDE.md` and in `PLAN.md`: section 1 (Workflow, PR ru
         +les, "When something isn't specified"), section 2 (Decisions), 
         +section 3 (Implementation spec), section 4 (Test scenarios) and
         + your task in section 5.                                       
      11 +- Everything that needs judgment is already decided in PLAN.md.
         + Follow the spec literally: file names, signatures, field names
         +, constants, exact strings, libraries. Don't redesign, rename o
         +r "improve" it.                                                
      12 +- Not specified → choose the simplest option consistent with th
         +e plan and list it under "Decisions taken" in the PR. If it wou
         +ld touch the API contract, the data/cleaning rules, the detecti
         +on math/constants, the ranking, or another task's scope → stop 
         +and report back instead.                                       
      13  
      14  While coding:
      14 -- Branch `task/<id>-<slug>` from an up-to-date `main`.         
      15 -- Stay inside the task's scope. Note anything else as a follow-
         -up in the PR.                                                  
      16 -- TypeScript strict, function components, small components, mat
         -ch the existing code. Types come from the contract. The fronten
         -d displays what the API returns: no re-ranking, no re-computing
         - verdicts.                                                     
      17 -- Accessibility: status is never shown by colour alone (icon + 
         -text), labelled controls, keyboard-usable pickers.             
      18 -- Pin every new dependency to an exact version; commit the lock
         -file.                                                          
      19 -- Tests use fixture JSON shaped exactly like the contract, neve
         -r a live API.                                                  
      15 +- Branch `task/<id>-<slug>` from an up-to-date `main`. Implemen
         +t only the task's **Scope**, then write everything in its **Tes
         +ts** section (prefer integration tests through the public inter
         +face).                                                         
      16 +- If the diff will exceed 700 lines (command in PLAN.md section
         + 1), use **stacked PRs** exactly as PLAN.md describes: split al
         +ong the Scope bullets, each PR with its own passing tests.     
      17 +- Pin every new dependency to an exact version (latest stable a
         +t implementation time). Only libraries listed in PLAN.md 3.1.  
      18 +- TypeScript strict, function components, no `any`. Types come 
         +from `src/api/types.ts` (generated from `openapi.json`). Never 
         +change the backend or `openapi.json`; if the contract seems wro
         +ng, stop and report.                                           
      19 +- The UI shows what the API returns: no re-sorting, no re-compu
         +ting statuses or numbers. Use the exact copy, formats, icons an
         +d colours from PLAN.md 3.7.                                    
      20 +- Tests render through Testing Library with HTTP mocked by MSW 
         +and fixtures typed with `satisfies`; never call a live API in t
         +ests. Commit the lockfile.                                     
      21  
      21 -Before opening the PR:                                         
      22 -- Run the task's **Quickstart** exactly; lint, tests and build 
         -must pass. Check the manual steps in a running app when the tas
         -k lists them, and describe what you saw.                       
      23 -- Check the line count with the command in PLAN.md (< 700).    
      24 -- Commit, push, and open the PR with `gh pr create` (base `main
         -`). Description: Goal · Changes · Quickstart output (trimmed) ·
         - Manual check · Line count · Deviations from PLAN.md · Open que
         -stions · Follow-ups.                                           
      22 +Before opening each PR:                                        
      23 +- Run the task's **Quickstart** exactly as written; every comma
         +nd must pass. Paste the trimmed output in the PR.              
      24 +- Check the line count (< 700).                                
      25 +- Commit (`<type>(<area>): <summary>`), push, and open the PR w
         +ith `gh pr create` (base `main`, or the previous branch for a s
         +tacked PR). Description: Goal · Changes · Tests added · Quickst
         +art output · Line count · Decisions taken · Deviations · Follow
         +-ups.                                                          
      26  
     … 2 more lines (ctrl+o to expand)
  ⎿  Updated .claude/agents/api-reviewer.md (+17 -13)
       1  ---
       2  name: api-reviewer
       3 -description: Reviews a backend PR from api-builder against PLAN
         -.md, re-runs the task's quickstart and posts a review on the PR
         -. Use after api-builder opens a PR.                            
       3 +description: Reviews a backend PR from api-builder against PLAN
         +.md, re-runs the task's quickstart and posts a review comment o
         +n the PR. Use after api-builder opens a PR.                    
       4  model: sonnet
       5  tools: Bash, Read, Grep, Glob
       6  ---
       7  
       8 -You review ONE backend PR (number and task id given in your pro
         -mpt). You don't change code: you report findings, and the build
         -er fixes them.                                                 
       8 +You review ONE backend PR (PR number and task id given in your 
         +prompt).                                                       
       9  
      10 +You don't change code: you report findings, and the builder fix
         +es them.                                                       
      11 +                                                               
      12  Steps:
      11 -1. Read `CLAUDE.md`, the "Workflow", "Decisions" and "API contr
         -act" sections of `PLAN.md`, and the task. Read `Detection_tunin
         -g.md` if detection is touched.                                 
      12 -2. `gh pr checkout <n>`; read the full diff (`git diff main...H
         -EAD`) and the PR description.                                  
      13 -3. Re-run the task's **Quickstart** and the full test suite. Re
         -cord the actual output.                                        
      13 +1. Read `CLAUDE.md` and `PLAN.md` sections 1–4 plus the task in
         + section 5. Read `Detection_tuning.md` if detection is touched.
      14 +2. `gh pr checkout <n>`; read the PR description and the full d
         +iff (`git diff <base>...HEAD`; for a stacked PR the base is the
         + previous branch).                                             
      15 +3. Re-run the task's **Quickstart** exactly and record the real
         + output. Also run the full `pytest` (including `slow`).        
      16  4. Check, at least:
      15 -   - **Scope:** only this task; < 700 changed lines (command in
         - PLAN.md).                                                     
      16 -   - **Contract:** response shapes, status codes, nulls and ord
         -ering exactly as in PLAN.md.                                   
      17 -   - **Decisions:** dedupe-only view; Mon–Sun local weeks via `
         -zoneinfo`; no timezone math in SQL; N = 8, min history 4, k = 2
         -.5, floors 3 / 20%, low_volume ≤ 6; ranking rule; partial weeks
         - never get a verdict.                                          
      18 -   - **Correctness:** off-by-one in week ranges and baseline wi
         -ndows (the evaluated week must never be in its own history), DS
         -T/Phoenix/UTC handling, `usual = 0`, empty accounts, duplicate 
         -counting.                                                      
      19 -   - **Portability:** SQL and migrations work on both Postgres 
         -and SQLite; seed and raw tables untouched; dependencies pinned.
      20 -   - **Tests:** they cover the cases the task lists and would f
         -ail if the logic were wrong (no tautological tests).           
      21 -5. Post the review with `gh pr review <n> --comment --body-file
         - <file>`. Always use `--comment`: the PRs are opened from the s
         -ame GitHub account, and GitHub rejects approve or request-chang
         -es on your own PR, so the verdict goes in the body. Format: Ver
         -dict (APPROVE / CHANGES REQUESTED) · Quickstart result · Findin
         -gs, each with severity (blocking / should-fix / nit), `file:lin
         -e`, problem and suggested fix · What was verified.             
      17 +   - **Scope and size:** only this task's Scope; < 700 changed 
         +lines (command in PLAN.md section 1); stacked correctly if spli
         +t.                                                             
      18 +   - **Spec compliance:** file layout, names, signatures, exact
         + strings and libraries as in PLAN.md section 3. Every deviation
         + is listed and justified in the PR.                            
      19 +   - **"Decisions taken":** each one is really unspecified by t
         +he plan and doesn't touch the contract, data rules, detection m
         +ath or ranking. If it does, it's a blocking finding.           
      20 +   - **Decisions (section 2):** dedupe-only view; Mon–Sun local
         + weeks via `zoneinfo`, no timezone math in SQL; the evaluated w
         +eek never in its own history; series start, first/latest comple
         +te week and as-of rules; constants K 2.5, N 8, MIN_HISTORY 4, M
         +IN_ABS 3, MIN_PCT 0.20, LOW_VOLUME_USUAL 6; ranking; data-note 
         +strings; rounding.                                             
      21 +   - **Contract (3.4/3.5):** field names, nulls, status codes a
         +nd exact error messages.                                       
      22 +   - **Correctness traps:** off-by-one week ranges, DST/Phoenix
         +/UTC, `usual = 0`, empty accounts and an empty dataset, SQLite 
         +returning timestamps as strings.                               
      23 +   - **Portability:** migrations and SQL run on Postgres and SQ
         +Lite; seed and raw tables untouched; dependencies pinned.      
      24 +   - **Tests:** every item in the task's Tests section exists, 
         +uses the expected values from PLAN.md section 4 where given, an
         +d would fail if the logic were wrong (no tautologies, no assert
         +ing on mocks only).                                            
      25 +5. Post the review with `gh pr review <n> --comment --body-file
         + <file>`. Always use `--comment`: the PRs are opened from the s
         +ame GitHub account, and GitHub rejects approve or request-chang
         +es on your own PR, so the verdict goes in the body. Format: **V
         +erdict** (APPROVE / CHANGES REQUESTED) · Quickstart result · Fi
         +ndings (severity blocking / should-fix / nit, `file:line`, prob
         +lem, suggested fix) · What was verified.                       
      26  
      23 -Only report findings you verified (by reading the code or runni
         -ng it). Final report: verdict, blocking findings, PR URL (≤ 15 
         -lines).                                                        
      27 +Only report findings you verified by reading or running the cod
         +e. Final report to the orchestrator (≤ 15 lines): verdict, bloc
         +king findings, PR URL.                                         
  ⎿  Updated .claude/agents/frontend-reviewer.md (+17 -13)
       1  ---
       2  name: frontend-reviewer
       3 -description: Reviews a frontend PR from frontend-builder agains
         -t PLAN.md and the wireframe, re-runs the task's quickstart and 
         -posts a review on the PR. Use after frontend-builder opens a PR
         -.                                                              
       3 +description: Reviews a frontend PR from frontend-builder agains
         +t PLAN.md and the wireframe, re-runs the task's quickstart and 
         +posts a review comment on the PR. Use after frontend-builder op
         +ens a PR.                                                      
       4  model: sonnet
       5  tools: Bash, Read, Grep, Glob
       6  ---
       7  
       8 -You review ONE frontend PR (number and task id given in your pr
         -ompt). You don't change code: you report findings, and the buil
         -der fixes them.                                                
       8 +You review ONE frontend PR (PR number and task id given in your
         + prompt).                                                      
       9  
      10 +You don't change code: you report findings, and the builder fix
         +es them.                                                       
      11 +                                                               
      12  Steps:
      11 -1. Read `CLAUDE.md`, the "Workflow", "Decisions", "API contract
         -" and "Wireframe" sections of `PLAN.md`, the task, and `openapi
         -.json`.                                                        
      12 -2. `gh pr checkout <n>`; read the full diff (`git diff main...H
         -EAD`) and the PR description.                                  
      13 -3. Re-run the task's **Quickstart** (lint, tests, build). Recor
         -d the actual output. If the task lists manual checks and the AP
         -I is available, verify them against the running app.           
      13 +1. Read `CLAUDE.md` and `PLAN.md` sections 1–4 plus the task in
         + section 5. Also read `openapi.json`.                          
      14 +2. `gh pr checkout <n>`; read the PR description and the full d
         +iff (`git diff <base>...HEAD`; for a stacked PR the base is the
         + previous branch).                                             
      15 +3. Re-run the task's **Quickstart** exactly and record the real
         + output. If the task lists a manual check and the stack is runn
         +ing (`docker compose up`), verify it too.                      
      16  4. Check, at least:
      15 -   - **Scope:** only this task; < 700 changed lines (command in
         - PLAN.md, lockfiles and generated files excluded).             
      16 -   - **Contract:** types match `openapi.json`; nulls handled (`
         -usual`, `pct_vs_usual` when not_enough_history); no re-sorting 
         -or re-computing of what the API decides.                       
      17 -   - **Wireframe and states:** layout as in PLAN.md; loading, e
         -rror, not enough history, single location, low volume and UTC n
         -ote handled where the task requires them.                      
      18 -   - **UX/accessibility:** status shown with icon + text, not c
         -olour alone; labelled, keyboard-usable controls; readable numbe
         -rs (percent signs, rounding).                                  
      19 -   - **Quality:** strict TypeScript without `any` escapes; depe
         -ndencies pinned; no dead code or leftover debug output.        
      20 -   - **Tests:** cover the task's cases with contract-shaped fix
         -tures and would fail if the UI were wrong.                     
      21 -5. Post the review with `gh pr review <n> --comment --body-file
         - <file>`. Always use `--comment`: the PRs are opened from the s
         -ame GitHub account, and GitHub rejects approve or request-chang
         -es on your own PR, so the verdict goes in the body. Format: Ver
         -dict (APPROVE / CHANGES REQUESTED) · Quickstart result · Findin
         -gs, each with severity (blocking / should-fix / nit), `file:lin
         -e`, problem and suggested fix · What was verified.             
      17 +   - **Scope and size:** only this task's Scope; < 700 changed 
         +lines (command in PLAN.md section 1); stacked correctly if spli
         +t.                                                             
      18 +   - **Spec compliance:** file layout, names, signatures, exact
         + strings and libraries as in PLAN.md section 3. Every deviation
         + is listed and justified in the PR.                            
      19 +   - **"Decisions taken":** each one is really unspecified by t
         +he plan and doesn't touch the contract, data rules, detection m
         +ath or ranking. If it does, it's a blocking finding.           
      20 +   - **Contract:** types from `src/api/types.ts` only; nulls ha
         +ndled (`usual`, `pct_vs_usual`, `lower`, `upper`); no client-si
         +de sorting or re-computed verdicts.                            
      21 +   - **Wireframe and copy (3.7):** layout, exact copy strings, 
         +formats (U+2212 minus, `~X`, ranges, week label, tz abbreviatio
         +n), StatusBadge icon + text + colour variables; the states the 
         +task requires.                                                 
      22 +   - **UX/accessibility:** labelled, keyboard-usable controls; 
         +status never conveyed by colour alone.                         
      23 +   - **Quality:** strict TS, no `any`, no dead code or leftover
         + logs; only libraries from 3.1, exact pins; lockfile committed.
      24 +   - **Tests:** every item in the task's Tests section exists, 
         +uses the expected values from PLAN.md section 4 where given, an
         +d would fail if the logic were wrong (no tautologies, no assert
         +ing on mocks only).                                            
      25 +5. Post the review with `gh pr review <n> --comment --body-file
         + <file>`. Always use `--comment`: the PRs are opened from the s
         +ame GitHub account, and GitHub rejects approve or request-chang
         +es on your own PR, so the verdict goes in the body. Format: **V
         +erdict** (APPROVE / CHANGES REQUESTED) · Quickstart result · Fi
         +ndings (severity blocking / should-fix / nit, `file:line`, prob
         +lem, suggested fix) · What was verified.                       
      26  
      23 -Only report findings you verified. Final report: verdict, block
         -ing findings, PR URL (≤ 15 lines).                             
      27 +Only report findings you verified by reading or running the cod
         +e. Final report to the orchestrator (≤ 15 lines): verdict, bloc
         +king findings, PR URL.                                         

● One trap in my own spec: class Day: date: date breaks in Pydantic, because the
  field name shadows the type. Fixing it:

● Bash(cd /home/admin123/projects/qualitra_challenge && python3 - <<'EOF'
      p='PLAN.md'; s=open(p).read()…)
  ⎿  498
  ⎿  Updated PLAN.md (+1 -1)
      154  # domain/ranking.py
      155  def rank_locations(items: Sequence[tuple[str, Evaluation]]) ->
            list[tuple[str, Evaluation]]
      156  ```
      157 -Pydantic models (`schemas.py`). Field names are the contract: 
      157 +Pydantic models (`schemas.py`). Field names are the contract. 
          +Use `import datetime as dt` and annotate dates as `dt.date`, b
          +ecause a field named `date` typed `date` shadows the type and 
          +breaks Pydantic:                                              
      158  ```python
      159  class Health(BaseModel): status: Literal["ok", "error"]; db: L
           iteral["ok", "error"]
      160  class AccountSummary(BaseModel): id: int; name: str; industry:
            str; timezone: str; location_count: int; latest_complete_week
           : date | None

● I've rewritten PLAN.md and the four agent definitions. Nothing is committed
  yet. I checked every expected value in the scenario tables against the
  detection rule with a small script, and they all match.

  What changed:

  - Sonnet with nothing left to decide: all four agents now run on Sonnet. A new
    section 3 in PLAN.md fixes every design choice they'd otherwise have to
    make:
    - the allowed libraries (anything else means stopping to ask)
    - file layout, function signatures, Pydantic models and field names
    - the SQL for the view, endpoints, and the exact error messages
    - the test harness, rounding rules, and the exact UI text, formats, icons
      and colours
    - who holds UI state

    If something still isn't specified, the agent picks the simplest option and
    lists it in the PR under "Decisions taken". If it would touch the contract,
    the data rules, the detection math or the ranking, it stops and asks
    instead.
  - Stacked PRs: a task that won't fit under 700 lines is split along its scope
    bullets into task/<id>a, task/<id>b, each based on the previous branch. The
    plan says how to retarget each one after the previous merges.
  - Tests: every task has its own Tests section, mostly integration tests
    through the API with SQLite and fake accounts. Section 4 is a scenario
    catalog with exact expected values:
    - your 4 required cases: no events, normal values, abnormal higher/lower,
      and locations needing review while the account itself is normal
    - math boundaries (8 cases)
    - data quirks (7)
    - API validation and errors (8)
    - golden tests against the real seed (8)
    - frontend tests with mocked HTTP (MSW) only (10)
  - Dedicated test tasks: tasks 6 and 7 for the API scenarios and task 11 for
    the frontend scenarios. If a test there finds an app bug, the agent fixes it
    in the same PR when the fix is under 50 lines; otherwise it stops and
    reports.
  - Every task ends in a PR, including the foundation (Task 0) and the write-up
    (Task 13). There are now 14 tasks; every agent task is estimated at 150–450
    lines.

  Two traps fixed while checking:
  - Test data starting on the wrong weekday: the earliest fake event decides the
    test database's first complete week, so events placed on a Tuesday would
    have quietly dropped a history week. The factories now place events on
    Monday, and the three timezone cases each got an extra Monday event.
  - Pydantic date field: a field named date with type date breaks Pydantic. The
    spec now tells the agents to annotate it as dt.date.

  To start Task 0, I still need the URL of the empty GitHub repo, under a name
  of your own.

✻ Sautéed for 6m 15s · done 6:40 PM

❯ Before starting to implement this, let's commit what we have in git status.   
  Make different commits according to the changes. Also something that you have 
  to remember is that this instance is running inside Docker sandboxes. To      
  push a pull request or to interact with GitHub in general, you will have to   
  use the existing MCP.                                                         

  Ran 1 shell command (ctrl+o to expand)

● The ignored files are correct: .env, the venv, caches and the starter folder.
  I'll make 9 commits on main, grouped by concern:

  Ran 1 shell command (ctrl+o to expand)

● All 9 commits are on main and the working tree is clean. Now I'll save the
  GitHub-through-MCP rule and check what the MCP offers:

  Listed 1 directory, called mcp-gateway, wrote 2 memories (ctrl+o to expand)

● I committed everything on main in 9 commits, split by concern. Nothing is
  pushed, and there's no origin remote yet.

  cf5099e docs: add CLAUDE.md
  043a329 chore: add builder and reviewer agent definitions
  aba3a88 docs: add decision log and implementation plan
  8c1b981 docs: add detection parameter tuning and reproducible script
  77c8c48 docs: add data integrity report and open questions
  cc554e0 chore(db): add unmodified seed data and loader script
  23cd4e5 feat(db): add Alembic setup and initial schema migration
  3ef50bc chore(infra): add Postgres docker compose and env example
  c05a6c8 chore: add .gitignore

  .env, the virtual environment, the caches and relay-analytics-starter/ stayed
  out because they're gitignored. Since this went straight to main, Task 0 no
  longer needs a foundation PR, only the push.

  I saved a memory to use the GitHub MCP, not gh, for anything on GitHub.
  Searching the gateway found three GitHub servers, none added to this session
  yet: github-readonly, github-comments-approval and github-issues-approval.

  Before Task 1, I need to sort out three things:
  1. Creating PRs: none of the three names suggests it can open a pull request.
     Once one is added I can check its tools, but there may not be a server that
     does this.
  2. Pushing branches: that's plain git push, which the sandbox handles itself,
     so I'll use git for it unless you say otherwise.
  3. The agents and the plan: they still say gh pr create and gh pr review. Both
     reviewer agents are limited to Bash, Read, Grep and Glob, so they couldn't
     reach MCP tools anyway. I'll switch those instructions to the MCP tools
     and allow them in each agent once I know the tool names.

  Can I add the GitHub MCP servers to this session to see their tools, and which
  of the three do you want? I'd still need the repo URL for origin.

✻ Brewed for 44s · done 6:49 PM

❯ https://github.com/gonzalezmauricioalan-folderit/Qualitara-relay-analytics-st 
  arter                                                                         

  Ran 2 shell commands (ctrl+o to expand)
● The repo Qualitara-relay-analytics-starter still contains the starter's name,
  which the README asked you to change, so I'd suggest renaming it on GitHub and
  updating origin to match.

● User answered Claude's questions:
  ⎿  · The repo name contains 'relay-analytics-starter', which the starter 
     README asks not to keep. How do you want to proceed? → I'll rename it first

● main stays local until the repo is renamed. Once you've renamed it on GitHub
  (Settings → General → Repository name), send me the new URL. I'll then:

  1. update origin and push main,
  2. add the GitHub MCP servers and check their tools, mainly whether one can
     create PRs,
  3. switch the agents and PLAN.md from gh to those MCP tools.

✻ Cooked for 18s · done 6:51 PM

❯ I will restart the session and fix this name later outside of the history     
  because this is not relevant. Before now I want you to review the plan that   
  we created. Review the folder that contains the original challenge to see if  
  we missed something that needs to be added to the plan. also this is could be 
  relevant:                                                                     
  # Senior AI Engineer — Take-Home Prompt (Shareable / Candidate-Facing)        
                                                                                
  Thanks for continuing with the process. This exercise is designed to look     
  like the real work you'd be doing in this role: you'll receive a short        
  product background, a lightly-specified ticket, and a seed dataset — and      
  you'll decide what to build, plan it, and implement it the way the team you'd 
  be joining actually works: **agent-first**.                                   
                                                                                
  We care far more about **senior engineering and product judgment** than about 
  completeness. A smaller, correct, well-reasoned slice beats a broad one       
  that's half-broken.                                                           
                                                                                
  ### ⏱ Scope & time                                                            
                                                                                
  - **Budget your effort to 4–6 hours of focused work.** This is a deliberate   
  cap, not a target to exceed. Part of what we're evaluating is how you         
  prioritize under a real constraint.                                           
  - Agent leverage doesn't raise the bar on breadth — a correct, well-reasoned  
  slice still beats a broad one. If your agents make you fast, spend the        
  surplus on verification and edge cases, not more features.                    
  - If you run out of time, **stop and document** what you'd do next in the     
  README rather than rushing a broken feature.                                  
                                                                                
  ### 🤖 AI use                                                                 
                                                                                
  **We expect you to work agent-first — this is how the team you'd join         
  works.** Engineers on this team pick up a ticket, build an AI-assisted        
  implementation plan, and implement with AI coding agents (Claude Code,        
  Copilot, Cursor, etc.) by default. We are not testing whether you can write   
  code without AI. Doing this challenge without AI tooling is not a bonus — it  
  tells us nothing we need to know. What we're interested in is *how you        
  direct, review, and verify* agent output.                                     
                                                                                
  Because of that, two artifacts are **required deliverables** (details under   
  "What to submit"):                                                            
                                                                                
  1. **An implementation plan (`PLAN.md`)** written *before* you implement. Raw 
  and unpolished is fine — better, even. We expect the plan to visibly precede  
  the bulk of implementation in your AI log (planning conversations early,      
  code generation after). We expect to see you plan with (or before) the agent, 
  not just generate code. Your plan must also include a short **"Where would    
  an LLM fit?"** section — see *AI in the product* below.                       
  2. **An AI interaction log** with as much raw                                 
  ──── (69 lines hidden) ────────────────────────────────────────────────────── 
  the product* is neither of these.)                                            
  - **Production infra** — no Kubernetes or CI required. Local run is fine.     
  - **Visual polish** — function over form. Unstyled-but-clear beats            
  pretty-but-broken.                                                            
                                                                                
  ### 📦 What to submit                                                         
                                                                                
  Reply **directly to the recruiter's email** with a link to a **public GitHub  
  repository** containing:                                                      
                                                                                
  1. **The code** — backend, frontend, and migrations, in a repo we can clone   
  and run.                                                                      
  2. **`README.md`** — how to run it locally (DB setup, env vars, commands);    
  your interpretation of the ticket; key **assumptions** and **design           
  decisions** with the **trade-offs** you weighed; what you **deliberately      
  deferred** and why; what you'd do with another day.                           
  3. **`PLAN.md`** — the implementation plan you built from the ticket *before* 
  coding, including the short *Where would an LLM fit?* section. Leave it       
  as-written; don't retrofit it to match the final code.                        
  4. **AI interaction log** (`ai-log/` directory or `AI_LOG.md`) — as described 
  above, plus any committed agent-context artifacts.                            
  5. **Tests** that run.                                                        
                                                                                
  Please make sure the repo is **public** and that the README, PLAN.md, and AI  
  log are committed before you reply.                                           
                                                                                
  ### 🔎 How we evaluate                                                        
                                                                                
  At a high level, we're looking at:                                            
                                                                                
  - **Product & spec judgment** — how you interpreted an underspecified ticket: 
  what you asked or assumed, what you chose to build and *not* build, and why.  
  - **Agentic working discipline** — a plan that genuinely preceded the code,   
  agent direction with precise context, and evidence you caught and corrected   
  agent mistakes rather than rubber-stamping output.                            
  - **AI-in-the-product judgment** — the quality of your                        
  *where-would-an-LLM-fit* reasoning, and — only if you built it — the quality  
  of the integration (verification, failure handling, cost/latency awareness).  
  Skipping the build is never penalized.                                        
  - **Correctness & engineering judgment** — does it work, and are the          
  decisions sound for a senior engineer? Aggregates that are *actually right*   
  against the seed data matter more than feature count.                         
  - **Data handling** — SQL/aggregation reasoning, and honest treatment of      
  messy real-world data.                                                        
  - **Test quality** — meaningful tests on the parts that matter, not coverage  
  farming.                                                                      
  - **Communication** — a README and plan that let us reconstruct your          
  reasoning without you in the room.                                            
                                                                                
  We don't expect perfection in 4–6 hours. We expect to see how a senior,       
  agent-first engineer reasons, prioritizes, and ships a correct slice.         
                                                                                
  Good luck — we're looking forward to seeing how you think.                    

● I re-read the starter folder (README, docs/, schema, seed) and compared the
  plan with the take-home prompt. The starter material is all covered. The
  prompt adds requirements the plan misses, and one of them contradicts a
  decision we made.

  Must fix (required by the prompt)

  #: 1
  Gap: A user-controlled input whose state survives a page reload
  Where we stand: ❌ We put "persisting UI state in the URL" out of scope, and
  the spec says state lives only in React. This is a hard skeleton requirement.
  ────────────────────────────────────────
  #: 2
  Gap: "Where would an LLM fit?" section in PLAN.md
  Where we stand: ❌ Missing. Your first-iteration plan has the start of a "not
  here" argument. The prompt says an LLM used for explanation or summarization
  is fair game, so the deferral needs a better argument than "it can't explain
  why".
  ────────────────────────────────────────
  #: 3
  Gap: AI interaction log (ai-log/ or AI_LOG.md)
  Where we stand: ❌ Not in the plan. It needs raw prompts and responses, where
  you accepted, rejected or redirected the AI, specific moments you caught it
  being wrong, and one line on which tools/models did what. A sanitized log is
  "a serious negative signal".
  ────────────────────────────────────────
  #: 4
  Gap: Questions and assumptions documented in PLAN.md
  Where we stand: ⚠️ They're in OPEN_QUESTIONS.md. The prompt asks for them in
  PLAN.md, so add a section or at least a summary with a link.
  ────────────────────────────────────────
  #: 5
  Gap: PLAN.md "leave it as-written; don't retrofit"
  Where we stand: ⚠️ Our agents treat PLAN.md as a living spec. Once
  implementation starts, changes must go somewhere else (e.g. PLAN_CHANGES.md
  or the README), never into PLAN.md. Freeze it.
  ────────────────────────────────────────
  #: 6
  Gap: README contents
  Where we stand: ⚠️ Task 13 is missing: stack and why, notable choices (Core
  SQL
  vs. ORM, state approach), a one-line test command, "what you'd do with
  another day", and a check that a fresh clone runs in ~15 minutes.
  ────────────────────────────────────────
  #: 7
  Gap: Interpretation up front
  Where we stand: ⚠️ "Your interpretation and scoping decisions are evaluated
  criteria." PLAN.md jumps straight to mechanics. It needs a short opening
  section: what "normal" means, which window, which view, what we chose not to
  build, and why.

  Risks worth a decision

  8. Time budget: 4–6 hours. 14 tasks, each with builder → reviewer → your
     review, likely blows the budget. The prompt rewards a correct slice and
     says to spend surplus on verification, which our plan does well. It also
     says "if you run out of time, stop and document". We need fewer, larger
     tasks (still under 700 lines each) and an explicit cut line.
  9. Where the aggregation happens. "Data handling: SQL/aggregation reasoning"
     is a criterion. The endpoint must do "real aggregation, not pass-through".
     Our repository fetches every raw event for an account and does all the
     aggregation in Python, which a reviewer could read as pass-through SQL. The
     cause is the SQLite-for-tests decision, since SQLite can't do timezones.
  10. Account picker vs. "a single trusted customer admin". Picking any account
      is fine as a demo convenience, but the README should say that in
      production the account comes from the session.

  Minor

  - CLAUDE.md is partly stale. Its MCP note says not to use GitHub tools in this
    session, which now conflicts. Its spike description says "starting around
    06-03"; it's actually one day.
  - PLAN.md and the agents still use gh. The switch to MCP is pending your
    restart.
  - The repo must be public at submission. You're handling the name.

● User answered Claude's questions:
  ⎿  · How should UI state survive a page reload? → localStorage
     · How do we fit the 4–6 hour budget? → Keep as is
     · Where should the weekly aggregation happen? → Keep Python, justify
     · LLM in the product? → Keep the idea that I put on the first iteration of 
     the plan: an LLM will add no value here because the deterministic part 
     already explained what the ticket asked. The LLM will add another moving 
     part that we have to create and maintain with no value. 

● I'll apply your choices and the must-fix items to PLAN.md.

● Bash(python3 - <<'EOF'
      p='PLAN.md'; s=open(p).read()…)
  ⎿  12:## 0. Interpretation of the ticket
     25:## 0.1 Questions and working assumptions
     39:## 0.2 Where would an LLM fit?
     … +21 lines (ctrl+o to expand)
  ⎿  Updated PLAN.md (+93 -16)
       5  
       6  **Agents run on Sonnet. Everything that needs judgment has alre
          ady been decided in this file.** Agents implement; they don't r
          edesign.
       7  
       8 +**This file is frozen once Task 1 starts.** The prompt asks for
         + the plan as written before coding, so it's never retrofitted t
         +o match the code. Anything that changes during implementation g
         +oes to `PLAN_CHANGES.md` (what changed, why, which PR) and is s
         +ummarized in the README.                                       
       9 +                                                               
      10  ---
      11  
      12 +## 0. Interpretation of the ticket                             
      13 +                                                               
      14 +- **The question:** "Is this week's activity normal *for us*?",
         + asked by a customer admin on Monday morning about the week tha
         +t just ended.                                                  
      15 +- **"Normal"** = the account's own recent history, not a benchm
         +ark against other customers: the median of the previous 8 compl
         +ete weeks, with a band robust to one-off spikes (median ± 2.5 ×
         + a MAD-based spread, with floors for small counts). Weeks are M
         +on–Sun in the account's local time.                            
      16 +- **What it shows:** one verdict for the account (normal / high
         +er / lower / not enough history), the 7 days of the week next t
         +o their usual values as context, and every location with its ow
         +n verdict, ranked so the locations that dropped come first. Tha
         +t covers both product signals: "is this number normal?" (accoun
         +t managers) and "which location needs attention?" (support).   
      17 +- **What we chose not to build, and why:**                     
      18 +  - Daily verdicts: ~1 event per location per weekday, so they'
         +d be noise.                                                    
      19 +  - Per-event-type or outcome metrics: too little volume per se
         +ries; we'd ask product which one matters most.                 
      20 +  - Seasonality: only ~25 weeks of data.                       
      21 +  - Holiday/campaign annotations, alerting, ML forecasting, aut
         +h.                                                             
      22 +- **Single trusted admin:** the account picker is a demo conven
         +ience. In production, the account would come from the logged-in
         + session.                                                      
      23 +- **Metric:** total events (calls + leads + appointments), dedu
         +plicated.                                                      
      24 +                                                               
      25 +## 0.1 Questions and working assumptions                       
      26 +                                                               
      27 +On a real ticket these would go to product or the data owners. 
         +Full table with evidence: `OPEN_QUESTIONS.md`.                 
      28 +                                                               
      29 +| Question | Working assumption |                              
      30 +|---|---|                                                      
      31 +| Why do some accounts have no events (#20)? | Not onboarded ye
         +t → "not enough history". |                                    
      32 +| Why is #18's timezone `UTC`? | Probably a misconfiguration → 
         +use it as stored and show a warning note. |                    
      33 +| Why ~20% of events before 07:00 local? | Automated processes 
         +→ count everything, no business-hours filter. |                
      34 +| Why the one-day spike for #6 (Wed 2026-06-03, 805 events, all
         + 15 sites) and +94% for #15 the same week? | A marketing campai
         +gn → keep it, flag it as higher, use a median-based baseline so
         + it doesn't distort later weeks. |                             
      35 +| Why are `duration_seconds` (313 calls) and `outcome` (398 row
         +s) NULL? | Not captured / not known yet → irrelevant to an even
         +t count; the rows still count. |                               
      36 +| Which metric matters most (total vs. per type vs. missed-call
         + rate)? | Total events, for volume and simplicity. |           
      37 +| Do businesses work weekends? | Every account has some weekend
         + activity (2–12%) → full Mon–Sun weeks. |                      
      38 +                                                               
      39 +## 0.2 Where would an LLM fit?                                 
      40 +                                                               
      41 +**Not in this slice.** The ticket asks a customer to see at a g
         +lance whether their week is normal and which location needs att
         +ention. The deterministic part already answers that completely:
         + a verdict, a number ("−32% vs. your usual week"), and a ranked
         + list. Those are exact, free, instant and testable. An LLM woul
         +d add another moving part to build and maintain (prompts, outpu
         +t validation, failure fallbacks, cost and latency) without addi
         +ng value. It could only restate numbers we already show. It als
         +o couldn't explain *why* a week was unusual, because the data h
         +as no causes in it: no campaigns, holidays or staffing. Any "ex
         +planation" would be invented, which is worse than none on a das
         +hboard customers act on.                                       
      42 +                                                               
      43 +**When it would fit:** if the product later captured context th
         +e numbers can't express, such as customer-entered notes, call t
         +ranscripts or campaign records, an LLM could summarize or class
         +ify that context next to the verdict. It would sit behind a tru
         +st boundary: it never changes the numbers or the status, its cl
         +aims are checked against the data, and there's a deterministic 
         +fallback when the call fails.                                  
      44 +                                                               
     … 126 more lines (ctrl+o to expand)

● I'll also update Task 0, since main is already committed, and fix the stale
  parts of CLAUDE.md:

● Bash(python3 - <<'EOF'
      p='PLAN.md'; s=open(p).read()…)
  ⎿   M CLAUDE.md
      M PLAN.md
  ⎿  Updated PLAN.md (+6 -4)
      356  
      357  ## 5. Tasks
      358  
      359 -### Task 0 — Foundation (orchestrator + human) → PR           
      360 -**Goal:** get the existing foundation onto GitHub through a PR
          -.                                                             
      359 +### Task 0 — Foundation (orchestrator + human)                
      360 +**Goal:** get the foundation onto GitHub, then switch GitHub a
          +ccess to the MCP.                                             
      361 +**Status:** the foundation is already committed directly on `m
          +ain` (9 commits, before this plan was frozen), so there's no f
          +oundation PR; that's an exception to "every task ends in a PR"
          +.                                                             
      362  **Scope:**
      362 -- Human: create an empty GitHub repo with your own name (not a
          - fork, not `relay-analytics-starter`) and add it as `origin`. 
      363 -- Orchestrator: commit `.gitignore` alone on `main` and push. 
          -Then, on branch `task/0-foundation`, commit the rest (compose,
          - migration 0001, seed, scripts, analysis, docs, `.claude/agent
          -s/`, CLAUDE.md pointing to this plan) and open a PR. The seed 
          -is excluded from the line count. If the docs push the PR over 
          -700 lines, stack them: infra in `0a`, docs in `0b`.           
      363 +- Human: rename the GitHub repo to a name of your own (no `rel
          +ay-analytics-starter`) and make it public before submission.  
      364 +- Orchestrator: update `origin`, push `main`, add the GitHub M
          +CP servers, and replace the `gh` instructions in section 1 and
          + `.claude/agents/*.md` with the MCP tools (also allowing those
          + tools in the reviewers' `tools:`). This is the last edit to P
          +LAN.md before it's frozen.                                    
      365  
      366  **Tests:** none (no app code).
      367  **Quickstart:**
      368  ```bash
      369 +git ls-remote origin main      # main is on GitHub            
      370  docker compose down -v && docker compose up -d --wait && ./scr
           ipts/load_seed.sh   # accounts=20, activity_events=12626
      371  ```
      372  
  ⎿  Updated CLAUDE.md (+5 -3)
       4  
       5  ## IMPORTANT
       6  
       7 -You are running inside a docker sandbox. You have access to som
         -e MCP (eg Github, Jira.) But There is no need to use in this se
         -ssion                                                          
       7 +You are running inside a docker sandbox. Use the existing GitHu
         +b MCP (through the MCP gateway) for every GitHub interaction (P
         +Rs, reviews, comments), not the `gh` CLI. Jira MCP: not needed.
       8  
       9 +The implementation plan is `PLAN.md` (frozen once Task 1 starts
         +; changes go to `PLAN_CHANGES.md`). The decision log is `PLAN_f
         +irst_iteration.md`.                                            
      10 +                                                               
      11  ## What this repo is
      12  
      13  A take-home exercise for "Relay", a fictional B2B SaaS that tra
          cks inbound customer activity (calls, leads, appointments) acro
          ss a customer's locations. The task is ticket **DASH-247** (`re
          lay-analytics-starter/docs/TICKET.md`): help a customer answer 
          *"is this week's activity normal for us?"* on their dashboard.
     ...
      61  
      62  ## Known data quirks (from profiling the seed; re-verify before
           relying on them)
      63  
      62 -- Events run 2026-02-01 → 2026-07-27, about 26 weeks. The last 
         -week may be partial.                                           
      64 +- Events run 2026-02-01 → 2026-07-27: 25 complete local weeks (
         +2026-02-02 … 2026-07-20); the first and last weeks have one day
         + each.                                                         
      65  - Account 20 (Quiet Harbor Spa) has **no events at all**, so th
          e baseline has to handle an empty history.
      66  - Accounts range from 1 location to 15. Location names follow t
          he pattern `Site A`…`Site O` and are unique only *within* an ac
          count.
      65 -- Account 6 (Metro Collision Centers, 15 sites) has a large spi
         -ke across many sites starting around 2026-06-03, so a naive mea
         -n baseline would be skewed by it.                              
      67 +- Account 6 (Metro Collision Centers, 15 sites) has a one-day s
         +pike on Wed 2026-06-03 (805 events across all 15 sites vs ~13 o
         +n a normal day), so a naive mean baseline would be skewed by it
         +. Account 15 is +94% the same week.                            
      68  - About 12 groups of exact duplicate events have the same accou
          nt, location, type and timestamp but different `id`s.
      69  - `outcome` is NULL on about 400 rows across all types. `durati
          on_seconds` applies only to calls (20–1500s) and is NULL on abo
          ut 313 calls.
      70  - Account timezones include `America/Phoenix`, which has no DST
          , and plain `UTC`.

● I've updated PLAN.md and CLAUDE.md. Both are modified but not committed yet.

  What changed in PLAN.md:
  - Three new opening sections:
    - 0. Interpretation of the ticket: what "normal" means, the window, what the
      screen shows, what we chose not to build and why, and that the account
      picker is a demo convenience for a single trusted admin.
    - 0.1 Questions and working assumptions: a summary table that links to
      OPEN_QUESTIONS.md. The prompt asks for these inside PLAN.md.
    - 0.2 Where would an LLM fit?: your argument from the first iteration, with
      your wording. The numbers already answer what the ticket asks, and an LLM
      is another moving part to build and maintain with no added value. It also
      notes that the data has no causes in it, so any "explanation" would be
      invented. It ends with when it would fit and what guardrails that would
      need.
  - Freeze rule: PLAN.md is frozen once Task 1 starts. Changes go to
    PLAN_CHANGES.md and get summarized in the README, because the prompt says
    "don't retrofit it".
  - State survives reload with localStorage:
    - a storage.ts module, key relay.dashboard.v1
    - a saved selection is ignored if the account no longer exists or the week
      is invalid
    - every storage access is wrapped in try/catch
    - three new frontend scenarios: F11 restores after reload, F12 falls back on
      invalid data, F13 keeps working when storage throws
    - added to the Task 8 tests and to the live check in Task 11
  - Aggregation in Python: the plan now justifies it (timezones, SQLite, ≤ ~2.7k
    rows per account) and gives the production alternative, a daily rollup
    table.
  - Task 13 README: now covers everything the prompt lists: run instructions
    checked against a fresh clone in ≤ 15 minutes, the test one-liners, stack
    and why, notable choices, interpretation, assumptions, trade-offs, what was
    deferred, what you'd do with another day, and changes from the plan.
  - New Task 14, the AI interaction log:
    - raw transcripts in ai-log/
    - the one-line tools/models note: Opus plans and orchestrates, Sonnet builds
      and reviews, you decide and review PRs
    - what you accepted, rejected or redirected
    - a reflection already seeded with real moments from this session
  - Running notes: after each of your PR reviews, I'll add notes to
    ai-log/notes.md so the log isn't rebuilt from memory at the end.
  - Task 0: updated to match reality. main is already committed, and the switch
    from gh to the MCP will be the last edit before the freeze.

  CLAUDE.md: the MCP note now says to use the GitHub MCP and points to PLAN.md
  and the freeze rule. I also corrected the description of the data range and
  the spike.

  What I left as you decided:
  - 14 tasks: that's very likely over the 4–6 hour budget.
  - No cut line: the prompt says to stop and document if time runs out.

  You can still add a cut line later without restructuring anything.

  Want me to commit these two files? Once you restart and send the renamed repo
  URL, the next step is the MCP switch.

✻ Crunched for 2m 15s · done 7:02 PM

❯ yes, commit them                                                              

  Ran 1 shell command (ctrl+o to expand)

● I made two more commits on main, and the working tree is clean:

  acb32e6 docs: point CLAUDE.md to the plan and GitHub MCP, fix data notes
  2d99c7b docs: add interpretation, assumptions, LLM section and AI log task to 
  plan

  That makes 11 commits, and none of them are pushed yet. After you restart and
  rename the repo, send me the new URL. I'll update origin, push main, add the
  GitHub MCP servers, and switch the plan and agents from gh to the MCP tools.
  That change will be the last edit to PLAN.md before the freeze.

✻ Brewed for 9s · done 7:03 PM

! mkdir ai-log                                                                  
  ⎿  (Bash completed with no output)

● ai-log/ exists now. Git won't track it until there's a file inside.

  I could seed ai-log/notes.md now, while this session is still fresh: the
  timeline so far, the decisions you accepted, rejected or redirected, and the
  moments where the AI was wrong or got corrected. That's the running-notes file
  from Task 14. I can also copy this session's raw transcript into
  ai-log/transcripts/ before you restart. That's the full record of the
  planning, which shows it came before any code. Should I do both?

✻ Worked for 5s · done 7:04 PM