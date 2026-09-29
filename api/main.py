"""
AgroContas Backend — FastAPI Entry Point
Responsável por: receber PDFs de notas fiscais e extrair dados com Gemini AI
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import invoice

# ---------------------------------------------------------------------------
# Criação da aplicação
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AgroContas API",
    description="Backend para extração de dados de notas fiscais com IA Gemini",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS — permite que o frontend Vue acesse a API
# ⚠️  Em produção, substitua por domínios reais
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(invoice.router, prefix="/api/v1", tags=["Notas Fiscais"])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", summary="Verificação de saúde da API")
async def health_check() -> dict:
    return {"status": "ok", "version": "0.1.0"}


# ---------------------------------------------------------------------------
# Entry point para desenvolvimento
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,          # Hot-reload em desenvolvimento
        log_level="info",
    )
