from __future__ import annotations

from pydantic.json_schema import GenerateJsonSchema


class THLGenerateJsonSchema(GenerateJsonSchema):
    def field_title_should_be_set(self, schema: object, field_name: str | None = None) -> bool:
        return False

    def model_title_should_be_set(self, schema: object, model_name: str | None = None) -> bool:
        return False
