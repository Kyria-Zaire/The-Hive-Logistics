from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from thl_api.problems import FieldError, ProblemDetails
from thl_api.schemas import (
    PreferredTiming,
    QuoteRequestCreateBase,
)


def _strip_null_property_defaults(document: dict[str, Any]) -> None:
    schemas = document.get("components", {}).get("schemas", {})
    if not isinstance(schemas, dict):
        return
    for schema in schemas.values():
        if not isinstance(schema, dict):
            continue
        props = schema.get("properties", {})
        if not isinstance(props, dict):
            continue
        for prop in props.values():
            if isinstance(prop, dict) and prop.get("default") is None:
                prop.pop("default", None)


def _ensure_pydantic_schema_refs(document: dict[str, Any]) -> None:
    """Complète les composants Pydantic référencés par $ref mais absents de get_openapi."""
    components = document.setdefault("components", {})
    schemas = components.setdefault("schemas", {})
    if not isinstance(schemas, dict):
        return

    if "PreferredTiming" not in schemas:
        schemas["PreferredTiming"] = PreferredTiming.__get_pydantic_json_schema__(None, None)

    if "QuoteRequestCreateBase" not in schemas:
        schemas["QuoteRequestCreateBase"] = QuoteRequestCreateBase.model_json_schema(
            ref_template="#/components/schemas/{model}",
        )

    if "FieldError" not in schemas:
        schemas["FieldError"] = FieldError.model_json_schema(
            ref_template="#/components/schemas/{model}",
        )

    if "ProblemDetails" not in schemas:
        schemas["ProblemDetails"] = ProblemDetails.model_json_schema(
            ref_template="#/components/schemas/{model}",
        )


def generate_raw_openapi(app: FastAPI) -> dict[str, Any]:
    generated = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
        servers=app.servers,
        contact=app.contact,
    )
    _strip_null_property_defaults(generated)
    _ensure_pydantic_schema_refs(generated)
    _strip_null_property_defaults(generated)
    return generated
