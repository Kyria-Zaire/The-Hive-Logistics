from __future__ import annotations

from alembic.config import Config


def escape_alembic_ini_value(value: str) -> str:
    """Échappe % pour ConfigParser ; l’URL lue reste identique à l’originale."""
    return value.replace("%", "%%")


def configure_alembic_database_url(config: Config, database_url: str) -> None:
    config.set_main_option("sqlalchemy.url", escape_alembic_ini_value(database_url))


def read_alembic_database_url(config: Config) -> str:
    url = config.get_main_option("sqlalchemy.url")
    if url is None:
        msg = "sqlalchemy.url is not configured"
        raise RuntimeError(msg)
    return url
