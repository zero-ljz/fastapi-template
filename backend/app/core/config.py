# app/core/config.py

import json
from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    ROOT_PATH: Path = Path(__file__).resolve().parent.parent.parent

    PROJECT_NAME: str = "FastAPI Application"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    SECRET_KEY: str = "change-me-to-a-random-secret-key-32chars-min"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # --- Database ---
    DB_DRIVER: str = "mysql"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: str = "3306"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "db1"

    # --- Initial superuser seed ---
    FIRST_SUPERUSER: str = ""
    FIRST_SUPERUSER_EMAIL: str = ""
    FIRST_SUPERUSER_PASSWORD: str = ""

    # --- 日志 ---
    LOG_LEVEL: str = "INFO"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if not value:
            return []

        value = value.strip()
        if value.startswith("["):
            return json.loads(value)
        return [origin.strip() for origin in value.split(",") if origin.strip()]

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return value

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.ENVIRONMENT.lower() == "production":
            if self.DEBUG:
                raise ValueError("DEBUG must be false in production")
            if self.SECRET_KEY == "change-me-to-a-random-secret-key-32chars-min":
                raise ValueError("SECRET_KEY must be changed in production")
            if self.FIRST_SUPERUSER_PASSWORD == "change-me-admin-password":
                raise ValueError(
                    "FIRST_SUPERUSER_PASSWORD must be changed in production"
                )
        return self


settings = Settings()
