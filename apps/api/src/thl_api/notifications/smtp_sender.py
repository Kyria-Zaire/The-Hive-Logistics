from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from email.message import EmailMessage

import aiosmtplib

from thl_api.notifications.contracts import (
    SMTP_TOTAL_TIMEOUT_SECONDS,
    OutboundEmail,
    SendResult,
    WorkerSettings,
)

logger = logging.getLogger(__name__)


class EmailSendError(Exception):
    code: str = "EMAIL_PROVIDER_ERROR"


class EmailTimeoutError(EmailSendError):
    code = "EMAIL_TIMEOUT"


class EmailConnectionError(EmailSendError):
    code = "EMAIL_CONNECTION"


class EmailAuthError(EmailSendError):
    code = "EMAIL_AUTH"


class EmailRecipientRejectedError(EmailSendError):
    code = "EMAIL_RECIPIENT_REJECTED"


def _build_mime(message: OutboundEmail) -> EmailMessage:
    mime = EmailMessage()
    mime["From"] = message.from_address
    mime["To"] = message.to_address
    mime["Subject"] = message.subject
    mime["Message-ID"] = message.message_id
    mime.set_content(message.text_body)
    mime.add_alternative(message.html_body, subtype="html")
    return mime


def _map_smtp_exception(exc: Exception) -> EmailSendError:
    if isinstance(exc, EmailSendError):
        return exc
    if isinstance(exc, TimeoutError):
        return EmailTimeoutError()
    name = type(exc).__name__.lower()
    if "auth" in name or "authentication" in name:
        return EmailAuthError()
    if "recipient" in name or "refused" in name:
        return EmailRecipientRejectedError()
    if "connect" in name or "connection" in name:
        return EmailConnectionError()
    return EmailSendError()


@dataclass(frozen=True, slots=True)
class SmtpEmailSender:
    settings: WorkerSettings

    async def send(self, message: OutboundEmail) -> SendResult:
        mime = _build_mime(message)
        password = (
            self.settings.notification_smtp_password.get_secret_value()
            if self.settings.notification_smtp_password is not None
            else None
        )
        try:
            async with asyncio.timeout(SMTP_TOTAL_TIMEOUT_SECONDS):
                response = await aiosmtplib.send(
                    mime,
                    hostname=self.settings.notification_smtp_host,
                    port=self.settings.notification_smtp_port,
                    username=self.settings.notification_smtp_user,
                    password=password,
                    start_tls=self.settings.notification_smtp_starttls,
                    use_tls=self.settings.notification_smtp_use_tls,
                )
        except TimeoutError as exc:
            logger.warning(
                "SMTP send timed out",
                extra={"event": "notification_smtp_timeout", "error_code": "EMAIL_TIMEOUT"},
            )
            raise EmailTimeoutError from exc
        except Exception as exc:
            mapped = _map_smtp_exception(exc)
            logger.warning(
                "SMTP send failed",
                extra={
                    "event": "notification_smtp_failure",
                    "error_code": mapped.code,
                    "exception_type": type(exc).__name__,
                },
            )
            raise mapped from exc

        provider_id = str(response) if response else message.message_id
        return SendResult(provider_message_id=provider_id[:128])
