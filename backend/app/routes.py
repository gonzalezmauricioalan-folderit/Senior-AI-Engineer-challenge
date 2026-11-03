from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import Connection

from app import repository, service
from app.db import get_connection
from app.schemas import AccountSummary, Health

router = APIRouter()

Conn = Annotated[Connection, Depends(get_connection)]  # for the data endpoints


@router.get("/health", response_model=Health)
def health(request: Request) -> JSONResponse:
    # Open the connection inside the try: an unreachable DB must give 503, not a dependency 500.
    try:
        with request.app.state.engine.connect() as conn:
            repository.ping(conn)
    except Exception:
        return JSONResponse(Health(status="error", db="error").model_dump(), status_code=503)
    return JSONResponse(Health(status="ok", db="ok").model_dump())


@router.get("/accounts", response_model=list[AccountSummary])
def accounts(request: Request, conn: Conn) -> list[AccountSummary]:
    return service.list_accounts(conn, request.app.state.settings)
