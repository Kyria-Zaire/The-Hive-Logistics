from __future__ import annotations

import logging
from datetime import UTC

import pytest

from lead_schema_fixtures import QUOTE_MINIMAL
from thl_api.leads.canonicalization import canonical_json_bytes, nfc_string
from thl_api.leads.fingerprint import build_fingerprint_payload, payload_fingerprint_hex
from thl_api.leads.hmac_keyring import HmacKeyring, HmacSecret
from thl_api.leads.lock_id import advisory_lock_id
from thl_api.leads.public_reference import crockford8_from_random, public_reference_for_accepted_at
from thl_api.leads.trusted_proxy import client_ip_for_rate_limit
from thl_api.models.enums import IdempotencyScope
from thl_api.problems import ProblemDetails
from thl_api.schemas.leads import QuoteRequestCreate
from thl_api.turnstile.httpx_client import HttpxTurnstileVerifier


def test_nfc_and_canonical_json_sorted_keys() -> None:
    payload = {"b": "1", "a": "é"}  # NFC combinable
    raw = canonical_json_bytes(payload)
    assert raw == b'{"a":"\xc3\xa9","b":"1"}'
    assert nfc_string("e\u0301") == "é"


def test_hmac_keyring_rotation_lookup() -> None:
    ring = HmacKeyring(
        current=HmacSecret(version=2, secret=b"current-secret-value-0123456789"),
        previous=HmacSecret(version=1, secret=b"previous-secret-value-012345678"),
    )
    message = b"quote_requests|550e8400-e29b-41d4-a716-446655440000"
    digests = ring.digests_for_lookup(message)
    assert len(digests) == 2
    assert digests[0][1] == 2
    replay, version = ring.digest_hex(message, for_version=1)
    assert version == 1
    assert len(replay) == 64


def test_public_reference_format() -> None:
    from datetime import datetime

    accepted = datetime(2026, 9, 12, 23, 59, tzinfo=UTC)
    ref = public_reference_for_accepted_at(accepted)
    assert ref.startswith("THL-20260912-")
    suffix = ref.split("-", maxsplit=2)[-1]
    assert len(suffix) == 8
    assert all(ch in "0123456789ABCDEFGHJKMNPQRSTVWXYZ" for ch in suffix)
    assert len({crockford8_from_random() for _ in range(4)}) > 1


def test_lock_id_stable() -> None:
    first = advisory_lock_id("quote_requests", "550e8400-e29b-41d4-a716-446655440000")
    second = advisory_lock_id("quote_requests", "550e8400-e29b-41d4-a716-446655440000")
    assert first == second
    assert -2**63 <= first < 2**63


def test_trusted_proxy_only_when_enabled() -> None:
    assert (
        client_ip_for_rate_limit(
            direct_host="203.0.113.10",
            forwarded_for="198.51.100.20, 203.0.113.10",
            trusted_proxy_enabled=False,
        )
        == "203.0.113.10"
    )
    assert (
        client_ip_for_rate_limit(
            direct_host="203.0.113.10",
            forwarded_for="198.51.100.20, 203.0.113.10",
            trusted_proxy_enabled=True,
        )
        == "198.51.100.20"
    )


def test_problem_details_shape() -> None:
    problem = ProblemDetails(
        type="urn:thl:problem:validation-error",
        title="Données invalides",
        status=422,
        code="VALIDATION_ERROR",
        correlation_id="corr-1",
    )
    dumped = problem.model_dump(mode="json")
    assert dumped["status"] == 422


def test_fingerprint_excludes_turnstile_and_honeypot() -> None:
    body = QuoteRequestCreate.model_validate(QUOTE_MINIMAL)
    payload = build_fingerprint_payload(
        IdempotencyScope.quote_requests,
        body,
        fingerprint_algo_version=1,
    )
    assert "turnstile_token" not in payload
    assert "honeypot" not in payload
    assert payload["scope"] == "quote_requests"


@pytest.mark.asyncio
async def test_turnstile_client_does_not_log_token(caplog: pytest.LogCaptureFixture) -> None:
    verifier = HttpxTurnstileVerifier(
        secret="secret",
        expected_hostname="example.test",
        timeout_seconds=0.01,
    )
    token = "super-secret-turnstile-token-value"
    with caplog.at_level(logging.WARNING):
        try:
            await verifier.verify(token, action="quote_request")
        except Exception:
            pass
    assert token not in caplog.text


def test_payload_fingerprint_deterministic() -> None:
    body = QuoteRequestCreate.model_validate(QUOTE_MINIMAL)
    ring = HmacKeyring(
        current=HmacSecret(version=1, secret=b"fingerprint-secret-012345678901234"),
        previous=None,
    )
    one, _ = payload_fingerprint_hex(
        ring,
        IdempotencyScope.quote_requests,
        body,
        fingerprint_algo_version=1,
    )
    two, _ = payload_fingerprint_hex(
        ring,
        IdempotencyScope.quote_requests,
        body,
        fingerprint_algo_version=1,
    )
    assert one == two
