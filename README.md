# 🌱 AgroContas

Sistema de gestão financeira para agronegócio com extração inteligente de Notas Fiscais via IA.

## Estrutura do Projeto

```
Agrocontas/
├── src/                                 # Frontend Vue 3 + TypeScript
│   ├── components/
│   │   ├── AppNavbar.vue               # Navegação global entre módulos
│   │   ├── InvoiceUploader.vue         # Upload de PDF com drag & drop
│   │   ├── InvoiceAnalysis.vue         # 2ª Etapa: Análise e Lançamento automático
│   │   └── JsonViewer.vue              # Visualização dos dados extraídos
│   ├── views/
│   │   ├── HomeView.vue                # 1ª e 2ª Etapa (Extração + Lançamento)
│   │   ├── PessoasView.vue             # Manter Pessoas (Fornecedor, Faturado, Cliente)
│   │   ├── ClassificacoesView.vue      # Manter Classificações (Despesas e Receitas)
│   │   └── MovimentosView.vue          # Registrar Contas a Pagar / A Receber
│   ├── stores/
│   │   └── invoiceStore.ts             # Estado global de extração (Pinia)
│   ├── services/
│   │   └── api.ts                      # Comunicação com o backend (todos os módulos)
│   ├── types/
│   │   ├── invoice.ts                  # Tipos da NF-e extraída
│   │   └── models.ts                   # Tipos dos modelos do banco de dados
│   └── assets/
│       └── main.css                    # Design System global
│
├── api/                                 # Backend Python + FastAPI
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py               # Configurações (pydantic-settings)
│   │   │   └── database.py             # Conexão assíncrona (SQLAlchemy + aiosqlite/asyncpg)
│   │   ├── models/
│   │   │   ├── invoice.py              # Modelos Pydantic da NF-e (Gemini AI)
│   │   │   ├── db_models.py            # Modelos ORM SQLAlchemy (Pessoa, Classificacao, etc.)
│   │   │   └── schemas.py              # Schemas de request/response para a API
│   │   ├── routers/
│   │   │   ├── invoice.py              # POST /extract — Extração de NF-e via Gemini
│   │   │   ├── analysis.py             # POST /analysis/check-entities + launch-movement
│   │   │   ├── pessoas.py              # CRUD Pessoas (Fornecedor, Faturado, Cliente)
│   │   │   ├── classificacoes.py       # CRUD Classificações (Despesas e Receitas)
│   │   │   └── movimentos.py           # CRUD Movimentos e Parcelas
│   │   └── services/
│   │       └── gemini_service.py       # Integração com Gemini AI
│   ├── main.py                         # Entry point FastAPI (lifespan + routers)
│   ├── requirements.txt                # Dependências Python
│   └── .env.example                    # Template de variáveis de ambiente
│
├── vite.config.ts                       # Config Vite (proxy para o backend)
└── .env.example                         # Template de variáveis (frontend)
```

## Setup Rápido

### 1. Clone e entre na pasta
```bash
cd "Agrocontas-"
```

### 2. Instale as dependências do frontend
> **Pré-requisito**: Node.js 18+. Baixe em https://nodejs.org
```bash
npm install
```

### 3. Configure o Backend

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edite .env e configure o GEMINI_API_KEY
```

### 4. Inicie os servidores

**Terminal 1 — Backend:**
```bash
cd api
source .venv/bin/activate
python main.py
```

**Terminal 2 — Frontend:**
```bash
npm run dev
```

### 5. Acesse
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Banco de Dados

O backend usa **SQLite** por padrão em desenvolvimento. Para usar PostgreSQL em produção, configure:

```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/agrocontas_db
```

As tabelas são criadas automaticamente na inicialização da API.

## Módulos Disponíveis

| Módulo | URL | Descrição |
|---|---|---|
| Extração NF-e | `/` | Upload PDF + extração via Gemini AI |
| Manter Pessoas | `/pessoas` | Fornecedores, Faturados, Clientes (inativação/reativação) |
| Manter Classificações | `/classificacoes` | Tipos de Despesas e Receitas |
| Contas a Pagar/Receber | `/movimentos` | Movimentos e Parcelas com vencimentos |

## Fluxo — 2ª Etapa: Análise e Lançamento Automático

Após extrair uma NF-e, o sistema executa automaticamente:

1. **Consulta o banco de dados** — verifica se o Fornecedor, Faturado e Despesa já existem
2. **Exibe resultado** — EXISTE (ID: X) ou NÃO EXISTE para cada entidade
3. **Cria os registros necessários** — Pessoa(Fornecedor), Pessoa(Faturado), Classificação(Despesa)
4. **Lança o Movimento** — APAGAR com data de emissão e valor total da NF-e
5. **Cria a Parcela** — ÚNICA com data de vencimento e status PENDENTE
6. **Confirma ao usuário** — exibe os IDs de todos os registros criados/vinculados

## Sprint 1 — Funcionalidades

- [x] Upload de PDF de Nota Fiscal (drag & drop)
- [x] Extração de dados via Gemini AI
- [x] Visualização formatada dos dados
- [x] Visualização JSON com syntax highlight
- [x] Copiar JSON para clipboard
- [x] Feedback de progresso de upload
- [x] Indicador de processamento do Gemini
- [x] Tratamento de erros com mensagens amigáveis

## Sprint 2 — Funcionalidades (Banco de Dados)

- [x] Conexão assíncrona com banco de dados (SQLite dev / PostgreSQL prod)
- [x] Modelos ORM: Pessoa, Classificação, MovimentoContas, MovimentoClassificação, ParcelaContas
- [x] Manter Pessoas (Criar, Editar, **Inativar**, **Reativar**)
- [x] Manter Classificações de Despesas e Receitas
- [x] Registrar Contas a Pagar (múltiplas despesas e múltiplas parcelas)
- [x] Registrar Contas a Receber (múltiplas receitas e múltiplas parcelas)
- [x] Marcar parcelas como PAGAS
- [x] Análise automática da NF-e extraída (consulta Fornecedor, Faturado, Despesa)
- [x] Lançamento automático ao banco de dados após extração da NF-e
- [x] Barra de navegação global entre os módulos
- [x] Dados iniciais de exemplo (Faturado ID:19, Despesa "MANUTENÇÃO E OPERAÇÃO" ID:22)
