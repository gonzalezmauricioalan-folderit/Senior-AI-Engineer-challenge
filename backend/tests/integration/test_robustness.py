"""Robustness and data quirks R1-R7 (PLAN.md section 4), through the API on SQLite with fake accounts.

Plus one extra test (not a scenario id) that pins the MAD computation to the full 8-week history.
"""

from datetime import date, datetime

from fastapi.testclient import TestClient
from sqlalchemy import Connection

from tests.factories import add_account, add_event, add_weekly, weeks_before

TZ = "America/Chicago"
WEEK = date(2026, 7, 20)
UTC_NOTE = (
    "This account's timezone is set to UTC, which may be a misconfiguration; days and weeks may be shifted."
)


def _get(client: TestClient, account_id: int, week: str = "2026-07-20") -> dict:
    r = client.get(f"/accounts/{account_id}/weekly-insight", params={"week_start": week})
    assert r.status_code == 200
    return r.json()


def _series(conn: Connection, account_id: int, history: list[int], value: int, tz: str = TZ) -> None:
    add_account(conn, account_id, tz=tz)
    add_weekly(conn, account_id, "Main", tz, {**weeks_before(WEEK, history), WEEK: value})


def test_r1_history_spike_does_not_inflate_the_band(client: TestClient, conn: Connection) -> None:
    history = [20, 20, 20, 300, 20, 20, 20, 20]
    _series(conn, 121, history, 20)
    _series(conn, 122, history, 5)

    normal = _get(client, 121)["summary"]
    assert normal["status"] == "normal"
    assert (normal["total"], normal["usual"], normal["lower"], normal["upper"]) == (20, 20.0, 8.8, 31.2)

    lower = _get(client, 122)["summary"]
    assert lower["status"] == "lower_than_usual"
    assert (lower["total"], lower["usual"], lower["pct_vs_usual"]) == (5, 20.0, -0.75)


def test_r2_exact_duplicate_is_removed_and_noted(client: TestClient, conn: Connection) -> None:
    _series(conn, 123, [20] * 8, 20)
    # Same account, location, type and timestamp as the first event add_weekly placed (Monday 12:00).
    add_event(conn, 123, "Main", datetime(2026, 7, 20, 12, 0), TZ)

    body = _get(client, 123)
    assert body["summary"]["total"] == 20
    assert body["data_notes"] == ["1 duplicate event removed from this week."]


def test_r3_new_location_without_history_ranks_last(client: TestClient, conn: Connection) -> None:
    add_account(conn, 124)
    add_weekly(conn, 124, "Old", TZ, {**weeks_before(WEEK, [20] * 8), WEEK: 20})
    add_weekly(conn, 124, "New", TZ, {**weeks_before(WEEK, [5, 5]), WEEK: 5})

    body = _get(client, 124)
    assert body["summary"]["status"] != "not_enough_history"
    assert [loc["location"] for loc in body["locations"]] == ["Old", "New"]
    new = body["locations"][-1]
    assert new["status"] == "not_enough_history"
    assert new["history_weeks"] == 2
    assert body["locations"][0]["status"] == "normal"


def test_r4_week_boundary_uses_local_time(client: TestClient, conn: Connection) -> None:
    add_account(conn, 125)
    for local in (
        datetime(2026, 7, 13, 12, 0),  # anchor: sets the first complete week
        datetime(2026, 7, 19, 23, 59),  # Sunday night local, already Monday in UTC
        datetime(2026, 7, 20, 0, 30),  # Monday just after local midnight
        datetime(2026, 7, 26, 23, 30),  # Sunday night local (= Monday UTC)
    ):
        add_event(conn, 125, "Main", local, TZ)

    body = _get(client, 125)
    assert body["summary"]["total"] == 2
    assert body["days"][0]["total"] == 1
    assert body["days"][6]["total"] == 1

    # The 07-19 event belongs to the previous week (with the anchor on Monday).
    prev = _get(client, 125, "2026-07-13")
    assert prev["summary"]["total"] == 2
    assert prev["days"][0]["total"] == 1
    assert prev["days"][6]["total"] == 1


def test_r5_dst_week_keeps_both_ends(client: TestClient, conn: Connection) -> None:
    add_account(conn, 126)
    add_event(conn, 126, "Main", datetime(2026, 3, 2, 12, 0), TZ)
    add_event(conn, 126, "Main", datetime(2026, 3, 8, 23, 30), TZ)  # DST starts that day

    body = _get(client, 126, "2026-03-02")
    assert body["summary"]["total"] == 2
    assert body["days"][0]["total"] == 1
    assert body["days"][6]["total"] == 1


def test_r6_phoenix_has_no_dst(client: TestClient, conn: Connection) -> None:
    tz = "America/Phoenix"
    add_account(conn, 127, tz=tz)
    add_event(conn, 127, "Main", datetime(2026, 7, 20, 12, 0), tz)
    add_event(conn, 127, "Main", datetime(2026, 7, 26, 23, 30), tz)

    body = _get(client, 127)
    assert body["summary"]["total"] == 2
    assert body["days"][0]["total"] == 1
    assert body["days"][6]["total"] == 1


def test_r7_utc_note_only_for_utc_accounts(client: TestClient, conn: Connection) -> None:
    _series(conn, 128, [20] * 8, 20, tz="UTC")
    _series(conn, 129, [20] * 8, 20, tz=TZ)

    assert UTC_NOTE in _get(client, 128)["data_notes"]
    assert UTC_NOTE not in _get(client, 129)["data_notes"]


def test_extra_oldest_history_week_counts_in_the_mad(client: TestClient, conn: Connection) -> None:
    """Not a scenario id: kills the mutant that drops the oldest week from the MAD only.

    History (oldest first) 100 110 130 70 100 130 70 100: usual 100, deviations 0 10 30 30 0 30 30 0.
    All 8: sorted deviations 0 0 0 10 30 30 30 30 -> MAD 20, spread 29.65, band 25.9 - 174.1, so 200 is
    higher_than_usual. Without the oldest week (deviation 0) MAD would be 30 and the band would reach 211.2:
    200 would pass as normal.
    """
    _series(conn, 130, [100, 110, 130, 70, 100, 130, 70, 100], 200)
    s = _get(client, 130)["summary"]
    assert (s["usual"], s["lower"], s["upper"]) == (100.0, 25.9, 174.1)
    assert s["status"] == "higher_than_usual"
