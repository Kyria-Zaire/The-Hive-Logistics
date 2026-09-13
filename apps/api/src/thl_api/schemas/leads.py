from __future__ import annotations

import re
from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import AwareDatetime, Field, StrictBool, field_validator, model_validator
from pydantic.functional_validators import BeforeValidator
from pydantic.json_schema import SkipJsonSchema

from thl_api.models.enums import (
    ContactPreference,
    ContactSubject,
    ServiceType,
    VehicleCategory,
)
from thl_api.schemas.common import (
    PUBLIC_REFERENCE_PATTERN,
    EmailAddress,
    EmailValidatedMixin,
    OptionalPhoneNumber,
    PhoneNumber,
    PrivacyAcknowledgementMixin,
    RedactedRequestRepresentationMixin,
    THLSchemaBase,
    reject_null_for_optional_fields,
)

TurnstileToken = Annotated[
    str,
    Field(min_length=10, max_length=2048, json_schema_extra={"writeOnly": True}),
]
HoneypotField = Annotated[
    str,
    Field(max_length=200, json_schema_extra={"writeOnly": True}),
]
PersonName = Annotated[str, Field(min_length=1, max_length=80)]
CityName = Annotated[str, Field(min_length=1, max_length=120)]
PostalCode = Annotated[str, Field(min_length=4, max_length=12)]
VehicleMakeModel = Annotated[str, Field(min_length=1, max_length=80)]
CompanyName = Annotated[str, Field(max_length=160)]
SpecialConstraints = Annotated[str, Field(max_length=2000)]
AdditionalMessage = Annotated[str, Field(max_length=4000)]
ContactMessageBody = Annotated[str, Field(min_length=10, max_length=8000)]
VehicleOtherDetail = Annotated[str, Field(min_length=2, max_length=200)]
PeriodText = Annotated[str, Field(min_length=3, max_length=500)]

PublicReference = Annotated[str, Field(pattern=PUBLIC_REFERENCE_PATTERN.pattern)]

_RFC3339_FULL_DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


def _parse_rfc3339_full_date(value: object) -> object:
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        return value
    if not _RFC3339_FULL_DATE.fullmatch(value):
        msg = "exact_date must be an RFC 3339 full-date (YYYY-MM-DD)"
        raise ValueError(msg)
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        msg = "exact_date is not a valid calendar date"
        raise ValueError(msg) from exc


Rfc3339FullDate = Annotated[date, BeforeValidator(_parse_rfc3339_full_date)]


class PreferredTimingExactDate(THLSchemaBase):
    kind: Literal["exact_date"]
    exact_date: Rfc3339FullDate


class PreferredTimingPeriod(THLSchemaBase):
    kind: Literal["period"]
    period_text: PeriodText


PreferredTiming = Annotated[
    PreferredTimingExactDate | PreferredTimingPeriod,
    Field(discriminator="kind"),
]

_QUOTE_OPTIONAL_FIELDS = (
    "company",
    "special_constraints",
    "additional_message",
    "contact_preference",
    "vehicle_category_other_detail",
)


class QuoteRequestCreate(
    RedactedRequestRepresentationMixin,
    PrivacyAcknowledgementMixin,
    EmailValidatedMixin,
    THLSchemaBase,
):
    turnstile_token: TurnstileToken
    honeypot: HoneypotField
    privacy_acknowledgement: Literal[True]
    first_name: PersonName
    last_name: PersonName
    email: EmailAddress
    phone: PhoneNumber
    service: ServiceType
    departure_city: CityName
    departure_postal_code: PostalCode
    arrival_city: CityName
    arrival_postal_code: PostalCode
    preferred_timing: PreferredTiming
    vehicle_category: VehicleCategory
    vehicle_category_other_detail: Annotated[
        VehicleOtherDetail | SkipJsonSchema[None],
        Field(
            default=None,
            description="Required when vehicle_category is other; must be omitted otherwise.",
        ),
    ] = None
    vehicle_make: VehicleMakeModel
    vehicle_model: VehicleMakeModel
    vehicle_rolling: StrictBool
    company: CompanyName | SkipJsonSchema[None] = None
    special_constraints: SpecialConstraints | SkipJsonSchema[None] = None
    additional_message: AdditionalMessage | SkipJsonSchema[None] = None
    contact_preference: ContactPreference | SkipJsonSchema[None] = None

    @model_validator(mode="before")
    @classmethod
    def _optional_nulls_and_vehicle_detail(cls, data: object) -> object:
        data = reject_null_for_optional_fields(data, _QUOTE_OPTIONAL_FIELDS)
        if not isinstance(data, dict):
            return data
        category = data.get("vehicle_category")
        has_detail_key = "vehicle_category_other_detail" in data
        is_other = category == VehicleCategory.other or category == VehicleCategory.other.value
        if is_other:
            if not has_detail_key or data.get("vehicle_category_other_detail") is None:
                msg = "vehicle_category_other_detail is required when vehicle_category is other"
                raise ValueError(msg)
        elif has_detail_key:
            msg = "vehicle_category_other_detail must be absent unless vehicle_category is other"
            raise ValueError(msg)
        return data


class ContactMessageCreate(
    RedactedRequestRepresentationMixin,
    PrivacyAcknowledgementMixin,
    EmailValidatedMixin,
    THLSchemaBase,
):
    turnstile_token: TurnstileToken
    honeypot: HoneypotField
    privacy_acknowledgement: Literal[True]
    first_name: PersonName
    last_name: PersonName
    email: EmailAddress
    subject: ContactSubject
    message: ContactMessageBody
    phone: OptionalPhoneNumber | SkipJsonSchema[None] = None
    company: CompanyName | SkipJsonSchema[None] = None

    @model_validator(mode="before")
    @classmethod
    def _reject_null_optionals(cls, data: object) -> object:
        return reject_null_for_optional_fields(data, ("phone", "company"))


class LeadSubmissionAccepted(THLSchemaBase):
    public_reference: PublicReference
    status: Literal["received"]
    created_at: AwareDatetime

    @field_validator("created_at", mode="after")
    @classmethod
    def _reject_naive_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError("created_at must include a timezone")
        return value
