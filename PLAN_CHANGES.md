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

## 2. Frontend dependencies beyond the 3.1 list, and TypeScript pinned to 5.9.3 (Task 8a)

- **Plan (section 3.1):** the frontend uses only the listed libraries.
- **Change:** four packages are added as required companions of listed libraries (the human approved them):
  - `@types/react-dom`: `tsc` fails without it (no types for `react-dom/client`).
  - `@types/react`: required peer of `@testing-library/react` and `@types/react-dom`.
  - `@testing-library/dom`: required peer of `@testing-library/react` and `@testing-library/user-event`.
  - `@eslint/js`: provides `js.configs.recommended` for the flat ESLint config.
  - `globals` was tried and dropped: lint is clean without it.
- **TypeScript is pinned to 5.9.3**, not the latest (7.0.2): `openapi-typescript@7.13.0` peers `typescript ^5`
  and `typescript-eslint@8.72.1` peers `typescript <6.1.0`, so 5.9.3 is the newest version both accept.
- **PR:** Task 8a (`task/8a-frontend-scaffold`).
