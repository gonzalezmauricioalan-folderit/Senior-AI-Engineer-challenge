"""Order locations so the ones needing attention come first (PLAN.md section 2: Ranking of locations).

How rank_locations() orders them, as three groups that are never mixed:

    input (any order)
          │
          ├── status LOWER ───────────────▶ 1. NEEDS ATTENTION   sort: pct ascending (biggest drop
          │                                                       first), ties by name
          ├── status HIGHER or NORMAL ────▶ 2. FINE              sort: by name only (higher is not
          │                                                       a problem, so no status priority)
          └── status NOT_ENOUGH ──────────▶ 3. NO VERDICT YET    sort: by name
          │
          ▼
    output = group 1 + group 2 + group 3

Example (scenario S4: four locations, each with a usual of ~20).

    input                                   output
    ─────────────────────────────           ─────────────────────────────────────────
    North   20 vs ~20   NORMAL               1. East    4 vs ~20  −80%  LOWER    ┐ needs
    South    8 vs ~20   LOWER  −60%          2. South   8 vs ~20  −60%  LOWER    ┘ attention
    East     4 vs ~20   LOWER  −80%          3. North  20 vs ~20   0%   NORMAL   ┐ fine, A→Z
    West    35 vs ~20   HIGHER +75%          4. West   35 vs ~20  +75%  HIGHER   ┘

    Ties: two LOWER locations at −50% keep name order ("Site B" before "Site D").

Note: the account total (67 vs ~80, lower bound 57.6) is within its band, so the summary says NORMAL
even though two locations dropped. The ranking is what surfaces them.
"""

from collections.abc import Sequence

from app.domain.detection import Evaluation, Status


def rank_locations(items: Sequence[tuple[str, Evaluation]]) -> list[tuple[str, Evaluation]]:
    """Three groups, in this order:

    1. lower_than_usual, biggest drop first (most negative pct), ties by name. Only "lower" counts as
       needing attention, so it leads.
    2. higher_than_usual and normal together, by name: neither is a problem, so no status priority.
    3. not_enough_history, by name: no verdict yet, shown last.
    """
    lower = [it for it in items if it[1].status is Status.LOWER]
    middle = [it for it in items if it[1].status in (Status.HIGHER, Status.NORMAL)]
    unknown = [it for it in items if it[1].status is Status.NOT_ENOUGH]
    # LOWER implies usual > 0, so pct is never None here; `or 0.0` only satisfies the type checker.
    lower.sort(key=lambda it: (it[1].pct_vs_usual or 0.0, it[0]))
    middle.sort(key=lambda it: it[0])
    unknown.sort(key=lambda it: it[0])
    return lower + middle + unknown
