from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from thl_api.config import Settings
from thl_api.db import get_engine
from thl_api.leads.fingerprint import idempotency_key_digest_hex, payload_fingerprint_hex
from thl_api.leads.lock_id import advisory_lock_id
from thl_api.leads.public_reference import public_reference_for_accepted_at
from thl_api.leads.trusted_proxy import client_ip_for_rate_limit
from thl_api.models.enums import IdempotencyScope, LeadType, RateLimitScope
from thl_api.repositories.advisory_lock import (
    AdvisoryLockBusyError,
    AdvisoryUnlockFailedError,
    release_session_lock,
    try_acquire_session_lock,
)
from thl_api.repositories.idempotency import expires_at_from_ttl, find_idempotency_record, utc_now
from thl_api.repositories.leads import insert_lead_with_reference_retry
from thl_api.repositories.rate_limit import increment_and_check, subject_digest_hex, window_bounds
from thl_api.schemas.leads import ContactMessageCreate, QuoteRequestCreate
from thl_api.turnstile.httpx_client import TurnstileUnavailableError
from thl_api.turnstile.protocol import TurnstileAction, TurnstileVerifier

_TurnstileBody = QuoteRequestCreate | ContactMessageCreate

logger = logging.getLogger(__name__)


class HoneypotTriggeredError(Exception):
    pass


class TurnstileRejectedError(Exception):
    pass


class IdempotencyConflictError(Exception):
    pass


class IdempotencyBusyError(Exception):
    pass


class RateLimitExceededError(Exception):
    def __init__(self, retry_after_seconds: int) -> None:
        self.retry_after_seconds = retry_after_seconds
        super().__init__("rate limited")


@dataclass(frozen=True, slots=True)
class SubmissionSuccess:
    body: dict[str, object]
    status_code: Literal[200, 201]
    replayed: bool


@dataclass(frozen=True, slots=True)
class LeadSubmissionService:
    settings: Settings
    turnstile: TurnstileVerifier
    engine: AsyncEngine | None = None

    def _engine(self) -> AsyncEngine:
        return self.engine if self.engine is not None else get_engine()

    async def submit_quote(
        self,
        body: QuoteRequestCreate,
        *,
        idempotency_key: str,
        client_host: str | None,
        forwarded_for: str | None,
    ) -> SubmissionSuccess:
        return await self._submit(
            scope=IdempotencyScope.quote_requests,
            rate_scope=RateLimitScope.quote_requests,
            lead_type=LeadType.quote,
            body=body,
            turnstile_action="quote_request",
            idempotency_key=idempotency_key,
            client_host=client_host,
            forwarded_for=forwarded_for,
        )

    async def submit_contact(
        self,
        body: ContactMessageCreate,
        *,
        idempotency_key: str,
        client_host: str | None,
        forwarded_for: str | None,
    ) -> SubmissionSuccess:
        return await self._submit(
            scope=IdempotencyScope.contact_messages,
            rate_scope=RateLimitScope.contact_messages,
            lead_type=LeadType.contact,
            body=body,
            turnstile_action="contact_message",
            idempotency_key=idempotency_key,
            client_host=client_host,
            forwarded_for=forwarded_for,
        )

    async def _submit(
        self,
        *,
        scope: IdempotencyScope,
        rate_scope: RateLimitScope,
        lead_type: LeadType,
        body: _TurnstileBody,
        turnstile_action: TurnstileAction,
        idempotency_key: str,
        client_host: str | None,
        forwarded_for: str | None,
    ) -> SubmissionSuccess:
        if getattr(body, "honeypot", ""):
            raise HoneypotTriggeredError

        client_ip = client_ip_for_rate_limit(
            direct_host=client_host,
            forwarded_for=forwarded_for,
            trusted_proxy_enabled=self.settings.trusted_proxy_enabled,
        )
        await self._enforce_rate_limit(rate_scope, client_ip)

        fingerprint, fp_version = payload_fingerprint_hex(
            self.settings.fingerprint_keyring(),
            scope,
            body,
            fingerprint_algo_version=self.settings.fingerprint_algo_version,
        )
        lock_id = advisory_lock_id(scope.value, idempotency_key)

        connection = await self._engine().connect()
        lock_held = False
        invalidate_connection = False
        try:
            try:
                await try_acquire_session_lock(connection, lock_id)
            except AdvisoryLockBusyError as exc:
                raise IdempotencyBusyError(str(exc)) from exc
            lock_held = True

            record = await find_idempotency_record(
                connection,
                scope=scope,
                idempotency_key=idempotency_key,
                keyring=self.settings.idempotency_keyring(),
            )
            if record is not None:
                recomputed, _ = payload_fingerprint_hex(
                    self.settings.fingerprint_keyring(),
                    scope,
                    body,
                    fingerprint_algo_version=record.fingerprint_algo_version,
                    for_key_version=record.fingerprint_key_version,
                )
                if recomputed != record.payload_fingerprint:
                    raise IdempotencyConflictError
                return SubmissionSuccess(
                    body=dict(record.response_body),
                    status_code=200,
                    replayed=True,
                )

            try:
                token: str = body.turnstile_token
                valid = await self.turnstile.verify(token, action=turnstile_action)
            except TurnstileUnavailableError:
                raise
            if not valid:
                raise TurnstileRejectedError

            await connection.rollback()
            async with connection.begin():
                accepted_at = (
                    await connection.execute(text("SELECT transaction_timestamp()"))
                ).scalar_one()
                if not isinstance(accepted_at, datetime):
                    msg = "transaction_timestamp() returned unexpected type"
                    raise TypeError(msg)
                if accepted_at.tzinfo is None:
                    accepted_at = accepted_at.replace(tzinfo=UTC)

                created_at_iso = accepted_at.astimezone(UTC).isoformat().replace(
                    "+00:00",
                    "Z",
                )
                response_template: dict[str, object] = {
                    "status": "received",
                    "created_at": created_at_iso,
                }
                key_digest, key_version = idempotency_key_digest_hex(
                    self.settings.idempotency_keyring(),
                    scope,
                    idempotency_key,
                )
                expires_at = expires_at_from_ttl(
                    accepted_at=accepted_at,
                    ttl_seconds=self.settings.idempotency_ttl_seconds,
                )
                idem_fields = {
                    "key_digest": key_digest,
                    "key_version": key_version,
                    "fingerprint_key_version": fp_version,
                    "fingerprint_algo_version": self.settings.fingerprint_algo_version,
                    "payload_fingerprint": fingerprint,
                    "original_status_code": 201,
                    "expires_at": expires_at,
                }
                public_reference = await insert_lead_with_reference_retry(
                    connection,
                    scope=scope,
                    lead_type=lead_type,
                    body=body,
                    privacy_policy_version=self.settings.privacy_policy_version,
                    accepted_at=accepted_at,
                    response_body_template=response_template,
                    idempotency_fields=idem_fields,
                    reference_generator=public_reference_for_accepted_at,
                )
                final_body = {
                    "public_reference": public_reference,
                    "status": "received",
                    "created_at": created_at_iso,
                }
                return SubmissionSuccess(
                    body=dict(final_body),
                    status_code=201,
                    replayed=False,
                )
        finally:
            if lock_held:
                try:
                    await connection.rollback()
                    await release_session_lock(connection, lock_id)
                except AdvisoryUnlockFailedError:
                    invalidate_connection = True
                    logger.error(
                        "Advisory unlock failed; invalidating connection",
                        extra={"lock_id": lock_id},
                    )
            if invalidate_connection:
                await connection.invalidate()
            else:
                await connection.close()

    async def _enforce_rate_limit(self, scope: RateLimitScope, client_ip: str) -> None:
        settings = self.settings
        if scope == RateLimitScope.quote_requests:
            max_requests = settings.rate_limit_quote_requests_max
            window_seconds = settings.rate_limit_quote_requests_window_seconds
        else:
            max_requests = settings.rate_limit_contact_messages_max
            window_seconds = settings.rate_limit_contact_messages_window_seconds
        if max_requests is None or window_seconds is None:
            msg = "Rate limit thresholds are not configured"
            raise RuntimeError(msg)

        digest, key_version = subject_digest_hex(
            settings.rate_limit_keyring(),
            scope,
            client_ip,
        )
        now = utc_now()
        window_start, expires = window_bounds(now, window_seconds=window_seconds)
        async with self._engine().connect() as connection:
            async with connection.begin():
                decision = await increment_and_check(
                    connection,
                    scope=scope,
                    subject_digest=digest,
                    key_version=key_version,
                    window_started_at=window_start,
                    expires_at=expires,
                    max_requests=max_requests,
                    now=now,
                )
        if not decision.allowed:
            raise RateLimitExceededError(decision.retry_after_seconds)
