from __future__ import annotations

import asyncio
import sys

import pytest

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from helpers import api_client
from thl_api.config import get_settings
from thl_api.main import create_app


@pytest.fixture(autouse=True)
def _dev_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("THL_ENV", "dev")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://thl_dev:thl_dev_password@127.0.0.1:5432/thl_dev",
    )
    get_settings.cache_clear()


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    async with api_client(app, raise_app_exceptions=False) as http_client:
        yield http_client
