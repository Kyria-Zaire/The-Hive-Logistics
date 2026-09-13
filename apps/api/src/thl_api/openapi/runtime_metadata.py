"""OpenAPI document metadata (Python literals, not loaded from YAML at runtime)."""

from __future__ import annotations

from typing import Any

OPENAPI_VERSION: str = "3.1.0"

INFO: dict[str, Any] = {
    "title": "THE HIVE LOGISTICS — API publique V1",
    "version": "1.0.1",
    "description": (
        "Contrat public V1 (leads Contact et Devis). Source de vérité des interfaces HTTP.\n"
        "PRD v0.1.4 — THL-ARCH-001 / 001A. Same-origin PROD (`servers.url: /`). Exemples fictifs.\n"
    ),
    "contact": {"name": "Kyria (Tech Lead)"},
}

SERVERS: list[dict[str, Any]] = [{"url": "/"}]

TAGS: list[dict[str, Any]] = [
    {"name": "quote-requests"},
    {"name": "contact-messages"},
    {"name": "health"},
]
