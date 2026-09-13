from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from thl_api.leads.hmac_keyring import HmacKeyring, HmacSecret

ThlEnvironment = Literal["dev", "recette", "preprod", "prod"]

_DEV_DATABASE_MARKERS = (
    "127.0.0.1",
    "localhost",
    "thl_dev_password",
    "/thl_dev",
)

_DEV_IDEMPOTENCY_SECRET = b"dev-idempotency-hmac-secret-32bytes!!"
_DEV_FINGERPRINT_SECRET = b"dev-fingerprint-hmac-secret-32bytes!!"
_DEV_RATE_LIMIT_SECRET = b"dev-rate-limit-hmac-secret-32bytes!!!!"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    thl_env: ThlEnvironment
    database_url: str
    log_level: str = "INFO"
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    privacy_policy_version: str = Field(default="2026-01-dev", max_length=64)

    idempotency_ttl_seconds: int = Field(default=86_400, ge=60)
    fingerprint_algo_version: int = Field(default=1, ge=1)

    idempotency_hmac_secret_current: str | None = None
    idempotency_hmac_secret_current_version: int | None = None
    idempotency_hmac_secret_previous: str | None = None
    idempotency_hmac_secret_previous_version: int | None = None

    fingerprint_hmac_secret_current: str | None = None
    fingerprint_hmac_secret_current_version: int | None = None
    fingerprint_hmac_secret_previous: str | None = None
    fingerprint_hmac_secret_previous_version: int | None = None

    rate_limit_hmac_secret_current: str | None = None
    rate_limit_hmac_secret_current_version: int | None = None

    rate_limit_quote_requests_max: int | None = None
    rate_limit_quote_requests_window_seconds: int | None = None
    rate_limit_contact_messages_max: int | None = None
    rate_limit_contact_messages_window_seconds: int | None = None

    turnstile_secret_key: str | None = None
    turnstile_expected_hostname: str | None = None

    trusted_proxy_enabled: bool = False

    @field_validator("database_url")
    @classmethod
    def database_url_non_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "DATABASE_URL is required"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def apply_environment_defaults_and_prod_guards(self) -> Settings:
        if self.thl_env == "prod":
            self._reject_prod_dev_database()
            self._require_prod_secrets()
        else:
            self._apply_dev_defaults()
        return self

    def _reject_prod_dev_database(self) -> None:
        lowered = self.database_url.lower()
        for marker in _DEV_DATABASE_MARKERS:
            if marker in lowered:
                msg = "THL_ENV=prod cannot use DEV-local DATABASE_URL markers"
                raise ValueError(msg)

    def _require_prod_secrets(self) -> None:
        missing: list[str] = []
        for name in (
            "idempotency_hmac_secret_current",
            "idempotency_hmac_secret_current_version",
            "fingerprint_hmac_secret_current",
            "fingerprint_hmac_secret_current_version",
            "rate_limit_hmac_secret_current",
            "rate_limit_hmac_secret_current_version",
            "rate_limit_quote_requests_max",
            "rate_limit_quote_requests_window_seconds",
            "rate_limit_contact_messages_max",
            "rate_limit_contact_messages_window_seconds",
            "turnstile_secret_key",
            "turnstile_expected_hostname",
            "privacy_policy_version",
        ):
            if getattr(self, name) in (None, ""):
                missing.append(name)
        if missing:
            msg = f"PROD missing required settings: {', '.join(missing)}"
            raise ValueError(msg)

    def _apply_dev_defaults(self) -> None:
        if not self.idempotency_hmac_secret_current:
            self.idempotency_hmac_secret_current = _DEV_IDEMPOTENCY_SECRET.decode()
            self.idempotency_hmac_secret_current_version = 1
        if not self.fingerprint_hmac_secret_current:
            self.fingerprint_hmac_secret_current = _DEV_FINGERPRINT_SECRET.decode()
            self.fingerprint_hmac_secret_current_version = 1
        if not self.rate_limit_hmac_secret_current:
            self.rate_limit_hmac_secret_current = _DEV_RATE_LIMIT_SECRET.decode()
            self.rate_limit_hmac_secret_current_version = 1
        if self.rate_limit_quote_requests_max is None:
            self.rate_limit_quote_requests_max = 120
        if self.rate_limit_quote_requests_window_seconds is None:
            self.rate_limit_quote_requests_window_seconds = 3_600
        if self.rate_limit_contact_messages_max is None:
            self.rate_limit_contact_messages_max = 120
        if self.rate_limit_contact_messages_window_seconds is None:
            self.rate_limit_contact_messages_window_seconds = 3_600
        if not self.turnstile_secret_key:
            self.turnstile_secret_key = "dev-turnstile-secret-placeholder"
        if not self.turnstile_expected_hostname:
            self.turnstile_expected_hostname = "localhost"

    def idempotency_keyring(self) -> HmacKeyring:
        return _build_keyring(
            self.idempotency_hmac_secret_current,
            self.idempotency_hmac_secret_current_version,
            self.idempotency_hmac_secret_previous,
            self.idempotency_hmac_secret_previous_version,
        )

    def fingerprint_keyring(self) -> HmacKeyring:
        return _build_keyring(
            self.fingerprint_hmac_secret_current,
            self.fingerprint_hmac_secret_current_version,
            self.fingerprint_hmac_secret_previous,
            self.fingerprint_hmac_secret_previous_version,
        )

    def rate_limit_keyring(self) -> HmacKeyring:
        current = _require_secret(
            self.rate_limit_hmac_secret_current,
            self.rate_limit_hmac_secret_current_version,
        )
        return HmacKeyring(current=current, previous=None)


def _require_secret(raw: str | None, version: int | None) -> HmacSecret:
    if raw is None or version is None:
        msg = "HMAC secret and version are required"
        raise ValueError(msg)
    return HmacSecret(version=version, secret=raw.encode("utf-8"))


def _build_keyring(
    current_raw: str | None,
    current_version: int | None,
    previous_raw: str | None,
    previous_version: int | None,
) -> HmacKeyring:
    current = _require_secret(current_raw, current_version)
    previous: HmacSecret | None = None
    if previous_raw and previous_version is not None:
        previous = HmacSecret(version=previous_version, secret=previous_raw.encode("utf-8"))
    return HmacKeyring(current=current, previous=previous)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
