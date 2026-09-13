from __future__ import annotations

import ipaddress
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
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
_DEV_PRIVACY_POLICY_VERSION = "2026-01-dev"

_MIN_HMAC_BYTES = 32


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    thl_env: ThlEnvironment
    database_url: SecretStr
    log_level: str = "INFO"
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    privacy_policy_version: str = Field(default="2026-01-dev", max_length=64)

    idempotency_ttl_seconds: int = Field(default=86_400, ge=60)
    fingerprint_algo_version: int = Field(default=1, ge=1)

    idempotency_hmac_secret_current: SecretStr | None = None
    idempotency_hmac_secret_current_version: int | None = None
    idempotency_hmac_secret_previous: SecretStr | None = None
    idempotency_hmac_secret_previous_version: int | None = None

    fingerprint_hmac_secret_current: SecretStr | None = None
    fingerprint_hmac_secret_current_version: int | None = None
    fingerprint_hmac_secret_previous: SecretStr | None = None
    fingerprint_hmac_secret_previous_version: int | None = None

    rate_limit_hmac_secret_current: SecretStr | None = None
    rate_limit_hmac_secret_current_version: int | None = None

    rate_limit_quote_requests_max: int | None = None
    rate_limit_quote_requests_window_seconds: int | None = None
    rate_limit_contact_messages_max: int | None = None
    rate_limit_contact_messages_window_seconds: int | None = None

    turnstile_secret_key: SecretStr | None = None
    turnstile_expected_hostname: str | None = None

    trusted_proxy_cidrs: str = ""

    @field_validator("database_url")
    @classmethod
    def database_url_non_empty(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            msg = "DATABASE_URL is required"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def apply_environment_defaults_and_guards(self) -> Settings:
        if self.thl_env == "dev":
            self._apply_dev_defaults()
        else:
            self._require_non_dev_configuration()
        if self.thl_env == "prod":
            self._reject_prod_dev_database()
        self._validate_hmac_material()
        self._validate_rate_limits()
        return self

    def _reject_prod_dev_database(self) -> None:
        lowered = self.database_url.get_secret_value().lower()
        for marker in _DEV_DATABASE_MARKERS:
            if marker in lowered:
                msg = "THL_ENV=prod cannot use DEV-local DATABASE_URL markers"
                raise ValueError(msg)

    def _require_non_dev_configuration(self) -> None:
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
        ):
            if getattr(self, name) in (None, ""):
                missing.append(name)
        privacy = self.privacy_policy_version.strip()
        if privacy == _DEV_PRIVACY_POLICY_VERSION:
            msg = (
                f"THL_ENV={self.thl_env} cannot use DEV privacy_policy_version "
                f"{_DEV_PRIVACY_POLICY_VERSION!r}"
            )
            raise ValueError(msg)
        if self.thl_env == "prod" and not privacy:
            missing.append("privacy_policy_version")
        if missing:
            msg = f"{self.thl_env.upper()} missing required settings: {', '.join(missing)}"
            raise ValueError(msg)

    def _apply_dev_defaults(self) -> None:
        if not self.idempotency_hmac_secret_current:
            self.idempotency_hmac_secret_current = SecretStr(_DEV_IDEMPOTENCY_SECRET.decode())
            self.idempotency_hmac_secret_current_version = 1
        if not self.fingerprint_hmac_secret_current:
            self.fingerprint_hmac_secret_current = SecretStr(_DEV_FINGERPRINT_SECRET.decode())
            self.fingerprint_hmac_secret_current_version = 1
        if not self.rate_limit_hmac_secret_current:
            self.rate_limit_hmac_secret_current = SecretStr(_DEV_RATE_LIMIT_SECRET.decode())
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
            self.turnstile_secret_key = SecretStr("dev-turnstile-secret-placeholder")
        if not self.turnstile_expected_hostname:
            self.turnstile_expected_hostname = "localhost"

    def _validate_hmac_material(self) -> None:
        pairs: list[tuple[SecretStr | None, int | None, str]] = [
            (
                self.idempotency_hmac_secret_current,
                self.idempotency_hmac_secret_current_version,
                "idempotency current",
            ),
            (
                self.idempotency_hmac_secret_previous,
                self.idempotency_hmac_secret_previous_version,
                "idempotency previous",
            ),
            (
                self.fingerprint_hmac_secret_current,
                self.fingerprint_hmac_secret_current_version,
                "fingerprint current",
            ),
            (
                self.fingerprint_hmac_secret_previous,
                self.fingerprint_hmac_secret_previous_version,
                "fingerprint previous",
            ),
            (
                self.rate_limit_hmac_secret_current,
                self.rate_limit_hmac_secret_current_version,
                "rate_limit current",
            ),
        ]
        for secret, version, label in pairs:
            if secret is None and version is None:
                continue
            if secret is None or version is None:
                msg = f"HMAC {label} requires both secret and version"
                raise ValueError(msg)
            raw = secret.get_secret_value().encode("utf-8")
            if len(raw) < _MIN_HMAC_BYTES:
                msg = f"HMAC {label} secret must be at least {_MIN_HMAC_BYTES} bytes"
                raise ValueError(msg)
            if version < 1:
                msg = f"HMAC {label} version must be >= 1"
                raise ValueError(msg)
        self._reject_duplicate_hmac_rotation()

    def _reject_duplicate_hmac_rotation(self) -> None:
        for current_version, previous_version, label in (
            (
                self.idempotency_hmac_secret_current_version,
                self.idempotency_hmac_secret_previous_version,
                "idempotency",
            ),
            (
                self.fingerprint_hmac_secret_current_version,
                self.fingerprint_hmac_secret_previous_version,
                "fingerprint",
            ),
        ):
            if current_version is None or previous_version is None:
                continue
            if current_version == previous_version:
                msg = f"HMAC {label} current and previous version must differ"
                raise ValueError(msg)
        for current, previous, label in (
            (
                self.idempotency_hmac_secret_current,
                self.idempotency_hmac_secret_previous,
                "idempotency",
            ),
            (
                self.fingerprint_hmac_secret_current,
                self.fingerprint_hmac_secret_previous,
                "fingerprint",
            ),
        ):
            if current is None or previous is None:
                continue
            if current.get_secret_value() == previous.get_secret_value():
                msg = f"HMAC {label} current and previous secret must differ"
                raise ValueError(msg)

    def _validate_rate_limits(self) -> None:
        for name, value in (
            ("rate_limit_quote_requests_max", self.rate_limit_quote_requests_max),
            (
                "rate_limit_quote_requests_window_seconds",
                self.rate_limit_quote_requests_window_seconds,
            ),
            ("rate_limit_contact_messages_max", self.rate_limit_contact_messages_max),
            (
                "rate_limit_contact_messages_window_seconds",
                self.rate_limit_contact_messages_window_seconds,
            ),
        ):
            if value is not None and value <= 0:
                msg = f"{name} must be > 0"
                raise ValueError(msg)

    def trusted_proxy_networks(self) -> tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...]:
        if not self.trusted_proxy_cidrs.strip():
            return ()
        networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
        for part in self.trusted_proxy_cidrs.split(","):
            item = part.strip()
            if not item:
                continue
            networks.append(ipaddress.ip_network(item, strict=False))
        return tuple(networks)

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

    @property
    def database_url_str(self) -> str:
        return self.database_url.get_secret_value()


def _require_secret(raw: SecretStr | None, version: int | None) -> HmacSecret:
    if raw is None or version is None:
        msg = "HMAC secret and version are required"
        raise ValueError(msg)
    return HmacSecret(version=version, secret=raw.get_secret_value().encode("utf-8"))


def _build_keyring(
    current_raw: SecretStr | None,
    current_version: int | None,
    previous_raw: SecretStr | None,
    previous_version: int | None,
) -> HmacKeyring:
    current = _require_secret(current_raw, current_version)
    previous: HmacSecret | None = None
    if previous_raw and previous_version is not None:
        previous = HmacSecret(
            version=previous_version,
            secret=previous_raw.get_secret_value().encode("utf-8"),
        )
    return HmacKeyring(current=current, previous=previous)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
