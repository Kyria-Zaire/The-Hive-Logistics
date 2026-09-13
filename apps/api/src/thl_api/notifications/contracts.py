from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal, Protocol, Self

from pydantic import EmailStr, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from thl_api.models.enums import LeadType, NotificationKind

LOCK_LEASE_SECONDS = 60
SMTP_TOTAL_TIMEOUT_SECONDS = 10.0
DEFAULT_MAX_ATTEMPTS = 5
BACKOFF_AFTER_FAILURE_MINUTES: tuple[int, ...] = (1, 5, 15, 60)

ErrorCode = Literal[
    "EMAIL_TIMEOUT",
    "EMAIL_CONNECTION",
    "EMAIL_AUTH",
    "EMAIL_RECIPIENT_REJECTED",
    "EMAIL_PROVIDER_ERROR",
    "LEASE_LOST",
]


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: SecretStr
    notification_smtp_host: str = Field(max_length=253)
    notification_smtp_port: int = Field(default=587, ge=1, le=65535)
    notification_smtp_user: str | None = None
    notification_smtp_password: SecretStr | None = None
    notification_smtp_starttls: bool = True
    notification_smtp_use_tls: bool = False
    notification_email_from: EmailStr
    notification_email_to: EmailStr
    worker_id: str | None = Field(default=None, max_length=64)
    worker_poll_interval_seconds: float = Field(default=1.0, gt=0.0, le=60.0)

    @field_validator("database_url")
    @classmethod
    def database_url_non_empty(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            msg = "DATABASE_URL is required for the notification worker"
            raise ValueError(msg)
        return value

    @field_validator("notification_smtp_host", mode="before")
    @classmethod
    def smtp_host_trim_non_empty(cls, value: object) -> str:
        if value is None:
            msg = "NOTIFICATION_SMTP_HOST is required"
            raise ValueError(msg)
        text = str(value).strip()
        if not text:
            msg = "NOTIFICATION_SMTP_HOST must not be empty"
            raise ValueError(msg)
        return text

    @field_validator("notification_email_from", "notification_email_to", mode="before")
    @classmethod
    def email_trim_non_empty(cls, value: object) -> str:
        if value is None:
            msg = "Email address is required"
            raise ValueError(msg)
        text = str(value).strip()
        if not text:
            msg = "Email address must not be empty"
            raise ValueError(msg)
        if "\r" in text or "\n" in text:
            msg = "Email address must not contain CRLF"
            raise ValueError(msg)
        return text

    @field_validator("notification_smtp_user", mode="before")
    @classmethod
    def smtp_user_optional_trim(cls, value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text if text else None

    @field_validator("notification_smtp_password", mode="before")
    @classmethod
    def smtp_password_optional(cls, value: object) -> SecretStr | None:
        if value is None or value == "":
            return None
        if isinstance(value, SecretStr):
            return None if value.get_secret_value() == "" else value
        return SecretStr(str(value))

    @model_validator(mode="after")
    def smtp_tls_and_auth(self) -> Self:
        if self.notification_smtp_starttls and self.notification_smtp_use_tls:
            msg = "STARTTLS and USE_TLS cannot both be enabled"
            raise ValueError(msg)
        has_user = self.notification_smtp_user is not None
        has_password = self.notification_smtp_password is not None
        if has_user != has_password:
            msg = "SMTP username and password must be configured together"
            raise ValueError(msg)
        return self

    @property
    def database_url_str(self) -> str:
        return self.database_url.get_secret_value()


def provider_dedup_key(public_reference: str, notification_kind: NotificationKind) -> str:
    return f"thl:{public_reference}:{notification_kind.value}:v1"


def deterministic_message_id(dedup_key: str) -> str:
    safe = dedup_key.replace(":", ".")
    return f"<{safe}@notifications.the-hive-logistics.local>"


def backoff_after_failure(
    attempt_count: int,
    *,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> timedelta | None:
    if attempt_count >= max_attempts:
        return None
    index = attempt_count - 1
    if index < 0:
        return None
    if index >= len(BACKOFF_AFTER_FAILURE_MINUTES):
        index = len(BACKOFF_AFTER_FAILURE_MINUTES) - 1
    return timedelta(minutes=BACKOFF_AFTER_FAILURE_MINUTES[index])


@dataclass(frozen=True, slots=True)
class JobFence:
    job_id: int
    locked_by: str
    locked_at: datetime


@dataclass(frozen=True, slots=True)
class ContactLeadSnapshot:
    public_reference: str
    received_at: datetime
    first_name: str
    last_name: str
    email: str
    phone: str | None
    company: str | None
    subject: str
    message: str


@dataclass(frozen=True, slots=True)
class QuoteLeadSnapshot:
    public_reference: str
    received_at: datetime
    first_name: str
    last_name: str
    email: str
    phone: str | None
    company: str | None
    service: str
    departure_city: str
    departure_postal_code: str
    arrival_city: str
    arrival_postal_code: str
    timing_label: str
    vehicle_category: str
    vehicle_make: str
    vehicle_model: str
    vehicle_rolling: bool
    special_constraints: str | None
    additional_message: str | None
    contact_preference: str | None


LeadSnapshot = ContactLeadSnapshot | QuoteLeadSnapshot


@dataclass(frozen=True, slots=True)
class ClaimedJob:
    job_id: int
    attempt_count: int
    max_attempts: int
    notification_kind: NotificationKind
    fence: JobFence
    lead_type: LeadType
    snapshot: LeadSnapshot


@dataclass(frozen=True, slots=True)
class OutboundEmail:
    from_address: str
    to_address: str
    subject: str
    text_body: str
    html_body: str
    message_id: str
    dedup_key: str


@dataclass(frozen=True, slots=True)
class SendResult:
    provider_message_id: str


class EmailSender(Protocol):
    async def send(self, message: OutboundEmail) -> SendResult:
        """Send email; raise EmailSendError subclasses on failure."""
