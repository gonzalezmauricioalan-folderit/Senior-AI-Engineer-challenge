from datetime import date, datetime

from sqlalchemy import Connection, text

from tests.factories import add_account, add_event, add_weekly, weeks_before

TZ = "America/Chicago"
T = datetime(2026, 7, 1, 10, 0)


def clean_ids(conn: Connection) -> list[int]:
    return [r[0] for r in conn.execute(text("SELECT id FROM clean_activity_events ORDER BY id"))]


def test_view_keeps_lowest_id_of_identical_rows(conn: Connection) -> None:
    add_account(conn, 101)
    first = add_event(conn, 101, "Site A", T, TZ, outcome="connected", duration=60)
    add_event(conn, 101, "Site A", T, TZ, outcome="connected", duration=60)
    other = add_event(conn, 101, "Site A", T, TZ, outcome="missed", duration=60)
    assert clean_ids(conn) == [first, other]


def test_view_dedupes_identical_rows_with_null_outcome(conn: Connection) -> None:
    add_account(conn, 101)
    first = add_event(conn, 101, "Site A", T, TZ, outcome=None)
    add_event(conn, 101, "Site A", T, TZ, outcome=None)
    other = add_event(conn, 101, "Site B", T, TZ, outcome=None)
    assert clean_ids(conn) == [first, other]


def test_factories_place_events_on_local_weeks(conn: Connection) -> None:
    add_account(conn, 101)
    week = date(2026, 7, 20)
    counts = weeks_before(week, [2, 3])
    assert counts == {date(2026, 7, 6): 2, date(2026, 7, 13): 3}
    add_weekly(conn, 101, "Site A", TZ, counts)
    rows = conn.execute(text("SELECT occurred_at FROM clean_activity_events ORDER BY occurred_at")).all()
    assert len(rows) == 5
    # Mon 12:00 America/Chicago (CDT, UTC-5) == 17:00 UTC
    assert str(rows[0][0]).startswith("2026-07-06 17:00:00")
