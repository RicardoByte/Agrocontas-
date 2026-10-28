"""
Router para Gerenciamento de Classificações (Tipos de Despesa e Receita).
Regras de negócio:
- Cadastros NÃO podem ser excluídos.
- Cadastros devem ser INATIVADOS.
- Cadastros devem permitir REATIVAR um registro INATIVO.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.db_models import Classificacao
from app.models.schemas import (
    ClassificacaoCreate,
    ClassificacaoUpdate,
    ClassificacaoResponse,
)

router = APIRouter(prefix="/classificacoes", tags=["Manter Classificação (Despesas e Receitas)"])


@router.get("", response_model=List[ClassificacaoResponse])
async def list_classificacoes(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo: DESPESA ou RECEITA"),
    busca: Optional[str] = Query(None, description="Busca por descrição"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo/inativo. Vazio retorna todos"),
    db: AsyncSession = Depends(get_db),
) -> List[ClassificacaoResponse]:
    stmt = select(Classificacao).order_by(Classificacao.descricao)

    if tipo:
        stmt = stmt.where(Classificacao.tipo == tipo)

    if ativo is not None:
        stmt = stmt.where(Classificacao.ativo == ativo)

    if busca:
        termo = f"%{busca.strip()}%"
        stmt = stmt.where(Classificacao.descricao.ilike(termo))

    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("", response_model=ClassificacaoResponse, status_code=201)
async def create_classificacao(
    data: ClassificacaoCreate,
    db: AsyncSession = Depends(get_db),
) -> ClassificacaoResponse:
    classificacao = Classificacao(
        tipo=data.tipo.upper(),
        descricao=data.descricao.strip(),
        ativo=True,
    )
    db.add(classificacao)
    await db.commit()
    await db.refresh(classificacao)
    return classificacao


@router.get("/{classificacao_id}", response_model=ClassificacaoResponse)
async def get_classificacao(
    classificacao_id: int,
    db: AsyncSession = Depends(get_db),
) -> ClassificacaoResponse:
    classificacao = await db.get(Classificacao, classificacao_id)
    if not classificacao:
        raise HTTPException(status_code=404, detail="Classificação não encontrada")
    return classificacao


@router.put("/{classificacao_id}", response_model=ClassificacaoResponse)
async def update_classificacao(
    classificacao_id: int,
    data: ClassificacaoUpdate,
    db: AsyncSession = Depends(get_db),
) -> ClassificacaoResponse:
    classificacao = await db.get(Classificacao, classificacao_id)
    if not classificacao:
        raise HTTPException(status_code=404, detail="Classificação não encontrada")

    update_dict = data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        if field == "tipo" and value:
            value = value.upper()
        setattr(classificacao, field, value)

    await db.commit()
    await db.refresh(classificacao)
    return classificacao


@router.patch("/{classificacao_id}/inativar", response_model=ClassificacaoResponse)
async def inativar_classificacao(
    classificacao_id: int,
    db: AsyncSession = Depends(get_db),
) -> ClassificacaoResponse:
    """Regra de negócio: Cadastros NÃO podem ser excluídos, devem ser INATIVADOS."""
    classificacao = await db.get(Classificacao, classificacao_id)
    if not classificacao:
        raise HTTPException(status_code=404, detail="Classificação não encontrada")

    classificacao.ativo = False
    await db.commit()
    await db.refresh(classificacao)
    return classificacao


@router.patch("/{classificacao_id}/reativar", response_model=ClassificacaoResponse)
async def reativar_classificacao(
    classificacao_id: int,
    db: AsyncSession = Depends(get_db),
) -> ClassificacaoResponse:
    """Regra de negócio: Deve ser possível REATIVAR um registro INATIVO."""
    classificacao = await db.get(Classificacao, classificacao_id)
    if not classificacao:
        raise HTTPException(status_code=404, detail="Classificação não encontrada")

    classificacao.ativo = True
    await db.commit()
    await db.refresh(classificacao)
    return classificacao
