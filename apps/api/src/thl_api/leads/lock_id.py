from __future__ import annotations

import hashlib


def advisory_lock_id(scope: str, idempotency_key: str) -> int:
    material = hashlib.sha256(f"{scope}:{idempotency_key}".encode()).digest()
    raw = int.from_bytes(material[:8], byteorder="big", signed=False)
    if raw >= 2**63:
        return raw - 2**64
    return raw
