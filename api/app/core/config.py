"""
Configurações centralizadas via variáveis de ambiente (pydantic-settings)
"""
import json
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# api/app/core/config.py -> api/.env (independe do diretório de onde o uvicorn é iniciado)
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # variáveis desconhecidas no .env não derrubam a API
    )

    # Gemini
    gemini_api_key: str = "GEMINI_API_KEY"

    # Modelo Gemini (ex: "gemini-3.8-flash", "gemini-1.5-mini")
    gemini_model: str = "gemini-3.5-flash"

    # Banco de dados (ainda não utilizado pela API)
    database_url: str = "sqlite:///./agrocontas_dev.db"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    # Aceita JSON (["http://a","http://b"]) OU lista separada por vírgula (http://a,http://b)
    allowed_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
    ]

    # Upload
    max_upload_size_mb: int = 10

    # Ambiente
    environment: str = "development"

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _parse_origins(cls, value):
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("["):
                return json.loads(value)
            return [o.strip() for o in value.split(",") if o.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()