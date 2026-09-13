from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from thl_api.api.router import api_router
from thl_api.config import get_settings
from thl_api.db import close_db, init_db
from thl_api.errors import unhandled_exception_handler
from thl_api.middleware.correlation import CorrelationMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    init_db(settings.database_url)
    try:
        yield
    finally:
        await close_db()


def create_app() -> FastAPI:
    app = FastAPI(
        title="THE HIVE LOGISTICS API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
    )
    app.add_middleware(CorrelationMiddleware)
    app.add_exception_handler(Exception, unhandled_exception_handler)
    app.include_router(api_router)
    return app


app = create_app()
