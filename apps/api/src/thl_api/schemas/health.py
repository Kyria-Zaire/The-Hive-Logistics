from __future__ import annotations

from typing import Literal

from thl_api.schemas.common import THLSchemaBase


class HealthLive(THLSchemaBase):
    status: Literal["ok"]


class HealthReadyChecks(THLSchemaBase):
    database: Literal["ok", "fail"] | None = None


class HealthReady(THLSchemaBase):
    status: Literal["ok"]
    checks: HealthReadyChecks
