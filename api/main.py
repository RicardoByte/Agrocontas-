"""
AgroContas Backend — FastAPI Entry Point
Responsável por:
- Extração de NF-e via IA Gemini
- Gestão de Pessoas (Fornecedores, Faturados, Clientes)
- Gestão de Classificações (Despesas e Receitas)
- Registro de Contas a Pagar e a Receber (Movimentos e Parcelas)
- Análise e Lançamento Automático da 2ª Etapa
"""
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal
from app.models.db_models import Pessoa, Classificacao
from app.routers import invoice, analysis, pessoas, classificacoes, movimentos


async def seed_initial_data():
    """Gera dados iniciais de exemplo caso o banco de dados esteja vazio"""
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Pessoa))
        if not res.scalars().first():
            # Inserir Faturado de exemplo do PDF: BELTRANO DA SILVA (ID 19 no exemplo)
            # Para manter idêntico ao exemplo, inserimos alguns registros ou configuramos o faturado
            faturado_exemplo = Pessoa(
                id=19,
                tipo="FATURADO",
                razao_social="BELTRANO DA SILVA",
                cpf_cnpj="999.999.999-99",
                ativo=True,
            )
            fornecedor_exemplo = Pessoa(
                tipo="CLIENTE-FORNECEDOR",
                razao_social="AGRO INDUSTRIAL BRASIL S/A",
                cpf_cnpj="04.123.456/0001-90",
                ativo=True,
            )
            db.add(faturado_exemplo)
            db.add(fornecedor_exemplo)

            # Inserir Classificação de exemplo do PDF: MANUTENÇÃO E OPERAÇÃO (ID 22 no exemplo)
            despesa_exemplo = Classificacao(
                id=22,
                tipo="DESPESA",
                descricao="MANUTENÇÃO E OPERAÇÃO",
                ativo=True,
            )
            receita_exemplo = Classificacao(
                tipo="RECEITA",
                descricao="VENDA DE SOJA EM GRÃOS",
                ativo=True,
            )
            despesa_combustivel = Classificacao(
                tipo="DESPESA",
                descricao="COMBUSTÍVEIS E LUBRIFICANTES",
                ativo=True,
            )
            db.add(despesa_exemplo)
            db.add(receita_exemplo)
            db.add(despesa_combustivel)

            await db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Cria tabelas e carrega sementes
    await init_db()
    try:
        await seed_initial_data()
    except Exception as e:
        # Não bloqueia inicialização se os IDs já existirem
        pass
    yield
    # Shutdown


# ---------------------------------------------------------------------------
# Criação da aplicação
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AgroContas API",
    description="Backend para extração de notas fiscais com IA Gemini e gestão financeira do agronegócio",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — permite que o frontend Vue acesse a API
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(invoice.router, prefix="/api/v1", tags=["Notas Fiscais"])
app.include_router(analysis.router, prefix="/api/v1", tags=["2ª Etapa — Análise e Lançamento"])
app.include_router(pessoas.router, prefix="/api/v1", tags=["Manter Pessoas"])
app.include_router(classificacoes.router, prefix="/api/v1", tags=["Manter Classificação"])
app.include_router(movimentos.router, prefix="/api/v1", tags=["Movimento de Contas e Parcelas"])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", summary="Verificação de saúde da API")
async def health_check() -> dict:
    return {
        "status": "ok",
        "version": "0.2.0",
        "database": settings.database_url.split(":")[0],
    }


# ---------------------------------------------------------------------------
# Entry point para desenvolvimento
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="info",
    )
