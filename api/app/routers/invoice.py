"""
Router de Notas Fiscais — endpoints para upload e extração de dados
"""
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.services.gemini_service import GeminiService, get_gemini_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Tipos MIME aceitos (apenas PDF)
ALLOWED_MIME_TYPES = {"application/pdf"}
MAX_BYTES = settings.max_upload_size_mb * 1024 * 1024  # converter MB → bytes


@router.post(
    "/extract",
    summary="Extrai dados de uma Nota Fiscal em PDF",
    response_description="JSON com todos os campos da nota fiscal extraídos pela IA",
    status_code=status.HTTP_200_OK,
)
async def extract_invoice(
    file: Annotated[UploadFile, File(description="Arquivo PDF da nota fiscal")],
    gemini: Annotated[GeminiService, Depends(get_gemini_service)],
) -> dict[str, Any]:
    """
    Recebe um arquivo PDF de nota fiscal, envia para o Gemini AI
    e retorna os dados estruturados em JSON.

    **Limites:**
    - Apenas arquivos PDF são aceitos
    - Tamanho máximo: 10 MB (configurável via MAX_UPLOAD_SIZE_MB)
    """
    # --- Validação de tipo de arquivo ---
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Tipo de arquivo não suportado: '{file.content_type}'. "
                "Apenas arquivos PDF (application/pdf) são aceitos."
            ),
        )

    # --- Leitura e validação de tamanho ---
    pdf_bytes = await file.read()

    if len(pdf_bytes) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"Arquivo muito grande: {len(pdf_bytes) / 1024 / 1024:.1f} MB. "
                f"Máximo permitido: {settings.max_upload_size_mb} MB."
            ),
        )

    if len(pdf_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo PDF enviado está vazio.",
        )

    # --- Extração via Gemini ---
    try:
        logger.info(
            "Extraindo dados de: %s (%.2f KB)",
            file.filename,
            len(pdf_bytes) / 1024,
        )
        extracted_data = await gemini.extract_invoice_data(pdf_bytes)

        return {
            "success": True,
            "filename": file.filename,
            "size_kb": round(len(pdf_bytes) / 1024, 2),
            "data": extracted_data,
        }

    except ValueError as e:
        # Gemini retornou JSON inválido
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e
    except RuntimeError as e:
        # Falha na API Gemini
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        ) from e
