"""OpenAPI problem and success response fragments for lead and health routes."""

from __future__ import annotations

from typing import Any

CORRELATION_ID_RESPONSE_HEADER: dict[str, Any] = {
    "description": "Identifiant de corrélation de la requête",
    "schema": {"type": "string", "maxLength": 64},
}

IDEMPOTENCY_REPLAYED_FALSE_HEADER: dict[str, Any] = {
    "schema": {"type": "string", "enum": ["false"]},
}

IDEMPOTENCY_REPLAYED_TRUE_HEADER: dict[str, Any] = {
    "schema": {"type": "string", "enum": ["true"]},
}

_BAD_REQUEST_EXAMPLE: dict[str, Any] = {
    "type": "urn:thl:problem:malformed-request",
    "title": "Requête invalide",
    "status": 400,
    "detail": "La requête n'a pas pu être lue.",
    "code": "MALFORMED_REQUEST",
    "correlation_id": "corr-fictif-001",
}

_UNPROCESSABLE_EXAMPLE: dict[str, Any] = {
    "type": "urn:thl:problem:validation-error",
    "title": "Données invalides",
    "status": 422,
    "detail": "Une ou plusieurs valeurs sont incorrectes.",
    "code": "VALIDATION_ERROR",
    "correlation_id": "corr-fictif-002",
    "errors": [{"field": "email", "message": "Format email invalide."}],
}

_FORBIDDEN_EXAMPLE: dict[str, Any] = {
    "type": "urn:thl:problem:request-denied",
    "title": "Demande refusée",
    "status": 403,
    "detail": "La demande n'a pas pu être acceptée.",
    "code": "REQUEST_DENIED",
    "correlation_id": "corr-fictif-003",
}

_IDEMPOTENCY_CONFLICT_EXAMPLE: dict[str, Any] = {
    "type": "urn:thl:problem:idempotency-conflict",
    "title": "Conflit d'idempotence",
    "status": 409,
    "detail": "Cette clé a déjà été utilisée avec un contenu différent.",
    "code": "IDEMPOTENCY_CONFLICT",
    "correlation_id": "corr-fictif-004",
}

_RATE_LIMITED_EXAMPLE: dict[str, Any] = {
    "type": "urn:thl:problem:rate-limited",
    "title": "Trop de requêtes",
    "status": 429,
    "detail": "Réessayez plus tard.",
    "code": "RATE_LIMITED",
    "correlation_id": "corr-fictif-005",
}

_PAYLOAD_TOO_LARGE_EXAMPLE: dict[str, Any] = {
    "type": "urn:thl:problem:payload-too-large",
    "title": "Payload trop volumineux",
    "status": 413,
    "code": "PAYLOAD_TOO_LARGE",
    "correlation_id": "corr-fictif-006",
}

_SERVICE_UNAVAILABLE_EXAMPLE: dict[str, Any] = {
    "type": "urn:thl:problem:dependency-unavailable",
    "title": "Service temporairement indisponible",
    "status": 503,
    "detail": "Impossible de traiter la demande pour le moment.",
    "code": "DEPENDENCY_UNAVAILABLE",
    "correlation_id": "corr-fictif-007",
}


def _problem_response(
    *,
    description: str,
    example: dict[str, Any] | None = None,
    extra_headers: dict[str, Any] | None = None,
) -> dict[str, Any]:
    headers: dict[str, Any] = {"X-Correlation-Id": CORRELATION_ID_RESPONSE_HEADER}
    if extra_headers:
        headers.update(extra_headers)
    content: dict[str, Any] = {
        "schema": {"$ref": "#/components/schemas/ProblemDetails"},
    }
    if example is not None:
        content["example"] = example
    return {
        "description": description,
        "headers": headers,
        "content": {"application/problem+json": content},
    }


BAD_REQUEST_RESPONSE: dict[str, Any] = _problem_response(
    description="JSON malformé ou en-tête invalide",
    example=_BAD_REQUEST_EXAMPLE,
)

UNPROCESSABLE_RESPONSE: dict[str, Any] = _problem_response(
    description="Schéma ou règle métier invalide (post-Pydantic)",
    example=_UNPROCESSABLE_EXAMPLE,
)

FORBIDDEN_RESPONSE: dict[str, Any] = _problem_response(
    description="Refus générique (honeypot, Turnstile)",
    example=_FORBIDDEN_EXAMPLE,
)

IDEMPOTENCY_CONFLICT_RESPONSE: dict[str, Any] = _problem_response(
    description="Même Idempotency-Key avec payload différent",
    example=_IDEMPOTENCY_CONFLICT_EXAMPLE,
)

RATE_LIMITED_RESPONSE: dict[str, Any] = _problem_response(
    description="Trop de requêtes",
    example=_RATE_LIMITED_EXAMPLE,
    extra_headers={
        "Retry-After": {
            "schema": {"type": "integer", "description": "Délai en secondes"},
        },
    },
)

PAYLOAD_TOO_LARGE_RESPONSE: dict[str, Any] = _problem_response(
    description="Corps > 64 KiB",
    example=_PAYLOAD_TOO_LARGE_EXAMPLE,
)

UNSUPPORTED_MEDIA_TYPE_RESPONSE: dict[str, Any] = _problem_response(
    description="Content-Type non application/json",
)

SERVICE_UNAVAILABLE_RESPONSE: dict[str, Any] = _problem_response(
    description="Dépendance requise indisponible (Turnstile, etc.)",
    example=_SERVICE_UNAVAILABLE_EXAMPLE,
)

def lead_post_responses(*, created_description: str) -> dict[int | str, Any]:
    return {
        "201": {
            "description": created_description,
            "headers": {
                "Idempotency-Replayed": IDEMPOTENCY_REPLAYED_FALSE_HEADER,
                "X-Correlation-Id": CORRELATION_ID_RESPONSE_HEADER,
            },
            "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/LeadSubmissionAccepted"},
            },
        },
        },
        "200": {
            "description": "Replay idempotent",
            "headers": {
                "Idempotency-Replayed": IDEMPOTENCY_REPLAYED_TRUE_HEADER,
                "X-Correlation-Id": CORRELATION_ID_RESPONSE_HEADER,
            },
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/LeadSubmissionAccepted"},
                },
            },
        },
        "400": BAD_REQUEST_RESPONSE,
        "403": FORBIDDEN_RESPONSE,
        "409": IDEMPOTENCY_CONFLICT_RESPONSE,
        "413": PAYLOAD_TOO_LARGE_RESPONSE,
        "415": UNSUPPORTED_MEDIA_TYPE_RESPONSE,
        "422": UNPROCESSABLE_RESPONSE,
        "429": RATE_LIMITED_RESPONSE,
        "503": SERVICE_UNAVAILABLE_RESPONSE,
    }


HEALTH_LIVE_RESPONSES: dict[int | str, Any] = {
    "200": {
        "description": "Processus vivant",
        "headers": {"X-Correlation-Id": CORRELATION_ID_RESPONSE_HEADER},
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/HealthLive"},
            },
        },
    },
}

HEALTH_READY_RESPONSES: dict[int | str, Any] = {
    "200": {
        "description": "Prêt",
        "headers": {"X-Correlation-Id": CORRELATION_ID_RESPONSE_HEADER},
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/HealthReady"},
            },
        },
    },
    "503": {
        "description": "Non prêt",
        "headers": {"X-Correlation-Id": CORRELATION_ID_RESPONSE_HEADER},
        "content": {
            "application/problem+json": {
                "schema": {"$ref": "#/components/schemas/ProblemDetails"},
            },
        },
    },
}
