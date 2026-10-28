"""
Router para Gerenciamento de Pessoas (Fornecedores, Clientes, Faturados).
Regras de negócio:
- Cadastros NÃO podem ser excluídos.
- Cadastros devem ser INATIVADOS.
- Cadastros devem permitir REATIVAR um registro INATIVO.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.db_models import Pessoa
from app.models.schemas import PessoaCreate, PessoaUpdate, PessoaResponse

router = APIRouter(prefix="/pessoas", tags=["Manter Pessoas (Fornecedor, Cliente, Faturado)"])


@router.get("", response_model=List[PessoaResponse])
async def list_pessoas(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo: FORNECEDOR, FATURADO, CLIENTE, CLIENTE-FORNECEDOR"),
    busca: Optional[str] = Query(None, description="Busca por nome, razão social ou CPF/CNPJ"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo/inativo. Vazio retorna todos"),
    db: AsyncSession = Depends(get_db),
) -> List[PessoaResponse]:
    stmt = select(Pessoa).order_by(Pessoa.razao_social)

    if tipo:
        stmt = stmt.where(Pessoa.tipo == tipo)

    if ativo is not None:
        stmt = stmt.where(Pessoa.ativo == ativo)

    if busca:
        termo = f"%{busca.strip()}%"
        stmt = stmt.where(
            or_(
                Pessoa.razao_social.ilike(termo),
                Pessoa.cpf_cnpj.ilike(termo),
            )
        )

    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("", response_model=PessoaResponse, status_code=201)
async def create_pessoa(
    data: PessoaCreate,
    db: AsyncSession = Depends(get_db),
) -> PessoaResponse:
    pessoa = Pessoa(
        tipo=data.tipo,
        razao_social=data.razao_social.strip(),
        cpf_cnpj=data.cpf_cnpj.strip() if data.cpf_cnpj else None,
        inscricao_estadual=data.inscricao_estadual.strip() if data.inscricao_estadual else None,
        endereco=data.endereco.strip() if data.endereco else None,
        telefone=data.telefone.strip() if data.telefone else None,
        ativo=True,
    )
    db.add(pessoa)
    await db.commit()
    await db.refresh(pessoa)
    return pessoa


@router.get("/{pessoa_id}", response_model=PessoaResponse)
async def get_pessoa(
    pessoa_id: int,
    db: AsyncSession = Depends(get_db),
) -> PessoaResponse:
    pessoa = await db.get(Pessoa, pessoa_id)
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    return pessoa


@router.put("/{pessoa_id}", response_model=PessoaResponse)
async def update_pessoa(
    pessoa_id: int,
    data: PessoaUpdate,
    db: AsyncSession = Depends(get_db),
) -> PessoaResponse:
    pessoa = await db.get(Pessoa, pessoa_id)
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    update_dict = data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(pessoa, field, value)

    await db.commit()
    await db.refresh(pessoa)
    return pessoa


@router.patch("/{pessoa_id}/inativar", response_model=PessoaResponse)
async def inativar_pessoa(
    pessoa_id: int,
    db: AsyncSession = Depends(get_db),
) -> PessoaResponse:
    """Regra de negócio: Cadastros NÃO podem ser excluídos, devem ser INATIVADOS."""
    pessoa = await db.get(Pessoa, pessoa_id)
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    pessoa.ativo = False
    await db.commit()
    await db.refresh(pessoa)
    return pessoa


@router.patch("/{pessoa_id}/reativar", response_model=PessoaResponse)
async def reativar_pessoa(
    pessoa_id: int,
    db: AsyncSession = Depends(get_db),
) -> PessoaResponse:
    """Regra de negócio: Deve ser possível REATIVAR um registro INATIVO."""
    pessoa = await db.get(Pessoa, pessoa_id)
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    pessoa.ativo = True
    await db.commit()
    await db.refresh(pessoa)
    return pessoa
