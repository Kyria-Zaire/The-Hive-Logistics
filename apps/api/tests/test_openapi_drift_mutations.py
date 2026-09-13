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


def _mutate_runtime_actual(mutator) -> dict:
    actual = generate_raw_openapi(create_app())
    mutated = deepcopy(actual)
    mutator(mutated)
    return mutated


def test_mutation_idempotency_requiredness_breaks_gate() -> None:
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        expected = yaml.safe_load(handle)

    def _break(doc: dict) -> None:
        parameters = doc["paths"]["/api/v1/quote-requests"]["post"]["parameters"]
        for param in parameters:
            if param.get("name") == "Idempotency-Key":
                param["required"] = False

    actual = _mutate_runtime_actual(_break)
    assert openapi_diff(expected, actual)


def test_mutation_response_status_breaks_gate() -> None:
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        expected = yaml.safe_load(handle)

    def _break(doc: dict) -> None:
        doc["paths"]["/api/v1/quote-requests"]["post"]["responses"]["201"]["headers"] = {}

    actual = _mutate_runtime_actual(_break)
    assert openapi_diff(expected, actual)


def test_mutation_request_enum_breaks_gate() -> None:
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        expected = yaml.safe_load(handle)

    def _break(doc: dict) -> None:
        service = doc["components"]["schemas"]["ServiceType"]
        service["enum"] = list(service["enum"]) + ["invalid"]

    actual = _mutate_runtime_actual(_break)
    assert openapi_diff(expected, actual)


def test_mutation_nullability_breaks_gate() -> None:
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        expected = yaml.safe_load(handle)

    def _break(doc: dict) -> None:
        phone = doc["components"]["schemas"]["QuoteRequestCreateBase"]["properties"]["phone"]
        phone["type"] = ["string", "null"]

    actual = _mutate_runtime_actual(_break)
    assert openapi_diff(expected, actual)


def test_mutation_request_body_schema_breaks_gate() -> None:
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        expected = yaml.safe_load(handle)

    def _break(doc: dict) -> None:
        doc["paths"]["/api/v1/contact-messages"]["post"]["requestBody"]["required"] = False

    actual = _mutate_runtime_actual(_break)
    assert openapi_diff(expected, actual)


def test_mutation_problem_details_breaks_gate() -> None:
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        expected = yaml.safe_load(handle)

    def _break(doc: dict) -> None:
        schema = doc["components"]["schemas"]["ProblemDetails"]
        schema["required"] = ["type", "title"]

    actual = _mutate_runtime_actual(_break)
    assert openapi_diff(expected, actual)


def test_mutation_vehicle_other_conditional_breaks_gate() -> None:
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        expected = yaml.safe_load(handle)

    def _break(doc: dict) -> None:
        quote = doc["components"]["schemas"]["QuoteRequestCreate"]
        quote["allOf"][1]["then"]["required"] = []

    actual = _mutate_runtime_actual(_break)
    assert openapi_diff(expected, actual)


def test_baseline_gate_is_clean() -> None:
    assert _baseline_diffs() == []
