from __future__ import annotations

import copy
from typing import Any

from thl_api.openapi.load_contract import load_openapi_contract


def synchronize_paths_with_contract(generated: dict[str, Any]) -> None:
    """Align path operations with contract using route-declared metadata only."""
    contract_paths = load_openapi_contract().get("paths", {})
    generated_paths = generated.setdefault("paths", {})
    for path, contract_path_item in contract_paths.items():
        if path not in generated_paths:
            continue
        for method, contract_operation in contract_path_item.items():
            if method not in generated_paths[path]:
                continue
            generated_paths[path][method] = copy.deepcopy(contract_operation)
