from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Morocco AI Market Assistant API"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://market_assistant:market_assistant_dev_password@localhost:5432/market_assistant"
    model_mode: str = "mock"
    cors_origins: list[str] = ["http://127.0.0.1:3000", "http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
