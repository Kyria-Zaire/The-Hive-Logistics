from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from thl_api.middleware.correlation import CORRELATION_HEADER, resolve_correlation_id

PROBLEM_MEDIA = "application/problem+json"


class FieldError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str = Field(max_length=128)
    message: str = Field(max_length=256)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: object, handler: object) -> dict[str, Any]:
        schema = handler(core_schema)  # type: ignore[operator]
        assert isinstance(schema, dict)
        schema.pop("additionalProperties", None)
        return schema


class ProblemDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = Field(
        json_schema_extra={"examples": ["urn:thl:problem:validation-error"]},
    )
    title: str = Field(max_length=128)
    status: int
    detail: str | None = Field(default=None, max_length=512)
    instance: str | None = Field(default=None, max_length=256)
    code: str | None = Field(default=None, max_length=64)
    correlation_id: str | None = Field(default=None, max_length=64)
    errors: list[FieldError] | None = Field(default=None, max_length=50)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: object, handler: object) -> dict[str, Any]:
        schema = handler(core_schema)  # type: ignore[operator]
        assert isinstance(schema, dict)
        schema["description"] = "RFC 9457 Problem Details"
        properties = schema.setdefault("properties", {})
        assert isinstance(properties, dict)
        for name, spec in (
            ("detail", {"type": "string", "maxLength": 512}),
            ("instance", {"type": "string", "format": "uri-reference", "maxLength": 256}),
            ("code", {"type": "string", "maxLength": 64}),
            ("correlation_id", {"type": "string", "maxLength": 64}),
            (
                "errors",
                {
                    "type": "array",
                    "maxItems": 50,
                    "items": {
                        "type": "object",
                        "required": ["field", "message"],
                        "properties": {
                            "field": {"type": "string", "maxLength": 128},
                            "message": {"type": "string", "maxLength": 256},
                        },
                    },
                },
            ),
        ):
            properties[name] = spec
        schema.pop("additionalProperties", None)
        return schema


def correlation_from_request(request: Request) -> str:
    value = getattr(request.state, "correlation_id", None)
    if isinstance(value, str) and value:
        return value
    raw = request.headers.get(CORRELATION_HEADER)
    return resolve_correlation_id(raw)


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
