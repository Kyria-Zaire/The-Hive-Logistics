from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_live_returns_200(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Correlation-Id" in response.headers


@pytest.mark.asyncio
async def test_health_live_does_not_check_database(client: AsyncClient) -> None:
    with patch(
        "thl_api.api.routes.health.check_database_available",
        new=AsyncMock(side_effect=AssertionError("database must not be called")),
    ):
        response = await client.get("/api/v1/health/live")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_ready_ok_when_database_available(client: AsyncClient) -> None:
    with patch(
        "thl_api.api.routes.health.check_database_available",
        new=AsyncMock(return_value=True),
    ):
        response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": "ok"}}


@pytest.mark.asyncio
async def test_health_ready_503_problem_when_database_unavailable(
    client: AsyncClient,
) -> None:
    with patch(
        "thl_api.api.routes.health.check_database_available",
        new=AsyncMock(return_value=False),
    ):
        response = await client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert body["status"] == 503
    assert body["code"] == "DEPENDENCY_UNAVAILABLE"
    assert "correlation_id" in body
    serialized = response.text.lower()
    assert "postgresql" not in serialized
    assert "thl_dev_password" not in serialized
