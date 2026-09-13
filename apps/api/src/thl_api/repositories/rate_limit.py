from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from thl_api.leads.hmac_keyring import HmacKeyring
from thl_api.models.enums import RateLimitScope


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    allowed: bool
    retry_after_seconds: int


def subject_digest_hex(
    keyring: HmacKeyring,
    scope: RateLimitScope,
    client_ip: str,
) -> tuple[str, int]:
    message = f"{scope.value}|{client_ip}".encode()
    return keyring.digest_hex(message)


def window_bounds(
    now: datetime,
    *,
    window_seconds: int,
) -> tuple[datetime, datetime]:
    if now.tzinfo is None:
        msg = "now must be timezone-aware"
        raise ValueError(msg)
    epoch = int(now.timestamp())
    start_epoch = epoch - (epoch % window_seconds)
    window_start = datetime.fromtimestamp(start_epoch, tz=UTC)
    expires = window_start + timedelta(seconds=window_seconds)
    return window_start, expires


async def increment_and_check(
    connection: AsyncConnection,
    *,
    scope: RateLimitScope,
    subject_digest: str,
    key_version: int,
    window_started_at: datetime,
    expires_at: datetime,
    max_requests: int,
    now: datetime,
) -> RateLimitDecision:
    stmt = text(
        """
        INSERT INTO rate_limit_buckets (
            scope, subject_digest, key_version, window_started_at,
            request_count, expires_at, created_at, updated_at
        ) VALUES (
            CAST(:scope AS rate_limit_scope_enum),
            :subject_digest,
            :key_version,
            :window_started_at,
            1,
            :expires_at,
            :now,
            :now
        )
        ON CONFLICT (scope, subject_digest, window_started_at)
        DO UPDATE SET
            request_count = rate_limit_buckets.request_count + 1,
            updated_at = EXCLUDED.updated_at
        RETURNING request_count, expires_at
        """
    )
    result = await connection.execute(
        stmt,
        {
            "scope": scope.value,
            "subject_digest": subject_digest,
            "key_version": key_version,
            "window_started_at": window_started_at,
            "expires_at": expires_at,
            "now": now,
        },
    )
    row = result.one()
    count = int(row.request_count)
    row_expires: datetime = row.expires_at
    if count > max_requests:
        retry = max(1, int((row_expires - now).total_seconds()))
        return RateLimitDecision(allowed=False, retry_after_seconds=retry)
    return RateLimitDecision(allowed=True, retry_after_seconds=0)
