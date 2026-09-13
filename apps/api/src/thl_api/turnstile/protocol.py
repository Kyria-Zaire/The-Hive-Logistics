from __future__ import annotations

from typing import Literal, Protocol

TurnstileAction = Literal["quote_request", "contact_message"]


class TurnstileVerifier(Protocol):
    async def verify(
        self,
        token: str,
        *,
        action: TurnstileAction,
    ) -> bool: ...
