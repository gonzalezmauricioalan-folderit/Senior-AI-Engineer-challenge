"""Order locations so the ones needing attention come first (PLAN.md section 2: Ranking of locations)."""

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
