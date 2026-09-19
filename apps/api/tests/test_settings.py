import pytest
from pydantic import SecretStr, ValidationError

from control_plane.core.settings import Settings
from control_plane.main import create_app


def test_redis_optional(settings: Settings) -> None:
    assert settings.redis_url is None
    assert not settings.redis_required


def test_required_redis_needs_configuration(settings: Settings) -> None:
    with pytest.raises(ValidationError):
        Settings(database_url=settings.database_url, redis_required=True)


def test_production_rejects_migration_identity() -> None:
    with pytest.raises(ValidationError):
        Settings(
            environment="production",
            database_url=SecretStr("postgresql+psycopg://platform_migrator:secret@localhost/db"),
        )


def test_production_disables_documentation() -> None:
    config = Settings(
        environment="production",
        database_url=SecretStr("postgresql+psycopg://platform_app:test-only-password@localhost/db"),
    )
    app = create_app(config)
    assert app.docs_url is None
    assert app.openapi_url is None


def test_sqlite_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(database_url=SecretStr("sqlite:///test.db"))
