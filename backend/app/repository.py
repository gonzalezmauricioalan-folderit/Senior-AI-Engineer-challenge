"""SQL only (PLAN.md 3.3). Every function takes a Connection.

All reads go through the `clean_activity_events` view, except `duplicate_timestamps`, which needs the
raw table. No timezone logic here: timestamps are naive UTC and the service converts them in Python.
"""

import datetime as dt
from typing import Any

from sqlalchemy import Connection, text


def ping(conn: Connection) -> None:
    conn.execute(text("SELECT 1"))


def _to_datetime(value: Any) -> dt.datetime:
    # SQLite hands timestamps back as strings, Postgres as datetimes (PLAN.md 3.2).
    return dt.datetime.fromisoformat(value) if isinstance(value, str) else value


def list_accounts(conn: Connection) -> list[dict[str, Any]]:
    # LEFT JOIN so an account without events still appears, with location_count 0.
    rows = conn.execute(
        text(
            "SELECT a.id, a.name, a.industry, a.timezone, COUNT(DISTINCT c.location) AS location_count "
            "FROM accounts a LEFT JOIN clean_activity_events c ON c.account_id = a.id "
            "GROUP BY a.id, a.name, a.industry, a.timezone ORDER BY a.name"
        )
    )
    return [dict(r._mapping) for r in rows]


def get_account(conn: Connection, account_id: int) -> dict[str, Any] | None:
    row = conn.execute(
        text("SELECT id, name, industry, timezone FROM accounts WHERE id = :id"), {"id": account_id}
    ).first()
    return dict(row._mapping) if row else None


def dataset_bounds(conn: Connection) -> tuple[dt.datetime, dt.datetime] | None:
    """Min and max `occurred_at` of the whole clean view; None when it is empty."""
    lo, hi = conn.execute(text("SELECT MIN(occurred_at), MAX(occurred_at) FROM clean_activity_events")).one()
    if lo is None or hi is None:
        return None
    return _to_datetime(lo), _to_datetime(hi)


def account_events(conn: Connection, account_id: int) -> list[tuple[str, dt.datetime]]:
    rows = conn.execute(
        text("SELECT location, occurred_at FROM clean_activity_events WHERE account_id = :id"),
        {"id": account_id},
    )
    return [(r[0], _to_datetime(r[1])) for r in rows]


def duplicate_timestamps(conn: Connection, account_id: int) -> list[dt.datetime]:
    """`occurred_at` of raw rows that the clean view dropped."""
    rows = conn.execute(
        text(
            "SELECT occurred_at FROM activity_events WHERE account_id = :id "
            "AND id NOT IN (SELECT id FROM clean_activity_events)"
        ),
        {"id": account_id},
    )
    return [_to_datetime(r[0]) for r in rows]
