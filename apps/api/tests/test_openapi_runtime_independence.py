from __future__ import annotations

import ast
from pathlib import Path

import pytest

from thl_api.main import create_app
from thl_api.openapi.raw import generate_raw_openapi

RUNTIME_ROOT = Path(__file__).resolve().parents[1] / "src" / "thl_api"

FORBIDDEN_RUNTIME_NAMES = frozenset(
    {
        "load_openapi_contract",
        "synchronize_paths_with_contract",
        "RUNTIME_OPENAPI_COMPONENTS",
        "RUNTIME_SCHEMA_OVERRIDES",
    }
)

FORBIDDEN_RUNTIME_IMPORT_ROOTS = frozenset({"yaml"})


def _iter_python_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.py") if "tests" not in path.parts)


def test_runtime_package_does_not_import_canonical_contract_loader() -> None:
    hits: list[str] = []
    for path in _iter_python_files(RUNTIME_ROOT):
        if path.parts[-2:] == ("openapi", "raw.py"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        rel = path.relative_to(RUNTIME_ROOT)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.split(".")[0] in FORBIDDEN_RUNTIME_IMPORT_ROOTS:
                    hits.append(f"{rel}: import from {module}")
                for alias in node.names:
                    if alias.name in FORBIDDEN_RUNTIME_NAMES:
                        hits.append(f"{rel}: imports {alias.name}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    root_name = alias.name.split(".")[0]
                    if root_name in FORBIDDEN_RUNTIME_IMPORT_ROOTS:
                        hits.append(f"{rel}: import {alias.name}")
    assert not hits, "Forbidden runtime OpenAPI/YAML coupling:\n" + "\n".join(hits)


def test_raw_openapi_has_no_yaml_or_contract_sync() -> None:
    raw_path = RUNTIME_ROOT / "openapi" / "raw.py"
    tree = ast.parse(raw_path.read_text(encoding="utf-8"))
    forbidden = FORBIDDEN_RUNTIME_NAMES | {"yaml", "OPENAPI_PATH", "load_contract"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imported.add(module.split(".")[-1])
            imported.add(module.split(".")[0])
            for alias in node.names:
                imported.add(alias.name)
    hits = sorted(name for name in imported if name in forbidden)
    assert not hits, f"Forbidden imports/names in raw.py: {hits}"


def test_app_openapi_without_canonical_yaml_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing-openapi.yaml"

    def _fail_open(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        path = Path(self.name if args else kwargs.get("file", ""))
        if path.as_posix().endswith("contracts/openapi/openapi.yaml"):
            raise FileNotFoundError("canonical yaml must not be read at runtime")
        return _fail_open._original_open(self, *args, **kwargs)  # type: ignore[attr-defined]

    _fail_open._original_open = Path.open  # type: ignore[attr-defined]
    monkeypatch.setattr(Path, "open", _fail_open)

    app = create_app()
    spec = generate_raw_openapi(app)
    assert spec["paths"]
    assert not missing.exists()
