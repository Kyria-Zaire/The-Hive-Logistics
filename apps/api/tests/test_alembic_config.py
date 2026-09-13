from __future__ import annotations

from alembic.config import Config

from thl_api.alembic_config import (
    configure_alembic_database_url,
    read_alembic_database_url,
)


def test_alembic_database_url_percent_encoding_roundtrip() -> None:
    cfg = Config()
    samples = (
        "postgresql+psycopg://user:p%40ss@127.0.0.1:5433/thl_test_x",
        "postgresql+psycopg://user:pa%2Fss@127.0.0.1:5433/thl_test_y",
        "postgresql+psycopg://user:pa%25ss@127.0.0.1:5433/thl_test_z",
    )
    for url in samples:
        configure_alembic_database_url(cfg, url)
        assert read_alembic_database_url(cfg) == url
