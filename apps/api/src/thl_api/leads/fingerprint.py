from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from thl_api.leads.canonicalization import canonical_json_bytes
from thl_api.leads.hmac_keyring import HmacKeyring
from thl_api.models.enums import IdempotencyScope

_FINGERPRINT_EXCLUDE = {"turnstile_token", "honeypot"}


def build_fingerprint_payload(
    scope: IdempotencyScope,
    body: BaseModel,
    *,
    fingerprint_algo_version: int,
) -> dict[str, Any]:
    data = body.model_dump(mode="json", exclude=_FINGERPRINT_EXCLUDE)
    data["scope"] = scope.value
    data["fingerprint_algo_version"] = fingerprint_algo_version
    return data


def payload_fingerprint_hex(
    keyring: HmacKeyring,
    scope: IdempotencyScope,
    body: BaseModel,
    *,
    fingerprint_algo_version: int,
    for_key_version: int | None = None,
) -> tuple[str, int]:
    payload = build_fingerprint_payload(
        scope,
        body,
        fingerprint_algo_version=fingerprint_algo_version,
    )
    canonical = canonical_json_bytes(payload)
    message = f"{scope.value}|{fingerprint_algo_version}|".encode() + canonical
    return keyring.digest_hex(message, for_version=for_key_version)


def idempotency_key_digest_hex(
    keyring: HmacKeyring,
    scope: IdempotencyScope,
    raw_uuid: str,
    *,
    for_key_version: int | None = None,
) -> tuple[str, int]:
    message = f"{scope.value}|{raw_uuid}".encode()
    return keyring.digest_hex(message, for_version=for_key_version)
