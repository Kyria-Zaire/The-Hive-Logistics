from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import ColumnElement, Select, and_, func, or_, select, text, update
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, async_sessionmaker

from thl_api.models.enums import LeadType, NotificationStatus
from thl_api.models.lead import ContactMessageDetail, Lead, QuoteRequestDetail
from thl_api.models.notification import NotificationJob
from thl_api.notifications.contracts import (
    LOCK_LEASE_SECONDS,
    ClaimedJob,
    ContactLeadSnapshot,
    JobFence,
    LeadSnapshot,
    QuoteLeadSnapshot,
)

logger = logging.getLogger(__name__)

_CONTACT_SUBJECT_LABELS = {
    "information": "Information",
    "quote": "Devis",
    "partnership": "Partenariat",
    "other": "Autre",
}

_SERVICE_LABELS = {
    "convoyage_premium": "Convoyage premium",
    "fleet_coordination": "Coordination de flotte",
    "automotive_logistics": "Logistique automobile",
    "vehicle_preparation": "Préparation véhicule",
}

_VEHICLE_LABELS = {
    "city_sedan": "Berline citadine",
    "suv_4x4": "SUV / 4x4",
    "premium_sport": "Premium / sport",
    "light_commercial": "Utilitaire léger",
    "classic_collector": "Classique / collection",
    "other": "Autre",
}

_CONTACT_PREF_LABELS = {
    "email": "Email",
    "phone": "Téléphone",
    "no_preference": "Sans préférence",
}


def _eligible_jobs_clause(now: datetime) -> ColumnElement[bool]:
    return or_(
        and_(
            NotificationJob.status.in_(
                (NotificationStatus.pending, NotificationStatus.retry_scheduled)
            ),
            NotificationJob.next_attempt_at <= now,
        ),
        and_(
            NotificationJob.status == NotificationStatus.processing,
            NotificationJob.lock_expires_at.is_not(None),
            NotificationJob.lock_expires_at < now,
        ),
    )


async def _load_snapshot(
    session: AsyncSession,
    lead_id: int,
) -> tuple[LeadType, LeadSnapshot]:
    row = await session.get(Lead, lead_id)
    if row is None:
        msg = f"Lead {lead_id} not found"
        raise RuntimeError(msg)
    if row.lead_type == LeadType.contact:
        detail = (
            await session.execute(
                select(ContactMessageDetail).where(ContactMessageDetail.lead_id == lead_id),
            )
        ).scalars().first()
        if detail is None:
            msg = f"Contact detail for lead {lead_id} not found"
            raise RuntimeError(msg)
        subject = _CONTACT_SUBJECT_LABELS.get(detail.subject.value, detail.subject.value)
        snapshot: LeadSnapshot = ContactLeadSnapshot(
            public_reference=row.public_reference,
            received_at=row.created_at,
            first_name=row.first_name,
            last_name=row.last_name,
            email=row.email,
            phone=row.phone,
            company=row.company,
            subject=subject,
            message=detail.message,
        )
        return LeadType.contact, snapshot

    quote_detail = (
        await session.execute(
            select(QuoteRequestDetail).where(QuoteRequestDetail.lead_id == lead_id),
        )
    ).scalars().first()
    if quote_detail is None:
        msg = f"Quote detail for lead {lead_id} not found"
        raise RuntimeError(msg)
    if quote_detail.timing_kind.value == "exact_date" and quote_detail.exact_date is not None:
        timing_label = quote_detail.exact_date.isoformat()
    else:
        timing_label = quote_detail.period_text or ""
    category = quote_detail.vehicle_category.value
    if quote_detail.vehicle_category_other_detail:
        category = (
            f"{_VEHICLE_LABELS.get(category, category)} "
            f"({quote_detail.vehicle_category_other_detail})"
        )
    else:
        category = _VEHICLE_LABELS.get(category, category)
    pref = quote_detail.contact_preference
    pref_label = _CONTACT_PREF_LABELS.get(pref.value, pref.value) if pref else None
    snapshot = QuoteLeadSnapshot(
        public_reference=row.public_reference,
        received_at=row.created_at,
        first_name=row.first_name,
        last_name=row.last_name,
        email=row.email,
        phone=row.phone,
        company=row.company,
        service=_SERVICE_LABELS.get(quote_detail.service.value, quote_detail.service.value),
        departure_city=quote_detail.departure_city,
        departure_postal_code=quote_detail.departure_postal_code,
        arrival_city=quote_detail.arrival_city,
        arrival_postal_code=quote_detail.arrival_postal_code,
        timing_label=timing_label,
        vehicle_category=category,
        vehicle_make=quote_detail.vehicle_make,
        vehicle_model=quote_detail.vehicle_model,
        vehicle_rolling=quote_detail.vehicle_rolling,
        special_constraints=quote_detail.special_constraints,
        additional_message=quote_detail.additional_message,
        contact_preference=pref_label,
    )
    return LeadType.quote, snapshot


async def _finalize_terminal_at_max_attempts(
    connection: AsyncConnection,
    job: NotificationJob,
    *,
    now: datetime,
) -> None:
    await connection.execute(
        update(NotificationJob)
        .where(NotificationJob.id == job.id)
        .values(
            status=NotificationStatus.failed_terminal,
            next_attempt_at=None,
            locked_at=None,
            lock_expires_at=None,
            locked_by=None,
            last_error_code="EMAIL_PROVIDER_ERROR",
            updated_at=now,
        )
    )
    logger.error(
        "Notification job failed terminally after max attempts on reclaim",
        extra={
            "event": "notification_job_failed_terminal",
            "job_id": job.id,
            "attempt_count": job.attempt_count,
            "error_code": "EMAIL_PROVIDER_ERROR",
        },
    )


def build_claim_select(now: datetime) -> Select[tuple[NotificationJob]]:
    return (
        select(NotificationJob)
        .where(_eligible_jobs_clause(now))
        .order_by(
            func.coalesce(NotificationJob.next_attempt_at, NotificationJob.lock_expires_at),
            NotificationJob.id,
        )
        .limit(1)
        .with_for_update(skip_locked=True)
    )


async def claim_next_job(
    engine: AsyncEngine,
    *,
    worker_id: str,
    lock_lease_seconds: int = LOCK_LEASE_SECONDS,
    session_factory: async_sessionmaker[AsyncSession] | None = None,
) -> ClaimedJob | None:
    from thl_api.db import get_session_factory

    factory = session_factory or get_session_factory()
    async with factory() as session:
        async with session.begin():
            connection = await session.connection()
            now = (await connection.execute(text("SELECT transaction_timestamp()"))).scalar_one()
            if not isinstance(now, datetime):
                msg = "transaction_timestamp() returned unexpected type"
                raise TypeError(msg)

            stmt = build_claim_select(now)
            job = (await session.execute(stmt)).scalars().first()
            if job is None:
                return None

            if (
                job.status == NotificationStatus.processing
                and job.lock_expires_at is not None
                and job.lock_expires_at < now
                and job.attempt_count >= job.max_attempts
            ):
                await _finalize_terminal_at_max_attempts(connection, job, now=now)
                return None

            locked_at = now
            lock_expires_at = locked_at + timedelta(seconds=lock_lease_seconds)
            new_attempt_count = job.attempt_count + 1

            await session.execute(
                update(NotificationJob)
                .where(NotificationJob.id == job.id)
                .values(
                    status=NotificationStatus.processing,
                    attempt_count=new_attempt_count,
                    locked_at=locked_at,
                    lock_expires_at=lock_expires_at,
                    locked_by=worker_id,
                    updated_at=now,
                )
            )

            lead_type, snapshot = await _load_snapshot(session, job.lead_id)
            job_id = job.id
            max_attempts = job.max_attempts
            notification_kind = job.notification_kind

        fence = JobFence(job_id=job_id, locked_by=worker_id, locked_at=locked_at)
        return ClaimedJob(
            job_id=job_id,
            attempt_count=new_attempt_count,
            max_attempts=max_attempts,
            notification_kind=notification_kind,
            fence=fence,
            lead_type=lead_type,
            snapshot=snapshot,
        )


async def mark_sent(
    engine: AsyncEngine,
    fence: JobFence,
    *,
    provider_message_id: str,
) -> bool:
    async with engine.connect() as connection:
        async with connection.begin():
            now = datetime.now(tz=UTC)
            trimmed = provider_message_id[:128]
            result = await connection.execute(
                update(NotificationJob)
                .where(
                    NotificationJob.id == fence.job_id,
                    NotificationJob.status == NotificationStatus.processing,
                    NotificationJob.locked_by == fence.locked_by,
                    NotificationJob.locked_at == fence.locked_at,
                )
                .values(
                    status=NotificationStatus.sent,
                    provider_message_id=trimmed,
                    next_attempt_at=None,
                    locked_at=None,
                    lock_expires_at=None,
                    locked_by=None,
                    last_error_code=None,
                    updated_at=now,
                )
            )
            return result.rowcount == 1


async def mark_retry_or_terminal(
    engine: AsyncEngine,
    fence: JobFence,
    *,
    attempt_count: int,
    max_attempts: int,
    error_code: str,
    next_attempt_at: datetime | None,
) -> bool:
    async with engine.connect() as connection:
        async with connection.begin():
            now = datetime.now(tz=UTC)
            if next_attempt_at is None:
                status = NotificationStatus.failed_terminal
                values = {
                    "status": status,
                    "next_attempt_at": None,
                    "locked_at": None,
                    "lock_expires_at": None,
                    "locked_by": None,
                    "last_error_code": error_code[:64],
                    "updated_at": now,
                }
            else:
                status = NotificationStatus.retry_scheduled
                values = {
                    "status": status,
                    "next_attempt_at": next_attempt_at,
                    "locked_at": None,
                    "lock_expires_at": None,
                    "locked_by": None,
                    "last_error_code": error_code[:64],
                    "updated_at": now,
                }
            result = await connection.execute(
                update(NotificationJob)
                .where(
                    NotificationJob.id == fence.job_id,
                    NotificationJob.status == NotificationStatus.processing,
                    NotificationJob.locked_by == fence.locked_by,
                    NotificationJob.locked_at == fence.locked_at,
                )
                .values(**values)
            )
            updated = result.rowcount == 1
            if updated and status == NotificationStatus.failed_terminal:
                logger.error(
                    "Notification job failed terminally",
                    extra={
                        "event": "notification_job_failed_terminal",
                        "job_id": fence.job_id,
                        "attempt_count": attempt_count,
                        "error_code": error_code,
                    },
                )
            return updated
