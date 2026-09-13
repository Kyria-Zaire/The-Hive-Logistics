from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ThlEnvironment = Literal["dev", "recette", "preprod", "prod"]

_DEV_DATABASE_MARKERS = (
    "127.0.0.1",
    "localhost",
    "thl_dev_password",
    "/thl_dev",
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    thl_env: ThlEnvironment
    database_url: str
    log_level: str = "INFO"
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    @field_validator("database_url")
    @classmethod
    def database_url_non_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "DATABASE_URL is required"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def reject_prod_with_dev_secrets(self) -> Settings:
        if self.thl_env != "prod":
            return self
        lowered = self.database_url.lower()
        for marker in _DEV_DATABASE_MARKERS:
            if marker in lowered:
                msg = "THL_ENV=prod cannot use DEV-local DATABASE_URL markers"
                raise ValueError(msg)
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
