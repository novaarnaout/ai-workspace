from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Workspace API"
    environment: str = "development"
    debug: bool = True


settings = Settings()