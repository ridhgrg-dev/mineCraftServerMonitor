import asyncio
from dataclasses import dataclass

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from control_plane.core.database import create_engine
from control_plane.core.settings import Settings


@dataclass
class Resources:
    engine: AsyncEngine
    redis: Redis | None
    timeout: float
    redis_required: bool

    @classmethod
    def create(cls, settings: Settings) -> Resources:
        cache = None
        if settings.redis_url is not None:
            cache = Redis.from_url(
                settings.redis_url.get_secret_value(),
                socket_connect_timeout=settings.dependency_timeout_seconds,
                socket_timeout=settings.dependency_timeout_seconds,
            )
        return cls(
            create_engine(settings),
            cache,
            settings.dependency_timeout_seconds,
            settings.redis_required,
        )

    async def check_ready(self) -> None:
        async with asyncio.timeout(self.timeout):
            async with self.engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            if self.redis_required:
                if self.redis is None:
                    raise RuntimeError("Required Redis client is unavailable")
                await self.redis.ping()

    async def close(self) -> None:
        try:
            if self.redis is not None:
                await self.redis.aclose()
        finally:
            await self.engine.dispose()
