from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import BaseModel

from helpers import api_client
from thl_api.main import create_app


class _CountBody(BaseModel):
    count: int


@pytest.fixture
def app_with_routes() -> FastAPI:
    app = create_app()

    @app.post("/api/v1/_test/validate")
    async def validate_body(body: _CountBody) -> dict[str, int]:
        return {"count": body.count}

    @app.get("/api/v1/_test/boom")
    async def boom() -> None:
        msg = "internal-db-password-leak-marker"
        raise RuntimeError(msg)

    return app


@pytest.fixture
async def routed_client(app_with_routes: FastAPI):
    async with api_client(app_with_routes, raise_app_exceptions=False) as http_client:
        yield http_client


@pytest.mark.asyncio
async def test_correlation_preserves_valid_raw_value(client: AsyncClient) -> None:
    correlation = "corr-valid_123.test"
    response = await client.get(
        "/api/v1/health/live",
        headers={"X-Correlation-Id": correlation},
    )
    assert response.headers["X-Correlation-Id"] == correlation


@pytest.mark.asyncio
async def test_correlation_replaces_whitespace_value(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/health/live",
        headers={"X-Correlation-Id": "  padded  "},
    )
    resolved = response.headers["X-Correlation-Id"]
    assert resolved != "  padded  "
    assert len(resolved) <= 64


@pytest.mark.asyncio
async def test_correlation_replaces_overlong_value(client: AsyncClient) -> None:
    too_long = "a" * 65
    response = await client.get(
        "/api/v1/health/live",
        headers={"X-Correlation-Id": too_long},
    )
    assert response.headers["X-Correlation-Id"] != too_long


@pytest.mark.asyncio
async def test_correlation_replaces_duplicate_header(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/health/live",
        headers=[("X-Correlation-Id", "one"), ("X-Correlation-Id", "two")],
    )
    assert response.headers["X-Correlation-Id"] not in {"one", "two"}


@pytest.mark.asyncio
async def test_not_found_includes_correlation_header(client: AsyncClient) -> None:
    response = await client.get("/api/v1/unknown-route")
    assert response.status_code == 404
    assert "X-Correlation-Id" in response.headers


@pytest.mark.asyncio
async def test_validation_error_includes_correlation_header(
    routed_client: AsyncClient,
) -> None:
    response = await routed_client.post(
        "/api/v1/_test/validate",
        json={"count": "not-an-int"},
        headers={"X-Correlation-Id": "corr-422-test"},
    )
    assert response.status_code == 422
    assert response.headers["X-Correlation-Id"] == "corr-422-test"


@pytest.mark.asyncio
async def test_internal_error_problem_json_and_correlation(
    routed_client: AsyncClient,
) -> None:
    response = await routed_client.get(
        "/api/v1/_test/boom",
        headers={"X-Correlation-Id": "corr-500-test"},
    )
    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.headers["X-Correlation-Id"] == "corr-500-test"
    body = response.json()
    assert body["status"] == 500
    assert body["code"] == "INTERNAL_ERROR"
    assert body["type"] == "urn:thl:problem:internal-error"
    assert body["correlation_id"] == "corr-500-test"
    serialized = response.text.lower()
    assert "internal-db-password-leak-marker" not in serialized
    assert "runtimeerror" not in serialized
    assert "traceback" not in serialized
