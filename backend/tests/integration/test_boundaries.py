"""Boundaries and math edges B1-B8 (PLAN.md section 4), through the API on SQLite."""

from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import Connection

from tests.factories import add_account, add_weekly, weeks_before

TZ = "America/Chicago"
WEEK = date(2026, 7, 20)


def _setup(conn: Connection, account_id: int, history: list[int], value: int) -> None:
    add_account(conn, account_id)
    add_weekly(conn, account_id, "Main", TZ, {**weeks_before(WEEK, history), WEEK: value})


def _summary_and_loc(client: TestClient, account_id: int) -> tuple[dict, dict, dict]:
    r = client.get(f"/accounts/{account_id}/weekly-insight", params={"week_start": "2026-07-20"})
    assert r.status_code == 200
    body = r.json()
    assert len(body["locations"]) == 1
    # Single location: its verdict must match the account's
    assert {k: v for k, v in body["locations"][0].items() if k in body["summary"]} == body["summary"]
    return body["summary"], body["locations"][0], body["baseline"]


def _isolated_zero_history(conn: Connection, account_id: int, value: int) -> None:
    """1 event 9 weeks before, then 8 zero weeks, then `value` in the evaluated week."""
    add_account(conn, account_id)
    add_weekly(conn, account_id, "Main", TZ, {WEEK - timedelta(weeks=9): 1, WEEK: value})


def test_b1_three_weeks_is_not_enough_history(client: TestClient, conn: Connection) -> None:
    _setup(conn, 111, [20, 20, 20], 5)
    s, loc, b = _summary_and_loc(client, 111)
    assert s["status"] == "not_enough_history"
    assert (s["usual"], s["lower"], s["upper"], s["pct_vs_usual"]) == (None, None, None, None)
    assert s["low_volume"] is False
    assert loc["history_weeks"] == 3
    assert b["weeks_used"] == 3


def test_b2_five_weeks_is_enough(client: TestClient, conn: Connection) -> None:
    _setup(conn, 112, [20] * 5, 5)
    s, loc, b = _summary_and_loc(client, 112)
    assert s["status"] == "lower_than_usual"
    assert (s["total"], s["usual"], s["lower"], s["upper"], s["pct_vs_usual"]) == (5, 20.0, 8.8, 31.2, -0.75)
    assert loc["history_weeks"] == 5
    assert b["weeks_used"] == 5


def test_b3_zero_usual_three_events_is_higher(client: TestClient, conn: Connection) -> None:
    _isolated_zero_history(conn, 113, 3)
    s, loc, b = _summary_and_loc(client, 113)
    assert s["status"] == "higher_than_usual"
    assert (s["total"], s["usual"], s["lower"], s["upper"]) == (3, 0.0, 0.0, 0.0)
    assert s["pct_vs_usual"] is None
    assert s["low_volume"] is True
    assert b["weeks_used"] == 8 and loc["history_weeks"] == 8


def test_b4_zero_usual_two_events_is_normal(client: TestClient, conn: Connection) -> None:
    _isolated_zero_history(conn, 114, 2)
    s, _, b = _summary_and_loc(client, 114)
    assert s["status"] == "normal"
    assert (s["total"], s["usual"], s["lower"], s["upper"]) == (2, 0.0, 0.0, 0.0)
    assert s["pct_vs_usual"] is None
    assert s["low_volume"] is True
    assert b["weeks_used"] == 8


def test_b5_zero_events_low_volume_is_normal(client: TestClient, conn: Connection) -> None:
    # An older week keeps the series going; the evaluated week has no events at all.
    _setup(conn, 115, [5] * 8, 0)
    s, _, _ = _summary_and_loc(client, 115)
    assert s["status"] == "normal"
    assert (s["total"], s["usual"], s["lower"]) == (0, 5.0, 0.0)
    assert s["upper"] == 10.6
    assert s["pct_vs_usual"] == -1.0
    assert s["low_volume"] is True


def test_b6_above_upper_but_under_pct_is_normal(client: TestClient, conn: Connection) -> None:
    _setup(conn, 116, [200] * 8, 236)
    s, _, _ = _summary_and_loc(client, 116)
    assert s["status"] == "normal"
    assert (s["total"], s["usual"], s["lower"], s["upper"]) == (236, 200.0, 164.6, 235.4)
    assert s["pct_vs_usual"] == 0.18
    assert s["low_volume"] is False


def test_b7_above_upper_and_pct_is_higher(client: TestClient, conn: Connection) -> None:
    _setup(conn, 117, [200] * 8, 241)
    s, _, _ = _summary_and_loc(client, 117)
    assert s["status"] == "higher_than_usual"
    assert (s["total"], s["usual"], s["lower"], s["upper"]) == (241, 200.0, 164.6, 235.4)
    assert s["pct_vs_usual"] == 0.205
    assert s["low_volume"] is False


def test_b8_small_diff_below_min_abs_is_normal(client: TestClient, conn: Connection) -> None:
    _setup(conn, 118, [1, 1, 1, 1, 0, 0, 0, 0], 3)
    s, _, b = _summary_and_loc(client, 118)
    assert s["status"] == "normal"
    assert (s["total"], s["usual"], s["lower"], s["upper"]) == (3, 0.5, 0.0, 2.4)
    assert s["pct_vs_usual"] == 5.0
    assert s["low_volume"] is True
    assert b["weeks_used"] == 8


# Extra edge cases beyond the B1-B8 rows: they pin the exact comparison operators and constants
# (MIN_HISTORY, LOW_VOLUME_USUAL, strict "> upper", inclusive MIN_PCT) found by the mutation check.
def test_b2b_four_weeks_is_the_minimum_history(client: TestClient, conn: Connection) -> None:
    _setup(conn, 119, [20] * 4, 5)
    s, loc, b = _summary_and_loc(client, 119)
    assert s["status"] == "lower_than_usual"
    assert (loc["history_weeks"], b["weeks_used"]) == (4, 4)


def test_b6b_value_equal_to_upper_is_normal(client: TestClient, conn: Connection) -> None:
    # usual 100 -> upper = 100 + 2.5 * 10 = 125 exactly; "above upper" is strict.
    _setup(conn, 120, [100] * 8, 125)
    s, _, _ = _summary_and_loc(client, 120)
    assert (s["upper"], s["pct_vs_usual"], s["status"]) == (125.0, 0.25, "normal")


def test_b7b_pct_exactly_at_min_pct_is_flagged(client: TestClient, conn: Connection) -> None:
    # 240 vs 200 is exactly +20%: the MIN_PCT guard is inclusive (>=).
    _setup(conn, 121, [200] * 8, 240)
    s, _, _ = _summary_and_loc(client, 121)
    assert (s["pct_vs_usual"], s["status"]) == (0.2, "higher_than_usual")


def test_b5b_low_volume_threshold_is_inclusive(client: TestClient, conn: Connection) -> None:
    _setup(conn, 122, [6] * 8, 6)
    _setup(conn, 123, [7] * 8, 7)
    assert _summary_and_loc(client, 122)[0]["low_volume"] is True
    assert _summary_and_loc(client, 123)[0]["low_volume"] is False


def test_b1b_not_enough_history_has_no_daily_usual(client: TestClient, conn: Connection) -> None:
    _setup(conn, 124, [20, 20, 20], 5)
    days = client.get("/accounts/124/weekly-insight").json()["days"]
    assert [d["usual"] for d in days] == [None] * 7
    assert days[0]["total"] == 5
