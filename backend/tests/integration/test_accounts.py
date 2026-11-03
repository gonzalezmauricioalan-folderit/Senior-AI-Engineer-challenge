from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Connection, Engine, text

from app.config import Settings
from app.main import create_app
from app.seed import load_seed
from tests.factories import add_account, add_event

SEED = Path(__file__).resolve().parents[3] / "data" / "seed.sql"
TZ = "America/Chicago"


def test_accounts_ordered_by_name_with_counts_and_latest_week(client: TestClient, conn: Connection) -> None:
    add_account(conn, 102, name="Zeta Co")
    add_account(conn, 101, name="Alpha Co")
    add_account(conn, 103, name="Empty Co")
    t = datetime(2026, 7, 1, 10, 0)
    add_event(conn, 101, "Site A", t, TZ)
    add_event(conn, 101, "Site B", t, TZ)
    add_event(conn, 101, "Site B", datetime(2026, 7, 2, 10, 0), TZ)
    add_event(conn, 102, "Site A", t, TZ)

    r = client.get("/accounts")

    assert r.status_code == 200
    body = r.json()
    assert [a["name"] for a in body] == ["Alpha Co", "Empty Co", "Zeta Co"]
    assert [a["location_count"] for a in body] == [2, 0, 1]
    # Fixture AS_OF_DATE is 2026-07-28 (a Tuesday), so the latest complete week starts on 2026-07-20.
    assert {a["latest_complete_week"] for a in body} == {"2026-07-20"}
    assert set(body[0]) == {"id", "name", "industry", "timezone", "location_count", "latest_complete_week"}


def test_accounts_location_count_ignores_duplicate_rows(client: TestClient, conn: Connection) -> None:
    add_account(conn, 101)
    t = datetime(2026, 7, 1, 10, 0)
    add_event(conn, 101, "Site A", t, TZ)
    add_event(conn, 101, "Site A", t, TZ)
    assert client.get("/accounts").json()[0]["location_count"] == 1


def test_latest_complete_week_from_data_when_as_of_unset(
    engine: Engine, conn: Connection, db_url: str
) -> None:
    add_account(conn, 101, name="Chicago Co", tz="America/Chicago")
    add_account(conn, 102, name="Tokyo Co", tz="Asia/Tokyo")
    # Earlier event: using the dataset min instead of the max would give a different week.
    add_event(conn, 101, "Site A", datetime(2026, 5, 6, 10, 0), "America/Chicago")
    # Dataset max: Sun 2026-07-26 23:30 Chicago = Mon 2026-07-27 04:30 UTC = Mon 13:30 Tokyo.
    add_event(conn, 101, "Site A", datetime(2026, 7, 26, 23, 30), "America/Chicago")
    settings = Settings(database_url=db_url, as_of_date=None, cors_origins=[])
    with TestClient(create_app(settings)) as c:
        latest = {a["name"]: a["latest_complete_week"] for a in c.get("/accounts").json()}
    # Chicago local date is Sun 07-26 -> Monday 07-20 -> latest complete week 07-13
    # (the UTC date would give 07-20).
    assert latest["Chicago Co"] == "2026-07-13"
    # Tokyo is already on Mon 07-27 -> latest complete week 07-20: the rule is per account timezone.
    assert latest["Tokyo Co"] == "2026-07-20"


def test_latest_complete_week_is_null_for_empty_dataset_without_as_of(
    engine: Engine, conn: Connection, db_url: str
) -> None:
    add_account(conn, 101)
    settings = Settings(database_url=db_url, as_of_date=None, cors_origins=[])
    with TestClient(create_app(settings)) as c:
        body = c.get("/accounts").json()
    assert body[0]["latest_complete_week"] is None
    assert body[0]["location_count"] == 0


def test_accounts_with_unreachable_db_fails(tmp_path: Path) -> None:
    settings = Settings(
        database_url=f"sqlite:///{tmp_path}/missing-dir/test.db", as_of_date=None, cors_origins=[]
    )
    with TestClient(create_app(settings), raise_server_exceptions=False) as c:
        assert c.get("/accounts").status_code == 500


@pytest.mark.slow
def test_load_seed_loads_once(engine: Engine) -> None:
    assert load_seed(engine, SEED) is True
    with engine.connect() as c:
        assert c.execute(text("SELECT COUNT(*) FROM accounts")).scalar_one() == 20
        assert c.execute(text("SELECT COUNT(*) FROM activity_events")).scalar_one() == 12626
    assert load_seed(engine, SEED) is False


@pytest.mark.slow
def test_seed_accounts_endpoint(client: TestClient, engine: Engine) -> None:
    load_seed(engine, SEED)
    body = client.get("/accounts").json()
    assert len(body) == 20
    assert [a["name"] for a in body] == sorted(a["name"] for a in body)
    spa = next(a for a in body if a["name"] == "Quiet Harbor Spa")
    assert spa["location_count"] == 0
    assert spa["latest_complete_week"] == "2026-07-20"
