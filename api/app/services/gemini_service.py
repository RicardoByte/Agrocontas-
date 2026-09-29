"""
Serviço de integração com a API Gemini para extração de dados de NF-e
(SDK oficial atual: google-genai)

Resiliência: retry com backoff exponencial + jitter, timeout por chamada e
fallback automático para o modelo reserva quando o principal está
sobrecarregado (503) ou indisponível (404).
"""
import asyncio
import json
import logging
import random
import re
from typing import Any

from fastapi import HTTPException, status
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)

# Valores de exemplo que NÃO são chaves reais
_PLACEHOLDER_KEYS = {"", "GEMINI_API_KEY", "Chave da API do Gemini"}

# Erros temporários: vale tentar de novo / trocar de modelo
_RETRYABLE_CODES = {429, 500, 503, 504}

# Tentativas por modelo, antes de passar para o próximo
_MAX_ATTEMPTS_PER_MODEL = 3
# Tempo máximo de espera por uma chamada (segundos)
_REQUEST_TIMEOUT_S = 90

# ---------------------------------------------------------------------------
# Prompt de extração — instrui o Gemini sobre o formato esperado
# ---------------------------------------------------------------------------
EXTRACTION_PROMPT = """
Você é um especialista em análise de documentos fiscais brasileiros (NF-e, NFS-e).
Analise a nota fiscal fornecida e extraia TODOS os dados disponíveis.

Retorne APENAS um JSON válido (sem markdown, sem ```json, sem explicações), com a seguinte estrutura:

{
  "numero": "número da nota",
  "serie": "série",
  "data_emissao": "YYYY-MM-DD",
  "chave_acesso": "44 dígitos ou null",
  "natureza_operacao": "descrição ou null",
  "tipo_operacao": "Entrada ou Saída",
  "fornecedor": {
    "nome": "razão social",
    "cnpj": "00.000.000/0000-00",
    "endereco": "endereço completo ou null",
    "ie": "inscrição estadual ou null",
    "telefone": "telefone ou null"
  },
  "destinatario": {
    "nome": "nome/razão social",
    "cnpj_cpf": "documento",
    "endereco": "endereço ou null",
    "ie": "IE ou null"
  },
  "itens": [
    {
      "codigo": "código ou null",
      "descricao": "descrição do produto",
      "ncm": "NCM ou null",
      "cfop": "CFOP ou null",
      "unidade": "UN/KG/CX etc ou null",
      "quantidade": 0.0,
      "valor_unitario": 0.0,
      "valor_total": 0.0,
      "icms_aliquota": 0.0
    }
  ],
  "totais": {
    "valor_produtos": 0.0,
    "valor_frete": 0.0,
    "valor_seguro": 0.0,
    "valor_desconto": 0.0,
    "valor_ipi": 0.0,
    "valor_icms": 0.0,
    "valor_total_nota": 0.0
  },
  "informacoes_complementares": "texto ou null"
}

Se algum campo não estiver disponível no documento, use null.
Todos os valores monetários devem ser números (float), não strings.
"""


class GeminiUnavailableError(RuntimeError):
    """Gemini sobrecarregado/indisponível em todos os modelos tentados.

    Herda de RuntimeError, então handlers existentes continuam funcionando.
    No router, capture esta classe antes de RuntimeError para devolver 503
    (em vez de 502) ao frontend.
    """


class GeminiService:
    """Encapsula a comunicação com a API Gemini"""

    def __init__(self) -> None:
        if settings.gemini_api_key.strip() in _PLACEHOLDER_KEYS:
            raise ValueError(
                "GEMINI_API_KEY não configurada. "
                "Copie api/.env.example para api/.env e preencha sua chave."
            )
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model

        # Cadeia de modelos: principal -> reserva (vazio = desativado).
        # Requer `gemini_fallback_model: str = ""` em app/core/config.py.
        fallback = (getattr(settings, "gemini_fallback_model", "") or "").strip()
        self.models: list[str] = [self.model]
        if fallback and fallback != self.model:
            self.models.append(fallback)

    async def extract_invoice_data(self, pdf_bytes: bytes) -> dict[str, Any]:
        """
        Envia o PDF para o Gemini e retorna os dados extraídos como dict.

        Raises:
            ValueError: Se o Gemini não retornar JSON válido
            GeminiUnavailableError: Se todos os modelos estiverem sobrecarregados
            RuntimeError: Se a API Gemini falhar
        """
        try:
            logger.info(
                "Enviando PDF para Gemini modelos=%s (%.2f KB)",
                self.models,
                len(pdf_bytes) / 1024,
            )

            contents = [
                types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                EXTRACTION_PROMPT,
            ]
            config = types.GenerateContentConfig(
                # Força saída JSON (dispensa depender só do prompt)
                response_mime_type="application/json",
                # Modelos com "thinking" contam o raciocínio neste limite;
                # NF com muitos itens estourava 8192 e truncava o JSON.
                max_output_tokens=16384,
            )

            response = await self._generate_with_fallback(contents, config)

            raw_text = (response.text or "").strip()
            if not raw_text:
                reason = None
                if response.candidates:
                    reason = response.candidates[0].finish_reason
                raise RuntimeError(f"O Gemini retornou uma resposta vazia (motivo: {reason}).")

            logger.info("Resposta Gemini recebida (%d chars)", len(raw_text))
            return self._extract_json(raw_text)

        except json.JSONDecodeError as e:
            logger.error("Gemini retornou JSON inválido: %s", e)
            raise ValueError(f"A IA retornou um formato inesperado: {e}") from e
        except ValueError:
            raise
        except RuntimeError:
            # inclui GeminiUnavailableError
            raise
        except genai_errors.APIError as e:
            # Erros não temporários (400, 401, 403...): não adianta insistir
            logger.error("Erro na API Gemini: %s", e)
            code = getattr(e, "code", None)
            raise RuntimeError(f"Erro ao processar com Gemini ({code}): {e}") from e
        except Exception as e:
            logger.exception("Erro inesperado ao chamar o Gemini")
            raise RuntimeError(f"Erro ao processar com Gemini: {e}") from e

    async def _generate_with_fallback(
        self, contents: list[Any], config: types.GenerateContentConfig
    ) -> types.GenerateContentResponse:
        """Tenta cada modelo da cadeia, com retry + backoff em erros temporários."""
        last_exc: Exception | None = None

        for model in self.models:
            for attempt in range(1, _MAX_ATTEMPTS_PER_MODEL + 1):
                try:
                    # client.aio = versão assíncrona (não bloqueia o event loop)
                    return await asyncio.wait_for(
                        self.client.aio.models.generate_content(
                            model=model, contents=contents, config=config
                        ),
                        timeout=_REQUEST_TIMEOUT_S,
                    )
                except asyncio.TimeoutError as e:
                    last_exc = e
                    logger.warning(
                        "Timeout (%ss) no modelo %s; indo para o próximo modelo",
                        _REQUEST_TIMEOUT_S,
                        model,
                    )
                    break  # timeout já custou muito: não insiste no mesmo modelo
                except genai_errors.APIError as e:
                    code = getattr(e, "code", None)
                    last_exc = e

                    if code == 404:
                        logger.error("Modelo '%s' indisponível (404); tentando o próximo", model)
                        break
                    if code not in _RETRYABLE_CODES:
                        raise  # erro real, não temporário

                    if attempt < _MAX_ATTEMPTS_PER_MODEL:
                        delay = (2 ** (attempt - 1)) + random.random()  # ~1s, ~2s
                        logger.warning(
                            "Gemini %s em %s (tentativa %d/%d); nova tentativa em %.1fs",
                            code,
                            model,
                            attempt,
                            _MAX_ATTEMPTS_PER_MODEL,
                            delay,
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.warning(
                            "Gemini %s em %s esgotou as tentativas; próximo modelo",
                            code,
                            model,
                        )

        # Todos os modelos falharam
        code = getattr(last_exc, "code", None)
        logger.error("Todos os modelos falharam %s. Último erro: %s", self.models, last_exc)
        if code == 404:
            raise RuntimeError(
                f"Modelo(s) {self.models} indisponível(is) no Gemini. "
                "Atualize GEMINI_MODEL / GEMINI_FALLBACK_MODEL no api/.env "
                "(veja [https://ai.google.dev/gemini-api/docs/deprecations](https://ai.google.dev/gemini-api/docs/deprecations))."
            ) from last_exc
        if code == 429:
            raise GeminiUnavailableError(
                "Limite de uso da API Gemini atingido. Tente novamente em instantes."
            ) from last_exc
        raise GeminiUnavailableError(
            "O serviço de IA está sobrecarregado no momento. "
            "Tente novamente em alguns instantes."
        ) from last_exc

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        """Remove markdown (se houver) e extrai o JSON puro da resposta"""
        cleaned = re.sub(r"```(?:json)?\s*", "", text).strip()
        cleaned = re.sub(r"```\s*$", "", cleaned).strip()
        data = json.loads(cleaned)
        if not isinstance(data, dict):
            raise ValueError("A IA retornou um JSON que não é um objeto de nota fiscal.")
        return data


# Singleton — instanciado uma vez na vida da aplicação
_service_instance: GeminiService | None = None


def get_gemini_service() -> GeminiService:
    """Dependency injection para FastAPI"""
    global _service_instance
    if _service_instance is None:
        try:
            _service_instance = GeminiService()
        except ValueError as e:
            # Configuração ausente vira 503 legível em vez de 500 genérico
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
            ) from e
    return _service_instance