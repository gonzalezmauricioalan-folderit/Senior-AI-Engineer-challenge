from collections.abc import Iterator

from fastapi import Request
from sqlalchemy import Connection, Engine, create_engine


def make_engine(url: str) -> Engine:
    return create_engine(url, pool_pre_ping=True)


def get_connection(request: Request) -> Iterator[Connection]:
    with request.app.state.engine.connect() as conn:
        yield conn
