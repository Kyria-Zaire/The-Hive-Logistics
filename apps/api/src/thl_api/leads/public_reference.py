from __future__ import annotations

import secrets
from datetime import UTC, datetime

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def crockford8_from_random() -> str:
    value = secrets.randbits(40)
    chars: list[str] = []
    for _ in range(8):
        chars.append(_CROCKFORD[value & 0x1F])
        value >>= 5
    return "".join(reversed(chars))


def public_reference_for_accepted_at(accepted_at: datetime) -> str:
    if accepted_at.tzinfo is None:
        msg = "accepted_at must be timezone-aware"
        raise ValueError(msg)
    utc = accepted_at.astimezone(UTC)
    date_part = utc.strftime("%Y%m%d")
    return f"THL-{date_part}-{crockford8_from_random()}"
