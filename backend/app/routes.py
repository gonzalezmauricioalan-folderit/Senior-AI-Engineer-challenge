from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import Connection

from app import repository
from app.db import get_connection

router = APIRouter()

Conn = Annotated[Connection, Depends(get_connection)]


@router.get("/health")
def health(conn: Conn) -> JSONResponse:
    try:
        repository.ping(conn)
    except Exception:
        return JSONResponse({"status": "error", "db": "error"}, status_code=503)
    return JSONResponse({"status": "ok", "db": "ok"})
