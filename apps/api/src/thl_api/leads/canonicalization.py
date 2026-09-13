from __future__ import annotations

import json
import unicodedata
from typing import Any


def nfc_string(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def normalize_fingerprint_tree(value: Any) -> Any:
    if isinstance(value, str):
        return nfc_string(value)
    if isinstance(value, dict):
        return {key: normalize_fingerprint_tree(val) for key, val in sorted(value.items())}
    if isinstance(value, list):
        return [normalize_fingerprint_tree(item) for item in value]
    return value


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    normalized = normalize_fingerprint_tree(payload)
    return json.dumps(normalized, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
