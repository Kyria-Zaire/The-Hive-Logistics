from __future__ import annotations

import re
from typing import Annotated

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.functional_validators import AfterValidator

# OpenAPI components/parameters/IdempotencyKey
_IDEMPOTENCY_KEY_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

# OpenAPI QuoteRequestCreateBase.properties.phone / ContactMessageCreate.properties.phone
PHONE_PATTERN = re.compile(r"^[+0-9().\s-]+$")

# OpenAPI components/schemas/PublicReference
PUBLIC_REFERENCE_PATTERN = re.compile(r"^THL-[0-9]{8}-[0-9A-HJKMNP-TV-Z]{8}$")

_HTTP_MODEL_CONFIG = ConfigDict(
    extra="forbid",
    str_strip_whitespace=False,
    validate_default=True,
)


class THLSchemaBase(BaseModel):
    model_config = _HTTP_MODEL_CONFIG


class RedactedRequestRepresentationMixin:
    """repr/str sans PII ni secrets (ADR-004 / ticket leads)."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(redacted)"

    def __str__(self) -> str:
        return self.__repr__()


def validate_email_syntax_preserve(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("email must be a string")
    if len(value) > 254:
        msg = "email must be at most 254 characters"
        raise ValueError(msg)
    try:
        validate_email(value, check_deliverability=False)
    except EmailNotValidError as exc:
        raise ValueError("invalid email format") from exc
    return value


EmailAddress = Annotated[
    str,
    Field(max_length=254, json_schema_extra={"format": "email"}),
]


class PrivacyAcknowledgementMixin:
    @field_validator("privacy_acknowledgement", mode="before")
    @classmethod
    def _privacy_must_be_json_true(cls, value: object) -> object:
        if value is not True:
            msg = "privacy_acknowledgement must be true"
            raise ValueError(msg)
        return value


class EmailValidatedMixin:
    @field_validator("email", mode="before")
    @classmethod
    def _validate_email_field(cls, value: object) -> object:
        if value is None:
            raise ValueError("null is not allowed")
        if not isinstance(value, str):
            return value
        return validate_email_syntax_preserve(value)


PhoneNumber = Annotated[
    str,
    Field(min_length=6, max_length=32, pattern=PHONE_PATTERN.pattern),
]

OptionalPhoneNumber = Annotated[
    str,
    Field(min_length=6, max_length=32, pattern=PHONE_PATTERN.pattern),
]


def validate_idempotency_key(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("Idempotency-Key must be a string")
    if len(value) > 36:
        msg = "Idempotency-Key must be at most 36 characters"
        raise ValueError(msg)
    if not _IDEMPOTENCY_KEY_PATTERN.fullmatch(value):
        msg = "Idempotency-Key must be a canonical lowercase UUID v4"
        raise ValueError(msg)
    return value


IdempotencyKey = Annotated[
    str,
    Field(max_length=36),
    AfterValidator(validate_idempotency_key),
]


class IdempotencyKeyHeader(BaseModel):
    """En-tête Idempotency-Key (validation hors corps JSON)."""

    model_config = _HTTP_MODEL_CONFIG

    value: IdempotencyKey

    @field_validator("value", mode="before")
    @classmethod
    def _validate_uuid_v4(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        return validate_idempotency_key(value)

    def __repr__(self) -> str:
        return "IdempotencyKeyHeader(redacted)"

    def __str__(self) -> str:
        return self.__repr__()


def reject_null_for_optional_fields(data: object, field_names: tuple[str, ...]) -> object:
    if not isinstance(data, dict):
        return data
    for name in field_names:
        if name in data and data[name] is None:
            msg = f"{name} must be omitted, not null"
            raise ValueError(msg)
    return data
