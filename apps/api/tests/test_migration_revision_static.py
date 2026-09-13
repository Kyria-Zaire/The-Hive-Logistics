from __future__ import annotations

import ast
from pathlib import Path

REVISION_PATH = (
    Path(__file__).resolve().parents[1] / "alembic" / "versions" / "0001_create_lead_data_model.py"
)


def _revision_source() -> str:
    return REVISION_PATH.read_text(encoding="utf-8")


def _revision_tree() -> ast.Module:
    return ast.parse(_revision_source())


def test_migration_does_not_import_application_models() -> None:
    tree = _revision_tree()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith("thl_api")
        if isinstance(node, ast.ImportFrom):
            assert node.module is None or not node.module.startswith("thl_api")


def test_migration_does_not_use_metadata_helpers() -> None:
    source = _revision_source()
    forbidden = (
        "target_metadata",
        "create_all",
        "drop_all",
        "POSTGRES_ENUM_TYPES",
        "Base.metadata",
    )
    for token in forbidden:
        assert token not in source


def test_migration_uses_explicit_create_table() -> None:
    source = _revision_source()
    assert "op.create_table" in source
    assert "op.drop_table" in source
