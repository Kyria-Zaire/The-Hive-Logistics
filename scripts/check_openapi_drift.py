from __future__ import annotations

import sys
from pathlib import Path

import yaml
from openapi_spec_validator import validate as validate_openapi_spec

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

import os

os.environ.setdefault("THL_ENV", "dev")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://thl_dev:thl_dev_password@127.0.0.1:5432/thl_dev",
)

from thl_api.main import create_app  # noqa: E402
from thl_api.openapi.drift import openapi_diff  # noqa: E402
from thl_api.openapi.raw import generate_raw_openapi  # noqa: E402

OPENAPI_PATH = ROOT / "contracts" / "openapi" / "openapi.yaml"


def main() -> int:
    with OPENAPI_PATH.open(encoding="utf-8") as handle:
        expected = yaml.safe_load(handle)
    app = create_app()
    actual = generate_raw_openapi(app)
    validate_openapi_spec(actual)
    validate_openapi_spec(expected)
    diffs = openapi_diff(expected, actual)
    if diffs:
        print("OpenAPI drift detected:", file=sys.stderr)
        for line in diffs[:50]:
            print(line, file=sys.stderr)
        return 1
    print("OpenAPI drift check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
