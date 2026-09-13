from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

REPO_ROOT = Path(__file__).resolve().parents[5]
OPENAPI_PATH = REPO_ROOT / "contracts" / "openapi" / "openapi.yaml"


def build_openapi(app: FastAPI) -> dict[str, Any]:
    if app.openapi_schema is not None:
        return app.openapi_schema

    generated = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        contract = yaml.safe_load(handle)

    generated["openapi"] = contract["openapi"]
    generated["info"] = contract["info"]
    generated["servers"] = contract["servers"]
    generated["tags"] = contract["tags"]

    contract_components = contract.get("components", {})
    generated_components = generated.setdefault("components", {})
    generated_components["parameters"] = contract_components.get("parameters", {})
    generated_components["headers"] = contract_components.get("headers", {})
    generated_components["responses"] = contract_components.get("responses", {})
    schemas = generated_components.setdefault("schemas", {})
    for name, schema in contract_components.get("schemas", {}).items():
        schemas[name] = schema

    contract_paths = contract.get("paths", {})
    for path, path_item in contract_paths.items():
        if path not in generated.get("paths", {}):
            continue
        for method, operation in path_item.items():
            if method not in generated["paths"][path]:
                continue
            gen_op = generated["paths"][path][method]
            for key in ("tags", "operationId", "summary", "description", "parameters", "responses"):
                if key in operation:
                    gen_op[key] = operation[key]
            if "requestBody" in operation:
                gen_op["requestBody"] = operation["requestBody"]

    app.openapi_schema = generated
    return generated
