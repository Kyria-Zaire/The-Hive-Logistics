from __future__ import annotations

import pytest
from pydantic import ValidationError

from thl_api.config import Settings, get_settings


def test_prod_rejects_dev_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("THL_ENV", "prod")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://thl_dev:thl_dev_password@127.0.0.1:5432/thl_dev",
    )
    get_settings.cache_clear()
    with pytest.raises(ValidationError):
        Settings()
