from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from thl_api.api.deps import get_lead_submission_service
from thl_api.openapi.parameters import LEAD_POST_PARAMETERS
from thl_api.openapi.problem_responses import lead_post_responses
from thl_api.problems import (
    DEPENDENCY_UNAVAILABLE,
    IDEMPOTENCY_CONFLICT,
    RATE_LIMITED,
    REQUEST_DENIED,
    correlation_from_request,
    lead_success_headers,
    problem_response,
)
from thl_api.schemas.common import validate_idempotency_key
from thl_api.schemas.leads import ContactMessageCreate, LeadSubmissionAccepted, QuoteRequestCreate
from thl_api.services.lead_submission import (
    HoneypotTriggeredError,
    IdempotencyBusyError,
    IdempotencyConflictError,
    LeadSubmissionService,
    RateLimitExceededError,
    SubmissionSuccess,
    TurnstileRejectedError,
)
from thl_api.turnstile.httpx_client import TurnstileUnavailableError

router = APIRouter()

_IDEMPOTENCY_HEADER = "Idempotency-Key"

_QUOTE_DESCRIPTION = (
    "Pipeline ADR-004. Turnstile uniquement après validation Pydantic et verrou idempotence "
    "(nouvelle opération).\n"
    "Réponse 201/200 uniquement après commit PostgreSQL.\n"
)

_QUOTE_REQUEST_EXAMPLE: dict[str, Any] = {
    "turnstile_token": "0.FAKE_TURNSTILE_TOKEN_EXAMPLE_ONLY",
    "honeypot": "",
    "privacy_acknowledgement": True,
    "first_name": "Alex",
    "last_name": "Martin",
    "email": "alex.martin@example.invalid",
    "phone": "+33 6 01 02 03 04",
    "service": "convoyage_premium",
    "departure_city": "Lyon",
    "departure_postal_code": "69002",
    "arrival_city": "Paris",
    "arrival_postal_code": "75008",
    "preferred_timing": {
        "kind": "period",
        "period_text": "Semaine du 15 au 22 octobre 2026",
    },
    "vehicle_category": "premium_sport",
    "vehicle_make": "Porsche",
    "vehicle_model": "911",
    "vehicle_rolling": True,
}

_CONTACT_REQUEST_EXAMPLE: dict[str, Any] = {
    "turnstile_token": "0.FAKE_TURNSTILE_TOKEN_EXAMPLE_ONLY",
    "honeypot": "",
    "privacy_acknowledgement": True,
    "first_name": "Sam",
    "last_name": "Dupont",
    "email": "sam.dupont@example.invalid",
    "subject": "information",
    "message": "Bonjour, j'aimerais en savoir plus sur vos services.",
    "phone": "+33 6 05 06 07 08",
}


def _invalid_idempotency_response(request: Request) -> JSONResponse:
    from thl_api.problems import MALFORMED_REQUEST

    return problem_response(
        request,
        status=400,
        problem_type=MALFORMED_REQUEST,
        title="Requête invalide",
        code="MALFORMED_REQUEST",
        detail="En-tête Idempotency-Key invalide.",
    )


def _client_host(request: Request) -> str | None:
    if request.client is None:
        return None
    return request.client.host


@router.post(
    "/quote-requests",
    tags=["quote-requests"],
    operation_id="createQuoteRequest",
    summary="Créer une demande de devis",
    description=_QUOTE_DESCRIPTION,
    response_model=LeadSubmissionAccepted,
    responses=lead_post_responses(created_description="Demande créée"),
    openapi_extra={
        "parameters": LEAD_POST_PARAMETERS,
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "examples": {
                        "fictifComplet": {
                            "summary": "Exemple fictif",
                            "value": _QUOTE_REQUEST_EXAMPLE,
                        },
                    },
                },
            },
        },
    },
)
async def create_quote_request(
    request: Request,
    body: QuoteRequestCreate,
) -> JSONResponse:
    idempotency_key = request.headers.get(_IDEMPOTENCY_HEADER)
    if idempotency_key is None:
        return _invalid_idempotency_response(request)
    try:
        validate_idempotency_key(idempotency_key)
    except ValueError:
        return _invalid_idempotency_response(request)
    service = get_lead_submission_service()
    return await _handle_submission(
        request,
        service,
        lambda: service.submit_quote(
            body,
            idempotency_key=idempotency_key,
            client_host=_client_host(request),
            forwarded_for=request.headers.get("x-forwarded-for"),
        ),
    )


@router.post(
    "/contact-messages",
    tags=["contact-messages"],
    operation_id="createContactMessage",
    summary="Créer un message contact",
    response_model=LeadSubmissionAccepted,
    responses=lead_post_responses(created_description="Message enregistré"),
    openapi_extra={
        "parameters": LEAD_POST_PARAMETERS,
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "examples": {
                        "fictif": {"value": _CONTACT_REQUEST_EXAMPLE},
                    },
                },
            },
        },
    },
)
async def create_contact_message(
    request: Request,
    body: ContactMessageCreate,
) -> JSONResponse:
    idempotency_key = request.headers.get(_IDEMPOTENCY_HEADER)
    if idempotency_key is None:
        return _invalid_idempotency_response(request)
    try:
        validate_idempotency_key(idempotency_key)
    except ValueError:
        return _invalid_idempotency_response(request)
    service = get_lead_submission_service()
    return await _handle_submission(
        request,
        service,
        lambda: service.submit_contact(
            body,
            idempotency_key=idempotency_key,
            client_host=_client_host(request),
            forwarded_for=request.headers.get("x-forwarded-for"),
        ),
    )


async def _handle_submission(
    request: Request,
    _service: LeadSubmissionService,
    call: Callable[[], Awaitable[SubmissionSuccess]],
) -> JSONResponse:
    correlation_id = correlation_from_request(request)
    try:
        result = await call()
    except HoneypotTriggeredError:
        return problem_response(
            request,
            status=403,
            problem_type=REQUEST_DENIED,
            title="Demande refusée",
            code="REQUEST_DENIED",
            detail="La demande n'a pas pu être acceptée.",
        )
    except TurnstileRejectedError:
        return problem_response(
            request,
            status=403,
            problem_type=REQUEST_DENIED,
            title="Demande refusée",
            code="REQUEST_DENIED",
            detail="La demande n'a pas pu être acceptée.",
        )
    except IdempotencyConflictError:
        return problem_response(
            request,
            status=409,
            problem_type=IDEMPOTENCY_CONFLICT,
            title="Conflit d'idempotence",
            code="IDEMPOTENCY_CONFLICT",
            detail="Cette clé a déjà été utilisée avec un contenu différent.",
        )
    except RateLimitExceededError as exc:
        return problem_response(
            request,
            status=429,
            problem_type=RATE_LIMITED,
            title="Trop de requêtes",
            code="RATE_LIMITED",
            detail="Réessayez plus tard.",
            extra_headers={"Retry-After": str(exc.retry_after_seconds)},
        )
    except IdempotencyBusyError:
        return problem_response(
            request,
            status=503,
            problem_type=DEPENDENCY_UNAVAILABLE,
            title="Service temporairement indisponible",
            code="IDEMPOTENCY_BUSY",
            detail="Impossible de traiter la demande pour le moment.",
        )
    except TurnstileUnavailableError:
        return problem_response(
            request,
            status=503,
            problem_type=DEPENDENCY_UNAVAILABLE,
            title="Service temporairement indisponible",
            code="DEPENDENCY_UNAVAILABLE",
            detail="Impossible de traiter la demande pour le moment.",
        )

    headers = lead_success_headers(replayed=result.replayed, correlation_id=correlation_id)
    return JSONResponse(status_code=result.status_code, content=result.body, headers=headers)
