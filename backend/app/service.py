"""Orchestration: repository rows -> domain -> API models (rounding and errors live here)."""

import datetime as dt
from zoneinfo import ZoneInfo

from sqlalchemy import Connection

from app import repository
from app.config import Settings
from app.domain import weeks
from app.schemas import AccountSummary


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
