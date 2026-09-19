import os
from uuid import uuid4

import pytest
from pydantic import SecretStr
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from control_plane.core.database import tenant_transaction
from control_plane.core.dependencies import Resources
from control_plane.core.settings import Settings

pytestmark = pytest.mark.integration


async def test_transaction_context_does_not_leak() -> None:
    engine = create_async_engine(os.environ["TEST_DATABASE_URL"], pool_size=1, max_overflow=0)
    tenant = uuid4()
    try:
        async with tenant_transaction(engine, tenant) as connection:
            value = await connection.scalar(
                text("SELECT current_setting('app.organization_id', true)")
            )
            assert value == str(tenant)
        async with engine.connect() as connection:
            assert await connection.scalar(
                text("SELECT current_setting('app.organization_id', true)")
            ) in (None, "")
        with pytest.raises(RuntimeError):
            async with tenant_transaction(engine, uuid4()):
                raise RuntimeError("rollback")
        async with engine.connect() as connection:
            assert await connection.scalar(
                text("SELECT current_setting('app.organization_id', true)")
            ) in (None, "")
    finally:
        await engine.dispose()


async def test_runtime_role_cannot_create_tables_or_bypass_rls() -> None:
    engine = create_async_engine(os.environ["TEST_DATABASE_URL"])
    try:
        async with engine.connect() as connection:
            row = (
                await connection.execute(
                    text(
                        "SELECT rolsuper, rolbypassrls, rolcreaterole "
                        "FROM pg_roles WHERE rolname = current_user"
                    )
                )
            ).one()
            assert tuple(row) == (False, False, False)
            assert not await connection.scalar(
                text("SELECT has_schema_privilege(current_user, 'platform', 'CREATE')")
            )
            assert not await connection.scalar(
                text("SELECT has_schema_privilege(current_user, 'public', 'CREATE')")
            )
    finally:
        await engine.dispose()


async def test_real_postgres_readiness_without_redis() -> None:
    settings = Settings(database_url=SecretStr(os.environ["TEST_DATABASE_URL"]))
    resources = Resources.create(settings)
    try:
        await resources.check_ready()
    finally:
        await resources.close()


async def test_real_redis_expiration() -> None:
    client = Redis.from_url(os.environ["TEST_REDIS_URL"])
    key = f"foundation-test:{uuid4()}"
    try:
        assert await client.ping()
        assert await client.set(key, "value", ex=10, nx=True)
        assert 0 < await client.ttl(key) <= 10
        assert not await client.set(key, "other", nx=True)
    finally:
        await client.delete(key)
        await client.aclose()
