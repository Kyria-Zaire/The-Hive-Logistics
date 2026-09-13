from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import aiosmtplib
import pytest
from pydantic import ValidationError

from notifications_fixtures import FakeEmailSender, worker_env_defaults
from thl_api.models.enums import NotificationKind
from thl_api.notifications.contracts import (
    BACKOFF_AFTER_FAILURE_MINUTES,
    SMTP_TOTAL_TIMEOUT_SECONDS,
    ContactLeadSnapshot,
    QuoteLeadSnapshot,
    WorkerSettings,
    backoff_after_failure,
    deterministic_message_id,
    provider_dedup_key,
)
from thl_api.notifications.renderer import render_contact, render_email, render_quote
from thl_api.notifications.smtp_sender import EmailTimeoutError, SmtpEmailSender

pytestmark = pytest.mark.worker


def test_backoff_minutes_exact() -> None:
    assert BACKOFF_AFTER_FAILURE_MINUTES == (1, 5, 15, 60)
    assert backoff_after_failure(1) == timedelta(minutes=1)
    assert backoff_after_failure(2) == timedelta(minutes=5)
    assert backoff_after_failure(3) == timedelta(minutes=15)
    assert backoff_after_failure(4) == timedelta(minutes=60)
    assert backoff_after_failure(5) is None


def test_backoff_respects_custom_max_attempts() -> None:
    assert backoff_after_failure(1, max_attempts=2) == timedelta(minutes=1)
    assert backoff_after_failure(2, max_attempts=2) is None
    assert backoff_after_failure(5, max_attempts=6) == timedelta(minutes=60)
    assert backoff_after_failure(6, max_attempts=6) is None


def test_dedup_key_and_message_id_deterministic() -> None:
    key = provider_dedup_key("THL-20260912-7K3M9Q2X", NotificationKind.internal_email)
    assert key == "thl:THL-20260912-7K3M9Q2X:internal_email:v1"
    mid = deterministic_message_id(key)
    assert mid == deterministic_message_id(key)
    assert "@" in mid


def _contact_snapshot() -> ContactLeadSnapshot:
    received = datetime(2026, 9, 12, 18, 0, tzinfo=UTC)
    return ContactLeadSnapshot(
        public_reference="THL-20260912-7K3M9Q2X",
        received_at=received,
        first_name="Ada",
        last_name="Lovelace",
        email="ada@example.com",
        phone="+33123456789",
        company="THL",
        subject="Information",
        message="Bonjour,\nworld",
    )


def test_render_contact_hostile_html_escaped() -> None:
    received = datetime(2026, 9, 12, 18, 0, tzinfo=UTC)
    snap = ContactLeadSnapshot(
        public_reference="THL-20260912-7K3M9Q2X",
        received_at=received,
        first_name="Jean<script>",
        last_name="Dupont&",
        email="ada@example.com",
        phone="+33123456789",
        company="THL",
        subject="Information",
        message="<script>alert(1)&</script>",
    )
    email = render_contact(snap, to_address="ops@test", from_address="from@test")
    assert email.subject == "[THL] Nouveau message de contact — THL-20260912-7K3M9Q2X"
    assert "<script>" not in email.html_body
    assert "&lt;script&gt;" in email.html_body
    assert "&amp;" in email.html_body
    assert "<script>alert(1)&</script>" in email.text_body


def test_render_quote_subject() -> None:
    received = datetime(2026, 9, 12, 18, 0, tzinfo=UTC)
    snap = QuoteLeadSnapshot(
        public_reference="THL-20260912-ABCDEFGH",
        received_at=received,
        first_name="A",
        last_name="B",
        email="a@b.test",
        phone=None,
        company=None,
        service="Convoyage premium",
        departure_city="Paris",
        departure_postal_code="75001",
        arrival_city="Lyon",
        arrival_postal_code="69001",
        timing_label="2026-10-01",
        vehicle_category="Berline",
        vehicle_make="Peugeot",
        vehicle_model="308",
        vehicle_rolling=True,
        special_constraints=None,
        additional_message=None,
        contact_preference=None,
    )
    email = render_quote(snap, to_address="ops@test", from_address="from@test")
    assert "Nouvelle demande de devis" in email.subject
    assert "THL-20260912-ABCDEFGH" in email.subject


def test_subject_has_no_crlf_injection() -> None:
    email = render_email(
        _contact_snapshot(),
        to_address="ops@test",
        from_address="from@test",
    )
    assert "\r" not in email.subject
    assert "\n" not in email.subject


def _apply_worker_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in worker_env_defaults().items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@127.0.0.1:5432/db")


def test_worker_settings_rejects_crlf_in_addresses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _apply_worker_env(monkeypatch)
    monkeypatch.setenv("NOTIFICATION_EMAIL_TO", "bad\r\n@example.test")
    with pytest.raises(ValidationError):
        WorkerSettings()


def test_worker_settings_rejects_empty_trimmed_host(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _apply_worker_env(monkeypatch)
    monkeypatch.setenv("NOTIFICATION_SMTP_HOST", "   ")
    with pytest.raises(ValidationError):
        WorkerSettings()


def test_worker_settings_rejects_invalid_email(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _apply_worker_env(monkeypatch)
    monkeypatch.setenv("NOTIFICATION_EMAIL_FROM", "not-an-email")
    with pytest.raises(ValidationError):
        WorkerSettings()


def test_worker_settings_rejects_dual_tls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _apply_worker_env(monkeypatch)
    monkeypatch.setenv("NOTIFICATION_SMTP_STARTTLS", "true")
    monkeypatch.setenv("NOTIFICATION_SMTP_USE_TLS", "true")
    with pytest.raises(ValidationError):
        WorkerSettings()


def test_worker_settings_rejects_partial_smtp_auth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _apply_worker_env(monkeypatch)
    monkeypatch.setenv("NOTIFICATION_SMTP_USER", "smtp-user")
    with pytest.raises(ValidationError):
        WorkerSettings()


def test_worker_settings_accepts_paired_smtp_auth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _apply_worker_env(monkeypatch)
    monkeypatch.setenv("NOTIFICATION_SMTP_USER", "smtp-user")
    monkeypatch.setenv("NOTIFICATION_SMTP_PASSWORD", "secret")
    settings = WorkerSettings()
    assert settings.notification_smtp_user == "smtp-user"
    assert settings.notification_smtp_password is not None


def test_worker_settings_missing_smtp_host_fail_fast(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@127.0.0.1:5432/db")
    monkeypatch.delenv("NOTIFICATION_SMTP_HOST", raising=False)
    with pytest.raises(ValidationError):
        WorkerSettings()


def test_smtp_timeout_constant() -> None:
    assert SMTP_TOTAL_TIMEOUT_SECONDS == 10.0


@pytest.mark.asyncio
async def test_fake_sender_no_network() -> None:
    sender = FakeEmailSender()
    msg = render_contact(_contact_snapshot(), to_address="ops@test", from_address="from@test")
    result = await sender.send(msg)
    assert result.provider_message_id == "fake-provider-id"


@pytest.mark.asyncio
async def test_smtp_send_times_out_on_slow_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def slow_send(*_args: object, **_kwargs: object) -> tuple[dict[str, str], str]:
        await asyncio.sleep(SMTP_TOTAL_TIMEOUT_SECONDS + 2.0)
        return ({}, "250 OK")

    monkeypatch.setattr(aiosmtplib, "send", slow_send)
    _apply_worker_env(monkeypatch)
    settings = WorkerSettings()
    sender = SmtpEmailSender(settings=settings)
    msg = render_contact(_contact_snapshot(), to_address="ops@test", from_address="from@test")
    with pytest.raises(EmailTimeoutError):
        await sender.send(msg)


@pytest.mark.asyncio
async def test_smtp_sender_mock_transport_no_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _apply_worker_env(monkeypatch)
    settings = WorkerSettings()
    monkeypatch.setattr(
        aiosmtplib,
        "send",
        AsyncMock(return_value=({}, "250 OK")),
    )
    sender = SmtpEmailSender(settings=settings)
    msg = render_contact(_contact_snapshot(), to_address="ops@test", from_address="from@test")
    result = await sender.send(msg)
    assert result.provider_message_id
