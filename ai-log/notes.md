# Orchestrator notes (raw material for Task 14)

These notes are kept after each review (PLAN.md section 1, step 5). Each entry records what the AI got wrong, what review caught, and what the human accepted, rejected or redirected.

## Task 1: API skeleton, clean view, health, test harness (PR #2)
- **Caught by review (blocking):** `/health` returned 500 instead of 503 when the DB was down. The builder only tested "ping raises", but the real connection was opened in the `get_connection` dependency, outside the handler's `try`. The reviewer found it by stopping the compose DB on its own initiative. It was fixed on the same branch, with a test that uses an unopenable SQLite path.
- **Human feedback:** "too cryptic" about `backend/pyproject.toml`, so the orchestrator added commented sections to it. This became the agent rule "why-comments on config".
- **Human decision:** agent improvements were proposed and then parked ("keep in memory").
- **Accepted as-is:** `ruff format` reflowed the already-applied migration 0001. The reviewer confirmed the change was whitespace only.

## Task 2: Domain logic (PR #3)
- **Caught by review (should-fix):** the reviewer's mutation spot-checks (requested in the prompt) found 5 untested rules: the MAD_SCALE factor, LOW_VOLUME_USUAL=6, MIN_PCT `>=`, series_start `>=` and the N_WEEKS cap. They were closed with tests only.
- **Human request:** an ASCII diagram for `detection.py`. The human reviewed it first, then asked for "the short version" as the module docstring.
- **Human request, redirected:** the same for `ranking.py`. The orchestrator proposed an example that merged S4 and R3. The human chose "S4 only".

## Agent definitions (PR #4, task/0b-agents)
- **Human decision:** apply all six proposed rules on a separate branch and review it on GitHub. The rules are real error-path tests, why-comments, warnings under Follow-ups, a diagram plus a single-scenario example for logic modules, reviewers triggering errors for real, and reviewer mutation spot-checks.
- **Rejected on purpose:** a rule about the formatter touching out-of-scope files, because the existing process already covered it.
- **Restart:** the session was restarted so the subagents would load the new definitions. Task 3 then ran with no rules pasted into the prompt, as a test that the definitions work on their own.

## Task 3: Repository, schemas, seed loader, GET /accounts (PR #5)
- **The new agent rules worked unprompted:** the builder added a real unreachable-DB test, fixed the Alembic `path_separator` warning, and stopped to ask instead of adding `httpx2` (a library not in the plan).
- **Caught by review (should-fix):** two mutations survived in `test_latest_complete_week_from_data_when_as_of_unset` (the UTC date instead of the local date, and min instead of max). The test was strengthened with a Chicago event on Sun 23:30 local (Mon UTC) and a Tokyo account.
- **Human decision:** keep `httpx` and accept the Starlette deprecation warning.

## Task 4: GET /accounts/{id}/weekly-insight (PR #6)
- **Seed parity:** G2–G8 matched section 4 on Postgres on the first build.
- **Caught by review (should-fix):** mutation gaps in rounding, the first-week boundary, the duplicate-note end bound, duplicates counted by UTC date, weekday-usuals gating, and the first week taken from the UTC date. They were closed with tests only.
- **AI wrong (orchestrator):** to prove "first complete week uses the local date", the orchestrator suggested a first event at Sun 23:30 Chicago. In that case local and UTC both give the same next Monday, so the test couldn't tell them apart. The builder caught this and used Tokyo instead (Tue 00:30 local = Mon UTC).
- **Builder judgment:** it reported that rounding `usual` at 2 vs 1 decimals is an equivalent mutant, because a median of integers is always x.0 or x.5.

## Task 5: API container + exported contract (PR #7)
- **Approved with no should-fix findings**, the first clean review. The reviewer:
  - verified the image contents and that the seed's sha256 is unchanged
  - confirmed the entrypoint is idempotent on restart and exits 1 with a bad DATABASE_URL
  - checked that `/health` returns 503 and the compose healthcheck reports unhealthy when the db is stopped
  - confirmed the stale-contract test catches a real field rename
- **Builder judgment:** the image keeps the repo layout (`/srv/backend`, `/srv/data`), so `seed.py` needed no change. Because `up` now also starts the api, it changed the CLAUDE.md db-only commands to `docker compose up -d --wait db`.
- **Nit, accepted:** with the db down, `/accounts` returns a plain 500. PLAN.md 3.5 doesn't specify that case.

## Task 6: API scenario tests S1–S4, B1–B8 (PR #8)
- **Plan values held:** every section 4 expectation passed on the first run, with no app fixes.
- **Builder:** ran 45 manual mutants and added 5 edge tests beyond the catalog. It deferred 4 survivors to Task 7, judging only against its own new files.
- **Orchestrator asked the reviewer to re-run the deferred survivors against the full suite.** Of the 4, 3 were already killed by the Task 2/4 tests, and only `history[1:]` in the MAD is really uncaught.
- **AI wrong (reviewer):** it proposed fixing the `usual` 2-digit rounding mutant with "a usual that isn't x.0/x.5". That's impossible, because a median of integers always ends in .0 or .5, which Task 4 had already established. The reviewer also proposed moving R1's outlier, which would change a plan scenario. The orchestrator rejected both, and the MAD mutant goes to a separate extra test in Task 7.

## Task 7: API scenario tests R1–R7, V1–V7, G1–G8 (PR #9)
- **Plan values held:** every section 4 expectation passed on the first run, with no app fixes.
- **First plan change:** the plan's V7 ("dependency override that raises") no longer worked, because the Task 1 fix moved `/health` off the dependency. The orchestrator decided to use an unreachable DB instead, which is recorded in `PLAN_CHANGES.md`.
- **Builder escalated correctly:** rounding `days[].usual` survives the whole suite, and section 2 doesn't specify it. The builder left the call to the human instead of widening scope. The reviewer confirmed the gap, and it was closed with a 4-line test.
- **Nit rejected:** "R5 doesn't depend on DST". R5's setup is the plan's, and the DST switch is covered by the Task 2 unit test.
- **Backend complete:** 88 tests (78 fast). The full suite takes about 33s; the fast loop's cost is per-event inserts in B6/B7.

## Task 8: frontend scaffold + pickers (stacked PRs 8a/8b, merged)
- **First frontend run, and the first stacked split:** the task came to 909 lines, so the builder split it into 8a (scaffold, 644 lines) and 8b (pickers, 304 lines), as PLAN.md section 1 describes.
- **Builder caught a trap:** in msw 3.0.3, `onUnhandledRequest` became `onUnhandledFrame`. The old name silently did nothing, so tests could have reached the live API. The reviewer confirmed it: a throwaway request got through to the real API.
- **The builder broke a rule:** it added 5 dev packages that aren't in PLAN.md 3.1 (`@types/react`, `@types/react-dom`, `@testing-library/dom`, `@eslint/js`, `globals`) without stopping to ask. The reviewer checked each one. The human kept the 4 required ones and dropped `globals`, recorded as `PLAN_CHANGES.md` entry 2. TypeScript is pinned to 5.9.3, because peer ranges force it.
- **Caught by review (should-fix):**
  - AbortSignal cancellation had no test; the code was correct.
  - Storage shape validation had no test.
  - A fixture contradicted the real API (account 20 had a null week).
  - One F8 test was flaky under load.
  - The PR bodies had wrong test totals and line counts.

  All were fixed, and 8b was rebased onto 8a.
- **Agent noise:** after finishing, the builder sent about 15 leftover "timer finished" notifications.

## Task 9: verdict card, daily chart, data notes (merged)
- **Parked rules worked when pasted into the prompt:** the builder's mutation run hit the 120 s tool limit and went to the background. The builder stopped it, restored the file, and verified the tree. It also re-measured the PR numbers after its last commit, and added no libraries.
- **AI wrong (orchestrator):** the reviewer prompt said account 6, week 2026-06-01 should show "+333%". The correct figure is (880−66)/66 = +1233%. The orchestrator sent a correction, and the reviewer used the API value.
- **Caught by review (should-fix):**
  - "1 events": the builder chose not to pluralise, and the reviewer and orchestrator recommended fixing it.
  - The `Line` `dataKey` usual→total mutant survived all tests.
- **The builder's mutation check found its own gap:** the Bar dataKey mutant passed until it added a bar-height assertion.
- **Accepted:** a global `testTimeout` of 20 s. The reviewer measured cold imports of 4–6 s for the first test of each file and found no missing `await` or real timers.

## Task 10: ranked locations table (merged)
- **Approved; review caught 2 test gaps:**
  - The visible header text was "tested" by an assertion that the hidden caption also satisfied.
  - Every fixture usual was an integer, so unrounded output passed. Real data (account 6) has 4.5 and 3.5.
- **Consistency fix from a reviewer nit:** the table used `Math.round` and the card used `formatNumber`. They now share one helper, so a location reads the same in both places.
- **Live parity:** account 6 has 15 rows, all higher. Account 8 has one row (~10, −30%). Account 20 shows `Locations (0)` plus the empty copy.

## Task 11: skipped (human decision)
- **Skipped for time.** The human chose to skip Task 11 (the consolidated F1–F13 scenario pass and the manual browser check) and keep Task 12 (one-command `docker compose up`), because the one-command run matters more to reviewers.
- The human's message read "continue with task 12 … skip task 12". The orchestrator asked which task was meant instead of guessing.
- **Recorded for reviewers:** `PLAN_CHANGES.md` entry 3 maps each F id to the Task 8–10 tests that still cover it, and says what was lost. The README's "Changes from the plan" section (Task 13) summarizes it.

## Task 12: web container + one-command run (PR #15, merged)
- **Approved with nits only.** The reviewer:
  - followed the README "Run it" section from `down -v`, and the stack came up in 34 s on a warm cache;
  - confirmed the bundle contains the API URL, the final image has only `dist` plus the config, cache headers are set, and a missing `/assets/*` returns 404;
  - with the api stopped, found the static app still served.
- **Builder caught a real bug:** the web healthcheck with `localhost` failed. Inside the alpine container `localhost` resolved to `::1`, but nginx listens on IPv4 only. The check uses `127.0.0.1` now, and the reviewer confirmed the cause.
- **Deferred to Task 13:** documenting `API_PORT` and the fixed 8080 web port (from the CORS default) in the README.
- **Still open:** no agent ever opened the dashboard in a real browser. That's left to the human.
- **Recurring:** the builder left watchers running that sent 2 empty notifications after finishing, even though the rule was pasted into its prompt.

## Task 13: README (orchestrator, PR #16, merged)
- **Written by the orchestrator directly**, from PLAN.md, `PLAN_CHANGES.md`, `Detection_tuning.md`, `Data_integrity.md` and `OPEN_QUESTIONS.md`.
- **Fresh clone:** 2 min 20 s with `build --no-cache` (base images already pulled).
- **Host issues found while bringing the stack up for the human:**
  - port 5432 is held by the Docker sandbox, so compose needs `POSTGRES_PORT=5434` on the host; now documented;
  - `backend/.venv` was created in the sandbox with Python 3.14 and doesn't run on the host (3.12); the tests ran in a temporary venv.
- **The human's live check found a confusing row:** account 14, Site B, 2 events vs usual 6.5 (−69%) reads "Normal" with no low-volume tag. The orchestrator first called it a gap in the rule. It is the limit already documented in `Detection_tuning.md` §7: the lower bound is ≈ 0 when usual ≤ k², and 6.5 is just above `LOW_VOLUME_USUAL = 6`. The README now documents it with this example. Raising the threshold is a follow-up for the human to decide.
- **The default week shows nothing to act on** on any account; the README lists weeks that do.
- **The human rejected the first README draft: "too technical".** The orchestrator rewrote it in plain language in a scratch file the human reviewed in VS Code. The formula, the env-var table and the plan-change details came out. "Changes from the plan" was cut to one point: we ran out of time, so we skipped Task 11.
- **"How it was built" was wrong, and the human corrected it:** it started at `PLAN.md`. The real order is the hand-written `PLAN_first_iteration.md`, then the AI as a challenger refining it into `PLAN.md`, then execution with the four agents.
- **The human redirected the known-limit section several times:**
  - The orchestrator first proposed raising `LOW_VOLUME_USUAL` to 10. It then found that 68 of 69 locations have usual ≤ 10, so the warning would be on almost every row. It dropped the idea.
  - It offered three options in a table. The human couldn't read it ("se rompe"), and it was re-sent as a list. The human then misread "0–13" as a number, so the orchestrator explained it as "from 0 to 13 events".
  - The human chose the UI-only option (show each location's normal range), saying it was enough and easier to understand than combining it with a rule change.
  - The human's idea that "the median was the problem" was checked and rejected with numbers: mean ± std gives Site B a range of 0.6–11, so 2 is normal there too.
  - The human asked to state the assumption that real customers have more volume. The orchestrator first wrote "re-check the settings on production data". The human rejected it, because this is a challenge with no production data.
  - The phrase "a limit of the volume, not of the method" sounded defensive, and the human rejected it. It became "we chose not to flag weeks like this, because a stricter rule would flag ordinary weeks at small locations almost every week".
- **The human authorized the orchestrator to push and merge** while the session ran outside the sandbox. #15 was already merged by the human; #16 was retargeted to `main` and merged.
