from __future__ import annotations

import pytest
from pydantic import ValidationError

from thl_api.config import Settings, get_settings

_NON_DEV_ENV_BASE = {
    "DATABASE_URL": "postgresql+psycopg://user:password@db.example.test:5432/thl",
    "IDEMPOTENCY_HMAC_SECRET_CURRENT": "a" * 32,
    "IDEMPOTENCY_HMAC_SECRET_CURRENT_VERSION": "1",
    "FINGERPRINT_HMAC_SECRET_CURRENT": "b" * 32,
    "FINGERPRINT_HMAC_SECRET_CURRENT_VERSION": "1",
    "RATE_LIMIT_HMAC_SECRET_CURRENT": "c" * 32,
    "RATE_LIMIT_HMAC_SECRET_CURRENT_VERSION": "1",
    "RATE_LIMIT_QUOTE_REQUESTS_MAX": "10",
    "RATE_LIMIT_QUOTE_REQUESTS_WINDOW_SECONDS": "60",
    "RATE_LIMIT_CONTACT_MESSAGES_MAX": "10",
    "RATE_LIMIT_CONTACT_MESSAGES_WINDOW_SECONDS": "60",
    "TURNSTILE_SECRET_KEY": "turnstile-secret",
    "TURNSTILE_EXPECTED_HOSTNAME": "example.test",
}


def _apply_non_dev_env(monkeypatch: pytest.MonkeyPatch, env: str) -> None:
    monkeypatch.setenv("THL_ENV", env)
    for key, value in _NON_DEV_ENV_BASE.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("PRIVACY_POLICY_VERSION", "2026-03-prod")
    get_settings.cache_clear()


def test_prod_rejects_dev_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("THL_ENV", "prod")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://thl_dev:thl_dev_password@127.0.0.1:5432/thl_dev",
    )
    get_settings.cache_clear()
    with pytest.raises(ValidationError):
        Settings()


@pytest.mark.parametrize("env", ["recette", "preprod", "prod"])
def test_non_dev_rejects_dev_privacy_policy_version(
    monkeypatch: pytest.MonkeyPatch,
    env: str,
) -> None:
    _apply_non_dev_env(monkeypatch, env)
    monkeypatch.setenv("PRIVACY_POLICY_VERSION", "2026-01-dev")
    get_settings.cache_clear()
    with pytest.raises(ValidationError, match="privacy_policy_version"):
        Settings()


def test_prod_requires_explicit_privacy_policy_version(monkeypatch: pytest.MonkeyPatch) -> None:
    _apply_non_dev_env(monkeypatch, "prod")
    monkeypatch.setenv("PRIVACY_POLICY_VERSION", "   ")
    get_settings.cache_clear()
    with pytest.raises(ValidationError, match="privacy_policy_version"):
        Settings()


def test_rejects_identical_hmac_rotation_versions(monkeypatch: pytest.MonkeyPatch) -> None:
    _apply_non_dev_env(monkeypatch, "recette")
    monkeypatch.setenv("IDEMPOTENCY_HMAC_SECRET_PREVIOUS", "d" * 32)
    monkeypatch.setenv("IDEMPOTENCY_HMAC_SECRET_PREVIOUS_VERSION", "1")
    get_settings.cache_clear()
    with pytest.raises(ValidationError, match="version must differ"):
        Settings()


def test_rejects_identical_hmac_rotation_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    _apply_non_dev_env(monkeypatch, "recette")
    secret = "e" * 32
    monkeypatch.setenv("FINGERPRINT_HMAC_SECRET_PREVIOUS", secret)
    monkeypatch.setenv("FINGERPRINT_HMAC_SECRET_PREVIOUS_VERSION", "2")
    monkeypatch.setenv("FINGERPRINT_HMAC_SECRET_CURRENT", secret)
    monkeypatch.setenv("FINGERPRINT_HMAC_SECRET_CURRENT_VERSION", "1")
    get_settings.cache_clear()
    with pytest.raises(ValidationError, match="secret must differ"):
        Settings()
