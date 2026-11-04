# Relay: "is this week's activity normal for us?" (DASH-247)

A dashboard that tells a customer admin, on Monday morning, whether last week's activity (calls, leads,
appointments) was normal for their business, and which of their locations dropped.

"Normal" means normal **for that customer**: we compare the week with the customer's own previous 8 weeks, not
with other customers.

## Run it

You need Docker with compose v2, and free ports 5432, 8000 and 8080.

```bash
docker compose up -d --build --wait    # database + api + dashboard; the api loads the data itself
```

- Dashboard: http://localhost:8080
- API: http://localhost:8000 (docs: http://localhost:8000/docs)

Start over with a clean database:

```bash
docker compose down -v && docker compose up -d --build --wait
```

From a fresh clone, the whole stack came up in about **2.5 minutes** (the budget was 15).

If port 5432 is already in use on your machine, run `POSTGRES_PORT=5434 docker compose up -d --build --wait`.
The other settings are in `.env.example`; the defaults work without changes.

### What to look at

The most recent week (July 20) is normal for every customer. These weeks show the other cases:

| Customer | Week | What you see |
|---|---|---|
| 6 Metro Collision Centers | June 1 | Much higher than usual, at every location (a one-day spike on June 3). |
| 2 Harbor Dental Partners | July 6 | Lower than usual (−45%). |
| 1 Summit Auto Group | June 1 | The customer is normal, but one location (Site F) dropped and is listed first. |
| 20 Quiet Harbor Spa | any | Not enough history yet (no activity at all). |
| 18 Capital City Storage | any | A warning that the customer's timezone looks misconfigured. |

## Tests

```bash
cd backend && .venv/bin/pytest -q      # api, 88 tests, no Docker needed
cd frontend && npm test -- --run       # dashboard, 46 tests, no running api needed
```

## How "normal" is decided

1. Take the customer's last 8 complete weeks (Monday to Sunday, in the customer's own timezone).
2. The **usual** week is the middle value of those 8 weeks (the median). One crazy week can't move it.
3. Around the usual value we draw a **range** of normal variation, based on how much those weeks normally move.
4. A week is **higher** or **lower than usual** only if it falls outside that range and the change is large
   enough to matter. Otherwise it's **normal**.
5. With fewer than 4 weeks of history, we say **not enough history** instead of guessing.

The same check runs for the whole customer and for each location. Locations that dropped are listed first.

Why this method: the data has a huge one-day spike (customer 6, June 3). An average-based method would treat
that spike as part of "usual" for the next two months, and then even a week with zero activity would look
normal. The median ignores the spike. We tuned how wide the range is so that it flags real changes without
flagging random noise every week. The numbers behind this are in `Detection_tuning.md`.

## Known limit: a small location can drop 70% and still say "normal"

You'll see it on customer 14, Site B, week of July 20: **2 events against a usual of about 7 (−69%), marked
"Normal"**.

**Why.** Site B usually gets about 7 events a week, and with so few events the number jumps around by pure
chance: its last 8 weeks were 5, 6, 8, 7, 2, 7, 4 and 8. A week of 2 already happened in June, and the next week
was back to 7. So from the data alone, this week can't be told apart from bad luck. We chose not to flag weeks like
this: a stricter rule would catch this one, but it would also flag ordinary weeks at small locations almost
every week, and a customer would stop trusting the warnings.

**We knew this from planning.** The tuning (`Detection_tuning.md`) showed that most locations get 10 events a
week or fewer, so at location level only very large drops can stand out. That's why:
- **The verdict at the top of the screen, for all locations together, is the one to read first.** Adding up
  every location gives enough events to catch real drops, such as customer 2's −45% in the week of July 6.
- **The location rows are the detail:** they show which location caused that change, with drops listed first.

**We assume real customers have more volume per location** than this sample (see Assumptions). With more
events the range gets tighter (0 to 13 at 7 a week, 32 to 68 at 50), so real drops stand out.

**What's missing is that the screen says so.** It shows "−69%" next to "Normal" without explaining why. The fix
is to show each location's normal range on its row, so the verdict explains itself:

> 2 events · usual 7 · normal for this location: 0 to 13

The rule stays the same. The API already returns the range; only the dashboard needs to show it.

## Assumptions

On a real ticket we'd ask product or the data owners. For the exercise we assumed:

| Question | Assumption |
|---|---|
| Why does customer 20 have no activity? | They haven't started using the product yet → "not enough history". |
| Why is customer 18's timezone UTC? | Probably a setup mistake → we use it as is and show a warning. |
| Why do ~20% of events happen before 7 am? | Automated processes → we count everything. |
| Why the spike for customer 6 on June 3 (and +94% for customer 15 that week)? | A marketing campaign → we keep it and show it as higher than usual. |
| Some events have no outcome or call duration. | Not recorded yet → they still count as events. |
| Which number matters most? | Total events (calls + leads + appointments). |
| Is this volume typical? Most locations get 10 events a week or fewer. | Real customers have more volume per location than this sample. |
| Do these businesses work weekends? | Every customer has some weekend activity → weeks are Monday to Sunday. |

## How we handled messy data

We used the data exactly as delivered and never changed it. The code handles its problems:

- **Exact duplicates** (12 pairs): counted once. The week shows a note when duplicates were removed.
- **The one-day spike:** kept, because it's real activity the customer should see. The method keeps it from
  distorting later weeks.
- **A customer with no data:** shows "not enough history" instead of an error.
- **Timezones:** every week and day is computed in the customer's own timezone, including daylight saving time
  and Phoenix, which has none.
- **Partial weeks** at the start and end of the data: never shown, because they would always look low.
- **The data ends months ago:** "this week" means the last week with data, not the calendar.

## Design decisions

- **Weekly verdicts, daily context.** A location has about one event per day, so a verdict per day would be
  noise. The chart shows each day next to its usual value, without a verdict.
- **Only drops count as "needs attention".** Locations that dropped come first. Higher-than-usual weeks are shown
  but not treated as problems.
- **No AI/LLM feature.** The numbers already answer the question exactly. An LLM could only repeat them, and it
  can't explain *why* a week was unusual, because the data doesn't contain causes (campaigns, holidays, staffing).
  An invented explanation is worse than none on a screen customers act on.
- **Stack:** FastAPI + Postgres on the backend, React + TypeScript on the frontend. It's the stack we know best.
  The calculations are in Python, where timezones are handled correctly and the tests are fast.

## Left out on purpose

- Alerts and notifications, forecasting (out of scope in the ticket).
- Separate numbers per event type or outcome (for example, missed calls): we'd first ask product which one
  matters.
- Seasonality: 6 months of data can't show yearly patterns.
- Marking holidays or campaigns, login and permissions.

## With another day

- **Show each location's normal range** on its row (see "Known limit"), so a big drop marked "Normal" explains
  itself.
- Numbers per event type or outcome, after asking product.
- Pre-computed daily totals, so the dashboard stays fast with much more data.
- Tests against Postgres, not only SQLite.
- A way to mark campaign or holiday weeks as expected.

## How it was built

1. **A first plan, written by hand** (`PLAN_first_iteration.md`): the questions to answer about the data, the
   options for each decision, and the open points.
2. **Refined with the AI as a challenger.** We used the AI to question the structure of that first plan, run the
   data checks (`Data_integrity.md`) and the tuning (`Detection_tuning.md`), and fill the gaps. Every decision
   was taken by a person. Several rounds produced the final plan (`PLAN.md`), frozen before any code.
3. **Executed by four agents**, one task at a time, each task on its own branch and pull request:
   - `api-builder` and `frontend-builder` implement a task from the plan;
   - `api-reviewer` and `frontend-reviewer` check it against the plan and re-run it;
   - a person reviews and merges each pull request.

The agent definitions are in `.claude/agents/`, and the AI log is in `ai-log/`.

**Changes from the plan:** we ran out of time, so we skipped one task: a final round of end-to-end tests of the
full dashboard and a manual check in the browser. The individual parts are still tested. Details are in
`PLAN_CHANGES.md`.
