from __future__ import annotations

import copy
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from thl_api.openapi.runtime_components import (
    RUNTIME_OPENAPI_COMPONENTS,
    RUNTIME_SCHEMA_OVERRIDES,
)
from thl_api.openapi.runtime_metadata import INFO, OPENAPI_VERSION, SERVERS, TAGS


def _merge_runtime_components(document: dict[str, Any]) -> None:
    runtime_schemas = RUNTIME_OPENAPI_COMPONENTS.get("schemas", {})
    components = document.setdefault("components", {})
    for section, items in RUNTIME_OPENAPI_COMPONENTS.items():
        target = components.setdefault(section, {})
        for name, definition in items.items():
            if section == "schemas" and name in RUNTIME_SCHEMA_OVERRIDES:
                continue
            target.setdefault(name, copy.deepcopy(definition))
    schemas = components.setdefault("schemas", {})
    for name in RUNTIME_SCHEMA_OVERRIDES:
        schemas[name] = copy.deepcopy(runtime_schemas[name])


def generate_raw_openapi(app: FastAPI) -> dict[str, Any]:
    generated = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    generated["openapi"] = OPENAPI_VERSION
    generated["info"] = copy.deepcopy(INFO)
    generated["servers"] = copy.deepcopy(SERVERS)
    generated["tags"] = copy.deepcopy(TAGS)
    _merge_runtime_components(generated)
    return generated
