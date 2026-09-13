from __future__ import annotations

import asyncio
import random
import time

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


class AdvisoryLockBusyError(Exception):
    """pg_try_advisory_lock deadline exceeded."""


class AdvisoryUnlockFailedError(Exception):
    """pg_advisory_unlock returned false."""


async def try_acquire_session_lock(
    connection: AsyncConnection,
    lock_id: int,
    *,
    deadline_seconds: float = 5.0,
) -> None:
    deadline = time.monotonic() + deadline_seconds
    while time.monotonic() < deadline:
        result = await connection.execute(
            text("SELECT pg_try_advisory_lock(:lock_id)"),
            {"lock_id": lock_id},
        )
        acquired = result.scalar_one()
        if acquired is True:
            return
        await asyncio.sleep(0.02 + random.random() * 0.03)
    raise AdvisoryLockBusyError


async def release_session_lock(connection: AsyncConnection, lock_id: int) -> None:
    result = await connection.execute(
        text("SELECT pg_advisory_unlock(:lock_id)"),
        {"lock_id": lock_id},
    )
    released = result.scalar_one()
    if released is not True:
        raise AdvisoryUnlockFailedError
