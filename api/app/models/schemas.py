"""
Schemas Pydantic para validação de requisições e respostas da API do AgroContas.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Schemas: PESSOA
# ============================================================================

class PessoaBase(BaseModel):
    tipo: str = Field(default="CLIENTE-FORNECEDOR", description="CLIENTE-FORNECEDOR, FORNECEDOR, FATURADO, CLIENTE")
    razao_social: str = Field(..., description="Razão Social ou Nome Completo")
    cpf_cnpj: Optional[str] = Field(default=None, description="CPF ou CNPJ")
    inscricao_estadual: Optional[str] = Field(default=None, description="Inscrição Estadual")
    endereco: Optional[str] = Field(default=None, description="Endereço")
    telefone: Optional[str] = Field(default=None, description="Telefone")


class PessoaCreate(PessoaBase):
    pass


class PessoaUpdate(BaseModel):
    tipo: Optional[str] = None
    razao_social: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    inscricao_estadual: Optional[str] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None


class PessoaResponse(PessoaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Schemas: CLASSIFICACAO
# ============================================================================

class ClassificacaoBase(BaseModel):
    tipo: str = Field(..., description="DESPESA ou RECEITA")
    descricao: str = Field(..., description="Descrição da classificação (ex: MANUTENÇÃO E OPERAÇÃO)")


class ClassificacaoCreate(ClassificacaoBase):
    pass


class ClassificacaoUpdate(BaseModel):
    tipo: Optional[str] = None
    descricao: Optional[str] = None


class ClassificacaoResponse(ClassificacaoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Schemas: PARCELACONTAS
# ============================================================================

class ParcelaCreate(BaseModel):
    identificacao: str = Field(default="ÚNICA", description="Identificação da parcela (ÚNICA, 1/3, etc)")
    numero_parcela: int = Field(default=1)
    data_vencimento: date
    valor: Decimal
    status: str = Field(default="PENDENTE")
    data_pagamento: Optional[date] = None


class ParcelaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    movimento_id: int
    identificacao: str
    numero_parcela: int
    data_vencimento: date
    valor: Decimal
    status: str
    data_pagamento: Optional[date] = None
    ativo: bool
    created_at: datetime


# ============================================================================
# Schemas: MOVIMENTOCONTAS
# ============================================================================

class MovimentoClassificacaoCreate(BaseModel):
    classificacao_id: int
    valor: Decimal


class MovimentoClassificacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    classificacao_id: int
    valor: Decimal
    classificacao: Optional[ClassificacaoResponse] = None


class MovimentoCreate(BaseModel):
    tipo: str = Field(default="APAGAR", description="APAGAR ou ARECEBER")
    fornecedor_id: Optional[int] = None
    faturado_id: Optional[int] = None
    cliente_id: Optional[int] = None
    numero_documento: Optional[str] = None
    serie: Optional[str] = None
    chave_acesso: Optional[str] = None
    data_emissao: Optional[date] = None
    valor_total: Decimal
    observacao: Optional[str] = None
    status: str = Field(default="PENDENTE")
    classificacoes: List[MovimentoClassificacaoCreate] = Field(default_factory=list)
    parcelas: List[ParcelaCreate] = Field(default_factory=list)


class MovimentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str
    fornecedor_id: Optional[int] = None
    faturado_id: Optional[int] = None
    cliente_id: Optional[int] = None
    numero_documento: Optional[str] = None
    serie: Optional[str] = None
    chave_acesso: Optional[str] = None
    data_emissao: Optional[date] = None
    valor_total: Decimal
    observacao: Optional[str] = None
    status: str
    ativo: bool
    created_at: datetime
    updated_at: datetime

    fornecedor: Optional[PessoaResponse] = None
    faturado: Optional[PessoaResponse] = None
    cliente: Optional[PessoaResponse] = None
    classificacoes: List[MovimentoClassificacaoResponse] = Field(default_factory=list)
    parcelas: List[ParcelaResponse] = Field(default_factory=list)


# ============================================================================
# Schemas: 2ª ETAPA — ANÁLISE E LANÇAMENTO AUTOMÁTICO
# ============================================================================

class EntityCheckQuery(BaseModel):
    fornecedor_nome: Optional[str] = None
    fornecedor_cnpj: Optional[str] = None
    faturado_nome: Optional[str] = None
    faturado_cpf_cnpj: Optional[str] = None
    despesa_descricao: Optional[str] = None
    tipo_classificacao: str = Field(default="DESPESA")


class EntitySearchResult(BaseModel):
    existe: bool
    id: Optional[int] = None
    nome_razao_social: Optional[str] = None
    documento: Optional[str] = None
    detalhes: Optional[str] = None
    ativo: Optional[bool] = None


class AnalysisCheckResponse(BaseModel):
    fornecedor: EntitySearchResult
    faturado: EntitySearchResult
    despesa: EntitySearchResult


class LaunchMovementRequest(BaseModel):
    # Fornecedor
    fornecedor_id: Optional[int] = None  # Se já existe
    fornecedor_nome: Optional[str] = None  # Se novo
    fornecedor_cnpj: Optional[str] = None
    fornecedor_ie: Optional[str] = None
    fornecedor_endereco: Optional[str] = None

    # Faturado
    faturado_id: Optional[int] = None  # Se já existe
    faturado_nome: Optional[str] = None  # Se novo
    faturado_cpf_cnpj: Optional[str] = None

    # Classificação / Despesa
    classificacao_id: Optional[int] = None  # Se já existe
    classificacao_descricao: Optional[str] = Field(default="MANUTENÇÃO E OPERAÇÃO")
    classificacao_tipo: str = Field(default="DESPESA")

    # Dados da NF-e / Movimento
    numero_documento: Optional[str] = None
    serie: Optional[str] = None
    chave_acesso: Optional[str] = None
    data_emissao: Optional[date] = None
    valor_total: Decimal = Field(default=Decimal("0.00"))
    tipo_movimento: str = Field(default="APAGAR")  # APAGAR ou ARECEBER
    observacao: Optional[str] = None

    # Parcelas (se vazia, gera ÚNICA com data_emissao ou hoje)
    parcelas: Optional[List[ParcelaCreate]] = None


class LaunchMovementResponse(BaseModel):
    sucesso: bool
    mensagem: str
    movimento_id: int
    fornecedor: EntitySearchResult
    faturado: EntitySearchResult
    despesa: EntitySearchResult
    total_parcelas: int
    valor_total: Decimal
