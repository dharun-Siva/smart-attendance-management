from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Smart Attendance Management API"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/smart_attendance"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    jwt_secret_key: str = "development-secret-change-before-deployment"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
