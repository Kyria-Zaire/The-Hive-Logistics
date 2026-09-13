from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from lead_schema_fixtures import QUOTE_MINIMAL, VALID_IDEMPOTENCY_KEY
from thl_api.middleware.lead_post_guard import (
    MAX_LEAD_BODY_BYTES,
    LeadPostGuardMiddleware,
    _read_body_from_receive,
)


def _headers(**extra: str) -> dict[str, str]:
    base = {"Idempotency-Key": VALID_IDEMPOTENCY_KEY, "X-Correlation-Id": "guard-test"}
    base.update(extra)
    return base


@pytest.mark.asyncio
async def test_empty_body_is_400_not_422(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/quote-requests",
        headers={**_headers(), "Content-Type": "application/json"},
        content=b"",
    )
    assert response.status_code == 400
    assert response.json()["code"] == "MALFORMED_REQUEST"
    assert response.headers["X-Correlation-Id"]


@pytest.mark.asyncio
async def test_invalid_utf8_is_400(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/quote-requests",
        headers={**_headers(), "Content-Type": "application/json"},
        content=b"\xff\xfe",
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_chunked_under_limit_allowed(
    client: AsyncClient,
    stub_service,
) -> None:
    from thl_api.services.lead_submission import SubmissionSuccess

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


@pytest.mark.asyncio
async def test_read_body_rejects_single_oversized_chunk() -> None:
    from starlette.requests import Request

    oversized = b"x" * (MAX_LEAD_BODY_BYTES + 1)

    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": oversized, "more_body": False}

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/",
        "headers": [],
    }
    request = Request(scope, receive)
    assert await _read_body_from_receive(request, MAX_LEAD_BODY_BYTES) is None


@pytest.mark.asyncio
async def test_single_chunk_over_limit_returns_413() -> None:
    async def ok(_request):
        return PlainTextResponse("ok")

    app = Starlette(
        routes=[Route("/api/v1/quote-requests", ok, methods=["POST"])],
        middleware=[Middleware(LeadPostGuardMiddleware)],
    )
    transport = ASGITransport(app=app)
    oversized = b"x" * (MAX_LEAD_BODY_BYTES + 1)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/quote-requests",
            headers={
                "Content-Type": "application/json",
                "Idempotency-Key": VALID_IDEMPOTENCY_KEY,
            },
            content=oversized,
        )
    assert response.status_code == 413
    assert response.json()["code"] == "PAYLOAD_TOO_LARGE"
