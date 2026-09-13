from __future__ import annotations

import copy
import re
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from thl_api.openapi.load_contract import load_openapi_contract
from thl_api.openapi.sync import synchronize_paths_with_contract

_REF_PATTERN = re.compile(r"#/components/(schemas|parameters|headers|responses)/([A-Za-z0-9_-]+)")


def _collect_refs(node: Any, refs: set[tuple[str, str]]) -> None:
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str):
            match = _REF_PATTERN.fullmatch(ref)
            if match:
                refs.add((match.group(1), match.group(2)))
        for value in node.values():
            _collect_refs(value, refs)
    elif isinstance(node, list):
        for item in node:
            _collect_refs(item, refs)


def _ensure_referenced_components(document: dict[str, Any], contract: dict[str, Any]) -> None:
    refs: set[tuple[str, str]] = set()
    _collect_refs(document, refs)
    contract_components = contract.get("components", {})
    document_components = document.setdefault("components", {})
    for section, name in sorted(refs):
        contract_section = contract_components.get(section, {})
        if name not in contract_section:
            continue
        target_section = document_components.setdefault(section, {})
        if name not in target_section:
            target_section[name] = copy.deepcopy(contract_section[name])


def generate_raw_openapi(app: FastAPI) -> dict[str, Any]:
    generated = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    contract = load_openapi_contract()
    generated["openapi"] = contract["openapi"]
    generated["info"] = contract["info"]
    generated["servers"] = contract["servers"]
    generated["tags"] = contract.get("tags", [])
    synchronize_paths_with_contract(generated)
    _ensure_referenced_components(generated, contract)
    contract_components = contract.get("components", {})
    generated_components = generated.setdefault("components", {})
    if "schemas" in contract_components:
        generated_components["schemas"] = copy.deepcopy(contract_components["schemas"])
    return generated
