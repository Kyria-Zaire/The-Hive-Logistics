from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN = frozenset(
    {
        "load_openapi_contract",
        "synchronize_paths_with_contract",
        "yaml",
        "OPENAPI_PATH",
    }
)


def test_raw_openapi_module_has_no_forbidden_imports() -> None:
    raw_path = (
        Path(__file__).resolve().parents[1] / "src" / "thl_api" / "openapi" / "raw.py"
    )
    tree = ast.parse(raw_path.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
                if alias.asname:
                    imported.add(alias.asname)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imported.add(module.split(".")[0])
            for alias in node.names:
                imported.add(alias.name)
                if alias.asname:
                    imported.add(alias.asname)
    hits = sorted(name for name in imported if name in FORBIDDEN)
    assert not hits, f"Forbidden imports/names in raw.py: {hits}"
