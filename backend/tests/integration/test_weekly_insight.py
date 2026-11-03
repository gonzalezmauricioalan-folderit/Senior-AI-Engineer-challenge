"""Weekly-insight scenarios S2, V4, V5 and the error paths added in Task 4 (PLAN.md section 4)."""

from datetime import date, datetime
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import Connection

from app.config import Settings
from app.main import create_app
from tests.factories import add_account, add_event, add_weekly, weeks_before

TZ = "America/Chicago"
WEEK = date(2026, 7, 20)
HISTORY = [20, 22, 18, 21, 19, 20, 23, 17]


def _s2(conn: Connection, account_id: int = 102) -> None:
    add_account(conn, account_id)
    add_weekly(conn, account_id, "Main", TZ, {**weeks_before(WEEK, HISTORY), WEEK: 21})


def test_s2_normal_week_with_band(client: TestClient, conn: Connection) -> None:
    _s2(conn)
    r = client.get("/accounts/102/weekly-insight", params={"week_start": "2026-07-20"})
    assert r.status_code == 200
    body = r.json()
    assert body["summary"] == {
        "total": 21,
        "usual": 20.0,
        "lower": 8.8,
        "upper": 31.2,
        "pct_vs_usual": 0.05,
        "status": "normal",
        "low_volume": False,
    }
    assert body["baseline"] == {
        "method": "median_mad",
        "weeks_used": 8,
        "start": "2026-05-25",
        "end": "2026-07-19",
    }
    assert [loc["location"] for loc in body["locations"]] == ["Main"]
    assert len(body["days"]) == 7 and body["days"][0]["total"] == 21
    assert body["data_notes"] == []


def test_v4_unknown_account_is_404(client: TestClient) -> None:
    r = client.get("/accounts/999/weekly-insight")
    assert r.status_code == 404
    assert r.json() == {"detail": "Account 999 not found"}


def test_v5_default_week_is_latest_complete(client: TestClient, conn: Connection) -> None:
    _s2(conn)
    body = client.get("/accounts/102/weekly-insight").json()
    assert body["week"] == {"start": "2026-07-20", "end": "2026-07-26"}


def test_week_start_validation_messages(client: TestClient, conn: Connection) -> None:
    _s2(conn)
    url = "/accounts/102/weekly-insight"
    r = client.get(url, params={"week_start": "2026-07-21"})
    assert (r.status_code, r.json()["detail"]) == (422, "week_start must be a Monday")
    r = client.get(url, params={"week_start": "2026-07-27"})
    assert r.json()["detail"] == "week_start is not complete yet; the latest complete week is 2026-07-20"
    r = client.get(url, params={"week_start": "2026-05-18"})
    assert (r.status_code, r.json()["detail"]) == (
        422,
        "week_start is before the first complete week (2026-05-25)",
    )
    assert client.get(url, params={"week_start": "nope"}).status_code == 422


def test_account_without_events_returns_empty_shape(client: TestClient, conn: Connection) -> None:
    _s2(conn)
    add_account(conn, 101, name="Empty Co")
    body = client.get("/accounts/101/weekly-insight").json()
    assert body["summary"]["status"] == "not_enough_history" and body["summary"]["total"] == 0
    assert body["locations"] == [] and body["baseline"]["weeks_used"] == 0
    assert [d["total"] for d in body["days"]] == [0] * 7 and {d["usual"] for d in body["days"]} == {None}


def test_empty_dataset_without_as_of_is_422(tmp_path: Path, engine, conn: Connection, db_url: str) -> None:
    add_account(conn, 101)
    settings = Settings(database_url=db_url, as_of_date=None, cors_origins=[])
    with TestClient(create_app(settings)) as c:
        r = c.get("/accounts/101/weekly-insight")
    assert (r.status_code, r.json()["detail"]) == (422, "no activity data available")


def test_unreachable_db_is_500(tmp_path: Path) -> None:
    settings = Settings(database_url=f"sqlite:///{tmp_path}/missing/x.db", as_of_date=None, cors_origins=[])
    with TestClient(create_app(settings), raise_server_exceptions=False) as c:
        assert c.get("/accounts/1/weekly-insight").status_code == 500


def test_duplicate_and_utc_notes(client: TestClient, conn: Connection) -> None:
    add_account(conn, 110, tz="UTC")
    add_weekly(conn, 110, "Main", "UTC", {**weeks_before(WEEK, [20] * 8), WEEK: 20})
    add_event(conn, 110, "Main", datetime(2026, 7, 20, 12, 0), "UTC")  # same minute as an existing event
    body = client.get("/accounts/110/weekly-insight").json()
    assert body["summary"]["total"] == 20
    assert body["data_notes"][0] == "1 duplicate event removed from this week."
    assert body["data_notes"][1].startswith("This account's timezone is set to UTC")


def test_rounding_is_one_decimal_for_band_and_three_for_pct(client: TestClient, conn: Connection) -> None:
    add_account(conn, 120)
    add_weekly(conn, 120, "Main", TZ, {**weeks_before(WEEK, [20, 21, 22, 23, 24, 25, 26, 27]), WEEK: 30})
    s = client.get("/accounts/120/weekly-insight").json()["summary"]
    # usual 23.5, spread = sqrt(23.5) = 4.8477 -> band 11.3807..35.6193; pct = 6.5 / 23.5 = 0.27659
    assert (s["usual"], s["lower"], s["upper"], s["pct_vs_usual"]) == (23.5, 11.4, 35.6, 0.277)


def test_first_complete_week_itself_is_accepted(client: TestClient, conn: Connection) -> None:
    _s2(conn)  # dataset min is Mon 2026-05-25, the first complete week
    r = client.get("/accounts/102/weekly-insight", params={"week_start": "2026-05-25"})
    assert r.status_code == 200
    assert r.json()["summary"]["status"] == "not_enough_history"


def test_duplicate_note_counts_by_local_date_of_the_selected_week(
    client: TestClient, conn: Connection
) -> None:
    add_account(conn, 130)
    add_weekly(conn, 130, "Main", TZ, {**weeks_before(WEEK, [20] * 8), WEEK: 20})
    # Local Sun 23:30 is already Monday in UTC. Each time is inserted twice (1 duplicate each).
    # Two pairs in the selected week and one in the previous week, so every mis-bucketing changes the count.
    for local in (
        datetime(2026, 7, 26, 23, 30),
        datetime(2026, 7, 26, 23, 45),
        datetime(2026, 7, 19, 23, 30),
    ):
        add_event(conn, 130, "Main", local, TZ)
        add_event(conn, 130, "Main", local, TZ)
    body = client.get("/accounts/130/weekly-insight").json()
    # Only the two 07-26 pairs belong to week 07-20; the 07-19 pair is the previous week's.
    assert body["data_notes"] == ["2 duplicate events removed from this week."]
    assert body["days"][6]["total"] == 2


def test_weekday_usuals_are_null_without_enough_history(client: TestClient, conn: Connection) -> None:
    add_account(conn, 140)
    add_weekly(conn, 140, "Main", TZ, {**weeks_before(WEEK, [20] * 3), WEEK: 20})
    body = client.get("/accounts/140/weekly-insight").json()
    assert body["summary"]["status"] == "not_enough_history"
    assert [d["usual"] for d in body["days"]] == [None] * 7


def test_first_complete_week_uses_the_accounts_local_date(client: TestClient, conn: Connection) -> None:
    # Tokyo local Tue 2026-07-07 00:30 is Mon 07-06 15:30 UTC. The local date is a Tuesday -> first complete
    # week 07-13; the UTC date (a Monday) would wrongly make 07-06 the first complete week.
    add_account(conn, 150, tz="Asia/Tokyo")
    add_event(conn, 150, "Main", datetime(2026, 7, 7, 0, 30), "Asia/Tokyo")
    url = "/accounts/150/weekly-insight"
    r = client.get(url, params={"week_start": "2026-07-06"})
    assert r.json()["detail"] == "week_start is before the first complete week (2026-07-13)"
    assert client.get(url, params={"week_start": "2026-07-13"}).status_code == 200
