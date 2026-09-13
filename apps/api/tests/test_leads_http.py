from __future__ import annotations

import pytest
from httpx import AsyncClient

from lead_schema_fixtures import CONTACT_MINIMAL, QUOTE_MINIMAL, VALID_IDEMPOTENCY_KEY
from thl_api.services.lead_submission import (
    HoneypotTriggeredError,
    IdempotencyBusyError,
    IdempotencyConflictError,
    RateLimitExceededError,
    SubmissionSuccess,
    TurnstileRejectedError,
)
from thl_api.turnstile.httpx_client import TurnstileUnavailableError


class _StubService:
    def __init__(self) -> None:
        self.outcome: Exception | SubmissionSuccess | None = None

    async def submit_quote(self, body, *, idempotency_key, client_host, forwarded_for):
        _ = (body, idempotency_key, client_host, forwarded_for)
        if isinstance(self.outcome, Exception):
            raise self.outcome
        assert self.outcome is not None
        return self.outcome

    async def submit_contact(self, body, *, idempotency_key, client_host, forwarded_for):
        return await self.submit_quote(
            body,
            idempotency_key=idempotency_key,
            client_host=client_host,
            forwarded_for=forwarded_for,
        )


@pytest.fixture
def stub_service(monkeypatch: pytest.MonkeyPatch) -> _StubService:
    stub = _StubService()
    monkeypatch.setattr(
        "thl_api.api.routes.leads.get_lead_submission_service",
        lambda: stub,
    )
    return stub


def _headers(key: str = VALID_IDEMPOTENCY_KEY) -> dict[str, str]:
    return {"Idempotency-Key": key, "X-Correlation-Id": "corr-http-test"}


@pytest.mark.asyncio
async def test_post_quote_201(client: AsyncClient, stub_service: _StubService) -> None:
    stub_service.outcome = SubmissionSuccess(
        body={
            "public_reference": "THL-20260912-7K3M9Q2X",
            "status": "received",
            "created_at": "2026-09-12T18:00:00Z",
        },
        status_code=201,
        replayed=False,
    )
    response = await client.post(
        "/api/v1/quote-requests",
        headers=_headers(),
        json=QUOTE_MINIMAL,
    )
    assert response.status_code == 201
    assert response.headers["Idempotency-Replayed"] == "false"
    assert response.headers["X-Correlation-Id"] == "corr-http-test"


@pytest.mark.asyncio
async def test_post_replay_200(client: AsyncClient, stub_service: _StubService) -> None:
    body = {
        "public_reference": "THL-20260912-7K3M9Q2X",
        "status": "received",
        "created_at": "2026-09-12T18:00:00Z",
    }
    stub_service.outcome = SubmissionSuccess(body=body, status_code=200, replayed=True)
    response = await client.post(
        "/api/v1/contact-messages",
        headers=_headers(),
        json=CONTACT_MINIMAL,
    )
    assert response.status_code == 200
    assert response.headers["Idempotency-Replayed"] == "true"


@pytest.mark.asyncio
async def test_post_415(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/quote-requests",
        headers={**_headers(), "Content-Type": "text/plain"},
        content=b"not-json",
    )
    assert response.status_code == 415


@pytest.mark.asyncio
async def test_post_413(client: AsyncClient) -> None:
    huge = b"x" * (65_537)
    response = await client.post(
        "/api/v1/quote-requests",
        headers={**_headers(), "Content-Type": "application/json"},
        content=huge,
    )
    assert response.status_code == 413


@pytest.mark.asyncio
async def test_post_400_malformed_json(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/quote-requests",
        headers={**_headers(), "Content-Type": "application/json"},
        content=b"{",
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_post_422(client: AsyncClient) -> None:
    bad_payload = {**QUOTE_MINIMAL, "email": "not-an-email"}
    response = await client.post(
        "/api/v1/quote-requests",
        headers=_headers(),
        json=bad_payload,
    )
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")


@pytest.mark.asyncio
async def test_post_403_honeypot(client: AsyncClient, stub_service: _StubService) -> None:
    stub_service.outcome = HoneypotTriggeredError()
    response = await client.post(
        "/api/v1/quote-requests",
        headers=_headers(),
        json=QUOTE_MINIMAL,
    )
    assert response.status_code == 403
    assert response.json()["code"] == "REQUEST_DENIED"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exc,status,code",
    [
        (TurnstileRejectedError(), 403, "REQUEST_DENIED"),
        (IdempotencyConflictError(), 409, "IDEMPOTENCY_CONFLICT"),
        (RateLimitExceededError(30), 429, "RATE_LIMITED"),
        (IdempotencyBusyError(), 503, "IDEMPOTENCY_BUSY"),
        (TurnstileUnavailableError(), 503, "DEPENDENCY_UNAVAILABLE"),
    ],
)
async def test_post_error_mapping(
    client: AsyncClient,
    stub_service: _StubService,
    exc: Exception,
    status: int,
    code: str,
) -> None:
    stub_service.outcome = exc
    response = await client.post(
        "/api/v1/quote-requests",
        headers=_headers(),
        json=QUOTE_MINIMAL,
    )
    assert response.status_code == status
    assert response.json()["code"] == code
    if status == 429:
        assert "Retry-After" in response.headers
