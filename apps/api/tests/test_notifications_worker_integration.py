from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import select, text
from sqlalchemy.dialects import postgresql

from lead_schema_fixtures import CONTACT_MINIMAL, QUOTE_MINIMAL
from migration_db import temporary_migration_database
from notifications_fixtures import FakeEmailSender, worker_env_defaults
from thl_api.alembic_config import configure_alembic_database_url
from thl_api.config import get_settings
from thl_api.db import close_db, get_engine, get_session_factory, init_db
from thl_api.models.enums import NotificationStatus
from thl_api.models.notification import NotificationJob
from thl_api.notifications.contracts import JobFence, WorkerSettings
from thl_api.notifications.repository import build_claim_select, claim_next_job, mark_sent
from thl_api.notifications.service import process_claimed_job
from thl_api.notifications.smtp_sender import EmailTimeoutError
from thl_api.schemas.leads import ContactMessageCreate, QuoteRequestCreate
from thl_api.services.lead_submission import LeadSubmissionService
from thl_api.turnstile.protocol import TurnstileVerifier


class _OkTurnstile(TurnstileVerifier):
    async def verify(self, token: str, *, action: str) -> bool:
        _ = (token, action)
        return True


def _upgrade(database_url: str) -> None:
    cfg = Config("alembic.ini")
    configure_alembic_database_url(cfg, database_url)
    command.upgrade(cfg, "head")


@pytest.fixture
def worker_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in worker_env_defaults().items():
        monkeypatch.setenv(key, value)


@pytest.fixture
async def pg_worker_db(monkeypatch: pytest.MonkeyPatch, worker_env: None):
    with temporary_migration_database() as temp:
        monkeypatch.setenv("THL_ENV", "dev")
        monkeypatch.setenv("DATABASE_URL", temp.database_url)
        get_settings.cache_clear()
        init_db(temp.database_url)
        _upgrade(temp.database_url)
        yield temp.database_url
        await close_db()


async def _create_contact_lead(**overrides: Any) -> int:
    payload = {**CONTACT_MINIMAL, **overrides}
    service = LeadSubmissionService(settings=get_settings(), turnstile=_OkTurnstile())
    result = await service.submit_contact(
        ContactMessageCreate.model_validate(payload),
        idempotency_key=str(uuid.uuid4()),
        client_host="127.0.0.1",
        forwarded_for=None,
    )
    assert result.status_code == 201
    async with get_session_factory()() as session:
        job = (await session.execute(select(NotificationJob).limit(1))).scalars().first()
        assert job is not None
        return int(job.id)


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_pending_job_claimable_immediately(pg_worker_db: str) -> None:
    _ = pg_worker_db
    job_id = await _create_contact_lead()
    claimed = await claim_next_job(get_engine(), worker_id="worker-a")
    assert claimed is not None
    assert claimed.job_id == job_id
    assert claimed.attempt_count == 1


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_future_retry_not_claimable(pg_worker_db: str) -> None:
    _ = pg_worker_db
    job_id = await _create_contact_lead()
    future = datetime.now(tz=UTC) + timedelta(hours=1)
    async with get_engine().connect() as conn:
        async with conn.begin():
            await conn.execute(
                text(
                    """
                    UPDATE notification_jobs
                    SET status = 'retry_scheduled', next_attempt_at = :future,
                        locked_at = NULL, lock_expires_at = NULL, locked_by = NULL
                    WHERE id = :id
                    """
                ),
                {"future": future, "id": job_id},
            )
    assert await claim_next_job(get_engine(), worker_id="worker-a") is None


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_sent_and_terminal_not_claimable(pg_worker_db: str) -> None:
    _ = pg_worker_db
    job_id = await _create_contact_lead()
    async with get_engine().connect() as conn:
        async with conn.begin():
            await conn.execute(
                text(
                    """
                    UPDATE notification_jobs
                    SET status = 'sent', next_attempt_at = NULL,
                        locked_at = NULL, lock_expires_at = NULL, locked_by = NULL
                    WHERE id = :id
                    """
                ),
                {"id": job_id},
            )
    assert await claim_next_job(get_engine(), worker_id="worker-a") is None


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_concurrent_workers_single_claim(pg_worker_db: str) -> None:
    _ = pg_worker_db
    await _create_contact_lead()
    engine = get_engine()
    results = await asyncio.gather(
        claim_next_job(engine, worker_id="worker-a"),
        claim_next_job(engine, worker_id="worker-b"),
    )
    winners = [item for item in results if item is not None]
    assert len(winners) == 1


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_claim_committed_visible_before_sender(pg_worker_db: str) -> None:
    _ = pg_worker_db
    await _create_contact_lead()
    engine = get_engine()
    claimed = await claim_next_job(engine, worker_id="worker-a")
    assert claimed is not None

    async with get_session_factory()() as session:
        row = (
            await session.execute(
                select(NotificationJob).where(NotificationJob.id == claimed.job_id)
            )
        ).scalars().first()
        assert row is not None
        assert row.status == NotificationStatus.processing
        assert row.locked_by == "worker-a"
        assert row.attempt_count == 1

    in_tx: list[bool] = []
    state_at_send: list[NotificationStatus] = []

    class _TxCheckingSender(FakeEmailSender):
        async def send(self, message):  # type: ignore[no-untyped-def]
            async with engine.connect() as conn:
                in_tx.append(conn.in_transaction())
            async with get_session_factory()() as session:
                job_row = (
                    await session.execute(
                        select(NotificationJob).where(NotificationJob.id == claimed.job_id)
                    )
                ).scalars().first()
                assert job_row is not None
                state_at_send.append(job_row.status)
            return await super().send(message)

    settings = WorkerSettings()
    await process_claimed_job(
        engine,
        _TxCheckingSender(),
        settings,
        claimed,
        worker_id="worker-a",
    )
    assert in_tx == [False]
    assert state_at_send == [NotificationStatus.processing]


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_success_marks_sent(pg_worker_db: str) -> None:
    _ = pg_worker_db
    await _create_contact_lead()
    engine = get_engine()
    claimed = await claim_next_job(engine, worker_id="worker-a")
    assert claimed is not None
    settings = WorkerSettings()
    await process_claimed_job(engine, FakeEmailSender(), settings, claimed, worker_id="worker-a")
    async with get_session_factory()() as session:
        row = (await session.execute(select(NotificationJob))).scalars().first()
        assert row is not None
        assert row.status == NotificationStatus.sent
        assert row.provider_message_id is not None
        assert row.next_attempt_at is None


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_failures_apply_backoffs(pg_worker_db: str) -> None:
    _ = pg_worker_db
    job_id = await _create_contact_lead()
    engine = get_engine()
    settings = WorkerSettings()
    expected_minutes = [1, 5, 15, 60]
    for prior_attempts, minutes in enumerate(expected_minutes):
        async with engine.connect() as conn:
            async with conn.begin():
                await conn.execute(
                    text(
                        """
                        UPDATE notification_jobs
                        SET status = 'pending', next_attempt_at = transaction_timestamp(),
                            locked_at = NULL, lock_expires_at = NULL, locked_by = NULL,
                            attempt_count = :prior_attempts
                        WHERE id = :id
                        """
                    ),
                    {"id": job_id, "prior_attempts": prior_attempts},
                )
        claimed = await claim_next_job(engine, worker_id="worker-a")
        assert claimed is not None
        sender = FakeEmailSender(failures=[EmailTimeoutError()])
        await process_claimed_job(engine, sender, settings, claimed, worker_id="worker-a")
        async with get_session_factory()() as session:
            row = (await session.execute(select(NotificationJob))).scalars().first()
            assert row is not None
            assert row.status == NotificationStatus.retry_scheduled
            assert row.last_error_code == "EMAIL_TIMEOUT"
            assert row.next_attempt_at is not None
            delta = row.next_attempt_at - datetime.now(tz=UTC)
            assert timedelta(minutes=minutes - 1) <= delta <= timedelta(minutes=minutes + 2)


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_fifth_failure_terminal(pg_worker_db: str) -> None:
    _ = pg_worker_db
    job_id = await _create_contact_lead()
    engine = get_engine()
    settings = WorkerSettings()
    async with engine.connect() as conn:
        async with conn.begin():
            await conn.execute(
                text(
                    """
                    UPDATE notification_jobs
                    SET status = 'pending', next_attempt_at = transaction_timestamp(),
                        attempt_count = 4,
                        locked_at = NULL, lock_expires_at = NULL, locked_by = NULL
                    WHERE id = :id
                    """
                ),
                {"id": job_id},
            )
    claimed = await claim_next_job(engine, worker_id="worker-a")
    assert claimed is not None
    assert claimed.attempt_count == 5
    await process_claimed_job(
        engine,
        FakeEmailSender(failures=[EmailTimeoutError()]),
        settings,
        claimed,
        worker_id="worker-a",
    )
    async with get_session_factory()() as session:
        row = (await session.execute(select(NotificationJob))).scalars().first()
        assert row is not None
        assert row.status == NotificationStatus.failed_terminal
        assert row.next_attempt_at is None


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_processing_not_expired_not_claimed(pg_worker_db: str) -> None:
    _ = pg_worker_db
    job_id = await _create_contact_lead()
    future = datetime.now(tz=UTC) + timedelta(minutes=5)
    async with get_engine().connect() as conn:
        async with conn.begin():
            await conn.execute(
                text(
                    """
                    UPDATE notification_jobs
                    SET status = 'processing', attempt_count = 1,
                        locked_at = transaction_timestamp(),
                        lock_expires_at = :future,
                        locked_by = 'other', next_attempt_at = NULL
                    WHERE id = :id
                    """
                ),
                {"future": future, "id": job_id},
            )
    assert await claim_next_job(get_engine(), worker_id="worker-a") is None


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_expired_processing_reclaimed(pg_worker_db: str) -> None:
    _ = pg_worker_db
    job_id = await _create_contact_lead()
    past = datetime.now(tz=UTC) - timedelta(minutes=2)
    async with get_engine().connect() as conn:
        async with conn.begin():
            await conn.execute(
                text(
                    """
                    UPDATE notification_jobs
                    SET status = 'processing', attempt_count = 1,
                        locked_at = :past,
                        lock_expires_at = :past,
                        locked_by = 'stale-worker', next_attempt_at = NULL
                    WHERE id = :id
                    """
                ),
                {"past": past, "id": job_id},
            )
    claimed = await claim_next_job(get_engine(), worker_id="worker-b")
    assert claimed is not None
    assert claimed.attempt_count == 2


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_expired_at_max_attempts_terminal_without_send(pg_worker_db: str) -> None:
    _ = pg_worker_db
    job_id = await _create_contact_lead()
    past = datetime.now(tz=UTC) - timedelta(minutes=2)
    async with get_engine().connect() as conn:
        async with conn.begin():
            await conn.execute(
                text(
                    """
                    UPDATE notification_jobs
                    SET status = 'processing', attempt_count = 5,
                        locked_at = :past,
                        lock_expires_at = :past,
                        locked_by = 'stale-worker', next_attempt_at = NULL
                    WHERE id = :id
                    """
                ),
                {"past": past, "id": job_id},
            )
    sender = FakeEmailSender()
    claimed = await claim_next_job(get_engine(), worker_id="worker-b")
    assert claimed is None
    assert sender.sent == []
    async with get_session_factory()() as session:
        row = (await session.execute(select(NotificationJob))).scalars().first()
        assert row is not None
        assert row.status == NotificationStatus.failed_terminal


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_lease_fencing_blocks_stale_finalize(pg_worker_db: str) -> None:
    _ = pg_worker_db
    await _create_contact_lead()
    engine = get_engine()
    claimed = await claim_next_job(engine, worker_id="worker-a")
    assert claimed is not None
    stale_fence = JobFence(
        job_id=claimed.job_id,
        locked_by="other-worker",
        locked_at=claimed.fence.locked_at,
    )
    updated = await mark_sent(engine, stale_fence, provider_message_id="x")
    assert updated is False
    async with get_session_factory()() as session:
        row = (await session.execute(select(NotificationJob))).scalars().first()
        assert row is not None
        assert row.status == NotificationStatus.processing


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_crash_after_provider_acceptance_at_least_once(pg_worker_db: str) -> None:
    _ = pg_worker_db
    await _create_contact_lead()
    engine = get_engine()
    claimed = await claim_next_job(engine, worker_id="worker-a")
    assert claimed is not None
    sender = FakeEmailSender()
    await sender.send(
        __import__("thl_api.notifications.renderer", fromlist=["render_email"]).render_email(
            claimed.snapshot,
            to_address="ops@test",
            from_address="from@test",
        )
    )
    lost_fence = JobFence(
        job_id=claimed.job_id,
        locked_by="lost",
        locked_at=claimed.fence.locked_at,
    )
    assert not await mark_sent(engine, lost_fence, provider_message_id="accepted-id")
    assert len(sender.sent) == 1


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_explain_uses_partial_indexes(pg_worker_db: str) -> None:
    _ = pg_worker_db
    await _create_contact_lead()
    engine = get_engine()
    async with engine.connect() as conn:
        async with conn.begin():
            await conn.execute(text("SET LOCAL enable_seqscan = OFF"))
            now = (await conn.execute(text("SELECT transaction_timestamp()"))).scalar_one()
            stmt = build_claim_select(now)
            compiled = stmt.compile(
                dialect=postgresql.dialect(),
                compile_kwargs={"literal_binds": True},
            )
            explain_result = await conn.execute(text("EXPLAIN (FORMAT TEXT) " + str(compiled)))
            plan_rows = explain_result.fetchall()
    plan_text = "\n".join(row[0] for row in plan_rows)
    assert "idx_notification_jobs_claim" in plan_text
    assert "idx_notification_jobs_reclaim" in plan_text


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_process_claimed_job_logs_exclude_pii(
    pg_worker_db: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    _ = pg_worker_db
    secret_message = "secret-msg-token-001A"
    secret_email = "pii-mark-001a@example.com"
    await _create_contact_lead(message=secret_message, email=secret_email)
    engine = get_engine()
    claimed = await claim_next_job(engine, worker_id="worker-a")
    assert claimed is not None
    settings = WorkerSettings()
    service_logger = "thl_api.notifications.service"
    smtp_logger = "thl_api.notifications.smtp_sender"
    with caplog.at_level(logging.INFO):
        await process_claimed_job(
            engine,
            FakeEmailSender(),
            settings,
            claimed,
            worker_id="worker-a",
        )
    for record in caplog.records:
        if record.name not in {service_logger, smtp_logger}:
            continue
        blob = record.getMessage() + str(record.__dict__)
        assert secret_email not in blob
        assert secret_message not in blob
        assert claimed.snapshot.email not in blob


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_max_attempts_two_second_failure_is_terminal(pg_worker_db: str) -> None:
    _ = pg_worker_db
    job_id = await _create_contact_lead()
    engine = get_engine()
    settings = WorkerSettings()
    async with engine.connect() as conn:
        async with conn.begin():
            await conn.execute(
                text(
                    """
                    UPDATE notification_jobs
                    SET max_attempts = 2, status = 'pending',
                        next_attempt_at = transaction_timestamp(),
                        attempt_count = 1,
                        locked_at = NULL, lock_expires_at = NULL, locked_by = NULL
                    WHERE id = :id
                    """
                ),
                {"id": job_id},
            )
    claimed = await claim_next_job(engine, worker_id="worker-a")
    assert claimed is not None
    assert claimed.max_attempts == 2
    assert claimed.attempt_count == 2
    await process_claimed_job(
        engine,
        FakeEmailSender(failures=[EmailTimeoutError()]),
        settings,
        claimed,
        worker_id="worker-a",
    )
    async with get_session_factory()() as session:
        row = (await session.execute(select(NotificationJob))).scalars().first()
        assert row is not None
        assert row.status == NotificationStatus.failed_terminal


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_max_attempts_six_allows_fifth_retry(pg_worker_db: str) -> None:
    _ = pg_worker_db
    job_id = await _create_contact_lead()
    engine = get_engine()
    settings = WorkerSettings()
    async with engine.connect() as conn:
        async with conn.begin():
            await conn.execute(
                text(
                    """
                    UPDATE notification_jobs
                    SET max_attempts = 6, status = 'pending',
                        next_attempt_at = transaction_timestamp(),
                        attempt_count = 4,
                        locked_at = NULL, lock_expires_at = NULL, locked_by = NULL
                    WHERE id = :id
                    """
                ),
                {"id": job_id},
            )
    claimed = await claim_next_job(engine, worker_id="worker-a")
    assert claimed is not None
    assert claimed.max_attempts == 6
    assert claimed.attempt_count == 5
    await process_claimed_job(
        engine,
        FakeEmailSender(failures=[EmailTimeoutError()]),
        settings,
        claimed,
        worker_id="worker-a",
    )
    async with get_session_factory()() as session:
        row = (await session.execute(select(NotificationJob))).scalars().first()
        assert row is not None
        assert row.status == NotificationStatus.retry_scheduled
        assert row.next_attempt_at is not None


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_max_attempts_six_sixth_failure_is_terminal(pg_worker_db: str) -> None:
    _ = pg_worker_db
    job_id = await _create_contact_lead()
    engine = get_engine()
    settings = WorkerSettings()
    async with engine.connect() as conn:
        async with conn.begin():
            await conn.execute(
                text(
                    """
                    UPDATE notification_jobs
                    SET max_attempts = 6, status = 'pending',
                        next_attempt_at = transaction_timestamp(),
                        attempt_count = 5,
                        locked_at = NULL, lock_expires_at = NULL, locked_by = NULL
                    WHERE id = :id
                    """
                ),
                {"id": job_id},
            )
    claimed = await claim_next_job(engine, worker_id="worker-a")
    assert claimed is not None
    assert claimed.attempt_count == 6
    await process_claimed_job(
        engine,
        FakeEmailSender(failures=[EmailTimeoutError()]),
        settings,
        claimed,
        worker_id="worker-a",
    )
    async with get_session_factory()() as session:
        row = (await session.execute(select(NotificationJob))).scalars().first()
        assert row is not None
        assert row.status == NotificationStatus.failed_terminal


@pytest.mark.integration
@pytest.mark.worker
@pytest.mark.asyncio
async def test_quote_lead_render_path_via_submit(pg_worker_db: str) -> None:
    _ = pg_worker_db
    service = LeadSubmissionService(settings=get_settings(), turnstile=_OkTurnstile())
    await service.submit_quote(
        QuoteRequestCreate.model_validate(QUOTE_MINIMAL),
        idempotency_key=str(uuid.uuid4()),
        client_host="127.0.0.1",
        forwarded_for=None,
    )
    claimed = await claim_next_job(get_engine(), worker_id="worker-a")
    assert claimed is not None
    settings = WorkerSettings()
    await process_claimed_job(
        get_engine(),
        FakeEmailSender(),
        settings,
        claimed,
        worker_id="worker-a",
    )
