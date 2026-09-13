from __future__ import annotations

from fastapi import FastAPI

from thl_api.openapi.raw import generate_raw_openapi


def build_openapi(app: FastAPI) -> dict[str, object]:
    if app.openapi_schema is not None:
        return app.openapi_schema

    generated = generate_raw_openapi(app)
    app.openapi_schema = generated
    return generated
