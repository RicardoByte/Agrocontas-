#!/usr/bin/env bash
# =============================================================
# AgroContas — Script de Setup do Ambiente de Desenvolvimento
# =============================================================
# Execute: bash setup.sh
# =============================================================

set -e  # Para imediatamente em caso de erro

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🌱 AgroContas — Setup do Ambiente${NC}\n"

# ── 1. Verificar Python ───────────────────────────────────────
echo -e "${YELLOW}[1/5] Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado. Instale Python 3.11+ e tente novamente.${NC}"
    exit 1
fi
echo -e "   ✅ $(python3 --version)"

# ── 2. Criar virtualenv do backend ───────────────────────────
echo -e "${YELLOW}[2/5] Configurando ambiente Python (virtualenv)...${NC}"
cd api
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "   ✅ Virtualenv criado em api/.venv"
else
    echo "   ✅ Virtualenv já existe"
fi

# Ativa o virtualenv
source .venv/bin/activate

# ── 3. Instalar dependências Python ──────────────────────────
echo -e "${YELLOW}[3/5] Instalando dependências Python...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "   ✅ Dependências Python instaladas"

# ── 4. Configurar .env do backend ────────────────────────────
echo -e "${YELLOW}[4/5] Configurando variáveis de ambiente...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "   ✅ Arquivo api/.env criado!"
    echo -e "   ${RED}⚠️  ATENÇÃO: Edite api/.env e adicione sua GEMINI_API_KEY!${NC}"
    echo -e "      Obtenha em: https://aistudio.google.com/app/apikey"
else
    echo "   ✅ api/.env já configurado"
fi

deactivate
cd ..

# ── 5. Configurar .env do frontend ───────────────────────────
echo -e "${YELLOW}[5/5] Configurando frontend...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   ✅ Arquivo .env frontend criado"
else
    echo "   ✅ .env frontend já configurado"
fi

# ── Resumo ────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}✨ Setup concluído! Próximos passos:${NC}"
echo ""
echo -e "   1. ${YELLOW}Edite api/.env${NC} e adicione sua GEMINI_API_KEY"
echo -e "      (Obtenha em: https://aistudio.google.com/app/apikey)"
echo ""
echo -e "   2. Instale as dependências frontend (precisa do Node.js):"
echo -e "      ${YELLOW}npm install${NC}"
echo ""
echo -e "   3. Inicie o backend:"
echo -e "      ${YELLOW}cd api && source .venv/bin/activate && python main.py${NC}"
echo ""
echo -e "   4. Em outro terminal, inicie o frontend:"
echo -e "      ${YELLOW}npm run dev${NC}"
echo ""
echo -e "   📍 Frontend: http://localhost:5173"
echo -e "   📍 Backend API: http://localhost:8000"
echo -e "   📍 Docs API: http://localhost:8000/docs"
echo ""
