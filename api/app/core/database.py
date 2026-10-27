"""
Configuração do banco de dados com SQLAlchemy assíncrono.
Suporta SQLite (local / desenvolvimento) e PostgreSQL (produção).
"""
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from app.core.config import settings

logger = logging.getLogger(__name__)

import re

# Ajusta a URL de conexão para usar drivers assíncronos caso necessário
def get_async_db_url(url: str) -> str:
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("sqlite://"):
        url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)

    # asyncpg espera 'ssl=require' em vez de 'sslmode=require'
    if "sslmode=" in url:
        url = re.sub(r"sslmode=([a-zA-Z0-9_-]+)", r"ssl=\1", url)

    # Remove parâmetros específicos do libpq que o asyncpg rejeita (como channel_binding)
    url = re.sub(r"[&?]channel_binding=[^&]+", "", url)

    # Se a remoção tirou o '?' inicial mas deixou '&', conserta o primeiro '&' para '?'
    if "?" not in url and "&" in url:
        url = url.replace("&", "?", 1)

    return url

db_url = get_async_db_url(settings.database_url)

# Engine assíncrono
engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    # Parâmetros específicos para SQLite vs Postgres
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
)

# Fábrica de sessões assíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection para rotas do FastAPI"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Inicializa tabelas do banco de dados na inicialização da aplicação"""
    async with engine.begin() as conn:
        # Importa os modelos para registrá-los no Base.metadata
        from app.models import db_models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Tabelas do banco de dados inicializadas com sucesso.")
