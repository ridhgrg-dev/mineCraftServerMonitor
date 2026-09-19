import asyncio
import logging
import signal
from pathlib import Path

from control_plane.core.dependencies import Resources
from control_plane.core.logging import configure_logging
from control_plane.core.settings import Settings

logger = logging.getLogger("control_plane")
READY_FILE = Path("/tmp/control-plane-worker.ready")


async def serve(settings: Settings, stop: asyncio.Event, ready_file: Path = READY_FILE) -> None:
    resources = Resources.create(settings)
    try:
        await resources.check_ready()
        await asyncio.to_thread(ready_file.touch, mode=0o600)
        logger.info("worker.started")
        # No jobs exist in Phase 1. Signals wake this wait immediately.
        await stop.wait()
    finally:
        await asyncio.to_thread(ready_file.unlink, missing_ok=True)
        await resources.close()
        logger.info("worker.stopped")


async def run() -> None:
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signum in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(signum, stop.set)
    try:
        await serve(Settings(), stop)  # type: ignore[call-arg]
    finally:
        for signum in (signal.SIGINT, signal.SIGTERM):
            loop.remove_signal_handler(signum)


def main() -> None:
    configure_logging()
    try:
        asyncio.run(run())
    except Exception:
        logger.error("worker.startup_failed")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
