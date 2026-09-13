from __future__ import annotations

import copy
from typing import Any

_STRIP_OPERATION_KEYS = frozenset({"description", "summary"})
_STRIP_SCHEMA_KEYS = frozenset({"description", "examples", "example", "title"})


def _strip_noise(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, item in value.items():
            if key in _STRIP_SCHEMA_KEYS:
                continue
            cleaned[key] = _strip_noise(item)
        return cleaned
    if isinstance(value, list):
        return [_strip_noise(item) for item in value]
    return value


def canonicalize_openapi(document: dict[str, Any]) -> dict[str, Any]:
    doc = copy.deepcopy(document)
    doc.pop("servers", None)
    paths = doc.get("paths", {})
    for path_item in paths.values():
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue
            for key in _STRIP_OPERATION_KEYS:
                operation.pop(key, None)
    cleaned = _strip_noise(doc)
    assert isinstance(cleaned, dict)
    return cleaned


def openapi_diff(
    expected: dict[str, Any],
    actual: dict[str, Any],
) -> list[str]:
    exp = canonicalize_openapi(expected)
    act = canonicalize_openapi(actual)
    diffs: list[str] = []

    def walk(path: str, left: Any, right: Any) -> None:
        if type(left) is not type(right):
            diffs.append(f"{path}: type {type(left).__name__} != {type(right).__name__}")
            return
        if isinstance(left, dict):
            left_keys = set(left.keys())
            right_keys = set(right.keys())
            for missing in sorted(left_keys - right_keys):
                diffs.append(f"{path}.{missing}: missing in actual")
            for extra in sorted(right_keys - left_keys):
                diffs.append(f"{path}.{extra}: unexpected in actual")
            for key in sorted(left_keys & right_keys):
                walk(f"{path}.{key}", left[key], right[key])
            return
        if isinstance(left, list):
            if len(left) != len(right):
                diffs.append(f"{path}: list length {len(left)} != {len(right)}")
                return
            for index, (l_item, r_item) in enumerate(zip(left, right, strict=True)):
                walk(f"{path}[{index}]", l_item, r_item)
            return
        if left != right:
            diffs.append(f"{path}: {left!r} != {right!r}")

    walk("root", exp, act)
    return diffs
