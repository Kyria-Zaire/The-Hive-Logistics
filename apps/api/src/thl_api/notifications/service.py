from __future__ import annotations

import logging
import time
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncEngine

from thl_api.notifications.contracts import (
    ClaimedJob,
    EmailSender,
    WorkerSettings,
    backoff_after_failure,
)
from thl_api.notifications.renderer import render_email
from thl_api.notifications.repository import mark_retry_or_terminal, mark_sent
from thl_api.notifications.smtp_sender import EmailSendError

logger = logging.getLogger(__name__)


async def process_claimed_job(
    engine: AsyncEngine,
    sender: EmailSender,
    settings: WorkerSettings,
    job: ClaimedJob,
    *,
    worker_id: str,
) -> None:
    public_reference = job.snapshot.public_reference
    started = time.perf_counter()
    outbound = render_email(
        job.snapshot,
        to_address=settings.notification_email_to,
        from_address=settings.notification_email_from,
    )
    try:
        result = await sender.send(outbound)
    except EmailSendError as exc:
        delay = backoff_after_failure(job.attempt_count, max_attempts=job.max_attempts)
        next_at = datetime.now(tz=UTC) + delay if delay is not None else None
        error_code = exc.code
        updated = await mark_retry_or_terminal(
            engine,
            job.fence,
            attempt_count=job.attempt_count,
            max_attempts=job.max_attempts,
            error_code=error_code,
            next_attempt_at=next_at,
        )
        if not updated:
            logger.warning(
                "Notification finalize skipped after send failure (lease lost)",
                extra={
                    "event": "notification_lease_lost",
                    "job_id": job.job_id,
                    "public_reference": public_reference,
                    "attempt_count": job.attempt_count,
                    "worker_id": worker_id,
                    "error_code": "LEASE_LOST",
                },
            )
            return
        logger.info(
            "Notification send failed; retry scheduled"
            if next_at is not None
            else "Notification send failed; terminal",
            extra={
                "event": "notification_send_failed",
                "job_id": job.job_id,
                "public_reference": public_reference,
                "attempt_count": job.attempt_count,
                "worker_id": worker_id,
                "error_code": error_code,
                "duration_ms": int((time.perf_counter() - started) * 1000),
            },
        )
        return

    updated = await mark_sent(engine, job.fence, provider_message_id=result.provider_message_id)
    if not updated:
        logger.warning(
            "Notification success not persisted (lease lost)",
            extra={
                "event": "notification_lease_lost",
                "job_id": job.job_id,
                "public_reference": public_reference,
                "attempt_count": job.attempt_count,
                "worker_id": worker_id,
                "error_code": "LEASE_LOST",
            },
        )
        return
    logger.info(
        "Notification sent",
        extra={
            "event": "notification_sent",
            "job_id": job.job_id,
            "public_reference": public_reference,
            "attempt_count": job.attempt_count,
            "worker_id": worker_id,
            "duration_ms": int((time.perf_counter() - started) * 1000),
        },
    )
