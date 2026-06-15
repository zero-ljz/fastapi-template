# app/core/config.py

import os, secrets
from typing import Any
from pathlib import Path

from pydantic import (
    AnyHttpUrl,
    HttpUrl,
    PostgresDsn,
    ValidationInfo,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    ROOT_PATH: Path = Path(__file__).resolve().parent.parent.parent

    PROJECT_NAME: str = "FastAPI Application"
    VERSION: str
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 60 minutes * 24 hours * 8 days = 8 days

    DB_DRIVER: str = "mysql"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: str = "3306"
    DB_USER: str = "root"
    DB_PASSWORD: str
    DB_NAME: str

settings = Settings()
