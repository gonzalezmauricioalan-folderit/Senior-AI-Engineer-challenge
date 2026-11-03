"""Data builders for tests. Ids come from a module-level counter."""

import itertools
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import sqlalchemy as sa
from sqlalchemy import Connection, text

_ids = itertools.count(1_000_000)


def add_account(
    conn: Connection, id: int, name: str = "Test Co", tz: str = "America/Chicago", industry: str = "Test"
) -> None:
    conn.execute(
        text(
            "INSERT INTO accounts (id, name, industry, timezone, created_at) "
            "VALUES (:id, :name, :industry, :tz, :created)"
        ).bindparams(sa.bindparam("created", type_=sa.DateTime)),
        {"id": id, "name": name, "industry": industry, "tz": tz, "created": datetime(2026, 1, 1)},
    )


def add_event(
    conn: Connection,
    account_id: int,
    location: str,
    local_dt: datetime,
    tz: str,
    event_type: str = "call_received",
    outcome: str | None = None,
    duration: int | None = None,
) -> int:
    event_id = next(_ids)
    utc = local_dt.replace(tzinfo=ZoneInfo(tz)).astimezone(UTC).replace(tzinfo=None)
    conn.execute(
        text(
            "INSERT INTO activity_events "
            "(id, account_id, location, event_type, occurred_at, duration_seconds, outcome) "
            "VALUES (:id, :account_id, :location, :event_type, :occurred_at, :duration, :outcome)"
        ).bindparams(sa.bindparam("occurred_at", type_=sa.DateTime)),
        {
            "id": event_id,
            "account_id": account_id,
            "location": location,
            "event_type": event_type,
            "occurred_at": utc,
            "duration": duration,
            "outcome": outcome,
        },
    )
    return event_id


def add_weekly(conn: Connection, account_id: int, location: str, tz: str, counts: dict[date, int]) -> None:
    """Place `count` events in each local week, on Monday from 12:00 local, one minute apart."""
    for monday, count in counts.items():
        start = datetime(monday.year, monday.month, monday.day, 12, 0)
        for i in range(count):
            add_event(conn, account_id, location, start + timedelta(minutes=i), tz)


def weeks_before(week: date, values: list[int]) -> dict[date, int]:
    """Map `values` to the consecutive weeks ending the week before `week` (oldest first)."""
    n = len(values)
    return {week - timedelta(weeks=n - i): v for i, v in enumerate(values)}
