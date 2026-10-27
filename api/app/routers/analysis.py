"""
Router para Análise dos Dados da NF-e (2ª Etapa da Sprint)
- Consulta Fornecedor, Faturado e Classificação no Banco de Dados
- Lança automaticamente novo fornecedor, faturado, despesa, movimento e parcela
"""
import re
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.db_models import (
    Pessoa,
    Classificacao,
    MovimentoContas,
    MovimentoClassificacao,
    ParcelaContas,
)
from app.models.schemas import (
    EntityCheckQuery,
    AnalysisCheckResponse,
    EntitySearchResult,
    LaunchMovementRequest,
    LaunchMovementResponse,
    ParcelaCreate,
)

router = APIRouter(prefix="/analysis", tags=["2ª Etapa — Análise e Lançamento"])


def clean_digits(val: str | None) -> str:
    """Remove caracteres não numéricos para comparação de CPF/CNPJ"""
    if not val:
        return ""
    return re.sub(r"\D", "", val)


@router.post("/check-entities", response_model=AnalysisCheckResponse)
async def check_entities(
    query: EntityCheckQuery,
    db: AsyncSession = Depends(get_db),
) -> AnalysisCheckResponse:
    """
    ATIVIDADE 2° Etapa:
    Consulta no banco de dados e informa se:
    - FORNECEDOR existe ou não
    - FATURADO existe ou não
    - DESPESA existe ou não
    """

    # 1. Checagem do FORNECEDOR
    fornecedor_result = EntitySearchResult(
        existe=False,
        nome_razao_social=query.fornecedor_nome,
        documento=query.fornecedor_cnpj,
    )
    clean_cnpj = clean_digits(query.fornecedor_cnpj)
    
    if clean_cnpj or query.fornecedor_nome:
        stmt = select(Pessoa)
        conditions = []
        if clean_cnpj:
            conditions.append(func.replace(func.replace(func.replace(Pessoa.cpf_cnpj, ".", ""), "/", ""), "-", "") == clean_cnpj)
            conditions.append(Pessoa.cpf_cnpj == query.fornecedor_cnpj)
        if query.fornecedor_nome and len(query.fornecedor_nome.strip()) > 3:
            conditions.append(Pessoa.razao_social.ilike(query.fornecedor_nome.strip()))

        stmt = stmt.where(or_(*conditions))
        result = await db.execute(stmt)
        found_fornecedor = result.scalars().first()

        if found_fornecedor:
            fornecedor_result.existe = True
            fornecedor_result.id = found_fornecedor.id
            fornecedor_result.nome_razao_social = found_fornecedor.razao_social
            fornecedor_result.documento = found_fornecedor.cpf_cnpj
            fornecedor_result.ativo = found_fornecedor.ativo
            fornecedor_result.detalhes = f"Tipo: {found_fornecedor.tipo} | Ativo: {'Sim' if found_fornecedor.ativo else 'Não (Inativo)'}"

    # 2. Checagem do FATURADO (Destinatário)
    faturado_result = EntitySearchResult(
        existe=False,
        nome_razao_social=query.faturado_nome,
        documento=query.faturado_cpf_cnpj,
    )
    clean_cpf_cnpj = clean_digits(query.faturado_cpf_cnpj)

    if clean_cpf_cnpj or query.faturado_nome:
        stmt = select(Pessoa)
        conditions = []
        if clean_cpf_cnpj:
            conditions.append(func.replace(func.replace(func.replace(Pessoa.cpf_cnpj, ".", ""), "/", ""), "-", "") == clean_cpf_cnpj)
            conditions.append(Pessoa.cpf_cnpj == query.faturado_cpf_cnpj)
        if query.faturado_nome and len(query.faturado_nome.strip()) > 3:
            conditions.append(Pessoa.razao_social.ilike(query.faturado_nome.strip()))

        stmt = stmt.where(or_(*conditions))
        result = await db.execute(stmt)
        found_faturado = result.scalars().first()

        if found_faturado:
            faturado_result.existe = True
            faturado_result.id = found_faturado.id
            faturado_result.nome_razao_social = found_faturado.razao_social
            faturado_result.documento = found_faturado.cpf_cnpj
            faturado_result.ativo = found_faturado.ativo
            faturado_result.detalhes = f"Tipo: {found_faturado.tipo} | Ativo: {'Sim' if found_faturado.ativo else 'Não (Inativo)'}"

    # 3. Checagem da CLASSIFICAÇÃO / DESPESA
    despesa_nome = query.despesa_descricao or "MANUTENÇÃO E OPERAÇÃO"
    despesa_result = EntitySearchResult(
        existe=False,
        nome_razao_social=despesa_nome,
    )

    if despesa_nome:
        stmt = select(Classificacao).where(
            Classificacao.descricao.ilike(despesa_nome.strip()),
            Classificacao.tipo == query.tipo_classificacao,
        )
        result = await db.execute(stmt)
        found_despesa = result.scalars().first()

        if found_despesa:
            despesa_result.existe = True
            despesa_result.id = found_despesa.id
            despesa_result.nome_razao_social = found_despesa.descricao
            despesa_result.ativo = found_despesa.ativo
            despesa_result.detalhes = f"Tipo: {found_despesa.tipo} | Ativo: {'Sim' if found_despesa.ativo else 'Não (Inativo)'}"

    return AnalysisCheckResponse(
        fornecedor=fornecedor_result,
        faturado=faturado_result,
        despesa=despesa_result,
    )


@router.post("/launch-movement", response_model=LaunchMovementResponse)
async def launch_movement(
    req: LaunchMovementRequest,
    db: AsyncSession = Depends(get_db),
) -> LaunchMovementResponse:
    """
    Executa os passos descritos no PDF da Sprint:
    1. CRIAR O NOVO FORNECEDOR (se for o caso)
    2. CRIAR O NOVO FATURADO (se for o caso)
    3. CRIAR NOVA DESPESA (se for o caso)
    4. CRIAR UM NOVO REGISTRO DO MOVIMENTO E SUA PARCELA
    5. INFORMAR AO USUÁRIO QUE O REGISTRO FOI LANÇADO COM SUCESSO
    """

    # 1. Tratar FORNECEDOR (Pessoa tipo CLIENTE-FORNECEDOR)
    fornecedor_obj: Pessoa | None = None
    if req.fornecedor_id:
        fornecedor_obj = await db.get(Pessoa, req.fornecedor_id)
        if not fornecedor_obj:
            raise HTTPException(status_code=404, detail="Fornecedor informado não encontrado")
    elif req.fornecedor_nome:
        # Verifica se já não existe com o mesmo documento/nome
        clean_doc = clean_digits(req.fornecedor_cnpj)
        stmt = select(Pessoa).where(
            or_(
                Pessoa.cpf_cnpj == req.fornecedor_cnpj,
                Pessoa.razao_social.ilike(req.fornecedor_nome.strip()),
            )
        )
        res = await db.execute(stmt)
        existing = res.scalars().first()
        if existing:
            fornecedor_obj = existing
        else:
            fornecedor_obj = Pessoa(
                tipo="CLIENTE-FORNECEDOR",
                razao_social=req.fornecedor_nome.strip(),
                cpf_cnpj=req.fornecedor_cnpj.strip() if req.fornecedor_cnpj else None,
                inscricao_estadual=req.fornecedor_ie,
                endereco=req.fornecedor_endereco,
                ativo=True,
            )
            db.add(fornecedor_obj)
            await db.flush()

    # 2. Tratar FATURADO (Pessoa tipo FATURADO)
    faturado_obj: Pessoa | None = None
    if req.faturado_id:
        faturado_obj = await db.get(Pessoa, req.faturado_id)
        if not faturado_obj:
            raise HTTPException(status_code=404, detail="Faturado informado não encontrado")
    elif req.faturado_nome:
        stmt = select(Pessoa).where(
            or_(
                Pessoa.cpf_cnpj == req.faturado_cpf_cnpj,
                Pessoa.razao_social.ilike(req.faturado_nome.strip()),
            )
        )
        res = await db.execute(stmt)
        existing = res.scalars().first()
        if existing:
            faturado_obj = existing
        else:
            faturado_obj = Pessoa(
                tipo="FATURADO",
                razao_social=req.faturado_nome.strip(),
                cpf_cnpj=req.faturado_cpf_cnpj.strip() if req.faturado_cpf_cnpj else None,
                ativo=True,
            )
            db.add(faturado_obj)
            await db.flush()

    # 3. Tratar CLASSIFICAÇÃO / DESPESA
    classificacao_obj: Classificacao | None = None
    desc_despesa = (req.classificacao_descricao or "MANUTENÇÃO E OPERAÇÃO").strip()
    if req.classificacao_id:
        classificacao_obj = await db.get(Classificacao, req.classificacao_id)
        if not classificacao_obj:
            raise HTTPException(status_code=404, detail="Classificação informada não encontrada")
    elif desc_despesa:
        stmt = select(Classificacao).where(
            Classificacao.descricao.ilike(desc_despesa),
            Classificacao.tipo == req.classificacao_tipo,
        )
        res = await db.execute(stmt)
        existing = res.scalars().first()
        if existing:
            classificacao_obj = existing
        else:
            classificacao_obj = Classificacao(
                tipo=req.classificacao_tipo,
                descricao=desc_despesa,
                ativo=True,
            )
            db.add(classificacao_obj)
            await db.flush()

    # 4. CRIAR REGISTRO DO MOVIMENTO E SUA PARCELA
    movimento = MovimentoContas(
        tipo=req.tipo_movimento,  # "APAGAR"
        fornecedor_id=fornecedor_obj.id if fornecedor_obj else None,
        faturado_id=faturado_obj.id if faturado_obj else None,
        numero_documento=req.numero_documento,
        serie=req.serie,
        chave_acesso=req.chave_acesso,
        data_emissao=req.data_emissao or date.today(),
        valor_total=req.valor_total,
        observacao=req.observacao,
        status="PENDENTE",
        ativo=True,
    )
    db.add(movimento)
    await db.flush()

    # Vincula a Classificação ao Movimento
    if classificacao_obj:
        mov_class = MovimentoClassificacao(
            movimento_id=movimento.id,
            classificacao_id=classificacao_obj.id,
            valor=req.valor_total,
        )
        db.add(mov_class)

    # Criação das parcelas
    parcelas_adicionadas = 0
    if req.parcelas and len(req.parcelas) > 0:
        for p in req.parcelas:
            db_p = ParcelaContas(
                movimento_id=movimento.id,
                identificacao=p.identificacao,
                numero_parcela=p.numero_parcela,
                data_vencimento=p.data_vencimento,
                valor=p.valor,
                status=p.status,
                ativo=True,
            )
            db.add(db_p)
            parcelas_adicionadas += 1
    else:
        # Cria parcela padrão "ÚNICA" com vencimento na data de emissão ou 30 dias depois
        db_p = ParcelaContas(
            movimento_id=movimento.id,
            identificacao="ÚNICA",
            numero_parcela=1,
            data_vencimento=req.data_emissao or date.today(),
            valor=req.valor_total,
            status="PENDENTE",
            ativo=True,
        )
        db.add(db_p)
        parcelas_adicionadas = 1

    await db.commit()
    await db.refresh(movimento)

    return LaunchMovementResponse(
        sucesso=True,
        mensagem="Registro de movimento e parcelas lançado com sucesso!",
        movimento_id=movimento.id,
        fornecedor=EntitySearchResult(
            existe=True,
            id=fornecedor_obj.id if fornecedor_obj else None,
            nome_razao_social=fornecedor_obj.razao_social if fornecedor_obj else None,
            documento=fornecedor_obj.cpf_cnpj if fornecedor_obj else None,
        ),
        faturado=EntitySearchResult(
            existe=True,
            id=faturado_obj.id if faturado_obj else None,
            nome_razao_social=faturado_obj.razao_social if faturado_obj else None,
            documento=faturado_obj.cpf_cnpj if faturado_obj else None,
        ),
        despesa=EntitySearchResult(
            existe=True,
            id=classificacao_obj.id if classificacao_obj else None,
            nome_razao_social=classificacao_obj.descricao if classificacao_obj else None,
        ),
        total_parcelas=parcelas_adicionadas,
        valor_total=req.valor_total,
    )
