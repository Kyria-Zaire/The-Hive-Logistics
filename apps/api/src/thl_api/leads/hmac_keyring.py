from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HmacSecret:
    version: int
    secret: bytes


@dataclass(frozen=True, slots=True)
class HmacKeyring:
    current: HmacSecret
    previous: HmacSecret | None

    def digest_hex(self, message: bytes, *, for_version: int | None = None) -> tuple[str, int]:
        if for_version is not None:
            secret = self._secret_for_version(for_version)
            return _hmac_hex(secret.secret, message), secret.version
        return _hmac_hex(self.current.secret, message), self.current.version

    def digests_for_lookup(self, message: bytes) -> list[tuple[str, int]]:
        out: list[tuple[str, int]] = [
            (_hmac_hex(self.current.secret, message), self.current.version),
        ]
        if self.previous is not None:
            prev = (_hmac_hex(self.previous.secret, message), self.previous.version)
            if prev not in out:
                out.append(prev)
        return out

    def _secret_for_version(self, version: int) -> HmacSecret:
        if version == self.current.version:
            return self.current
        if self.previous is not None and version == self.previous.version:
            return self.previous
        msg = f"Unknown HMAC key version: {version}"
        raise ValueError(msg)


def _hmac_hex(secret: bytes, message: bytes) -> str:
    return hmac.new(secret, message, hashlib.sha256).hexdigest()
