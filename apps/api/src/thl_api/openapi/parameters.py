"""OpenAPI parameter declarations attached to routes (not loaded from YAML)."""

from __future__ import annotations

from typing import Any

IDEMPOTENCY_KEY_PARAMETER: dict[str, Any] = {
    "name": "Idempotency-Key",
    "in": "header",
    "required": True,
    "description": "UUID v4 (RFC 9562). Portée distincte par endpoint.",
    "schema": {
        "type": "string",
        "format": "uuid",
        "maxLength": 36,
        "pattern": (
            r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        ),
    },
}

CORRELATION_ID_REQUEST_PARAMETER: dict[str, Any] = {
    "name": "X-Correlation-Id",
    "in": "header",
    "required": False,
    "description": (
        "Identifiant de corrélation non sensible ; validé ou remplacé par le serveur."
    ),
    "schema": {
        "type": "string",
        "maxLength": 64,
        "pattern": r"^[A-Za-z0-9._-]+$",
    },
}

LEAD_POST_PARAMETERS: list[dict[str, Any]] = [
    IDEMPOTENCY_KEY_PARAMETER,
    CORRELATION_ID_REQUEST_PARAMETER,
]
