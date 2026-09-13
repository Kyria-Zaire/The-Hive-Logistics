from __future__ import annotations

import argparse
import asyncio
import logging
import os
import signal
import socket
import sys

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncEngine

from thl_api.db import close_db, get_engine, init_db
from thl_api.notifications.contracts import WorkerSettings
from thl_api.notifications.repository import claim_next_job
from thl_api.notifications.service import process_claimed_job
from thl_api.notifications.smtp_sender import SmtpEmailSender

logger = logging.getLogger(__name__)


def _default_worker_id(settings: WorkerSettings) -> str:
    if settings.worker_id:
        return settings.worker_id[:64]
    host = socket.gethostname()[:32]
    pid = os.getpid()
    return f"{host}-{pid}"[:64]


async def run_once(engine: AsyncEngine, settings: WorkerSettings, sender: SmtpEmailSender) -> bool:
    worker_id = _default_worker_id(settings)
    job = await claim_next_job(engine, worker_id=worker_id)
    if job is None:
        return False
    await process_claimed_job(engine, sender, settings, job, worker_id=worker_id)
    return True


async def run_loop(engine: AsyncEngine, settings: WorkerSettings, sender: SmtpEmailSender) -> None:
    worker_id = _default_worker_id(settings)
    shutdown = asyncio.Event()

    def _request_shutdown(*_args: object) -> None:
        shutdown.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _request_shutdown)
        except NotImplementedError:
            signal.signal(sig, lambda *_a: shutdown.set())

    while not shutdown.is_set():
        job = await claim_next_job(engine, worker_id=worker_id)
        if job is None:
            try:
                await asyncio.wait_for(
                    shutdown.wait(),
                    timeout=settings.worker_poll_interval_seconds,
                )
            except TimeoutError:
                continue
            break
        try:
            await process_claimed_job(engine, sender, settings, job, worker_id=worker_id)
        except Exception:
            logger.exception(
                "Unhandled error processing notification job",
                extra={
                    "event": "notification_job_unhandled_error",
                    "job_id": job.job_id,
                    "public_reference": job.snapshot.public_reference,
                    "worker_id": worker_id,
                },
            )


async def _async_main(*, once: bool) -> int:
    try:
        settings = WorkerSettings()  # type: ignore[call-arg]
    except ValidationError as exc:
        logger.error(
            "Notification worker configuration invalid",
            extra={"event": "worker_config_invalid", "error_code": "EMAIL_PROVIDER_ERROR"},
        )
        print(exc, file=sys.stderr)
        return 1

    init_db(settings.database_url_str)
    engine = get_engine()
    sender = SmtpEmailSender(settings=settings)
    try:
        if once:
            await run_once(engine, settings, sender)
        else:
            await run_loop(engine, settings, sender)
    finally:
        await close_db()
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="THE HIVE LOGISTICS notification worker")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process at most one job then exit",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    raise SystemExit(asyncio.run(_async_main(once=args.once)))


if __name__ == "__main__":
    main()
