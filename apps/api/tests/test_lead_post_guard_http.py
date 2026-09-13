from __future__ import annotations

import pytest
from httpx import AsyncClient

from lead_schema_fixtures import QUOTE_MINIMAL, VALID_IDEMPOTENCY_KEY


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
