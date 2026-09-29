"""
Serviço de integração com a API Gemini para extração de dados de NF-e
"""
import json
import re
import logging
from typing import Any

import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)

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


class GeminiService:
    """Encapsula a comunicação com a API Gemini"""

    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY não configurada. "
                "Copie api/.env.example para api/.env e preencha sua chave."
            )
        genai.configure(api_key=settings.gemini_api_key)
        # gemini-2.0-flash: rápido, multimodal, bom custo-benefício
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    async def extract_invoice_data(self, pdf_bytes: bytes) -> dict[str, Any]:
        """
        Envia o PDF para o Gemini e retorna os dados extraídos como dict.

        Args:
            pdf_bytes: Conteúdo binário do arquivo PDF

        Returns:
            Dicionário com os dados da nota fiscal

        Raises:
            ValueError: Se o Gemini não retornar JSON válido
            RuntimeError: Se a API Gemini falhar
        """
        try:
            logger.info("Enviando PDF para Gemini (%.2f KB)", len(pdf_bytes) / 1024)

            # Gemini aceita PDF diretamente via inline_data
            response = self.model.generate_content(
                contents=[
                    {
                        "parts": [
                            {
                                "inline_data": {
                                    "mime_type": "application/pdf",
                                    "data": pdf_bytes,
                                }
                            },
                            {"text": EXTRACTION_PROMPT},
                        ]
                    }
                ],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,        # Baixa temperatura = respostas mais determinísticas
                    max_output_tokens=8192,
                ),
            )

            raw_text = response.text.strip()
            logger.info("Resposta Gemini recebida (%d chars)", len(raw_text))

            # Extrai JSON da resposta (remove possíveis marcadores markdown)
            json_data = self._extract_json(raw_text)
            return json_data

        except json.JSONDecodeError as e:
            logger.error("Gemini retornou JSON inválido: %s", e)
            raise ValueError(f"A IA retornou um formato inesperado: {e}") from e
        except Exception as e:
            logger.error("Erro na API Gemini: %s", e)
            raise RuntimeError(f"Erro ao processar com Gemini: {e}") from e

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        """Remove markdown e extrai JSON puro da resposta do Gemini"""
        # Remove blocos ```json ... ``` se presentes
        cleaned = re.sub(r"```(?:json)?\s*", "", text).strip()
        cleaned = re.sub(r"```\s*$", "", cleaned).strip()
        return json.loads(cleaned)


# Singleton — instanciado uma vez na vida da aplicação
_service_instance: GeminiService | None = None


def get_gemini_service() -> GeminiService:
    """Dependency injection para FastAPI"""
    global _service_instance
    if _service_instance is None:
        _service_instance = GeminiService()
    return _service_instance
