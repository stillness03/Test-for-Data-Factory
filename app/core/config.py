from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import date

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    APP_NAME: str = "user-credits"
    APP_ENV: str = "development"

    MYSQL_DATABASE: str
    MYSQL_ROOT_PASSWORD: str
    DATABASE_URL: str

    SNAPSHOT_DATE: date = date(2021, 12, 30)

@lru_cache
def get_settings() -> Settings:
    return Settings()