from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml

from thl_api.main import create_app
from thl_api.openapi.drift import openapi_diff
from thl_api.openapi.raw import generate_raw_openapi

REPO_ROOT = Path(__file__).resolve().parents[3]
OPENAPI_PATH = REPO_ROOT / "contracts" / "openapi" / "openapi.yaml"


def _baseline_diffs() -> list[str]:
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        expected = yaml.safe_load(handle)
    actual = generate_raw_openapi(create_app())
    return openapi_diff(expected, actual)


def test_mutation_idempotency_requiredness_breaks_gate() -> None:
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        expected = yaml.safe_load(handle)
    mutated = deepcopy(expected)
    mutated["components"]["parameters"]["IdempotencyKey"]["required"] = False
    actual = generate_raw_openapi(create_app())
    assert openapi_diff(mutated, actual)


def test_mutation_response_status_breaks_gate() -> None:
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        expected = yaml.safe_load(handle)
    mutated = deepcopy(expected)
    mutated["paths"]["/api/v1/quote-requests"]["post"]["responses"]["201"]["headers"] = {}
    actual = generate_raw_openapi(create_app())
    assert openapi_diff(mutated, actual)


def test_mutation_request_enum_breaks_gate() -> None:
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        expected = yaml.safe_load(handle)
    mutated = deepcopy(expected)
    service = mutated["components"]["schemas"]["ServiceType"]
    service["enum"] = list(service["enum"]) + ["invalid"]
    actual = generate_raw_openapi(create_app())
    assert openapi_diff(mutated, actual)


def test_mutation_nullability_breaks_gate() -> None:
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        expected = yaml.safe_load(handle)
    mutated = deepcopy(expected)
    phone = mutated["components"]["schemas"]["QuoteRequestCreateBase"]["properties"]["phone"]
    phone["type"] = ["string", "null"]
    actual = generate_raw_openapi(create_app())
    assert openapi_diff(mutated, actual)


def test_mutation_request_body_schema_breaks_gate() -> None:
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        expected = yaml.safe_load(handle)
    mutated = deepcopy(expected)
    mutated["paths"]["/api/v1/contact-messages"]["post"]["requestBody"]["required"] = False
    actual = generate_raw_openapi(create_app())
    assert openapi_diff(mutated, actual)


def test_baseline_gate_is_clean() -> None:
    assert _baseline_diffs() == []
