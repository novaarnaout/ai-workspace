import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Workspace API"
    environment: str = "development"
    debug: bool = True

    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_database_url(self) -> str:
        if os.getenv("PYTEST_CURRENT_TEST"):
            return self.database_url.replace("@db:5432", "@localhost:5433")

        return self.database_url


settings = Settings()