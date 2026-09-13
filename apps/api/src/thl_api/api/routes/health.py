from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from thl_api.db import check_database_available
from thl_api.openapi.load_contract import health_live_responses, health_ready_responses
from thl_api.problems import DEPENDENCY_UNAVAILABLE, problem_response
from thl_api.schemas.health import HealthLive, HealthReady, HealthReadyChecks

router = APIRouter(tags=["health"])


@router.get(
    "/health/live",
    operation_id="healthLive",
    summary="Liveness",
    response_model=HealthLive,
    responses=health_live_responses(),
)
async def health_live() -> HealthLive:
    return HealthLive(status="ok")


@router.get(
    "/health/ready",
    operation_id="healthReady",
    summary="Readiness (PostgreSQL)",
    response_model=HealthReady,
    responses=health_ready_responses(),
)
async def health_ready(request: Request) -> JSONResponse | HealthReady:
    database_ok = await check_database_available()
    if database_ok:
        return HealthReady(status="ok", checks=HealthReadyChecks(database="ok"))

    return problem_response(
        request,
        status=503,
        problem_type=DEPENDENCY_UNAVAILABLE,
        title="Service temporairement indisponible",
        code="DEPENDENCY_UNAVAILABLE",
        detail="Impossible de traiter la demande pour le moment.",
    )
