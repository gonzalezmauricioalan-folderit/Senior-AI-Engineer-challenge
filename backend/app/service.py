"""Orchestration: repository rows -> domain -> API models (rounding and errors live here)."""

import datetime as dt
from collections import defaultdict
from zoneinfo import ZoneInfo

from sqlalchemy import Connection

from app import repository
from app.config import Settings
from app.domain import detection, weeks
from app.domain.detection import Evaluation, Status
from app.domain.ranking import rank_locations
from app.schemas import (
    AccountRef,
    AccountSummary,
    Baseline,
    Day,
    LocationMetric,
    Metric,
    Week,
    WeeklyInsight,
)

WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
UTC_NOTE = (
    "This account's timezone is set to UTC, which may be a misconfiguration; days and weeks may be shifted."
)


class ServiceError(Exception):
    """A client-facing failure; the route turns it into `{"detail": detail}` with `status_code`."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def as_of_local(
    bounds: tuple[dt.datetime, dt.datetime] | None, tz: ZoneInfo, settings: Settings
) -> dt.date | None:
    """PLAN.md section 2 as-of rule: AS_OF_DATE if set, else the local date of the dataset's max event."""
    if settings.as_of_date is not None:
        return settings.as_of_date
    if bounds is None:
        return None
    return weeks.local_date(bounds[1], tz)


def list_accounts(conn: Connection, settings: Settings) -> list[AccountSummary]:
    bounds = repository.dataset_bounds(conn)
    result = []
    for row in repository.list_accounts(conn):
        as_of = as_of_local(bounds, ZoneInfo(row["timezone"]), settings)
        latest = weeks.latest_complete_week(as_of) if as_of is not None else None
        result.append(AccountSummary(**row, latest_complete_week=latest))
    return result


def _round(value: float | None, digits: int) -> float | None:
    return None if value is None else round(value, digits)


def _metric_fields(ev: Evaluation) -> dict[str, object]:
    # Rounding lives here, not in the domain (PLAN.md section 2: Rounding).
    return {
        "total": ev.total,
        "usual": _round(ev.usual, 1),
        "lower": _round(ev.lower, 1),
        "upper": _round(ev.upper, 1),
        "pct_vs_usual": _round(ev.pct_vs_usual, 3),
        "status": ev.status,
        "low_volume": ev.low_volume,
    }


def _history_for(
    timestamps: list[dt.datetime], tz: ZoneInfo, first_week: dt.date | None, week: dt.date
) -> tuple[dict[dt.date, int], list[tuple[dt.date, int]]]:
    """Weekly counts of one series and the zero-filled history of `week` (never including `week`)."""
    counts = weeks.weekly_counts(timestamps, tz)
    # With an empty dataset there is no lower bound, and `counts` is empty anyway.
    start = weeks.series_start(counts, first_week or dt.date.min)
    return counts, weeks.history(counts, start, week, detection.N_WEEKS)


def _evaluate_series(
    timestamps: list[dt.datetime], tz: ZoneInfo, first_week: dt.date | None, week: dt.date
) -> tuple[Evaluation, list[tuple[dt.date, int]]]:
    counts, hist = _history_for(timestamps, tz, first_week, week)
    return detection.evaluate(counts.get(week, 0), [n for _, n in hist]), hist


def build_weekly_insight(
    conn: Connection, settings: Settings, account_id: int, week_start: dt.date | None
) -> WeeklyInsight:
    # 1. Account and dataset bounds.
    account = repository.get_account(conn, account_id)
    if account is None:
        raise ServiceError(404, f"Account {account_id} not found")
    tz = ZoneInfo(account["timezone"])
    bounds = repository.dataset_bounds(conn)

    # 2. As-of and the first complete week (both in the account's timezone, from the dataset-wide min).
    as_of = as_of_local(bounds, tz, settings)
    if as_of is None:
        raise ServiceError(422, "no activity data available")
    latest = weeks.latest_complete_week(as_of)
    first_week = weeks.first_complete_week(weeks.local_date(bounds[0], tz)) if bounds else None

    # 3. Validation, in the order of the messages in PLAN.md 3.5.
    week = latest if week_start is None else week_start
    if week.weekday() != 0:
        raise ServiceError(422, "week_start must be a Monday")
    if first_week is not None and week < first_week:
        raise ServiceError(422, f"week_start is before the first complete week ({first_week})")
    if week > latest:
        raise ServiceError(422, f"week_start is not complete yet; the latest complete week is {latest}")

    # 4. Bucketing: the account's events, in total and per location.
    events = repository.account_events(conn, account_id)
    all_ts = [ts for _, ts in events]
    by_location: dict[str, list[dt.datetime]] = defaultdict(list)
    for location, ts in events:
        by_location[location].append(ts)

    # 5. Evaluate the account and each location.
    summary, hist = _evaluate_series(all_ts, tz, first_week, week)
    ranked = rank_locations(  # 7. ranking
        [(loc, _evaluate_series(ts, tz, first_week, week)[0]) for loc, ts in by_location.items()]
    )

    # 6. Daily context: `usual` only when the summary has a verdict.
    daily = weeks.daily_counts(all_ts, tz)
    usuals = (
        [None] * 7
        if summary.status is Status.NOT_ENOUGH
        else detection.weekday_usuals([w for w, _ in hist], daily)
    )
    days = [
        Day(
            date=week + dt.timedelta(days=i),
            weekday=WEEKDAYS[i],
            total=daily.get(week + dt.timedelta(days=i), 0),
            usual=_round(usuals[i], 1),
        )
        for i in range(7)
    ]

    # 8. Data notes (exact strings and order from PLAN.md section 2).
    week_end = week + dt.timedelta(days=6)
    notes: list[str] = []
    dupes = sum(
        1
        for ts in repository.duplicate_timestamps(conn, account_id)
        if week <= weeks.local_date(ts, tz) <= week_end
    )
    if dupes == 1:
        notes.append("1 duplicate event removed from this week.")
    elif dupes > 1:
        notes.append(f"{dupes} duplicate events removed from this week.")
    if account["timezone"] == "UTC":
        notes.append(UTC_NOTE)

    return WeeklyInsight(
        account=AccountRef(id=account["id"], name=account["name"], timezone=account["timezone"]),
        week=Week(start=week, end=week_end),
        baseline=Baseline(
            method="median_mad",
            weeks_used=len(hist),
            start=hist[0][0] if hist else None,
            end=hist[-1][0] + dt.timedelta(days=6) if hist else None,
        ),
        summary=Metric(**_metric_fields(summary)),
        days=days,
        locations=[
            LocationMetric(**_metric_fields(ev), location=loc, history_weeks=ev.history_weeks)
            for loc, ev in ranked
        ],
        data_notes=notes,
    )
