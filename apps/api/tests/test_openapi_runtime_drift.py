from __future__ import annotations

from pathlib import Path

import yaml
from openapi_spec_validator import validate as validate_openapi_spec

from thl_api.main import create_app
from thl_api.openapi.drift import openapi_diff
from thl_api.openapi.raw import generate_raw_openapi

REPO_ROOT = Path(__file__).resolve().parents[3]
OPENAPI_PATH = REPO_ROOT / "contracts" / "openapi" / "openapi.yaml"


def test_app_openapi_matches_contract_yaml() -> None:
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        expected = yaml.safe_load(handle)
    app = create_app()
    actual = generate_raw_openapi(app)
    validate_openapi_spec(actual)
    diffs = openapi_diff(expected, actual)
    assert not diffs, "OpenAPI drift:\n" + "\n".join(diffs[:40])
