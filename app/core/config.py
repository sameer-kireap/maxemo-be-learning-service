"""Application settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "Learning Analytics Service"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Must use postgresql+asyncpg:// scheme
    database_url: str

    allowed_origins: list[str] = ["*"]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
