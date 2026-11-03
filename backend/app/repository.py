"""SQL only. Every function takes a Connection."""

from sqlalchemy import Connection, text


def ping(conn: Connection) -> None:
    conn.execute(text("SELECT 1"))
