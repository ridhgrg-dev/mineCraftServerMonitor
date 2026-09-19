import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from control_plane.core.settings import Settings
from control_plane.worker import serve


async def test_worker_shuts_down_and_closes_resources(settings: Settings, tmp_path: Path) -> None:
    stop = asyncio.Event()
    stop.set()
    with patch("control_plane.worker.Resources.create") as factory:
        resource = factory.return_value
        resource.check_ready = AsyncMock()
        resource.close = AsyncMock()
        await serve(settings, stop, tmp_path / "ready")
        resource.check_ready.assert_awaited_once()
        resource.close.assert_awaited_once()
        assert not (tmp_path / "ready").exists()


async def test_worker_start_failure_cleans_up(settings: Settings, tmp_path: Path) -> None:
    with patch("control_plane.worker.Resources.create") as factory:
        resource = factory.return_value
        resource.check_ready = AsyncMock(side_effect=RuntimeError("unavailable"))
        resource.close = AsyncMock()
        with pytest.raises(RuntimeError):
            await serve(settings, asyncio.Event(), tmp_path / "ready")
        resource.close.assert_awaited_once()
