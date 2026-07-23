"""定义应用配置。"""

from pathlib import Path
from typing import Literal, Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    ROOT_PATH: Path = Path(__file__).resolve().parent.parent.parent

    PROJECT_NAME: str = "FastAPI Template"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = True

    SECRET_KEY: str = "change-me-to-a-random-secret-key-32chars-min"
    ALGORITHM: Literal["HS256"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30, gt=0)

    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # 数据库
    DB_DRIVER: str = "mysql+mysqldb"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = Field(default=3306, ge=1, le=65535)
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "db1"

    # 初始超级管理员
    FIRST_SUPERUSER: str = ""
    FIRST_SUPERUSER_EMAIL: str = ""
    FIRST_SUPERUSER_PASSWORD: str = ""

    # 日志
    LOG_LEVEL: str = "INFO"

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return value

    @model_validator(mode="after")
    def validate_production_settings(self) -> Self:
        if self.ENVIRONMENT == "production":
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
