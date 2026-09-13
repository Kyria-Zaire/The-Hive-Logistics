from __future__ import annotations

from dataclasses import dataclass, field

from thl_api.notifications.contracts import OutboundEmail, SendResult
from thl_api.notifications.smtp_sender import EmailSendError


@dataclass
class FakeEmailSender:
    results: list[SendResult] = field(default_factory=list)
    failures: list[EmailSendError] = field(default_factory=list)
    sent: list[OutboundEmail] = field(default_factory=list)

    async def send(self, message: OutboundEmail) -> SendResult:
        self.sent.append(message)
        if self.failures:
            raise self.failures.pop(0)
        if self.results:
            return self.results.pop(0)
        return SendResult(provider_message_id="fake-provider-id")


def worker_env_defaults() -> dict[str, str]:
    return {
        "NOTIFICATION_SMTP_HOST": "smtp.example.test",
        "NOTIFICATION_SMTP_PORT": "587",
        "NOTIFICATION_EMAIL_FROM": "noreply@example.com",
        "NOTIFICATION_EMAIL_TO": "ops@example.com",
        "NOTIFICATION_SMTP_STARTTLS": "true",
        "NOTIFICATION_SMTP_USE_TLS": "false",
    }
