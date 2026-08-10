from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Workspace API"
    environment: str = "development"
    debug: bool = True
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ai_workspace"


settings = Settings()