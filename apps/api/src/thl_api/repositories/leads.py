from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime

from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection

from thl_api.models.enums import (
    IdempotencyScope,
    LeadType,
    NotificationKind,
    NotificationStatus,
    TimingKind,
)
from thl_api.models.idempotency import IdempotencyRecord
from thl_api.models.lead import ContactMessageDetail, Lead, QuoteRequestDetail
from thl_api.models.notification import NotificationJob
from thl_api.schemas.leads import ContactMessageCreate, QuoteRequestCreate


def _is_public_reference_collision(exc: IntegrityError) -> bool:
    orig = exc.orig
    if orig is None:
        return False
    diag = getattr(orig, "diag", None)
    constraint = getattr(diag, "constraint_name", None) if diag is not None else None
    return constraint == "uq_leads_public_reference"


async def insert_lead_bundle(
    connection: AsyncConnection,
    *,
    scope: IdempotencyScope,
    lead_type: LeadType,
    body: QuoteRequestCreate | ContactMessageCreate,
    privacy_policy_version: str,
    accepted_at: datetime,
    public_reference: str,
    response_body: dict[str, object],
    idempotency_fields: dict[str, object],
    max_notification_attempts: int = 5,
) -> None:
    lead_stmt = (
        insert(Lead)
        .values(
            public_reference=public_reference,
            lead_type=lead_type,
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
            phone=getattr(body, "phone", None),
            company=getattr(body, "company", None),
            privacy_acknowledgement=True,
            privacy_policy_version=privacy_policy_version,
            privacy_acknowledged_at=accepted_at,
            created_at=accepted_at,
            updated_at=accepted_at,
        )
        .returning(Lead.id)
    )
    lead_id = (await connection.execute(lead_stmt)).scalar_one()

    if isinstance(body, QuoteRequestCreate):
        timing = body.preferred_timing
        if timing.kind == "exact_date":
            timing_kind = TimingKind.exact_date
            exact_date: date | None = timing.exact_date
            period_text = None
        else:
            timing_kind = TimingKind.period
            exact_date = None
            period_text = timing.period_text
        detail_stmt = insert(QuoteRequestDetail).values(
            lead_id=lead_id,
            service=body.service,
            departure_city=body.departure_city,
            departure_postal_code=body.departure_postal_code,
            arrival_city=body.arrival_city,
            arrival_postal_code=body.arrival_postal_code,
            timing_kind=timing_kind,
            exact_date=exact_date,
            period_text=period_text,
            vehicle_category=body.vehicle_category,
            vehicle_category_other_detail=body.vehicle_category_other_detail,
            vehicle_make=body.vehicle_make,
            vehicle_model=body.vehicle_model,
            vehicle_rolling=body.vehicle_rolling,
            special_constraints=body.special_constraints,
            additional_message=body.additional_message,
            contact_preference=body.contact_preference,
        )
        await connection.execute(detail_stmt)
    else:
        contact_stmt = insert(ContactMessageDetail).values(
            lead_id=lead_id,
            subject=body.subject,
            message=body.message,
        )
        await connection.execute(contact_stmt)

    idem_stmt = insert(IdempotencyRecord).values(
        scope=scope,
        lead_id=lead_id,
        created_at=accepted_at,
        **idempotency_fields,
    )
    await connection.execute(idem_stmt)

    notif_stmt = insert(NotificationJob).values(
        lead_id=lead_id,
        notification_kind=NotificationKind.internal_email,
        status=NotificationStatus.pending,
        attempt_count=0,
        max_attempts=max_notification_attempts,
        next_attempt_at=accepted_at,
        created_at=accepted_at,
        updated_at=accepted_at,
    )
    await connection.execute(notif_stmt)


async def insert_lead_with_reference_retry(
    connection: AsyncConnection,
    *,
    scope: IdempotencyScope,
    lead_type: LeadType,
    body: QuoteRequestCreate | ContactMessageCreate,
    privacy_policy_version: str,
    accepted_at: datetime,
    response_body_template: dict[str, object],
    idempotency_fields: dict[str, object],
    reference_generator: Callable[[datetime], str],
    max_attempts: int = 8,
) -> str:
    last_error: Exception | None = None
    for _ in range(max_attempts):
        public_reference = reference_generator(accepted_at)
        response_body: dict[str, object] = {
            **response_body_template,
            "public_reference": public_reference,
        }
        fields = {
            **idempotency_fields,
            "response_body": response_body,
        }
        try:
            async with connection.begin_nested():
                await insert_lead_bundle(
                    connection,
                    scope=scope,
                    lead_type=lead_type,
                    body=body,
                    privacy_policy_version=privacy_policy_version,
                    accepted_at=accepted_at,
                    public_reference=public_reference,
                    response_body=response_body,
                    idempotency_fields=fields,
                )
        except IntegrityError as exc:
            if not _is_public_reference_collision(exc):
                raise
            last_error = exc
            continue
        return public_reference
    msg = "public_reference collision retries exhausted"
    raise RuntimeError(msg) from last_error
