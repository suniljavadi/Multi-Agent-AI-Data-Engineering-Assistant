from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Multi-Agent Data Engineering Copilot"
    environment: str = "development"
    mock_mode: bool = True
    log_level: str = "INFO"
    database_url: SecretStr = SecretStr("sqlite:///./data/mock.db")
    postgres_url: SecretStr | None = None
    max_sql_rows: int = Field(default=1000, ge=1)
    timeout_seconds: int = Field(default=15, ge=1)
    jira_mock_mode: bool = True
    llm_api_key: SecretStr | None = None
    openai_api_key: SecretStr | None = None
    cors_origins: list[str] = Field(default_factory=list)
    vector_store_path: str = "./vector_store"


@lru_cache
def get_settings() -> Settings:
    return Settings()


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
