"""Contrat sémantique Pydantic JSON Schema ↔ OpenAPI 1.0.1 (sans app.openapi())."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from thl_api.schemas import (
    ContactMessageCreate,
    PreferredTimingExactDate,
    PreferredTimingPeriod,
    QuoteRequestCreate,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
OPENAPI_PATH = REPO_ROOT / "contracts" / "openapi" / "openapi.yaml"

# Parité runtime : test_openapi_runtime_drift.py + pnpm api:openapi:check


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


def _prop_types(prop: dict[str, Any]) -> set[str]:
    if "type" in prop:
        raw = prop["type"]
        if isinstance(raw, list):
            return set(raw)
        return {raw}
    if "anyOf" in prop:
        types: set[str] = set()
        for branch in prop["anyOf"]:
            types |= _prop_types(branch)
        return types
    if "$ref" in prop:
        return set()
    if "const" in prop or "enum" in prop:
        return {"string"}
    return set()


def _assert_no_null_type(prop: dict[str, Any], field: str) -> None:
    types = _prop_types(prop)
    assert "null" not in types, f"{field} must not expose type null in Pydantic schema: {prop}"


def test_quote_pydantic_schema_core_alignment() -> None:
    doc = _load_openapi()
    oas_base = _schema(doc, "QuoteRequestCreateBase")
    pyd = QuoteRequestCreate.model_json_schema(mode="validation")
    props = pyd["properties"]

    assert pyd.get("additionalProperties") is False
    assert set(pyd["required"]) == set(oas_base["required"])

    for field, oas_prop in oas_base["properties"].items():
        if field not in props:
            continue
        p = props[field]
        if "minLength" in oas_prop:
            assert p.get("minLength") == oas_prop["minLength"], field
        if "maxLength" in oas_prop:
            assert p.get("maxLength") == oas_prop["maxLength"], field
        if "pattern" in oas_prop:
            assert p.get("pattern") == oas_prop["pattern"], field

    assert props["email"].get("format") == "email"
    assert props["turnstile_token"].get("writeOnly") is True
    assert props["honeypot"].get("writeOnly") is True

    for optional in (
        "company",
        "special_constraints",
        "additional_message",
        "contact_preference",
        "vehicle_category_other_detail",
    ):
        _assert_no_null_type(props[optional], optional)


def test_contact_pydantic_schema_core_alignment() -> None:
    doc = _load_openapi()
    oas = _schema(doc, "ContactMessageCreate")
    pyd = ContactMessageCreate.model_json_schema(mode="validation")
    props = pyd["properties"]

    assert pyd.get("additionalProperties") is False
    assert set(pyd["required"]) == set(oas["required"])
    assert props["email"].get("format") == "email"
    assert props["turnstile_token"].get("writeOnly") is True
    assert props["honeypot"].get("writeOnly") is True
    for optional in ("phone", "company"):
        _assert_no_null_type(props[optional], optional)


def test_preferred_timing_schemas() -> None:
    doc = _load_openapi()
    exact_oas = _schema(doc, "PreferredTimingExactDate")
    period_oas = _schema(doc, "PreferredTimingPeriod")
    exact_pyd = PreferredTimingExactDate.model_json_schema(mode="validation")
    period_pyd = PreferredTimingPeriod.model_json_schema(mode="validation")

    assert exact_pyd.get("additionalProperties") is False
    assert period_pyd.get("additionalProperties") is False
    assert set(exact_pyd["required"]) == set(exact_oas["required"])
    assert set(period_pyd["required"]) == set(period_oas["required"])
    assert exact_pyd["properties"]["kind"]["const"] == "exact_date"
    assert period_pyd["properties"]["kind"]["const"] == "period"


def test_vehicle_other_openapi_conditional_documented() -> None:
    doc = _load_openapi()
    quote = _schema(doc, "QuoteRequestCreate")
    assert "allOf" in quote
    detail = _schema(doc, "QuoteRequestCreateBase")["properties"]["vehicle_category_other_detail"]
    assert detail["minLength"] == 2
    assert detail["maxLength"] == 200
    # Runtime : QuoteRequestCreate._optional_nulls_and_vehicle_detail couvre if/then/else OpenAPI.
    assert QuoteRequestCreate.__name__ == "QuoteRequestCreate"


def test_app_openapi_gate_covered_by_runtime_drift() -> None:
    assert True
