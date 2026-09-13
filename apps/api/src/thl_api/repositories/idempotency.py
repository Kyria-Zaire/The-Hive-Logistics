from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from thl_api.leads.hmac_keyring import HmacKeyring
from thl_api.models.enums import IdempotencyScope


@dataclass(frozen=True, slots=True)
class IdempotencyRecordRow:
    payload_fingerprint: str
    fingerprint_key_version: int
    fingerprint_algo_version: int
    response_body: dict[str, object]


async def find_idempotency_record(
    connection: AsyncConnection,
    *,
    scope: IdempotencyScope,
    idempotency_key: str,
    keyring: HmacKeyring,
) -> IdempotencyRecordRow | None:
    message = f"{scope.value}|{idempotency_key}".encode()
    stmt = text(
        """
        SELECT payload_fingerprint, fingerprint_key_version, fingerprint_algo_version, response_body
        FROM idempotency_records
        WHERE scope = CAST(:scope AS idempotency_scope_enum)
          AND key_digest = :key_digest
        LIMIT 1
        """
    )
    for digest, _version in keyring.digests_for_lookup(message):
        result = await connection.execute(
            stmt,
            {"scope": scope.value, "key_digest": digest},
        )
        row = result.one_or_none()
        if row is None:
            continue
        body = row.response_body
        if not isinstance(body, dict):
            continue
        return IdempotencyRecordRow(
            payload_fingerprint=row.payload_fingerprint,
            fingerprint_key_version=row.fingerprint_key_version,
            fingerprint_algo_version=row.fingerprint_algo_version,
            response_body=body,
        )
    return None


def expires_at_from_ttl(*, accepted_at: datetime, ttl_seconds: int) -> datetime:
    return accepted_at + timedelta(seconds=ttl_seconds)


def utc_now() -> datetime:
    from datetime import UTC

    return datetime.now(UTC)
