from __future__ import annotations

import asyncio
import uuid
from unittest.mock import patch

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import func, select

from lead_schema_fixtures import CONTACT_MINIMAL, QUOTE_MINIMAL
from migration_db import temporary_migration_database
from thl_api.alembic_config import configure_alembic_database_url
from thl_api.config import get_settings
from thl_api.db import close_db, init_db
from thl_api.models.enums import IdempotencyScope
from thl_api.models.idempotency import IdempotencyRecord
from thl_api.models.lead import Lead
from thl_api.repositories.advisory_lock import AdvisoryLockBusyError, AdvisoryUnlockFailedError
from thl_api.schemas.leads import ContactMessageCreate, QuoteRequestCreate
from thl_api.services.lead_submission import (
    PRODUCTION_LOCK_DEADLINE_SECONDS,
    HoneypotTriggeredError,
    IdempotencyBusyError,
    LeadSubmissionService,
)
from thl_api.turnstile.protocol import TurnstileVerifier


class _CountingTurnstile(TurnstileVerifier):
    calls: int = 0

    async def verify(self, token: str, *, action: str) -> bool:
        _CountingTurnstile.calls += 1
        _ = (token, action)
        return True


def _upgrade(database_url: str) -> None:
    cfg = Config("alembic.ini")
    configure_alembic_database_url(cfg, database_url)
    command.upgrade(cfg, "head")


@pytest.fixture
async def pg_database(monkeypatch: pytest.MonkeyPatch):
    with temporary_migration_database() as temp:
        monkeypatch.setenv("THL_ENV", "dev")
        monkeypatch.setenv("DATABASE_URL", temp.database_url)
        get_settings.cache_clear()
        init_db(get_settings().database_url_str)
        _upgrade(temp.database_url)
        yield temp.database_url
        await close_db()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_quote_and_contact_creation_counts(pg_database: str) -> None:
    _ = pg_database
    _CountingTurnstile.calls = 0
    service = LeadSubmissionService(settings=get_settings(), turnstile=_CountingTurnstile())
    await service.submit_quote(
        QuoteRequestCreate.model_validate(QUOTE_MINIMAL),
        idempotency_key=str(uuid.uuid4()),
        client_host="127.0.0.1",
        forwarded_for=None,
    )
    await service.submit_contact(
        ContactMessageCreate.model_validate(CONTACT_MINIMAL),
        idempotency_key=str(uuid.uuid4()),
        client_host="127.0.0.1",
        forwarded_for=None,
    )
    async with service._engine().connect() as conn:
        leads = (await conn.execute(select(func.count()).select_from(Lead))).scalar_one()
        assert leads == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrency_single_turnstile_single_row(pg_database: str) -> None:
    _ = pg_database
    _CountingTurnstile.calls = 0
    service = LeadSubmissionService(settings=get_settings(), turnstile=_CountingTurnstile())
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
    assert _CountingTurnstile.calls == 1
    async with service._engine().connect() as conn:
        count = (
            await conn.execute(
                select(func.count())
                .select_from(IdempotencyRecord)
                .where(IdempotencyRecord.scope == IdempotencyScope.contact_messages)
            )
        ).scalar_one()
        assert count == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_lock_timeout_503_no_turnstile_no_mutation(pg_database: str) -> None:
    _ = pg_database
    _CountingTurnstile.calls = 0
    service = LeadSubmissionService(settings=get_settings(), turnstile=_CountingTurnstile())
    payload = QuoteRequestCreate.model_validate(QUOTE_MINIMAL)
    with patch(
        "thl_api.services.lead_submission.try_acquire_session_lock",
        side_effect=AdvisoryLockBusyError,
    ):
        with pytest.raises(IdempotencyBusyError):
            await service.submit_quote(
                payload,
                idempotency_key=str(uuid.uuid4()),
                client_host="127.0.0.1",
                forwarded_for=None,
            )
    assert _CountingTurnstile.calls == 0
    async with service._engine().connect() as conn:
        leads = (await conn.execute(select(func.count()).select_from(Lead))).scalar_one()
        assert leads == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_honeypot_zero_db_zero_turnstile(pg_database: str) -> None:
    _ = pg_database
    _CountingTurnstile.calls = 0
    service = LeadSubmissionService(settings=get_settings(), turnstile=_CountingTurnstile())
    payload = QuoteRequestCreate.model_validate({**QUOTE_MINIMAL, "honeypot": "bot"})
    with pytest.raises(HoneypotTriggeredError):
        await service.submit_quote(
            payload,
            idempotency_key=str(uuid.uuid4()),
            client_host="127.0.0.1",
            forwarded_for=None,
        )
    assert _CountingTurnstile.calls == 0


@pytest.mark.integration
def test_production_lock_deadline_default_is_5s() -> None:
    assert PRODUCTION_LOCK_DEADLINE_SECONDS == 5.0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_unlock_failure_invalidates_connection(pg_database: str) -> None:
    _ = pg_database
    service = LeadSubmissionService(settings=get_settings(), turnstile=_CountingTurnstile())
    payload = ContactMessageCreate.model_validate(CONTACT_MINIMAL)
    with patch(
        "thl_api.services.lead_submission.release_session_lock",
        side_effect=AdvisoryUnlockFailedError,
    ):
        result = await service.submit_contact(
            payload,
            idempotency_key=str(uuid.uuid4()),
            client_host="127.0.0.1",
            forwarded_for=None,
        )
        assert result.status_code == 201


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rate_limit_enforced_before_turnstile(pg_database: str) -> None:
    _ = pg_database
    _CountingTurnstile.calls = 0
    service = LeadSubmissionService(settings=get_settings(), turnstile=_CountingTurnstile())
    payload = ContactMessageCreate.model_validate(CONTACT_MINIMAL)
    key = str(uuid.uuid4())

    async def _boom(*args: object, **kwargs: object) -> None:
        _ = (args, kwargs)
        raise RuntimeError("rate limit hit")

    with patch.object(LeadSubmissionService, "_enforce_rate_limit", _boom):
        with pytest.raises(RuntimeError, match="rate limit hit"):
            await service.submit_contact(
                payload,
                idempotency_key=key,
                client_host="127.0.0.1",
                forwarded_for=None,
            )
    assert _CountingTurnstile.calls == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_idempotency_replay_200_without_second_turnstile(pg_database: str) -> None:
    _ = pg_database
    _CountingTurnstile.calls = 0
    service = LeadSubmissionService(settings=get_settings(), turnstile=_CountingTurnstile())
    payload = ContactMessageCreate.model_validate(CONTACT_MINIMAL)
    key = str(uuid.uuid4())
    first = await service.submit_contact(
        payload,
        idempotency_key=key,
        client_host="127.0.0.1",
        forwarded_for=None,
    )
    second = await service.submit_contact(
        payload,
        idempotency_key=key,
        client_host="127.0.0.1",
        forwarded_for=None,
    )
    assert first.status_code == 201
    assert second.status_code == 200
    assert _CountingTurnstile.calls == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_no_sql_transaction_during_turnstile(pg_database: str) -> None:
    _ = pg_database
    service = LeadSubmissionService(settings=get_settings(), turnstile=_CountingTurnstile())
    payload = QuoteRequestCreate.model_validate(QUOTE_MINIMAL)
    observed: list[bool] = []

    async def verify_with_assertion(token: str, *, action: str) -> bool:
        _ = (token, action)
        connection = await service._engine().connect()
        try:
            observed.append(connection.in_transaction())
        finally:
            await connection.close()
        return True

    service.turnstile.verify = verify_with_assertion  # type: ignore[method-assign]
    await service.submit_quote(
        payload,
        idempotency_key=str(uuid.uuid4()),
        client_host="127.0.0.1",
        forwarded_for=None,
    )
    assert observed and all(value is False for value in observed)
