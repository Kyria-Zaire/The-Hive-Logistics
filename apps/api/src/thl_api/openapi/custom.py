from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from thl_api.openapi.load_contract import load_openapi_contract
from thl_api.openapi.raw import generate_raw_openapi


def _register_honest_components(generated: dict[str, Any], contract: dict[str, Any]) -> None:
    """Register contract components without overwriting path operations."""
    contract_components = contract.get("components", {})
    generated_components = generated.setdefault("components", {})
    for section in ("parameters", "headers", "responses"):
        if section in contract_components:
            generated_components[section] = contract_components[section]

    contract_schemas = contract_components.get("schemas", {})
    generated_schemas = generated_components.setdefault("schemas", {})
    for name, schema in contract_schemas.items():
        generated_schemas.setdefault(name, schema)


def build_openapi(app: FastAPI) -> dict[str, Any]:
    if app.openapi_schema is not None:
        return app.openapi_schema

    contract = load_openapi_contract()
    generated = generate_raw_openapi(app)
    generated["openapi"] = contract["openapi"]
    generated["info"] = contract["info"]
    generated["servers"] = contract["servers"]
    generated["tags"] = contract["tags"]
    _register_honest_components(generated, contract)
    app.openapi_schema = generated
    return generated
