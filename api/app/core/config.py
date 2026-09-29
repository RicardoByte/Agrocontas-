"""
Configurações centralizadas via variáveis de ambiente (pydantic-settings)
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Gemini
    gemini_api_key: str = ""

    # Banco de dados
    database_url: str = "sqlite:///./agrocontas_dev.db"  # fallback p/ dev local

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    allowed_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:4173",
    ]

    # Upload
    max_upload_size_mb: int = 10

    # Ambiente
    environment: str = "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()
