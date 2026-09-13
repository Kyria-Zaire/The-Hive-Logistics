from __future__ import annotations

from typing import Any, Literal

from thl_api.schemas.common import THLSchemaBase


class HealthLive(THLSchemaBase):
    status: Literal["ok"]

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: object, handler: object) -> dict[str, Any]:
        schema = handler(core_schema)  # type: ignore[operator]
        assert isinstance(schema, dict)
        schema["properties"]["status"] = {"type": "string", "enum": ["ok"]}
        schema.pop("additionalProperties", None)
        return schema


class HealthReadyChecks(THLSchemaBase):
    database: Literal["ok", "fail"] | None = None

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: object, handler: object) -> dict[str, Any]:
        schema = handler(core_schema)  # type: ignore[operator]
        assert isinstance(schema, dict)
        schema["properties"]["database"] = {"type": "string", "enum": ["ok", "fail"]}
        schema.pop("additionalProperties", None)
        return schema


class HealthReady(THLSchemaBase):
    status: Literal["ok"]
    checks: HealthReadyChecks

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: object, handler: object) -> dict[str, Any]:
        schema = handler(core_schema)  # type: ignore[operator]
        assert isinstance(schema, dict)
        schema["properties"]["status"] = {"type": "string", "enum": ["ok"]}
        schema.pop("additionalProperties", None)
        return schema
