from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from thl_api.config import get_settings
from thl_api.main import create_app

_INTEGRATION_DATABASE_URL = os.environ.get(
    "INTEGRATION_DATABASE_URL",
    "postgresql+psycopg://thl_dev:thl_dev_password@127.0.0.1:5433/thl_dev",
)


@pytest.mark.integration
def test_health_ready_against_real_postgres(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("THL_ENV", "dev")
    monkeypatch.setenv("DATABASE_URL", _INTEGRATION_DATABASE_URL)
    get_settings.cache_clear()

    app = create_app()
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(
            "/api/v1/health/ready",
            headers={"X-Correlation-Id": "integration-ready"},
        )

    assert response.status_code == 200, response.text
    assert response.json() == {"status": "ok", "checks": {"database": "ok"}}
    assert response.headers["X-Correlation-Id"] == "integration-ready"
    lowered = response.text.lower()
    assert "thl_dev_password" not in lowered
    assert "postgresql" not in lowered
