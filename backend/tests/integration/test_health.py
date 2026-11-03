from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_health_ok(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "db": "ok"}


def test_health_db_unreachable_returns_503(tmp_path: Path) -> None:
    settings = Settings(
        database_url=f"sqlite:///{tmp_path}/missing-dir/test.db", as_of_date=None, cors_origins=[]
    )
    with TestClient(create_app(settings)) as c:
        r = c.get("/health")
    assert r.status_code == 503
    assert r.json() == {"status": "error", "db": "error"}
