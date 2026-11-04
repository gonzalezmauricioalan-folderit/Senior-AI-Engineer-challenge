"""Required scenarios S1-S4 (PLAN.md section 4), run through the API on SQLite with fake accounts."""

from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import Connection

from tests.factories import add_account, add_weekly, weeks_before

TZ = "America/Chicago"
WEEK = date(2026, 7, 20)
HISTORY = [20, 22, 18, 21, 19, 20, 23, 17]


def _get(client: TestClient, account_id: int) -> dict:
    r = client.get(f"/accounts/{account_id}/weekly-insight", params={"week_start": "2026-07-20"})
    assert r.status_code == 200
    return r.json()


def _account_with_week(conn: Connection, account_id: int, week_total: int) -> None:
    add_account(conn, account_id)
    add_weekly(conn, account_id, "Main", TZ, {**weeks_before(WEEK, HISTORY), WEEK: week_total})


def test_s1_account_without_events(client: TestClient, conn: Connection) -> None:
    add_account(conn, 101, name="Empty Co")
    body = _get(client, 101)
    s = body["summary"]
    assert s["status"] == "not_enough_history"
    assert s["total"] == 0
    assert (s["usual"], s["lower"], s["upper"], s["pct_vs_usual"]) == (None, None, None, None)
    assert s["low_volume"] is False
    assert body["locations"] == []
    assert len(body["days"]) == 7
    assert all(d["total"] == 0 and d["usual"] is None for d in body["days"])
    assert body["baseline"]["weeks_used"] == 0


def test_s2_normal_week(client: TestClient, conn: Connection) -> None:
    _account_with_week(conn, 102, 21)
    body = _get(client, 102)
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
    assert body["week"] == {"start": "2026-07-20", "end": "2026-07-26"}
    # All events sit on Monday, so Monday's usual is the median of the history and the rest are 0.
    assert [(d["weekday"], d["total"], d["usual"]) for d in body["days"]] == [
        ("Mon", 21, 20.0),
        *[(wd, 0, 0.0) for wd in ("Tue", "Wed", "Thu", "Fri", "Sat", "Sun")],
    ]


def test_s3a_low_week_is_lower_than_usual(client: TestClient, conn: Connection) -> None:
    _account_with_week(conn, 103, 5)
    s = _get(client, 103)["summary"]
    assert s["status"] == "lower_than_usual"
    assert (s["total"], s["usual"], s["lower"], s["upper"]) == (5, 20.0, 8.8, 31.2)
    assert s["pct_vs_usual"] == -0.75
    assert s["low_volume"] is False


def test_s3b_high_week_is_higher_than_usual(client: TestClient, conn: Connection) -> None:
    _account_with_week(conn, 104, 40)
    s = _get(client, 104)["summary"]
    assert s["status"] == "higher_than_usual"
    assert (s["total"], s["usual"], s["lower"], s["upper"]) == (40, 20.0, 8.8, 31.2)
    assert s["pct_vs_usual"] == 1.0
    assert s["low_volume"] is False


def test_s4_locations_need_review(client: TestClient, conn: Connection) -> None:
    add_account(conn, 105)
    week_values = {"North": 20, "South": 8, "East": 4, "West": 35}
    for loc, value in week_values.items():
        add_weekly(conn, 105, loc, TZ, {**weeks_before(WEEK, [20] * 8), WEEK: value})
    body = _get(client, 105)

    # Account level looks fine: 67 vs usual 80, lower bound 80 - 2.5*sqrt(80) = 57.6
    s = body["summary"]
    assert s["status"] == "normal"
    assert (s["total"], s["usual"], s["lower"]) == (67, 80.0, 57.6)
    assert s["upper"] == 102.4
    assert s["pct_vs_usual"] == -0.163

    # Ranking: lower by biggest drop, then normal/higher by name
    locs = body["locations"]
    assert [(loc["location"], loc["status"]) for loc in locs] == [
        ("East", "lower_than_usual"),
        ("South", "lower_than_usual"),
        ("North", "normal"),
        ("West", "higher_than_usual"),
    ]
    assert [loc["pct_vs_usual"] for loc in locs] == [-0.8, -0.6, 0.0, 0.75]
    assert [loc["total"] for loc in locs] == [4, 8, 20, 35]
    assert all(loc["usual"] == 20.0 and loc["history_weeks"] == 8 for loc in locs)
