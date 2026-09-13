from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field

import httpx

from thl_api.turnstile.protocol import TurnstileAction

logger = logging.getLogger(__name__)

_SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
_TOTAL_TIMEOUT_SECONDS = 3.0


@dataclass(frozen=True, slots=True)
class HttpxTurnstileVerifier:
    secret: str
    expected_hostname: str
    timeout_seconds: float = _TOTAL_TIMEOUT_SECONDS
    transport: httpx.AsyncBaseTransport | None = field(default=None, compare=False)

    async def verify(
        self,
        token: str,
        *,
        action: TurnstileAction,
    ) -> bool:
        data = {
            "secret": self.secret,
            "response": token,
        }
        timeout = httpx.Timeout(self.timeout_seconds)
        try:
            async with asyncio.timeout(self.timeout_seconds):
                async with httpx.AsyncClient(timeout=timeout, transport=self.transport) as client:
                    response = await client.post(_SITEVERIFY_URL, data=data)
                    response.raise_for_status()
                    payload = response.json()
        except TimeoutError as exc:
            logger.warning(
                "Turnstile siteverify timed out",
                extra={"exception_type": type(exc).__name__},
            )
            raise TurnstileUnavailableError from exc
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning(
                "Turnstile siteverify failed",
                extra={"exception_type": type(exc).__name__},
            )
            raise TurnstileUnavailableError from exc
        if not isinstance(payload, dict):
            raise TurnstileUnavailableError
        if payload.get("success") is not True:
            return False
        if payload.get("action") != action:
            return False
        hostname = payload.get("hostname")
        if hostname != self.expected_hostname:
            return False
        return True


class TurnstileUnavailableError(Exception):
    """Siteverify timeout, transport error, or invalid response."""
