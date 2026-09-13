from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from thl_api.models.enums import (
    ContactPreference,
    ContactSubject,
    ServiceType,
    VehicleCategory,
)
from thl_api.schemas import (
    ContactMessageCreate,
    LeadSubmissionAccepted,
    PreferredTimingExactDate,
    PreferredTimingPeriod,
    QuoteRequestCreate,
)
from thl_api.schemas.common import PHONE_PATTERN, PUBLIC_REFERENCE_PATTERN

REPO_ROOT = Path(__file__).resolve().parents[3]
OPENAPI_PATH = REPO_ROOT / "contracts" / "openapi" / "openapi.yaml"

OPENAPI_SCHEMA_NAMES = (
    "QuoteRequestCreateBase",
    "QuoteRequestCreate",
    "ContactMessageCreate",
    "PreferredTimingExactDate",
    "PreferredTimingPeriod",
    "LeadSubmissionAccepted",
    "PublicReference",
)


def _load_openapi() -> dict[str, Any]:
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _schema(doc: dict[str, Any], name: str) -> dict[str, Any]:
    return doc["components"]["schemas"][name]


def _resolve(doc: dict[str, Any], node: dict[str, Any]) -> dict[str, Any]:
    ref = node.get("$ref")
    if ref is None:
        return node
    name = ref.rsplit("/", maxsplit=1)[-1]
    return doc["components"]["schemas"][name]


def test_openapi_version() -> None:
    doc = _load_openapi()
    assert doc["openapi"] == "3.1.0"
    assert doc["info"]["version"] == "1.0.1"


def test_schema_names_present() -> None:
    doc = _load_openapi()
    names = doc["components"]["schemas"]
    for name in OPENAPI_SCHEMA_NAMES:
        assert name in names


def test_quote_base_required_and_extra() -> None:
    doc = _load_openapi()
    oas = _schema(doc, "QuoteRequestCreateBase")
    assert oas["additionalProperties"] is False
    assert set(oas["required"]) == set(QuoteRequestCreate.model_fields.keys()) - {
        "company",
        "special_constraints",
        "additional_message",
        "contact_preference",
        "vehicle_category_other_detail",
    }


def test_contact_required_and_extra() -> None:
    doc = _load_openapi()
    oas = _schema(doc, "ContactMessageCreate")
    assert oas["additionalProperties"] is False
    assert set(oas["required"]) == set(ContactMessageCreate.model_fields.keys()) - {
        "phone",
        "company",
    }


def test_enums_match_openapi() -> None:
    doc = _load_openapi()
    base = _schema(doc, "QuoteRequestCreateBase")
    service = _resolve(doc, base["properties"]["service"])
    vehicle = _resolve(doc, base["properties"]["vehicle_category"])
    assert [member.value for member in ServiceType] == service["enum"]
    assert [member.value for member in VehicleCategory] == vehicle["enum"]
    contact = _schema(doc, "ContactMessageCreate")
    subject = _resolve(doc, contact["properties"]["subject"])
    assert [member.value for member in ContactSubject] == subject["enum"]
    assert [member.value for member in ContactPreference] == _schema(doc, "ContactPreference")[
        "enum"
    ]


def test_string_lengths_and_patterns() -> None:
    doc = _load_openapi()
    base = _schema(doc, "QuoteRequestCreateBase")
    phone = base["properties"]["phone"]
    assert phone["minLength"] == 6
    assert phone["maxLength"] == 32
    assert phone["pattern"] == PHONE_PATTERN.pattern

    pub = _schema(doc, "PublicReference")
    assert pub["pattern"] == PUBLIC_REFERENCE_PATTERN.pattern

    lead = _schema(doc, "LeadSubmissionAccepted")
    assert lead["additionalProperties"] is False
    assert lead["properties"]["status"]["const"] == "received"
    assert "status" in LeadSubmissionAccepted.model_fields


def test_preferred_timing_variants() -> None:
    doc = _load_openapi()
    exact = _schema(doc, "PreferredTimingExactDate")
    period = _schema(doc, "PreferredTimingPeriod")
    assert set(exact["required"]) == set(PreferredTimingExactDate.model_fields.keys())
    assert set(period["required"]) == set(PreferredTimingPeriod.model_fields.keys())
    period_text = period["properties"]["period_text"]
    assert period_text["minLength"] == 3
    assert period_text["maxLength"] == 500


def test_idempotency_key_parameter() -> None:
    doc = _load_openapi()
    param = doc["components"]["parameters"]["IdempotencyKey"]
    schema = param["schema"]
    assert schema["maxLength"] == 36
    pattern = schema["pattern"]
    assert re.compile(pattern).pattern == (
        r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )


def test_quote_vehicle_other_conditional_documented() -> None:
    doc = _load_openapi()
    quote = _schema(doc, "QuoteRequestCreate")
    assert "allOf" in quote
    detail = _schema(doc, "QuoteRequestCreateBase")["properties"]["vehicle_category_other_detail"]
    assert detail["minLength"] == 2
    assert detail["maxLength"] == 200
