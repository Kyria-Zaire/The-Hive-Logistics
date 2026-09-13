from __future__ import annotations

import asyncio
import ipaddress
import logging
from datetime import UTC

import httpx
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
from thl_api.repositories.leads import _is_public_reference_collision
from thl_api.schemas.leads import QuoteRequestCreate
from thl_api.turnstile.httpx_client import HttpxTurnstileVerifier, TurnstileUnavailableError


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


_TRUSTED_V4 = (ipaddress.ip_network("203.0.113.0/24"),)
_TRUSTED_V6 = (ipaddress.ip_network("2001:db8:1::/48"),)


def test_trusted_proxy_returns_first_untrusted_hop_from_peer() -> None:
    assert (
        client_ip_for_rate_limit(
            direct_host="203.0.113.10",
            forwarded_for="198.51.100.20, 203.0.113.10",
            trusted_networks=_TRUSTED_V4,
        )
        == "198.51.100.20"
    )


def test_trusted_proxy_ignores_xff_when_peer_untrusted() -> None:
    assert (
        client_ip_for_rate_limit(
            direct_host="198.51.100.99",
            forwarded_for="1.2.3.4, 203.0.113.10",
            trusted_networks=_TRUSTED_V4,
        )
        == "198.51.100.99"
    )


def test_trusted_proxy_untrusted_intermediate_in_chain() -> None:
    assert (
        client_ip_for_rate_limit(
            direct_host="203.0.113.10",
            forwarded_for="198.51.100.20, 198.51.100.50, 203.0.113.10",
            trusted_networks=_TRUSTED_V4,
        )
        == "198.51.100.50"
    )


def test_trusted_proxy_multiple_trusted_proxies_ipv6() -> None:
    assert (
        client_ip_for_rate_limit(
            direct_host="2001:db8:1::1",
            forwarded_for="2001:db8:1::9, 2001:db8:1::1",
            trusted_networks=_TRUSTED_V6,
        )
        == "2001:db8:1::9"
    )


def test_trusted_proxy_without_allowlist_uses_peer() -> None:
    assert (
        client_ip_for_rate_limit(
            direct_host="203.0.113.10",
            forwarded_for="198.51.100.20, 203.0.113.10",
            trusted_networks=(),
        )
        == "203.0.113.10"
    )


def test_public_reference_collision_only_unique_constraint() -> None:
    from sqlalchemy.exc import IntegrityError

    class _UqDiag:
        constraint_name = "uq_leads_public_reference"

    class _UqOrig(Exception):
        diag = _UqDiag()

    assert _is_public_reference_collision(IntegrityError("insert", {}, _UqOrig()))

    class _CheckDiag:
        constraint_name = "chk_leads_public_reference_format"

    class _CheckOrig(Exception):
        diag = _CheckDiag()

    assert not _is_public_reference_collision(IntegrityError("insert", {}, _CheckOrig()))


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


class _SlowTurnstileTransport(httpx.AsyncBaseTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        _ = request
        await asyncio.sleep(5.0)
        return httpx.Response(200, json={"success": True})


class _OkTurnstileTransport(httpx.AsyncBaseTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        _ = request
        return httpx.Response(
            200,
            json={
                "success": True,
                "action": "quote_request",
                "hostname": "example.test",
            },
        )


@pytest.mark.asyncio
async def test_turnstile_wall_clock_timeout_uses_mock_transport() -> None:
    verifier = HttpxTurnstileVerifier(
        secret="secret",
        expected_hostname="example.test",
        timeout_seconds=0.05,
        transport=_SlowTurnstileTransport(),
    )
    with pytest.raises(TurnstileUnavailableError):
        await verifier.verify("token-value", action="quote_request")


@pytest.mark.asyncio
async def test_turnstile_client_does_not_log_token(caplog: pytest.LogCaptureFixture) -> None:
    verifier = HttpxTurnstileVerifier(
        secret="secret",
        expected_hostname="example.test",
        timeout_seconds=1.0,
        transport=_OkTurnstileTransport(),
    )
    token = "super-secret-turnstile-token-value"
    with caplog.at_level(logging.WARNING):
        await verifier.verify(token, action="quote_request")
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
