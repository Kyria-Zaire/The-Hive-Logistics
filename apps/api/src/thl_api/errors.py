from __future__ import annotations

import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from thl_api.middleware.correlation import CORRELATION_HEADER
from thl_api.problems import (
    PROBLEM_MEDIA,
    VALIDATION_ERROR,
    FieldError,
    correlation_from_request,
)

logger = logging.getLogger(__name__)

INTERNAL_ERROR_TYPE = "urn:thl:problem:internal-error"
INTERNAL_ERROR_CODE = "INTERNAL_ERROR"


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    correlation_id = correlation_from_request(request)
    errors: list[FieldError] = []
    for item in exc.errors():
        loc = item.get("loc", ())
        field_parts = [str(part) for part in loc if part != "body"]
        field = ".".join(field_parts) if field_parts else "body"
        message = str(item.get("msg", "Invalid value"))
        if len(message) > 256:
            message = message[:256]
        if len(field) > 128:
            field = field[:128]
        errors.append(FieldError(field=field, message=message))
        if len(errors) >= 50:
            break
    body: dict[str, Any] = {
        "type": VALIDATION_ERROR,
        "title": "Données invalides",
        "status": 422,
        "detail": "Une ou plusieurs valeurs sont incorrectes.",
        "code": "VALIDATION_ERROR",
        "correlation_id": correlation_id,
        "errors": [item.model_dump() for item in errors],
    }
    return JSONResponse(
        status_code=422,
        content=body,
        media_type=PROBLEM_MEDIA,
        headers={CORRELATION_HEADER: correlation_id},
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if isinstance(exc, (StarletteHTTPException, RequestValidationError)):
        raise exc

    correlation_id = correlation_from_request(request)
    logger.error(
        "Unhandled server error",
        extra={
            "correlation_id": correlation_id,
            "exception_type": type(exc).__name__,
        },
    )
    body: dict[str, Any] = {
        "type": INTERNAL_ERROR_TYPE,
        "title": "Erreur interne",
        "status": 500,
        "detail": "Une erreur interne est survenue.",
        "code": INTERNAL_ERROR_CODE,
        "correlation_id": correlation_id,
    }
    return JSONResponse(
        status_code=500,
        content=body,
        media_type=PROBLEM_MEDIA,
        headers={CORRELATION_HEADER: correlation_id},
    )
