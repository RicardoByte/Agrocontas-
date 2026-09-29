# 🌱 AgroContas

Sistema de gestão financeira para agronegócio com extração inteligente de Notas Fiscais via IA.

## Stack Tecnológica

| Camada | Tecnologia |
|--------|-----------|
| **Frontend** | Vue 3 + TypeScript + Vite |
| **Estado** | Pinia |
| **Roteamento** | Vue Router 4 |
| **Backend** | Python + FastAPI |
| **IA** | Google Gemini 2.0 Flash |
| **Banco de Dados** | PostgreSQL + SQLAlchemy |
| **HTTP Client** | Axios |

## Estrutura do Projeto

```
Agrocontas/
├── src/                        # Frontend Vue 3 + TypeScript
│   ├── components/
│   │   ├── InvoiceUploader.vue # Upload de PDF com drag & drop
│   │   └── JsonViewer.vue      # Visualização dos dados extraídos
│   ├── views/
│   │   └── HomeView.vue        # Página principal
│   ├── stores/
│   │   └── invoiceStore.ts     # Estado global (Pinia)
│   ├── services/
│   │   └── api.ts              # Comunicação com o backend
│   ├── types/
│   │   └── invoice.ts          # Tipos TypeScript da NF-e
│   └── assets/
│       └── main.css            # Design System global
│
├── api/                        # Backend Python + FastAPI
│   ├── app/
│   │   ├── core/config.py      # Configurações (pydantic-settings)
│   │   ├── models/invoice.py   # Modelos Pydantic da NF-e
│   │   ├── routers/invoice.py  # Endpoints da API
│   │   └── services/
│   │       └── gemini_service.py # Integração com Gemini AI
│   ├── main.py                 # Entry point FastAPI
│   ├── requirements.txt        # Dependências Python
│   └── .env.example            # Template de variáveis de ambiente
│
├── vite.config.ts              # Config Vite (com proxy para o backend)
├── setup.sh                    # Script de setup automático
└── .env.example                # Template de variáveis de ambiente (frontend)
```

## Setup Rápido

### 1. Clone e entre na pasta
```bash
cd "Agrocontas "
```

### 2. Execute o script de setup
```bash
bash setup.sh
```

### 3. Configure a Gemini API Key
1. Acesse: https://aistudio.google.com/app/apikey
2. Crie uma chave gratuita
3. Edite `api/.env` e coloque sua chave:
```env
GEMINI_API_KEY=sua_chave_aqui
```

### 4. Instale as dependências do frontend
> **Pré-requisito**: Node.js 18+. Baixe em https://nodejs.org
```bash
npm install
```

### 5. Inicie os servidores

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

### 6. Acesse
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Sprint 1 — Funcionalidades

- [x] Upload de PDF de Nota Fiscal (drag & drop)
- [x] Extração de dados via Gemini 2.0 Flash
- [x] Visualização formatada dos dados
- [x] Visualização JSON com syntax highlight
- [x] Copiar JSON para clipboard
- [x] Feedback de progresso de upload
- [x] Indicador de processamento do Gemini
- [x] Tratamento de erros com mensagens amigáveis

## Segurança

- ✅ Gemini API Key em variável de ambiente (nunca no código)
- ✅ Validação de tipo de arquivo (apenas PDF)
- ✅ Limite de tamanho de upload (10MB)
- ✅ CORS configurado por lista de origens permitidas
- ✅ `.env` no `.gitignore`
