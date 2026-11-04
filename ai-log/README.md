# AI interaction log

This folder is the raw record of how the project was built with AI, plus this summary. The summary is an index
into the raw files: it points to the moments where I made a choice, redirected the model, or caught it being
wrong. The raw files are not edited.

| File | What it is |
|---|---|
| `creation_of_plan_raw.md` | The planning session, exported from the Claude Code terminal: from an empty repo to the frozen `PLAN.md`. |
| `implementation_process_raw.txt` | The implementation session: Tasks 1 to 12, with the orchestrator launching the builder and reviewer agents. |
| `notes.md` | Notes the orchestrator wrote after each of my PR reviews: what review caught, what I accepted, rejected or redirected. |

References like `plan:1191` mean line 1191 of `creation_of_plan_raw.md`; `impl:2978` means
`implementation_process_raw.txt`.

**Tools and models, in one line:** Claude Code with Opus for planning, data analysis and orchestration
(authoring the plan with me, writing prompts for the agents, the README); four Sonnet subagents for building and
reviewing code; me for every decision and every PR review and merge on GitHub. No other AI tools.

**Agent-context artifacts** (committed): `CLAUDE.md` and the four agent definitions in `.claude/agents/`
(`api-builder`, `api-reviewer`, `frontend-builder`, `frontend-reviewer`).

## How the work went

1. **A first plan, written by hand** (`PLAN_first_iteration.md`). Before involving the model I wrote down the
   data checks I wanted, the stack (FastAPI, React), a first API shape, the test cases (an account with no events,
   a normal week, a lower week, locations that need review), the assumptions, and the "no LLM" position. The
   points I hadn't decided were marked with `*`.

2. **The model as a challenger** (`plan:129`). I asked it not to write the plan or any code yet, and to take
   the `*` points one at a time, each with options to pick from and a way to push back. When its options weren't
   enough, I asked for the pros and cons (`plan:176`). Every decision went into `PLAN_first_iteration.md` as
   "DECIDED", with its reason, so that file is the decision log.

3. **Evidence from the data**, delegated to subagents so the main session kept its context:
   - Postgres in Docker Compose, the starter schema as an Alembic migration, and the seed loaded as-is
     (`plan:522`).
   - `Data_integrity.md`: 26 checks on the seed (duplicates, NULLs, timezones, spikes, weekends, volume per
     location), each with its query and result. I also connected to the database with pgAdmin to check the data
     myself (`plan:671`), and turned what I found into questions for product, with working assumptions (`OPEN_QUESTIONS.md`, `plan:707`).
   - `Detection_tuning.md`: a grid over the detection parameters on the seed, compared with pure random data, to
     pick values that flag real changes and not noise (`plan:1228`, results at `plan:1335`).

   The decisions I had held back were then taken with this evidence: the cleaning policy, Mon–Sun weeks, the
   detection method and its parameters.

4. **`PLAN.md`** (`plan:1447`, `plan:1804`). The model turned the decisions into 15 tasks (0–14), each with a
   goal, a scope, tests and a quickstart that an agent runs to check its own work. Because the agents run on
   Sonnet, the plan fixes everything an agent could otherwise redesign: file layout, function signatures, API
   models, the SQL, library versions, and the expected value for each test scenario. It also sets the workflow
   rules: one branch per task, PRs under 700 lines, stacked PRs when a task doesn't fit.

5. **Audit against the challenge prompt, then freeze** (`plan:3823`). I pasted the take-home prompt and asked
   what the plan missed. The audit found 7 gaps, including a hard requirement the plan broke (state that survives
   a reload). After fixing them, `PLAN.md` was frozen: every later change goes to `PLAN_CHANGES.md`, with the
   reason and the PR.

6. **Execution with four agents** (`impl`). The main Claude Code session acted as orchestrator. For each task:
   - `api-builder` or `frontend-builder` creates the branch, implements the task, writes its tests, runs the
     quickstart, and writes the PR description;
   - `api-reviewer` or `frontend-reviewer` checks the same branch against the plan, re-runs the quickstart,
     causes the error paths for real, and tries small code changes to confirm the tests catch them;
   - the builder fixes the findings on the same branch, and the reviewer checks again;
   - I review and merge the PR on GitHub. The sandbox can't push, so each task leaves a script that I run on the
     host to push the branch and open the PR.

   After each of my reviews, the orchestrator proposed changes to the agent definitions based on what the review
   caught. I applied them in batches, as their own PR (#4).

7. **Result.** 16 merged PRs (Task 8 split into two stacked PRs), 88 backend tests and 46 frontend tests, and a
   one-command `docker compose up`. Task 11 (frontend end-to-end tests) was skipped for time. Tasks 13 (the
   README) and 14 (this log) were written by the orchestrator with me, not by the agents.

## Decisions and how I directed the model

### Data first, then decisions

I didn't let the model settle anything the data could answer. Decisions that depended on the seed were held open
until the checks had run, and the checks were delegated to subagents so the main session kept its context
(`plan:522`).

- **Cleaning policy.** I fixed where cleaning lives (a SQL view, with timezone logic in Python) and held the
  policy itself until the integrity report existed (`plan:248`). With the evidence, the view removes only the
  12 exact duplicates; everything else is real activity and stays (`plan:963`).
- **Week definition.** I questioned whether weekends belong in the baseline (`plan:309`, `plan:707`). The data
  showed Saturday ≈ Sunday and about one event per location per weekday, so: Mon–Sun weeks, weekly verdicts,
  days as context only (`plan:849`).
- **Detection method.** I chose the median absolute deviation (MAD) for robustness to the spike, and made the
  model state its objections before committing (`plan:1191`). Its concern, small counts, led to both floors.
  Instead of picking k and N by feel, I had a subagent tune them on the seed against a pure-noise baseline
  (`plan:1228`).
- **Tuning result.** I accepted k = 2.5, N = 8, and required the small-account caveat in the plan and the UI
  (`plan:1362`). I kept the "lower only" ranking although the model showed it would usually be empty: a drop is
  what a Monday reader acts on, and I preferred an honest empty list to padding it with noise.

### Product and scope calls

- **Open questions as a product owner would get them** (`plan:707`): accounts with no events, a UTC timezone,
  events before 7 am, the 805-event spike, NULL durations and outcomes, each with a working assumption, recorded
  in `OPEN_QUESTIONS.md`.
- **One metric:** total events. Splitting by type needs volume the seed doesn't have, and the choice belongs to
  product (`plan:373`).
- **"Needs attention" means a drop** (`plan:1262`). The model's options ranked both directions.
- **No LLM in the product** (`plan:4002`). The deterministic answer is complete, and an LLM would be another
  component to build, verify and maintain for no added value. Together with the model's point that the data has
  no causes to explain, this is `PLAN.md` 0.2.
- **Cutting scope when time ran out** (`impl:2978`): I dropped Task 11 (frontend end-to-end tests) and kept the
  one-command run, because a reviewer who can't run the project can't evaluate it.

### Directing the agents

- **The workflow** was mine (`plan:1447`): four agents, builder → reviewer → human review, tasks small enough to
  review, PRs under 700 lines, stacked PRs when a task doesn't fit.
- **No design decisions left to Sonnet** (`plan:1804`): the plan fixes every high-level choice so the agents
  implement and don't redesign. Tests are their own tasks. I set the required scenarios and selected which of the
  model's extra ones to add (`plan:1851`).
- **The plan audited against the prompt before freezing it** (`plan:3823`). This caught a missed hard requirement
  (below). I chose `localStorage` for reload state, and kept the aggregation in Python with a written
  justification (`plan:4002`).
- **Review findings became agent rules, but only after review** (`impl:306`, `impl:853`): six rules, applied on
  their own branch and reviewed as a PR. Task 3 then ran without them in the prompt, to prove the definitions
  work on their own.
- **Holding the line on the plan:** the builder stopped to ask about a library outside the plan, and I kept the
  existing one (`impl:1372`). When a builder added five packages without asking, I accepted only the four that
  are required and dropped the fifth (`impl:2299`).

### Review standards

- **Code a reviewer can read:** config with comments that explain why, and logic modules with a short diagram
  and one example (`impl:182`, `impl:458`).
- **A README written for its reader,** not for us (Task 13).

## Where I corrected or overrode the model

### Planning

- **Asked for trade-offs instead of picking its recommended option** (`plan:163`, `plan:176`).
- **Held back its early recommendations** on cleaning, baseline and detection until the data checks ran
  (`plan:248`, `plan:309`, `plan:373`). The data changed the result: no daily verdicts, and tuned thresholds
  instead of guessed ones.
- **Made it argue against its own method** before committing to MAD (`plan:1191`). That surfaced the small-count
  problem.
- **Required the small-volume warning in the UI** (`plan:1362`).
- **Its first `PLAN.md` left decisions to the builders and had no test tasks** (`plan:1780`). I made the plan fix
  every decision and turned tests into their own tasks (`plan:1804`).
- **It planned to push from a sandbox that can't push** (`plan:3746`). The workflow became local branches plus a
  PR handoff that I run on the host.
- **Audited the plan against the challenge prompt** (`plan:3823`). It had put reload state out of scope, a hard
  requirement; the audit found that and six other gaps.
- **Went against three risks it raised** (`plan:4002`): fewer tasks for the time budget, moving the aggregation to
  SQL, and a weak "no LLM" argument.

### Implementation

- **Sent back config that was too cryptic** (`impl:182`). "Why-comments" became an agent rule.
- **Rejected a docstring example that mixed two scenarios** (`impl:727`).
- **Waited for a second review before changing the agents,** then applied six rules as their own PR
  (`impl:306`, `impl:853`).
- **Kept only the four required packages** a builder had added without asking (`impl:2299`).

### Final review (Task 13)

- **Found the "−69% but Normal" row** in the running dashboard. The model first misread it as a gap in the rule;
  it's the small-count limit, and the fix is to show each location's normal range.
- **Rejected the first README** as too technical, and corrected its account of how the work was done.

### Caught by the review process

- `/health` returned 500 instead of 503 with the database down (Task 1).
- Mutation checks found untested rules in almost every task.
- Two wrong numbers in the orchestrator's prompts, caught by the agents (Tasks 4 and 9).
