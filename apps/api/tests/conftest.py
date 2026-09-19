import pytest
from pydantic import SecretStr

from control_plane.core.settings import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        environment="test",
        database_url=SecretStr("postgresql+psycopg://test@127.0.0.1:1/test"),
        dependency_timeout_seconds=0.1,
    )
