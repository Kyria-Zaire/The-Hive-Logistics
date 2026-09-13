from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from thl_api.turnstile.protocol import TurnstileAction

logger = logging.getLogger(__name__)

_SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


@dataclass(frozen=True, slots=True)
class HttpxTurnstileVerifier:
    secret: str
    expected_hostname: str
    timeout_seconds: float = 3.0

    async def verify(
        self,
        token: str,
        *,
        action: TurnstileAction,
    ) -> bool:
        data = {
            "secret": self.secret,
            "response": token,
            "action": action,
            "hostname": self.expected_hostname,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(_SITEVERIFY_URL, data=data)
                response.raise_for_status()
                payload = response.json()
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
