from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy import CheckConstraint

import thl_api.models  # noqa: F401 — enregistre les tables
from schema_manifest import EXPECTED_CHECK_NAMES
from thl_api.models.base import Base

REVISION_PATH = (
    Path(__file__).resolve().parents[1] / "alembic" / "versions" / "0001_create_lead_data_model.py"
)


def _migration_check_names() -> frozenset[str]:
    source = REVISION_PATH.read_text(encoding="utf-8")
    names = re.findall(r'name="(chk_[^"]+)"', source)
    return frozenset(names)


def _model_check_names() -> frozenset[str]:
    names: set[str] = set()
    for table in Base.metadata.tables.values():
        for constraint in table.constraints:
            if isinstance(constraint, CheckConstraint) and constraint.name:
                names.add(constraint.name)
    return frozenset(names)


def test_check_naming_convention_preserves_explicit_names() -> None:
    model_names = _model_check_names()
    assert model_names == EXPECTED_CHECK_NAMES
    assert not any(name.startswith("ck_") for name in model_names)


def test_model_and_migration_check_names_match() -> None:
    migration_names = _migration_check_names()
    model_names = _model_check_names()
    assert migration_names == EXPECTED_CHECK_NAMES
    assert model_names == migration_names
    assert len(model_names) == 35
