from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import pytest
from email_validator import validate_email
from pydantic import ValidationError

from tests.lead_schema_fixtures import (
    CONTACT_FULL,
    CONTACT_MINIMAL,
    QUOTE_MINIMAL,
    QUOTE_OTHER,
    QUOTE_PERIOD_FULL,
    VALID_IDEMPOTENCY_KEY,
)
from thl_api.models.enums import (
    ContactPreference,
    ContactSubject,
    ServiceType,
    VehicleCategory,
)
from thl_api.schemas import (
    ContactMessageCreate,
    LeadSubmissionAccepted,
    QuoteRequestCreate,
    validate_idempotency_key,
)
from thl_api.schemas.common import IdempotencyKeyHeader


def _quote(data: dict[str, Any]) -> QuoteRequestCreate:
    return QuoteRequestCreate.model_validate(data)


def _contact(data: dict[str, Any]) -> ContactMessageCreate:
    return ContactMessageCreate.model_validate(data)


class TestFastAPIPythonPayload:
    def test_quote_wire_enums_coerce_to_strenum(self) -> None:
        model = _quote(QUOTE_MINIMAL)
        assert model.service is ServiceType.convoyage_premium
        assert model.vehicle_category is VehicleCategory.city_sedan
        assert model.preferred_timing.kind == "exact_date"

    def test_quote_period_and_contact_enums(self) -> None:
        quote = _quote(QUOTE_PERIOD_FULL)
        assert quote.contact_preference is ContactPreference.email
        contact = _contact(CONTACT_MINIMAL)
        assert contact.subject is ContactSubject.information

    @pytest.mark.parametrize("bad", ["true", "false", 1, 0])
    def test_vehicle_rolling_strict_bool(self, bad: object) -> None:
        data = dict(QUOTE_MINIMAL)
        data["vehicle_rolling"] = bad
        with pytest.raises(ValidationError):
            _quote(data)


class TestValidCases:
    def test_quote_minimal_exact_date(self) -> None:
        model = _quote(QUOTE_MINIMAL)
        assert model.preferred_timing.kind == "exact_date"

    def test_quote_full_period(self) -> None:
        model = _quote(QUOTE_PERIOD_FULL)
        assert model.contact_preference is not None
        assert model.company == "ACME"

    def test_quote_other_with_detail(self) -> None:
        _quote(QUOTE_OTHER)

    def test_contact_minimal(self) -> None:
        _contact(CONTACT_MINIMAL)

    def test_contact_full(self) -> None:
        model = _contact(CONTACT_FULL)
        assert model.phone is not None

    def test_lead_submission_accepted(self) -> None:
        LeadSubmissionAccepted.model_validate_json(
            json.dumps(
                {
                    "public_reference": "THL-20260912-7K3M9Q2X",
                    "status": "received",
                    "created_at": "2026-09-12T14:30:00+02:00",
                }
            )
        )

    def test_idempotency_key_valid(self) -> None:
        raw = VALID_IDEMPOTENCY_KEY
        assert validate_idempotency_key(raw) == raw
        header = IdempotencyKeyHeader.model_validate({"value": raw})
        assert header.value == raw


QUOTE_REQUIRED = [
    "turnstile_token",
    "honeypot",
    "privacy_acknowledgement",
    "first_name",
    "last_name",
    "email",
    "phone",
    "service",
    "departure_city",
    "departure_postal_code",
    "arrival_city",
    "arrival_postal_code",
    "preferred_timing",
    "vehicle_category",
    "vehicle_make",
    "vehicle_model",
    "vehicle_rolling",
]

CONTACT_REQUIRED = [
    "turnstile_token",
    "honeypot",
    "privacy_acknowledgement",
    "first_name",
    "last_name",
    "email",
    "subject",
    "message",
]


@pytest.mark.parametrize("missing", QUOTE_REQUIRED)
def test_quote_required_fields(missing: str) -> None:
    data = dict(QUOTE_MINIMAL)
    del data[missing]
    with pytest.raises(ValidationError):
        _quote(data)


@pytest.mark.parametrize("missing", CONTACT_REQUIRED)
def test_contact_required_fields(missing: str) -> None:
    data = dict(CONTACT_MINIMAL)
    del data[missing]
    with pytest.raises(ValidationError):
        _contact(data)


class TestBounds:
    def test_turnstile_min_max(self) -> None:
        data = dict(QUOTE_MINIMAL)
        data["turnstile_token"] = "1" * 10
        _quote(data)
        data["turnstile_token"] = "1" * 2048
        _quote(data)
        data["turnstile_token"] = "1" * 9
        with pytest.raises(ValidationError):
            _quote(data)
        data["turnstile_token"] = "1" * 2049
        with pytest.raises(ValidationError):
            _quote(data)

    def test_phone_bounds(self) -> None:
        data = dict(QUOTE_MINIMAL)
        data["phone"] = "123456"
        _quote(data)
        data["phone"] = "+" + ("1" * 32)
        with pytest.raises(ValidationError):
            _quote(data)

    def test_public_reference_invalid(self) -> None:
        with pytest.raises(ValidationError):
            LeadSubmissionAccepted.model_validate_json(
                json.dumps(
                    {
                        "public_reference": "THL-INVALID",
                        "status": "received",
                        "created_at": "2026-09-12T14:30:00Z",
                    }
                )
            )


class TestRfc3339FullDate:
    def test_valid_full_date(self) -> None:
        data = dict(QUOTE_MINIMAL)
        data["preferred_timing"] = {"kind": "exact_date", "exact_date": "2026-10-01"}
        _quote(data)

    @pytest.mark.parametrize(
        "bad_date",
        ["20261001", "2026-W40-4", "2026-02-30"],
    )
    def test_invalid_full_dates(self, bad_date: str) -> None:
        data = dict(QUOTE_MINIMAL)
        data["preferred_timing"] = {"kind": "exact_date", "exact_date": bad_date}
        with pytest.raises(ValidationError):
            _quote(data)


class TestStrictTypes:
    @pytest.mark.parametrize("bad", ["true", "false", 1, 0])
    def test_privacy_ack_rejects_non_bool(self, bad: object) -> None:
        data = dict(QUOTE_MINIMAL)
        data["privacy_acknowledgement"] = bad
        with pytest.raises(ValidationError):
            _quote(data)

    def test_privacy_ack_rejects_false(self) -> None:
        data = dict(QUOTE_MINIMAL)
        data["privacy_acknowledgement"] = False
        with pytest.raises(ValidationError):
            _quote(data)

    def test_unknown_enum_rejected(self) -> None:
        data = dict(QUOTE_MINIMAL)
        data["service"] = "unknown_service"
        with pytest.raises(ValidationError):
            _quote(data)

    def test_extra_property_rejected_quote(self) -> None:
        data = dict(QUOTE_MINIMAL)
        data["public_reference"] = "THL-20260912-7K3M9Q2X"
        with pytest.raises(ValidationError):
            _quote(data)

    def test_extra_in_preferred_timing_rejected(self) -> None:
        data = dict(QUOTE_MINIMAL)
        data["preferred_timing"] = {
            "kind": "exact_date",
            "exact_date": "2026-10-01",
            "extra": "x",
        }
        with pytest.raises(ValidationError):
            _quote(data)


QUOTE_OPTIONAL_FIELDS: list[tuple[str, dict[str, Any], Any | None]] = [
    ("company", QUOTE_MINIMAL, "ACME"),
    ("special_constraints", QUOTE_MINIMAL, "Accès difficile"),
    ("additional_message", QUOTE_MINIMAL, "Message additionnel"),
    ("contact_preference", QUOTE_MINIMAL, "email"),
]

CONTACT_OPTIONAL_FIELDS: list[tuple[str, dict[str, Any], Any | None]] = [
    ("phone", CONTACT_MINIMAL, "+33 6 00 00 00 01"),
    ("company", CONTACT_MINIMAL, "ACME"),
]


class TestNullability:
    def test_optional_absent_ok(self) -> None:
        model = _quote(QUOTE_MINIMAL)
        assert "company" not in model.model_fields_set

    @pytest.mark.parametrize(("field", "base", "valid_value"), QUOTE_OPTIONAL_FIELDS)
    def test_quote_optional_omitted_accepted(
        self, field: str, base: dict[str, Any], valid_value: Any | None
    ) -> None:
        data = dict(base)
        data.pop(field, None)
        _quote(data)

    @pytest.mark.parametrize(("field", "base", "valid_value"), QUOTE_OPTIONAL_FIELDS)
    def test_quote_optional_valid_value_accepted(
        self, field: str, base: dict[str, Any], valid_value: Any | None
    ) -> None:
        data = dict(base)
        data[field] = valid_value
        _quote(data)

    @pytest.mark.parametrize(("field", "base", "_valid_value"), QUOTE_OPTIONAL_FIELDS)
    def test_quote_optional_null_rejected(
        self, field: str, base: dict[str, Any], _valid_value: Any | None
    ) -> None:
        data = dict(base)
        data[field] = None
        with pytest.raises(ValidationError):
            _quote(data)

    def test_vehicle_other_detail_omitted_when_not_other(self) -> None:
        _quote(QUOTE_MINIMAL)

    def test_vehicle_other_detail_valid_when_other(self) -> None:
        _quote(QUOTE_OTHER)

    def test_vehicle_other_detail_null_rejected(self) -> None:
        data = dict(QUOTE_OTHER)
        data["vehicle_category_other_detail"] = None
        with pytest.raises(ValidationError):
            _quote(data)

    @pytest.mark.parametrize(("field", "base", "valid_value"), CONTACT_OPTIONAL_FIELDS)
    def test_contact_optional_omitted_accepted(
        self, field: str, base: dict[str, Any], valid_value: Any | None
    ) -> None:
        data = dict(base)
        data.pop(field, None)
        _contact(data)

    @pytest.mark.parametrize(("field", "base", "valid_value"), CONTACT_OPTIONAL_FIELDS)
    def test_contact_optional_valid_value_accepted(
        self, field: str, base: dict[str, Any], valid_value: Any | None
    ) -> None:
        data = dict(base)
        data[field] = valid_value
        _contact(data)

    @pytest.mark.parametrize(("field", "base", "_valid_value"), CONTACT_OPTIONAL_FIELDS)
    def test_contact_optional_null_rejected(
        self, field: str, base: dict[str, Any], _valid_value: Any | None
    ) -> None:
        data = dict(base)
        data[field] = None
        with pytest.raises(ValidationError):
            _contact(data)


class TestPreferredTiming:
    def test_period_valid(self) -> None:
        _quote(QUOTE_PERIOD_FULL)

    def test_unknown_kind(self) -> None:
        data = dict(QUOTE_MINIMAL)
        data["preferred_timing"] = {"kind": "soon", "exact_date": "2026-10-01"}
        with pytest.raises(ValidationError):
            _quote(data)

    def test_exact_date_missing_date(self) -> None:
        data = dict(QUOTE_MINIMAL)
        data["preferred_timing"] = {"kind": "exact_date"}
        with pytest.raises(ValidationError):
            _quote(data)

    def test_period_missing_text(self) -> None:
        data = dict(QUOTE_MINIMAL)
        data["preferred_timing"] = {"kind": "period"}
        with pytest.raises(ValidationError):
            _quote(data)

    def test_mixed_variants_rejected(self) -> None:
        data = dict(QUOTE_MINIMAL)
        data["preferred_timing"] = {
            "kind": "exact_date",
            "exact_date": "2026-10-01",
            "period_text": "Semaine 42",
        }
        with pytest.raises(ValidationError):
            _quote(data)


class TestVehicleOther:
    def test_other_without_detail(self) -> None:
        data = dict(QUOTE_MINIMAL)
        data["vehicle_category"] = "other"
        with pytest.raises(ValidationError):
            _quote(data)

    def test_non_other_with_detail_rejected(self) -> None:
        data = dict(QUOTE_MINIMAL)
        data["vehicle_category_other_detail"] = "Détail"
        with pytest.raises(ValidationError):
            _quote(data)

    def test_detail_null_rejected(self) -> None:
        data = dict(QUOTE_OTHER)
        data["vehicle_category_other_detail"] = None
        with pytest.raises(ValidationError):
            _quote(data)


class TestHoneypot:
    def test_empty_ok(self) -> None:
        _quote(QUOTE_MINIMAL)

    def test_nonempty_within_limit_ok(self) -> None:
        data = dict(QUOTE_MINIMAL)
        data["honeypot"] = "bot-value"
        _quote(data)

    def test_over_200_rejected(self) -> None:
        data = dict(QUOTE_MINIMAL)
        data["honeypot"] = "x" * 201
        with pytest.raises(ValidationError):
            _quote(data)


class TestSecurityRepresentation:
    def test_quote_repr_redacted(self) -> None:
        model = _quote(QUOTE_PERIOD_FULL)
        text = repr(model) + str(model)
        assert "redacted" in repr(model)
        for secret in (
            "1234567890",
            "Ada",
            "Lovelace",
            "ada@example.com",
            "+33",
            "ACME",
            "Peugeot",
            "Paris",
            "Lyon",
        ):
            assert secret not in text

    def test_idempotency_not_in_repr(self) -> None:
        header = IdempotencyKeyHeader.model_validate({"value": VALID_IDEMPOTENCY_KEY})
        assert VALID_IDEMPOTENCY_KEY not in repr(header)

    def test_email_no_network(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls: list[dict[str, object]] = []
        real_validate = validate_email

        def spy(address: str, /, *args: object, **kwargs: object) -> object:
            calls.append(dict(kwargs))
            assert kwargs.get("check_deliverability") is False
            return real_validate(address, *args, **kwargs)

        monkeypatch.setattr("thl_api.schemas.common.validate_email", spy)
        data = dict(QUOTE_MINIMAL)
        data["email"] = "user@example.com"
        model = _quote(data)
        assert model.email == "user@example.com"
        assert len(calls) == 1


class TestEmailPreserved:
    def test_email_case_preserved(self) -> None:
        data = dict(QUOTE_MINIMAL)
        data["email"] = "User.Name+Tag@Example.COM"
        model = _quote(data)
        assert model.email == "User.Name+Tag@Example.COM"
        validate_email(model.email, check_deliverability=False)


class TestIdempotencyKeyRules:
    @pytest.mark.parametrize(
        "bad",
        [
            "550E8400-E29B-41D4-A716-446655440000",
            "550e8400-e29b-41d4-a716-44665544000",
            "{550e8400-e29b-41d4-a716-446655440000}",
            "550e8400e29b41d4a716446655440000",
            "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        ],
    )
    def test_invalid_keys(self, bad: str) -> None:
        with pytest.raises(ValueError):
            validate_idempotency_key(bad)


class TestResponseTimezone:
    def test_naive_datetime_rejected(self) -> None:
        with pytest.raises(ValidationError):
            LeadSubmissionAccepted.model_validate(
                {
                    "public_reference": "THL-20260912-7K3M9Q2X",
                    "status": "received",
                    "created_at": datetime(2026, 9, 12, 12, 0, 0),
                }
            )

    def test_aware_ok(self) -> None:
        LeadSubmissionAccepted.model_validate(
            {
                "public_reference": "THL-20260912-7K3M9Q2X",
                "status": "received",
                "created_at": datetime(2026, 9, 12, 12, 0, 0, tzinfo=UTC),
            }
        )
