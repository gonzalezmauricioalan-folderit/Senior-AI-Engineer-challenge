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

## 3. Task 11 (frontend scenario pass + live check) skipped (Task 12)

- **Plan (section 5, Task 11):** `src/test/scenarios.test.tsx` with one consolidated full-screen test per F id
  (F1-F13), plus a manual browser check against the real API (account 6 week 2026-06-01, account 20, account 18,
  account 8, and reload restoring the selection).
- **Change:** the human skipped Task 11 for time. Nothing from it is implemented; Task 12 follows Task 10 directly.
- **What still covers each F scenario** (all F1-F13 have a covering test, found by grepping `frontend/src/**/*.test.tsx`):

  | F id | Test file | `describe` / test |
  |---|---|---|
  | F1 (card and chart) | `VerdictChart.test.tsx` | "F1 account without events (card and chart)" |
  | F1 (empty table) | `LocationsTable.test.tsx` | "F1 empty table" |
  | F2 | `VerdictChart.test.tsx` | "F2 normal week" |
  | F3 | `VerdictChart.test.tsx` | "F3 lower and higher weeks" (S3a, S3b) |
  | F4 | `LocationsTable.test.tsx` | "F4 ranked table (S4)" |
  | F5 (account part) | `VerdictChart.test.tsx` | "F5 low volume (account)" |
  | F5 (row part) | `LocationsTable.test.tsx` | "F5 low-volume row" |
  | F6 | `VerdictChart.test.tsx` | "F6 data notes" |
  | F7 | `LocationsTable.test.tsx` | "F7 single location" |
  | F8 | `App.test.tsx` | "F8 week navigation" |
  | F9 | `App.test.tsx` | "F9 errors and loading" |
  | F10 | `LocationsTable.test.tsx` | "F10 not_enough_history row" |
  | F11 | `App.test.tsx` | "F11 reload" |
  | F12 | `App.test.tsx` | "F12 invalid stored selection" (8 stored-value cases) |
  | F13 | `App.test.tsx` | "F13 blocked localStorage" |

- **What is lost:** (1) the single consolidated full-screen test per F id, so no test checks card, chart, notes
  and table together for one scenario; the pieces are tested separately. (2) The manual browser check: the Task 9
  and 10 reviewers only did curl/API-level live checks, so no one has looked at the rendered dashboard in a real
  browser against the seeded API.
- **PR:** Task 12 (`task/12-web-container`).
