from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AboEzzat Social Engine"
    environment: str = "development"
    api_bearer_token: str = "development-only-change-me"
    request_timeout_seconds: float = 20.0
    max_url_length: int = 4096
    enable_ytdlp: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
