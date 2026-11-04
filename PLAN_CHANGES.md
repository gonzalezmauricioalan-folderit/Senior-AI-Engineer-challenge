# PLAN_CHANGES.md

Changes to `PLAN.md` after Task 1 started. `PLAN.md` itself stays frozen; each entry says what changed,
why, and which PR introduced it.

## 1. V7 is tested with an unreachable database, not a dependency override (Task 7)

- **Plan (section 4, V7):** `/health` with a broken DB, "dependency override that raises" -> 503
  `{"status":"error","db":"error"}`.
- **Change:** V7 points the app at a SQLite file in a nonexistent directory and asserts the same 503 and body.
- **Why:** since the Task 1 fix, `/health` opens its connection from `request.app.state.engine` inside its
  own `try` instead of through the `get_connection` dependency, so overriding the dependency would test
  nothing. The real failure is what the test must cause.
- **PR:** Task 7 (`task/7-scenario-tests-robustness`).
