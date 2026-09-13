from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from thl_api.api.router import api_router
from thl_api.config import get_settings
from thl_api.db import close_db, init_db
from thl_api.errors import unhandled_exception_handler, validation_exception_handler
from thl_api.middleware.correlation import CorrelationMiddleware
from thl_api.middleware.lead_post_guard import LeadPostGuardMiddleware
from thl_api.openapi.custom import build_openapi


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    init_db(settings.database_url_str)
    try:
        yield
    finally:
        await close_db()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="THE HIVE LOGISTICS — API publique V1",
        version="1.0.1",
        description=(
            "Contrat public V1 (leads Contact et Devis). "
            "PRD v0.1.4 — THL-ARCH-001 / 001A."
        ),
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        openapi_tags=[
            {"name": "quote-requests"},
            {"name": "contact-messages"},
            {"name": "health"},
        ],
    )
    app.add_middleware(LeadPostGuardMiddleware)
    app.add_middleware(CorrelationMiddleware)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
    app.include_router(api_router)

    def custom_openapi() -> dict[str, object]:
        return build_openapi(app)

    app.openapi = custom_openapi  # type: ignore[method-assign]
    _ = settings.thl_env
    return app


app = create_app()
