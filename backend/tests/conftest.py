from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Connection, Engine

from app.config import Settings
from app.db import make_engine
from app.main import create_app

BACKEND_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture
def db_url(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path}/test.db"


@pytest.fixture
def engine(db_url: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[Engine]:
    monkeypatch.setenv("DATABASE_URL", db_url)
    command.upgrade(Config(str(BACKEND_DIR / "alembic.ini")), "head")
    eng = make_engine(db_url)
    yield eng
    eng.dispose()


@pytest.fixture
def conn(engine: Engine) -> Iterator[Connection]:
    """A connection whose writes are committed immediately."""
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as c:
        yield c


@pytest.fixture
def client(engine: Engine, db_url: str) -> Iterator[TestClient]:
    settings = Settings(database_url=db_url, as_of_date=date(2026, 7, 28), cors_origins=[])
    with TestClient(create_app(settings)) as c:
        yield c
