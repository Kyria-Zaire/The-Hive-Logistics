from __future__ import annotations

import asyncio
import os
import uuid

import pytest

from lead_schema_fixtures import CONTACT_MINIMAL, QUOTE_MINIMAL
from thl_api.config import get_settings
from thl_api.db import close_db, init_db
from thl_api.schemas.leads import ContactMessageCreate, QuoteRequestCreate
from thl_api.services.lead_submission import LeadSubmissionService
from thl_api.turnstile.protocol import TurnstileVerifier

_INTEGRATION_DATABASE_URL = os.environ.get(
    "INTEGRATION_DATABASE_URL",
    "postgresql+psycopg://thl_dev:thl_dev_password@127.0.0.1:5433/thl_dev",
)


class _AlwaysOkTurnstile(TurnstileVerifier):
    calls: int = 0

    async def verify(self, token: str, *, action: str) -> bool:
        _AlwaysOkTurnstile.calls += 1
        _ = (token, action)
        return True


@pytest.fixture
def integration_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("THL_ENV", "dev")
    monkeypatch.setenv("DATABASE_URL", _INTEGRATION_DATABASE_URL)
    get_settings.cache_clear()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_quote_creation_persists_atomically(integration_env: None) -> None:
    _AlwaysOkTurnstile.calls = 0
    settings = get_settings()
    init_db(settings.database_url)
    service = LeadSubmissionService(
        settings=settings,
        turnstile=_AlwaysOkTurnstile(),
    )
    payload = QuoteRequestCreate.model_validate(QUOTE_MINIMAL)
    key = str(uuid.uuid4())
    result = await service.submit_quote(
        payload,
        idempotency_key=key,
        client_host="127.0.0.1",
        forwarded_for=None,
    )
    assert result.status_code == 201
    assert result.body["status"] == "received"
    await close_db()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_idempotency_single_turnstile(integration_env: None) -> None:
    _AlwaysOkTurnstile.calls = 0
    settings = get_settings()
    init_db(settings.database_url)
    service = LeadSubmissionService(settings=settings, turnstile=_AlwaysOkTurnstile())
    payload = ContactMessageCreate.model_validate(CONTACT_MINIMAL)
    key = str(uuid.uuid4())

    async def once() -> None:
        await service.submit_contact(
            payload,
            idempotency_key=key,
            client_host="127.0.0.1",
            forwarded_for=None,
        )

    await asyncio.gather(once(), once())
    assert _AlwaysOkTurnstile.calls == 1
    replay = await service.submit_contact(
        payload,
        idempotency_key=key,
        client_host="127.0.0.1",
        forwarded_for=None,
    )
    assert replay.status_code == 200
    assert _AlwaysOkTurnstile.calls == 1
    await close_db()
