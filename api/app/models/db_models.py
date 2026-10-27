"""
Modelos ORM SQLAlchemy para o AgroContas.
Representa as tabelas do Banco de Dados:
- PESSOAS (Fornecedores, Faturados, Clientes)
- CLASSIFICACAO (Tipos de Despesa e Receita)
- MOVIMENTOCONTAS (Contas a Pagar / Contas a Receber)
- MOVIMENTO_CLASSIFICACAO (Associação Movimento <-> Classificação)
- PARCELACONTAS (Parcelas de pagamento/recebimento)

Regras de negócio implementadas:
- Soft delete: Nenhum cadastro é deletado; são marcados com ativo=False (inativados)
- Reativação permitida (ativo=True)
- Um movimento a pagar pode ter uma ou mais classificações de despesa
- Um movimento a receber pode ter uma ou mais classificações de receita
- Um movimento pode ter uma ou mais parcelas com vencimentos distintos
"""
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Pessoa(Base):
    """
    Entidade PESSOAS:
    Tipo: CLIENTE-FORNECEDOR, FORNECEDOR, FATURADO, CLIENTE
    """
    __tablename__ = "pessoas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tipo = Column(String(50), nullable=False, default="CLIENTE-FORNECEDOR", index=True)
    razao_social = Column(String(255), nullable=False, index=True)
    cpf_cnpj = Column(String(30), nullable=True, index=True)
    inscricao_estadual = Column(String(50), nullable=True)
    endereco = Column(String(255), nullable=True)
    telefone = Column(String(50), nullable=True)
    ativo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    movimentos_como_fornecedor = relationship(
        "MovimentoContas",
        foreign_keys="MovimentoContas.fornecedor_id",
        back_populates="fornecedor",
    )
    movimentos_como_faturado = relationship(
        "MovimentoContas",
        foreign_keys="MovimentoContas.faturado_id",
        back_populates="faturado",
    )
    movimentos_como_cliente = relationship(
        "MovimentoContas",
        foreign_keys="MovimentoContas.cliente_id",
        back_populates="cliente",
    )


class Classificacao(Base):
    """
    Entidade CLASSIFICACAO:
    Tipo: DESPESA ou RECEITA
    Descricao: Ex. "MANUTENÇÃO E OPERAÇÃO", "COMBUSTÍVEIS E LUBRIFICANTES"
    """
    __tablename__ = "classificacoes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tipo = Column(String(20), nullable=False, index=True)  # "DESPESA" ou "RECEITA"
    descricao = Column(String(255), nullable=False, index=True)
    ativo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamento com movimentos
    movimentos = relationship(
        "MovimentoClassificacao",
        back_populates="classificacao",
    )


class MovimentoContas(Base):
    """
    Entidade MOVIMENTOCONTAS:
    Tipo: APAGAR ou ARECEBER
    """
    __tablename__ = "movimentos_contas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tipo = Column(String(20), nullable=False, index=True)  # "APAGAR" ou "ARECEBER"
    
    # Vinculações com Pessoa
    fornecedor_id = Column(Integer, ForeignKey("pessoas.id"), nullable=True)
    faturado_id = Column(Integer, ForeignKey("pessoas.id"), nullable=True)
    cliente_id = Column(Integer, ForeignKey("pessoas.id"), nullable=True)
    
    numero_documento = Column(String(50), nullable=True, index=True)
    serie = Column(String(20), nullable=True)
    chave_acesso = Column(String(60), nullable=True, index=True)
    data_emissao = Column(Date, nullable=True)
    valor_total = Column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    observacao = Column(Text, nullable=True)
    
    status = Column(String(30), nullable=False, default="PENDENTE", index=True)  # PENDENTE, PAGO, RECEBIDO, CANCELADO
    ativo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    fornecedor = relationship("Pessoa", foreign_keys=[fornecedor_id], back_populates="movimentos_como_fornecedor")
    faturado = relationship("Pessoa", foreign_keys=[faturado_id], back_populates="movimentos_como_faturado")
    cliente = relationship("Pessoa", foreign_keys=[cliente_id], back_populates="movimentos_como_cliente")
    
    classificacoes = relationship(
        "MovimentoClassificacao",
        back_populates="movimento",
        cascade="all, delete-orphan",
    )
    parcelas = relationship(
        "ParcelaContas",
        back_populates="movimento",
        cascade="all, delete-orphan",
    )


class MovimentoClassificacao(Base):
    """
    Associação N:N entre MovimentoContas e Classificacao com valor rateado.
    """
    __tablename__ = "movimento_classificacoes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    movimento_id = Column(Integer, ForeignKey("movimentos_contas.id"), nullable=False)
    classificacao_id = Column(Integer, ForeignKey("classificacoes.id"), nullable=False)
    valor = Column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))

    # Relacionamentos
    movimento = relationship("MovimentoContas", back_populates="classificacoes")
    classificacao = relationship("Classificacao", back_populates="movimentos")


class ParcelaContas(Base):
    """
    Entidade PARCELACONTAS:
    Identificacao: "ÚNICA", "1/3", "2/3", "3/3", etc.
    """
    __tablename__ = "parcelas_contas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    movimento_id = Column(Integer, ForeignKey("movimentos_contas.id"), nullable=False)
    identificacao = Column(String(50), nullable=False, default="ÚNICA")
    numero_parcela = Column(Integer, nullable=False, default=1)
    data_vencimento = Column(Date, nullable=False)
    valor = Column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    status = Column(String(30), nullable=False, default="PENDENTE", index=True)  # PENDENTE, PAGO, CANCELADO
    data_pagamento = Column(Date, nullable=True)
    ativo = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento
    movimento = relationship("MovimentoContas", back_populates="parcelas")
