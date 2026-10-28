"""
Router para Gerenciamento de Movimento de Contas e Parcelas.
Regras de negócio:
- Um registro de contas a pagar, pode ser classificado em uma ou mais Tipo de DESPESAS.
- Um registro de contas a receber, pode ser classificado em uma ou mais Tipo de RECEITAS.
- Um registro de contas a pagar ou a receber, pode ter uma ou mais PARCELAS com data de vencimento distinto.
- Cadastros NÃO podem ser excluídos; devem ser INATIVADOS e podem ser REATIVADOS.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.db_models import (
    MovimentoContas,
    MovimentoClassificacao,
    ParcelaContas,
    Classificacao,
)
from app.models.schemas import (
    MovimentoCreate,
    MovimentoResponse,
    ParcelaCreate,
    ParcelaResponse,
)

router = APIRouter(prefix="/movimentos", tags=["Registrar Contas (A Pagar / A Receber)"])


@router.get("", response_model=List[MovimentoResponse])
async def list_movimentos(
    tipo: Optional[str] = Query(None, description="APAGAR ou ARECEBER"),
    status: Optional[str] = Query(None, description="PENDENTE, PAGO, RECEBIDO, CANCELADO"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo/inativo"),
    db: AsyncSession = Depends(get_db),
) -> List[MovimentoResponse]:
    stmt = (
        select(MovimentoContas)
        .options(
            selectinload(MovimentoContas.fornecedor),
            selectinload(MovimentoContas.faturado),
            selectinload(MovimentoContas.cliente),
            selectinload(MovimentoContas.classificacoes).selectinload(MovimentoClassificacao.classificacao),
            selectinload(MovimentoContas.parcelas),
        )
        .order_by(MovimentoContas.id.desc())
    )

    if tipo:
        stmt = stmt.where(MovimentoContas.tipo == tipo)

    if status:
        stmt = stmt.where(MovimentoContas.status == status)

    if ativo is not None:
        stmt = stmt.where(MovimentoContas.ativo == ativo)

    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("", response_model=MovimentoResponse, status_code=201)
async def create_movimento(
    data: MovimentoCreate,
    db: AsyncSession = Depends(get_db),
) -> MovimentoResponse:
    """
    Cria um novo movimento de contas (a pagar ou a receber) com suporte a
    múltiplas classificações e múltiplas parcelas com datas de vencimento distintas.
    """
    # Validação de regras de negócio:
    # Se tipo APAGAR -> classificações devem ser DESPESA
    # Se tipo ARECEBER -> classificações devem ser RECEITA
    tipo_esperado = "DESPESA" if data.tipo == "APAGAR" else "RECEITA"

    for mc in data.classificacoes:
        classif = await db.get(Classificacao, mc.classificacao_id)
        if not classif:
            raise HTTPException(status_code=400, detail=f"Classificação ID {mc.classificacao_id} não existe.")
        if classif.tipo != tipo_esperado:
            raise HTTPException(
                status_code=400,
                detail=f"Classificação '{classif.descricao}' é do tipo '{classif.tipo}', mas o movimento é do tipo '{data.tipo}' (esperado: {tipo_esperado}).",
            )

    movimento = MovimentoContas(
        tipo=data.tipo,
        fornecedor_id=data.fornecedor_id,
        faturado_id=data.faturado_id,
        cliente_id=data.cliente_id,
        numero_documento=data.numero_documento,
        serie=data.serie,
        chave_acesso=data.chave_acesso,
        data_emissao=data.data_emissao,
        valor_total=data.valor_total,
        observacao=data.observacao,
        status=data.status,
        ativo=True,
    )
    db.add(movimento)
    await db.flush()

    # Adiciona classificações
    for mc in data.classificacoes:
        mov_class = MovimentoClassificacao(
            movimento_id=movimento.id,
            classificacao_id=mc.classificacao_id,
            valor=mc.valor,
        )
        db.add(mov_class)

    # Adiciona parcelas
    for p in data.parcelas:
        parcela = ParcelaContas(
            movimento_id=movimento.id,
            identificacao=p.identificacao,
            numero_parcela=p.numero_parcela,
            data_vencimento=p.data_vencimento,
            valor=p.valor,
            status=p.status,
            data_pagamento=p.data_pagamento,
            ativo=True,
        )
        db.add(parcela)

    await db.commit()

    # Recarrega com relacionamentos
    stmt = (
        select(MovimentoContas)
        .options(
            selectinload(MovimentoContas.fornecedor),
            selectinload(MovimentoContas.faturado),
            selectinload(MovimentoContas.cliente),
            selectinload(MovimentoContas.classificacoes).selectinload(MovimentoClassificacao.classificacao),
            selectinload(MovimentoContas.parcelas),
        )
        .where(MovimentoContas.id == movimento.id)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


@router.get("/{movimento_id}", response_model=MovimentoResponse)
async def get_movimento(
    movimento_id: int,
    db: AsyncSession = Depends(get_db),
) -> MovimentoResponse:
    stmt = (
        select(MovimentoContas)
        .options(
            selectinload(MovimentoContas.fornecedor),
            selectinload(MovimentoContas.faturado),
            selectinload(MovimentoContas.cliente),
            selectinload(MovimentoContas.classificacoes).selectinload(MovimentoClassificacao.classificacao),
            selectinload(MovimentoContas.parcelas),
        )
        .where(MovimentoContas.id == movimento_id)
    )
    result = await db.execute(stmt)
    movimento = result.scalars().first()
    if not movimento:
        raise HTTPException(status_code=404, detail="Movimento de contas não encontrado")
    return movimento


@router.patch("/{movimento_id}/inativar", response_model=MovimentoResponse)
async def inativar_movimento(
    movimento_id: int,
    db: AsyncSession = Depends(get_db),
) -> MovimentoResponse:
    """Regra de negócio: Inativação de registro de movimento."""
    movimento = await db.get(MovimentoContas, movimento_id)
    if not movimento:
        raise HTTPException(status_code=404, detail="Movimento não encontrado")

    movimento.ativo = False
    await db.commit()
    return await get_movimento(movimento_id, db)


@router.patch("/{movimento_id}/reativar", response_model=MovimentoResponse)
async def reativar_movimento(
    movimento_id: int,
    db: AsyncSession = Depends(get_db),
) -> MovimentoResponse:
    """Regra de negócio: Reativação de registro inativo."""
    movimento = await db.get(MovimentoContas, movimento_id)
    if not movimento:
        raise HTTPException(status_code=404, detail="Movimento não encontrado")

    movimento.ativo = True
    await db.commit()
    return await get_movimento(movimento_id, db)


@router.patch("/{movimento_id}/parcelas/{parcela_id}/pagar", response_model=ParcelaResponse)
async def pagar_parcela(
    movimento_id: int,
    parcela_id: int,
    db: AsyncSession = Depends(get_db),
) -> ParcelaResponse:
    """Marca parcela como PAGA"""
    from datetime import date
    parcela = await db.get(ParcelaContas, parcela_id)
    if not parcela or parcela.movimento_id != movimento_id:
        raise HTTPException(status_code=404, detail="Parcela não encontrada")

    parcela.status = "PAGO"
    parcela.data_pagamento = date.today()
    await db.commit()
    await db.refresh(parcela)
    return parcela
