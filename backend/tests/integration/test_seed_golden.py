"""Seed golden tests G1-G8 (PLAN.md section 4): the real seed on SQLite, as_of_date=None.

One module-scoped seeded database; parity with Detection_tuning.md.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from app.config import Settings
from app.db import make_engine
from app.main import create_app
from app.seed import load_seed

pytestmark = pytest.mark.slow

BACKEND_DIR = Path(__file__).resolve().parents[2]
SEED = BACKEND_DIR.parent / "data" / "seed.sql"  # same file as Path("../data/seed.sql") from backend/
UTC_NOTE = (
    "This account's timezone is set to UTC, which may be a misconfiguration; days and weeks may be shifted."
)


@pytest.fixture(scope="module")
def seeded_engine(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Engine]:
    url = f"sqlite:///{tmp_path_factory.mktemp('golden')}/seed.db"
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DATABASE_URL", url)  # alembic's env.py reads it
        command.upgrade(Config(str(BACKEND_DIR / "alembic.ini")), "head")
    engine = make_engine(url)
    assert load_seed(engine, SEED) is True
    yield engine
    engine.dispose()


@pytest.fixture(scope="module")
def seed_client(seeded_engine: Engine) -> Iterator[TestClient]:
    settings = Settings(database_url=str(seeded_engine.url), as_of_date=None, cors_origins=[])
    with TestClient(create_app(settings)) as c:
        yield c


def _insight(client: TestClient, account_id: int, week: str | None = None) -> dict:
    params = {"week_start": week} if week else {}
    r = client.get(f"/accounts/{account_id}/weekly-insight", params=params)
    assert r.status_code == 200
    return r.json()


def test_g1_clean_view_drops_the_duplicates(seeded_engine: Engine) -> None:
    with seeded_engine.connect() as conn:
        clean = conn.execute(text("SELECT COUNT(*) FROM clean_activity_events")).scalar_one()
        raw = conn.execute(text("SELECT COUNT(*) FROM activity_events")).scalar_one()
    assert (clean, raw) == (12_614, 12_626)


def test_g2_default_week_of_account_6(seed_client: TestClient) -> None:
    assert _insight(seed_client, 6)["week"]["start"] == "2026-07-20"


def test_g3_spike_week_of_account_6(seed_client: TestClient) -> None:
    body = _insight(seed_client, 6, "2026-06-01")
    s = body["summary"]
    assert (s["total"], s["usual"], s["lower"], s["upper"]) == (880, 66.0, 27.1, 104.9)
    assert s["status"] == "higher_than_usual"
    assert len(body["locations"]) == 15
    assert {loc["status"] for loc in body["locations"]} == {"higher_than_usual"}
    site_a = next(loc for loc in body["locations"] if loc["location"] == "Site A")
    assert (site_a["total"], site_a["usual"]) == (49, 4.5)


def test_g4_week_after_the_spike_is_not_distorted(seed_client: TestClient) -> None:
    s = _insight(seed_client, 6, "2026-06-08")["summary"]
    assert s["total"] == 102
    assert s["status"] == "normal"


def test_g5_account_2_dip(seed_client: TestClient) -> None:
    s = _insight(seed_client, 2, "2026-07-06")["summary"]
    assert (s["total"], s["usual"]) == (18, 32.5)
    assert s["status"] == "lower_than_usual"


def test_g6_account_15_spike(seed_client: TestClient) -> None:
    assert _insight(seed_client, 15, "2026-06-01")["summary"]["status"] == "higher_than_usual"


def test_g7_account_without_events(seed_client: TestClient) -> None:
    body = _insight(seed_client, 20)
    assert body["summary"]["status"] == "not_enough_history"
    assert body["locations"] == []


def test_g8_utc_note_and_first_week_without_history(seed_client: TestClient) -> None:
    assert UTC_NOTE in _insight(seed_client, 18)["data_notes"]
    assert _insight(seed_client, 1, "2026-02-02")["summary"]["status"] == "not_enough_history"
