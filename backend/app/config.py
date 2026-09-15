from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./jobrate.db"
    anthropic_api_key: str = ""
    # Sonnet 5 - хорошее качество для структурированного извлечения за разумную цену;
    # для более высокого качества можно переключить на claude-opus-5 в .env
    anthropic_model: str = "claude-sonnet-5"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
