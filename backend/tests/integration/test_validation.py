"""API validation and errors V1-V7 (PLAN.md section 4). V8 (/accounts) lives in test_accounts.py."""

from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import Connection

from app.config import Settings
from app.main import create_app
from tests.factories import add_account, add_weekly, weeks_before

TZ = "America/Chicago"
WEEK = date(2026, 7, 20)


def _s2_account(conn: Connection, account_id: int = 102) -> None:
    add_account(conn, account_id)
    add_weekly(
        conn, account_id, "Main", TZ, {**weeks_before(WEEK, [20, 22, 18, 21, 19, 20, 23, 17]), WEEK: 21}
    )


def _get(client: TestClient, account_id: int, **params: str):
    return client.get(f"/accounts/{account_id}/weekly-insight", params=params)


def test_v1_week_start_must_be_a_monday(client: TestClient, conn: Connection) -> None:
    _s2_account(conn)
    r = _get(client, 102, week_start="2026-07-21")
    assert r.status_code == 422
    assert r.json() == {"detail": "week_start must be a Monday"}


def test_v2_incomplete_week_is_rejected(client: TestClient, conn: Connection) -> None:
    _s2_account(conn)
    r = _get(client, 102, week_start="2026-07-27")
    assert r.status_code == 422
    assert r.json() == {"detail": "week_start is not complete yet; the latest complete week is 2026-07-20"}


def test_v3_week_before_first_complete_week_is_rejected(client: TestClient, conn: Connection) -> None:
    _s2_account(conn)
    r = _get(client, 102, week_start="2026-05-18")
    assert r.status_code == 422
    assert r.json() == {"detail": "week_start is before the first complete week (2026-05-25)"}


def test_v4_unknown_account_is_404(client: TestClient) -> None:
    r = _get(client, 999)
    assert r.status_code == 404
    assert r.json() == {"detail": "Account 999 not found"}


def test_v5_default_week_is_the_latest_complete_one(client: TestClient, conn: Connection) -> None:
    _s2_account(conn)
    r = _get(client, 102)
    assert r.status_code == 200
    assert r.json()["week"] == {"start": "2026-07-20", "end": "2026-07-26"}


def test_v6_days_are_seven_zero_filled_weekdays(client: TestClient, conn: Connection) -> None:
    _s2_account(conn)  # events only on Mondays, so Tue..Sun must be zero-filled
    days = _get(client, 102).json()["days"]
    assert [d["weekday"] for d in days] == ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    assert [d["date"] for d in days] == [f"2026-07-{n}" for n in range(20, 27)]
    assert days[0]["total"] == 21
    assert [d["total"] for d in days[1:]] == [0] * 6


def test_v7_health_with_unreachable_db_is_503(tmp_path: Path) -> None:
    # /health opens its own connection from app.state.engine (not via get_connection), so a
    # dependency override would test nothing: point the app at a DB that cannot be opened instead.
    settings = Settings(
        database_url=f"sqlite:///{tmp_path}/no-such-dir/test.db", as_of_date=None, cors_origins=[]
    )
    with TestClient(create_app(settings)) as c:
        r = c.get("/health")
    assert r.status_code == 503
    assert r.json() == {"status": "error", "db": "error"}
