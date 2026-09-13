from __future__ import annotations

from fastapi import APIRouter

from thl_api.api.routes import health, leads

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(leads.router)
