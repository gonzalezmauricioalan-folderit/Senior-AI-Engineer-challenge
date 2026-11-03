from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import Connection

from app import repository
from app.db import get_connection

router = APIRouter()

Conn = Annotated[Connection, Depends(get_connection)]  # for the data endpoints


@router.get("/health")
def health(request: Request) -> JSONResponse:
    # Open the connection inside the try: an unreachable DB must give 503, not a dependency 500.
    try:
        with request.app.state.engine.connect() as conn:
            repository.ping(conn)
    except Exception:
        return JSONResponse({"status": "error", "db": "error"}, status_code=503)
    return JSONResponse({"status": "ok", "db": "ok"})
