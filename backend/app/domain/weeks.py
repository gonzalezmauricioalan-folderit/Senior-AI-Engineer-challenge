"""Date and timezone helpers for the weekly insight (PLAN.md section 2: Weeks, As-of, Series, History).

Everything here is pure. UTC -> local conversion happens only in `local_date`, using `zoneinfo`
(never in SQL, PLAN.md section 2 "Weeks"). Weeks are Monday..Sunday in the account's local time,
and a week is identified by its Monday.
"""

from collections import Counter
from collections.abc import Iterable, Mapping
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

WEEK = timedelta(days=7)


def local_date(occurred_at_utc: datetime, tz: ZoneInfo) -> date:
    """Local calendar date of a naive-UTC timestamp (the DB stores UTC without tzinfo)."""
    # Attach UTC explicitly: converting a naive value would silently use the machine's timezone.
    return occurred_at_utc.replace(tzinfo=UTC).astimezone(tz).date()


def monday_of(d: date) -> date:
    return d - timedelta(days=d.weekday())


def first_complete_week(min_local: date) -> date:
    """First fully observed week, given the local date of the dataset's earliest event (section 2).

    If the data starts mid-week, that week is partial and would look artificially low, so we skip it.
    """
    return min_local if min_local.weekday() == 0 else monday_of(min_local) + WEEK


def latest_complete_week(as_of_local: date) -> date:
    """Monday of the last week that is over: the week before the one containing `as_of_local`.

    The as-of week itself is never complete (even on a Sunday it is still in progress).
    """
    return monday_of(as_of_local) - WEEK


def weekly_counts(timestamps_utc: Iterable[datetime], tz: ZoneInfo) -> Counter[date]:
    """Events per week; key = local Monday."""
    return Counter(monday_of(local_date(ts, tz)) for ts in timestamps_utc)


def daily_counts(timestamps_utc: Iterable[datetime], tz: ZoneInfo) -> Counter[date]:
    """Events per local date."""
    return Counter(local_date(ts, tz) for ts in timestamps_utc)


def series_start(counts: Mapping[date, int], first_week: date) -> date | None:
    """First week (>= `first_week`) with at least one event, or None if there is none.

    Weeks before this point are not "zero activity", they are "before the series existed"
    (e.g. a location opened later), so they must not drag the baseline down (section 2: Series).
    """
    starts = [week for week, n in counts.items() if n >= 1 and week >= first_week]
    return min(starts) if starts else None


def history(
    counts: Mapping[date, int], start: date | None, week: date, n_weeks: int
) -> list[tuple[date, int]]:
    """(Monday, count) for up to `n_weeks` weeks before `week`, oldest first, zero-filled.

    The evaluated week is deliberately excluded: if it were part of its own baseline, an extreme
    week would pull the median/band towards itself and hide the anomaly (section 2: History of a week).
    """
    if start is None or start >= week:
        return []
    first = max(start, week - n_weeks * WEEK)
    n = (week - first) // WEEK
    weeks = [first + i * WEEK for i in range(n)]
    # Weeks inside the series with no events count as 0 (a quiet week is data, not a gap).
    return [(w, counts.get(w, 0)) for w in weeks]
