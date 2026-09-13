from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from thl_api.db import check_database_available
from thl_api.middleware.correlation import CORRELATION_HEADER

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def health_live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def health_ready(request: Request) -> JSONResponse:
    correlation_id: str = request.state.correlation_id
    database_ok = await check_database_available()
    if database_ok:
        body: dict[str, Any] = {
            "status": "ok",
            "checks": {"database": "ok"},
        }
        return JSONResponse(status_code=200, content=body)

    problem = {
        "type": "urn:thl:problem:dependency-unavailable",
        "title": "Service temporairement indisponible",
        "status": 503,
        "detail": "Impossible de traiter la demande pour le moment.",
        "code": "DEPENDENCY_UNAVAILABLE",
        "correlation_id": correlation_id,
    }
    return JSONResponse(
        status_code=503,
        content=problem,
        media_type="application/problem+json",
        headers={CORRELATION_HEADER: correlation_id},
    )
