from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Multi-Agent Data Engineering Copilot"
    environment: str = "development"
    mock_mode: bool = True
    log_level: str = "INFO"
    database_url: str = "sqlite:///./data/mock.db"
    postgres_url: str = "postgresql://postgres:postgres@postgres:5432/agentdb"
    max_sql_rows: int = 1000
    timeout_seconds: int = 15
    jira_mock_mode: bool = True
    llm_api_key: str | None = None
    openai_api_key: str | None = None
    vector_store_path: str = "./vector_store"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
