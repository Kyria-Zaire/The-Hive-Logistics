from __future__ import annotations

import asyncio
import os
import sys

import pytest

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

os.environ.setdefault("THL_ENV", "dev")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://thl_dev:thl_dev_password@127.0.0.1:5432/thl_dev",
)

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
    monkeypatch.setenv("PRIVACY_POLICY_VERSION", "2026-test")
    monkeypatch.setenv(
        "IDEMPOTENCY_HMAC_SECRET_CURRENT",
        "dev-idempotency-hmac-secret-32bytes!!",
    )
    monkeypatch.setenv("IDEMPOTENCY_HMAC_SECRET_CURRENT_VERSION", "1")
    monkeypatch.setenv(
        "FINGERPRINT_HMAC_SECRET_CURRENT",
        "dev-fingerprint-hmac-secret-32bytes!!",
    )
    monkeypatch.setenv("FINGERPRINT_HMAC_SECRET_CURRENT_VERSION", "1")
    monkeypatch.setenv(
        "RATE_LIMIT_HMAC_SECRET_CURRENT",
        "dev-rate-limit-hmac-secret-32bytes!!!!",
    )
    monkeypatch.setenv("RATE_LIMIT_HMAC_SECRET_CURRENT_VERSION", "1")
    monkeypatch.setenv("TURNSTILE_SECRET_KEY", "test-turnstile-secret")
    monkeypatch.setenv("TURNSTILE_EXPECTED_HOSTNAME", "test.local")
    get_settings.cache_clear()


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    async with api_client(app, raise_app_exceptions=False) as http_client:
        yield http_client
