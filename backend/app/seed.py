"""Seed loader: runs data/seed.sql unmodified, in one transaction, only into an empty database.

Usage: `python -m app.seed [path]` (default data/seed.sql relative to the repo root); DATABASE_URL as usual.
"""

import sys
from pathlib import Path

from sqlalchemy import Engine, text

DEFAULT_SEED = Path(__file__).resolve().parents[2] / "data" / "seed.sql"


def load_seed(engine: Engine, path: Path) -> bool:
    """Load `path` if `accounts` is empty. Returns False (and loads nothing) when it already has rows."""
    with engine.connect() as conn:
        if conn.execute(text("SELECT COUNT(*) FROM accounts")).scalar_one() > 0:
            return False
    sql = path.read_text()
    raw = engine.raw_connection()
    try:
        if engine.dialect.name == "sqlite":
            # executescript commits any open transaction first, so the BEGIN/COMMIT is explicit.
            raw.driver_connection.executescript(f"BEGIN;\n{sql}\nCOMMIT;")
        else:
            # psycopg runs a multi-statement string (no parameters) as a single implicit transaction.
            with raw.cursor() as cur:
                cur.execute(sql)
            raw.commit()
    except Exception:
        if engine.dialect.name == "sqlite":
            if raw.driver_connection.in_transaction:
                raw.driver_connection.execute("ROLLBACK")
        else:
            raw.rollback()
        raise
    finally:
        raw.close()
    return True


def main() -> None:
    from app.config import Settings
    from app.db import make_engine

    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SEED
    loaded = load_seed(make_engine(Settings.from_env().database_url), path)
    print("seed loaded" if loaded else "seed skipped: accounts already has rows")


if __name__ == "__main__":
    main()
