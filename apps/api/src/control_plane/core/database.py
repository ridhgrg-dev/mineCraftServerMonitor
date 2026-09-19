from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from control_plane.core.settings import Settings


def create_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(
        settings.database_url.get_secret_value(),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        pool_timeout=settings.dependency_timeout_seconds,
        connect_args={"connect_timeout": max(1, int(settings.dependency_timeout_seconds))},
        hide_parameters=True,
    )


@asynccontextmanager
async def tenant_transaction(
    engine: AsyncEngine, organization_id: UUID
) -> AsyncIterator[AsyncConnection]:
    """Bind future RLS context to one transaction; never use session-wide SET."""
    async with engine.begin() as connection:
        await connection.execute(
            text("SELECT set_config('app.organization_id', :organization_id, true)"),
            {"organization_id": str(organization_id)},
        )
        yield connection
