from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", extra="ignore", hide_input_in_errors=True)
    environment: Literal["development", "test", "production"] = "development"
    database_url: SecretStr
    redis_url: SecretStr | None = None
    redis_required: bool = False
    dependency_timeout_seconds: float = 2.0

    @model_validator(mode="after")
    def validate_configuration(self) -> Settings:
        url = make_url(self.database_url.get_secret_value())
        if url.drivername != "postgresql+psycopg":
            raise ValueError("A PostgreSQL psycopg database URL is required")
        if self.dependency_timeout_seconds <= 0 or self.dependency_timeout_seconds > 10:
            raise ValueError("Dependency timeout must be between zero and ten seconds")
        if self.redis_required and self.redis_url is None:
            raise ValueError("Redis URL is required when Redis gates readiness")
        if self.environment == "production":
            if not url.password or url.password.lower() in {"password", "changeme", "placeholder"}:
                raise ValueError("Production requires a non-placeholder database password")
            if url.password.upper().startswith("REPLACE_"):
                raise ValueError("Production requires real database credentials")
            if url.username != "platform_app":
                raise ValueError("Production must use the restricted platform_app role")
        return self
