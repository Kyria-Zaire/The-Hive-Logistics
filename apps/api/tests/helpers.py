from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from thl_api.config import get_settings
from thl_api.db import close_db, init_db


@asynccontextmanager
async def api_client(
    app: FastAPI,
    *,
    raise_app_exceptions: bool = False,
) -> AsyncIterator[AsyncClient]:
    settings = get_settings()
    init_db(settings.database_url)
    transport = ASGITransport(app=app, raise_app_exceptions=raise_app_exceptions)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
    finally:
        await close_db()
