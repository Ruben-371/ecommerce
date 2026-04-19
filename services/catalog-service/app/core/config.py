"""Application configuration loaded from environment variables."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    MONGODB_URI: str
    DB_NAME: str = "catalog"
    ALLOWED_ORIGINS: List[str] = ["*"]
    PORT: int = 3002


settings = Settings()  # type: ignore[call-arg]
