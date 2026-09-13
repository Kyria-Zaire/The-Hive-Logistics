from __future__ import annotations

import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from thl_api.middleware.correlation import CORRELATION_HEADER

logger = logging.getLogger(__name__)

INTERNAL_ERROR_TYPE = "urn:thl:problem:internal-error"
INTERNAL_ERROR_CODE = "INTERNAL_ERROR"


def correlation_from_request(request: Request) -> str:
    value = getattr(request.state, "correlation_id", None)
    if isinstance(value, str) and value:
        return value
    return "unknown"


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
        media_type="application/problem+json",
        headers={CORRELATION_HEADER: correlation_id},
    )
