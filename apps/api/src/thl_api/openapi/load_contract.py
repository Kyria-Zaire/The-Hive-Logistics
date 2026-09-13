from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, cast

import yaml

REPO_ROOT = Path(__file__).resolve().parents[5]
OPENAPI_PATH = REPO_ROOT / "contracts" / "openapi" / "openapi.yaml"


@lru_cache(maxsize=1)
def load_openapi_contract() -> dict[str, Any]:
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    assert isinstance(loaded, dict)
    return loaded


def contract_components() -> dict[str, Any]:
    return cast(dict[str, Any], load_openapi_contract().get("components", {}))


def contract_responses() -> dict[str, Any]:
    return cast(dict[str, Any], contract_components().get("responses", {}))


def contract_parameters() -> dict[str, Any]:
    return cast(dict[str, Any], contract_components().get("parameters", {}))


def contract_headers() -> dict[str, Any]:
    return cast(dict[str, Any], contract_components().get("headers", {}))


def contract_schemas() -> dict[str, Any]:
    return cast(dict[str, Any], contract_components().get("schemas", {}))


def lead_post_parameters() -> list[dict[str, Any]]:
    return [
        {"$ref": "#/components/parameters/IdempotencyKey"},
        {"$ref": "#/components/parameters/CorrelationIdRequest"},
    ]


def lead_post_responses() -> dict[int | str, Any]:
    path_item = load_openapi_contract()["paths"]["/api/v1/quote-requests"]["post"]
    responses = path_item["responses"]
    return {
        "200": responses["200"],
        "201": responses["201"],
        "400": {"$ref": "#/components/responses/BadRequestProblem"},
        "403": {"$ref": "#/components/responses/ForbiddenProblem"},
        "409": {"$ref": "#/components/responses/IdempotencyConflict"},
        "413": {"$ref": "#/components/responses/PayloadTooLarge"},
        "415": {"$ref": "#/components/responses/UnsupportedMediaType"},
        "422": {"$ref": "#/components/responses/UnprocessableProblem"},
        "429": {"$ref": "#/components/responses/RateLimited"},
        "503": {"$ref": "#/components/responses/ServiceUnavailable"},
    }


def health_live_responses() -> dict[int | str, Any]:
    return cast(
        dict[int | str, Any],
        load_openapi_contract()["paths"]["/api/v1/health/live"]["get"]["responses"],
    )


def health_ready_responses() -> dict[int | str, Any]:
    return cast(
        dict[int | str, Any],
        load_openapi_contract()["paths"]["/api/v1/health/ready"]["get"]["responses"],
    )
