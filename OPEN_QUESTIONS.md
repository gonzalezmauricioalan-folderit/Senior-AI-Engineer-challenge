# Open questions & assumptions

Questions that, on a real ticket, would go to product / data owners before building. For the challenge, each has a working assumption so work can proceed. Evidence is in `Data_integrity.md`.

| # | Question | Assumption for the challenge | Impact on the solution |
|---|---|---|---|
| 1 | Why are there accounts with no events (#20 Quiet Harbor Spa)? | The account hasn't been onboarded yet. | Show "not enough history yet" instead of a verdict. |
| 2 | Why does Capital City Storage (#18) have `UTC` as its timezone? | Probably a misconfiguration; the real local timezone is unknown. | Use the stored timezone as-is (we can't guess the right one); flag it as a data-quality note. Its local weeks/days may be shifted. |
| 3 | Why do some events happen before 07:00 local time (~20% overall)? | Some automated process creates a few events. | Don't filter by business hours; count all events. |
| 4 | Why the spike on Wed 2026-06-03 for Metro Collision Centers (#6): 805 events across all 15 sites vs ~13 on a normal day? | A marketing campaign. | Keep the data. It's a real "not normal" week the customer should see; use a robust (median-based) baseline so it doesn't distort later weeks. Annotating campaigns/holidays is out of scope (see plan). |
| 5 | Why do some calls (313) have a NULL `duration_seconds`? | *Proposed:* the duration wasn't captured (e.g. missed calls or a telephony integration gap). | Doesn't affect the metric (total event count); calls still count. |
| 6 | Why is `outcome` nullable (398 rows, ~3% of each event type)? | *Proposed:* the outcome isn't known yet or wasn't recorded (e.g. a lead still being worked). | Doesn't affect the metric (total event count); rows still count. |
| 7 | Why does Sierra Pest Solutions (#15, Phoenix) jump +94% in the same week as account 6's spike (week of 2026-06-01)? | The same kind of campaign as #4. | Kept as-is; flagged higher like account 6. If it's a data issue (e.g. a bulk import affecting several accounts), the cleaning view would need a rule. |

## Process note (for the write-up)

Claude Code runs in **bypass-permissions mode** inside a **Docker sandbox**. The sandbox restricts the damage the agent can do and isolates each instance, so the focus stays on high-level decisions (planning, spec interpretation, reviewing agent output) instead of approving every command manually.
