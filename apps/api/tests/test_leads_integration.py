from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from lead_schema_fixtures import CONTACT_MINIMAL, QUOTE_MINIMAL
from migration_db import temporary_migration_database
from thl_api.alembic_config import configure_alembic_database_url
from thl_api.config import get_settings
from thl_api.db import close_db, init_db
from thl_api.leads.public_reference import public_reference_for_accepted_at
from thl_api.models.enums import IdempotencyScope
from thl_api.models.idempotency import IdempotencyRecord
from thl_api.models.lead import ContactMessageDetail, Lead, QuoteRequestDetail
from thl_api.models.notification import NotificationJob
from thl_api.repositories import leads as leads_repo
from thl_api.repositories.advisory_lock import AdvisoryLockBusyError, AdvisoryUnlockFailedError
from thl_api.schemas.leads import ContactMessageCreate, QuoteRequestCreate
from thl_api.services.lead_submission import (
    PRODUCTION_LOCK_DEADLINE_SECONDS,
    HoneypotTriggeredError,
    IdempotencyBusyError,
    LeadSubmissionService,
    RateLimitExceededError,
)
from thl_api.turnstile.protocol import TurnstileVerifier


class _CountingTurnstile(TurnstileVerifier):
    calls: int = 0

    async def verify(self, token: str, *, action: str) -> bool:
        _CountingTurnstile.calls += 1
        _ = (token, action)
        return True


class _ConnectTrackerContext:
    def __init__(self, inner: object, pinned: list[object]) -> None:
        self._inner = inner
        self._pinned = pinned

    def __await__(self):
        return self._await_impl().__await__()

    async def _await_impl(self):
        connection = await self._inner
        self._record(connection)
        return connection

    async def __aenter__(self):
        connection = await self._inner.__aenter__()
        self._record(connection)
        return connection

    async def __aexit__(self, *exc: object) -> None:
        await self._inner.__aexit__(*exc)

    def _record(self, connection: object) -> None:
        if not self._pinned or self._pinned[-1] is not connection:
            self._pinned.append(connection)


class _ConnectTrackingEngine:
    def __init__(self, inner: AsyncEngine) -> None:
        self._inner = inner
        self.pinned: list[object] = []

    def connect(self):
        return _ConnectTrackerContext(self._inner.connect(), self.pinned)

    def __getattr__(self, name: str):
        return getattr(self._inner, name)


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
        with patch.object(AsyncConnection, "invalidate", new_callable=AsyncMock) as invalidate:
            result = await service.submit_contact(
                payload,
                idempotency_key=str(uuid.uuid4()),
                client_host="127.0.0.1",
                forwarded_for=None,
            )
            assert result.status_code == 201
            invalidate.assert_awaited_once()


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
    probe = LeadSubmissionService(settings=get_settings(), turnstile=_CountingTurnstile())
    tracking_engine = _ConnectTrackingEngine(probe._engine())
    service = LeadSubmissionService(
        settings=get_settings(),
        turnstile=_CountingTurnstile(),
        engine=tracking_engine,  # type: ignore[arg-type]
    )
    payload = QuoteRequestCreate.model_validate(QUOTE_MINIMAL)

    async def verify_with_assertion(token: str, *, action: str) -> bool:
        _ = (token, action)
        pinned_connection = tracking_engine.pinned[-1]
        assert pinned_connection.in_transaction() is False  # type: ignore[attr-defined]
        return True

    service.turnstile.verify = verify_with_assertion  # type: ignore[method-assign]
    await service.submit_quote(
        payload,
        idempotency_key=str(uuid.uuid4()),
        client_host="127.0.0.1",
        forwarded_for=None,
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_hmac_rotation_replay_with_previous_secret(
    pg_database: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = pg_database
    secret_v1 = "dev-idempotency-hmac-secret-32bytes!!"
    secret_v2 = "dev-idempotency-hmac-secret-v2-32bytes!"
    monkeypatch.setenv("IDEMPOTENCY_HMAC_SECRET_CURRENT", secret_v1)
    monkeypatch.setenv("IDEMPOTENCY_HMAC_SECRET_CURRENT_VERSION", "1")
    monkeypatch.delenv("IDEMPOTENCY_HMAC_SECRET_PREVIOUS", raising=False)
    monkeypatch.delenv("IDEMPOTENCY_HMAC_SECRET_PREVIOUS_VERSION", raising=False)
    get_settings.cache_clear()

    service = LeadSubmissionService(settings=get_settings(), turnstile=_CountingTurnstile())
    payload = ContactMessageCreate.model_validate(CONTACT_MINIMAL)
    key = str(uuid.uuid4())
    first = await service.submit_contact(
        payload,
        idempotency_key=key,
        client_host="127.0.0.1",
        forwarded_for=None,
    )
    assert first.status_code == 201

    monkeypatch.setenv("IDEMPOTENCY_HMAC_SECRET_CURRENT", secret_v2)
    monkeypatch.setenv("IDEMPOTENCY_HMAC_SECRET_CURRENT_VERSION", "2")
    monkeypatch.setenv("IDEMPOTENCY_HMAC_SECRET_PREVIOUS", secret_v1)
    monkeypatch.setenv("IDEMPOTENCY_HMAC_SECRET_PREVIOUS_VERSION", "1")
    get_settings.cache_clear()
    service_rotated = LeadSubmissionService(settings=get_settings(), turnstile=_CountingTurnstile())

    replay = await service_rotated.submit_contact(
        payload,
        idempotency_key=key,
        client_host="127.0.0.1",
        forwarded_for=None,
    )
    assert replay.status_code == 200
    assert replay.body == first.body


@pytest.mark.integration
@pytest.mark.asyncio
async def test_utc_midnight_public_reference_boundary(pg_database: str) -> None:
    _ = pg_database
    service = LeadSubmissionService(settings=get_settings(), turnstile=_CountingTurnstile())
    payload = QuoteRequestCreate.model_validate(QUOTE_MINIMAL)
    midnight_utc = datetime(2026, 9, 13, 0, 0, 0, tzinfo=UTC)

    from sqlalchemy.ext.asyncio import AsyncConnection

    real_execute = AsyncConnection.execute

    async def patched_execute(self, statement, parameters=None, *args, **kwargs):
        sql = str(statement)
        if "transaction_timestamp()" in sql:

            class _Scalar:
                def scalar_one(self) -> datetime:
                    return midnight_utc

            return _Scalar()
        return await real_execute(self, statement, parameters, *args, **kwargs)

    with patch.object(AsyncConnection, "execute", patched_execute):
        result = await service.submit_quote(
            payload,
            idempotency_key=str(uuid.uuid4()),
            client_host="127.0.0.1",
            forwarded_for=None,
        )
    ref = result.body["public_reference"]
    assert isinstance(ref, str)
    assert ref.startswith("THL-20260913-")
    assert result.body["created_at"].startswith("2026-09-13T00:00:00")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_public_reference_collision_retries_only_unique_violation(
    pg_database: str,
) -> None:
    _ = pg_database
    service = LeadSubmissionService(settings=get_settings(), turnstile=_CountingTurnstile())
    payload = QuoteRequestCreate.model_validate(QUOTE_MINIMAL)
    first = await service.submit_quote(
        payload,
        idempotency_key=str(uuid.uuid4()),
        client_host="127.0.0.1",
        forwarded_for=None,
    )
    duplicate_ref = first.body["public_reference"]
    attempts = {"count": 0}

    def generator(_accepted_at: datetime) -> str:
        attempts["count"] += 1
        if attempts["count"] == 1:
            return duplicate_ref
        return public_reference_for_accepted_at(_accepted_at)

    with patch(
        "thl_api.services.lead_submission.public_reference_for_accepted_at",
        side_effect=generator,
    ):
        second = await service.submit_quote(
            payload,
            idempotency_key=str(uuid.uuid4()),
            client_host="127.0.0.1",
            forwarded_for=None,
        )
    assert attempts["count"] >= 2
    assert second.body["public_reference"] != duplicate_ref


@pytest.mark.integration
@pytest.mark.asyncio
async def test_public_reference_non_unique_integrity_error_propagates(
    pg_database: str,
) -> None:
    _ = pg_database
    service = LeadSubmissionService(settings=get_settings(), turnstile=_CountingTurnstile())
    payload = ContactMessageCreate.model_validate(CONTACT_MINIMAL)

    class _CheckDiag:
        constraint_name = "chk_leads_public_reference_format"

    class _CheckOrig(Exception):
        diag = _CheckDiag()

    async def boom(*args, **kwargs):
        _ = (args, kwargs)
        raise IntegrityError("insert", {}, _CheckOrig())

    with patch.object(leads_repo, "insert_lead_bundle", side_effect=boom):
        with pytest.raises(IntegrityError):
            await service.submit_contact(
                payload,
                idempotency_key=str(uuid.uuid4()),
                client_host="127.0.0.1",
                forwarded_for=None,
            )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_intermediate_failure_rollback_zero_persistence(pg_database: str) -> None:
    _ = pg_database
    service = LeadSubmissionService(settings=get_settings(), turnstile=_CountingTurnstile())
    payload = QuoteRequestCreate.model_validate(QUOTE_MINIMAL)
    async def fail_after_lead_row(connection, **kwargs):
        from sqlalchemy import insert

        from thl_api.models.lead import Lead

        body = kwargs["body"]
        accepted_at = kwargs["accepted_at"]
        public_reference = kwargs["public_reference"]
        lead_stmt = (
            insert(Lead)
            .values(
                public_reference=public_reference,
                lead_type=kwargs["lead_type"],
                first_name=body.first_name,
                last_name=body.last_name,
                email=body.email,
                phone=getattr(body, "phone", None),
                company=getattr(body, "company", None),
                privacy_acknowledgement=True,
                privacy_policy_version=kwargs["privacy_policy_version"],
                privacy_acknowledged_at=accepted_at,
                created_at=accepted_at,
                updated_at=accepted_at,
            )
            .returning(Lead.id)
        )
        await connection.execute(lead_stmt)
        raise RuntimeError("simulated mid-transaction failure")

    with patch.object(leads_repo, "insert_lead_bundle", side_effect=fail_after_lead_row):
        with pytest.raises(RuntimeError, match="simulated mid-transaction failure"):
            await service.submit_quote(
                payload,
                idempotency_key=str(uuid.uuid4()),
                client_host="127.0.0.1",
                forwarded_for=None,
            )

    async with service._engine().connect() as conn:
        leads = (await conn.execute(select(func.count()).select_from(Lead))).scalar_one()
        quote_details = (
            await conn.execute(select(func.count()).select_from(QuoteRequestDetail))
        ).scalar_one()
        contact_details = (
            await conn.execute(select(func.count()).select_from(ContactMessageDetail))
        ).scalar_one()
        idem = (
            await conn.execute(select(func.count()).select_from(IdempotencyRecord))
        ).scalar_one()
        notifications = (
            await conn.execute(select(func.count()).select_from(NotificationJob))
        ).scalar_one()
        assert leads == 0
        assert quote_details == 0
        assert contact_details == 0
        assert idem == 0
        assert notifications == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rate_limit_shared_across_service_instances(
    pg_database: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = pg_database
    monkeypatch.setenv("RATE_LIMIT_CONTACT_MESSAGES_MAX", "1")
    monkeypatch.setenv("RATE_LIMIT_CONTACT_MESSAGES_WINDOW_SECONDS", "3600")
    get_settings.cache_clear()
    settings = get_settings()
    service_a = LeadSubmissionService(settings=settings, turnstile=_CountingTurnstile())
    service_b = LeadSubmissionService(settings=settings, turnstile=_CountingTurnstile())
    payload = ContactMessageCreate.model_validate(CONTACT_MINIMAL)

    await service_a.submit_contact(
        payload,
        idempotency_key=str(uuid.uuid4()),
        client_host="10.0.0.50",
        forwarded_for=None,
    )
    with pytest.raises(RateLimitExceededError):
        await service_b.submit_contact(
            payload,
            idempotency_key=str(uuid.uuid4()),
            client_host="10.0.0.50",
            forwarded_for=None,
        )
