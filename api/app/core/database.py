"""
Configuração do banco de dados com SQLAlchemy assíncrono.
Suporta SQLite (local / desenvolvimento) e PostgreSQL/Neon (produção).

Correções para Neon PostgreSQL + asyncpg:
- SSL passado via connect_args, não via URL query string
- channel_binding removido da URL (asyncpg não suporta)
- NullPool usado no ambiente serverless para evitar pool persistente incompatível
"""
import logging
import re
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_async_db_url(url: str) -> str:
    """
    Converte a DATABASE_URL para o driver assíncrono correto e
    remove parâmetros de query não suportados pelo asyncpg.
    O SSL será passado via connect_args, não pela URL.
    """
    # Normaliza prefixo para asyncpg / aiosqlite
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("sqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)

    # Remove toda a query string — SSL e parâmetros serão passados via connect_args
    if "?" in url:
        url = url.split("?")[0]

    return url


def get_connect_args(url: str) -> dict:
    """
    Retorna connect_args adequados para o driver.
    Para Neon PostgreSQL via asyncpg, habilita SSL obrigatório.
    """
    if "sqlite" in url:
        return {"check_same_thread": False}

    # Neon PostgreSQL exige SSL; asyncpg espera ssl=True ou objeto ssl
    return {"ssl": True}


db_url = get_async_db_url(settings.database_url)
connect_args = get_connect_args(settings.database_url)
is_sqlite = "sqlite" in db_url

# ── Engine ───────────────────────────────────────────────────────────────────
# Neon PostgreSQL é serverless — usa NullPool para não manter conexões abertas
# entre requests. SQLite mantém o pool padrão.
engine_kwargs: dict = {
    "echo": False,
    "future": True,
    "connect_args": connect_args,
}

if not is_sqlite:
    # NullPool: cria/fecha conexão a cada request — ideal para serverless
    engine_kwargs["poolclass"] = NullPool

engine = create_async_engine(db_url, **engine_kwargs)

# ── Session factory ───────────────────────────────────────────────────────────
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
