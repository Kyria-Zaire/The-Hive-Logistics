from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from thl_api.middleware.correlation import CORRELATION_HEADER

PROBLEM_MEDIA = "application/problem+json"


class FieldError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str = Field(max_length=128)
    message: str = Field(max_length=256)


class ProblemDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    title: str = Field(max_length=128)
    status: int
    detail: str | None = Field(default=None, max_length=512)
    instance: str | None = Field(default=None, max_length=256)
    code: str | None = Field(default=None, max_length=64)
    correlation_id: str | None = Field(default=None, max_length=64)
    errors: list[FieldError] | None = Field(default=None, max_length=50)


def correlation_from_request(request: Request) -> str:
    value = getattr(request.state, "correlation_id", None)
    if isinstance(value, str) and value:
        return value
    return "unknown"


def problem_response(
    request: Request,
    *,
    status: int,
    problem_type: str,
    title: str,
    code: str,
    detail: str | None = None,
    errors: list[FieldError] | None = None,
    extra_headers: dict[str, str] | None = None,
) -> JSONResponse:
    correlation_id = correlation_from_request(request)
    body = ProblemDetails(
        type=problem_type,
        title=title,
        status=status,
        detail=detail,
        code=code,
        correlation_id=correlation_id,
        errors=errors,
    )
    headers = {CORRELATION_HEADER: correlation_id}
    if extra_headers:
        headers.update(extra_headers)
    return JSONResponse(
        status_code=status,
        content=body.model_dump(mode="json", exclude_none=True),
        media_type=PROBLEM_MEDIA,
        headers=headers,
    )


MALFORMED_REQUEST = "urn:thl:problem:malformed-request"
VALIDATION_ERROR = "urn:thl:problem:validation-error"
REQUEST_DENIED = "urn:thl:problem:request-denied"
IDEMPOTENCY_CONFLICT = "urn:thl:problem:idempotency-conflict"
RATE_LIMITED = "urn:thl:problem:rate-limited"
PAYLOAD_TOO_LARGE = "urn:thl:problem:payload-too-large"
UNSUPPORTED_MEDIA = "urn:thl:problem:unsupported-media-type"
DEPENDENCY_UNAVAILABLE = "urn:thl:problem:dependency-unavailable"


def lead_success_headers(*, replayed: bool, correlation_id: str) -> dict[str, str]:
    return {
        CORRELATION_HEADER: correlation_id,
        "Idempotency-Replayed": "true" if replayed else "false",
    }


def json_response_body(content: dict[str, Any], *, headers: dict[str, str]) -> JSONResponse:
    return JSONResponse(status_code=200, content=content, headers=headers)
