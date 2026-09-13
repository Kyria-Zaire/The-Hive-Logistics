from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from urllib.parse import quote_plus, unquote_plus, urlparse, urlunparse

import psycopg

_LOCAL_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
_FORBIDDEN_DB_MARKERS = (
    "thl_prod",
    "preprod",
    "recette",
    "/prod",
    "_prod",
    "production",
)

DEFAULT_INTEGRATION_URL = (
    "postgresql+psycopg://thl_dev:thl_dev_password@127.0.0.1:5433/thl_dev"
)


@dataclass(frozen=True)
class TempDatabase:
    admin_url: str
    database_url: str
    database_name: str


def integration_server_url() -> str:
    raw = os.environ.get("INTEGRATION_DATABASE_URL", DEFAULT_INTEGRATION_URL)
    return raw.replace("postgresql+psycopg://", "postgresql://", 1)


def _assert_dev_local_server(url: str) -> None:
    if os.environ.get("THL_ENV", "dev") != "dev":
        msg = "THL_ENV must be dev for migration tests"
        raise RuntimeError(msg)
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if host not in _LOCAL_HOSTS:
        msg = f"Migration tests require local PostgreSQL host, got {host!r}"
        raise RuntimeError(msg)
    db_name = parsed.path.lstrip("/")
    lowered = f"{url.lower()}/{db_name.lower()}"
    for marker in _FORBIDDEN_DB_MARKERS:
        if marker in lowered:
            msg = f"Forbidden database marker {marker!r} in URL"
            raise RuntimeError(msg)


def _swap_database(url: str, database_name: str) -> str:
    parsed = urlparse(url)
    path = f"/{quote_plus(database_name, safe='')}"
    return urlunparse(parsed._replace(path=path))


def _database_name_from_url(url: str) -> str:
    name = urlparse(url).path.lstrip("/")
    return unquote_plus(name)


@contextmanager
def temporary_migration_database() -> Iterator[TempDatabase]:
    server_url = integration_server_url()
    _assert_dev_local_server(server_url)

    temp_name = f"thl_test_{uuid.uuid4().hex}"
    if not temp_name.startswith("thl_test_"):
        msg = "Temporary database name must use thl_test_ prefix"
        raise RuntimeError(msg)

    admin_url = _swap_database(server_url, "postgres")
    temp_url = _swap_database(server_url, temp_name)

    conn = psycopg.connect(admin_url, autocommit=True)
    try:
        conn.execute(f'CREATE DATABASE "{temp_name}"')
    finally:
        conn.close()

    try:
        yield TempDatabase(
            admin_url=admin_url,
            database_url=temp_url.replace("postgresql://", "postgresql+psycopg://", 1),
            database_name=temp_name,
        )
    finally:
        assert_safe_to_drop(temp_name)
        cleanup = psycopg.connect(admin_url, autocommit=True)
        try:
            cleanup.execute(f'DROP DATABASE IF EXISTS "{temp_name}" WITH (FORCE)')
        finally:
            cleanup.close()


def assert_safe_to_drop(database_name: str) -> None:
    if not database_name.startswith("thl_test_"):
        msg = f"Refusing DROP on non-temporary database {database_name!r}"
        raise RuntimeError(msg)
    if database_name == "thl_dev":
        msg = "Refusing DROP on thl_dev"
        raise RuntimeError(msg)
