"""
Modelos Pydantic para Notas Fiscais (NF-e)
Define a estrutura de dados que o Gemini deve retornar
"""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class Fornecedor(BaseModel):
    nome: str = Field(description="Razão social ou nome do fornecedor")
    cnpj: str = Field(description="CNPJ do fornecedor (somente números ou formatado)")
    endereco: Optional[str] = Field(default=None, description="Endereço completo")
    ie: Optional[str] = Field(default=None, description="Inscrição Estadual")
    telefone: Optional[str] = Field(default=None)


class Destinatario(BaseModel):
    nome: str = Field(description="Razão social ou nome do destinatário")
    cnpj_cpf: str = Field(description="CNPJ ou CPF do destinatário")
    endereco: Optional[str] = Field(default=None)
    ie: Optional[str] = Field(default=None, description="Inscrição Estadual")


class ItemNotaFiscal(BaseModel):
    codigo: Optional[str] = Field(default=None, description="Código do produto")
    descricao: str = Field(description="Descrição do produto ou serviço")
    ncm: Optional[str] = Field(default=None, description="Código NCM")
    cfop: Optional[str] = Field(default=None, description="CFOP da operação")
    unidade: Optional[str] = Field(default=None, description="Unidade de medida (ex: KG, UN, CX)")
    quantidade: Optional[Decimal] = Field(default=None)
    valor_unitario: Optional[Decimal] = Field(default=None)
    valor_total: Optional[Decimal] = Field(default=None)
    icms_aliquota: Optional[Decimal] = Field(default=None, description="Alíquota ICMS em %")


class Totais(BaseModel):
    valor_produtos: Optional[Decimal] = Field(default=None)
    valor_frete: Optional[Decimal] = Field(default=None)
    valor_seguro: Optional[Decimal] = Field(default=None)
    valor_desconto: Optional[Decimal] = Field(default=None)
    valor_ipi: Optional[Decimal] = Field(default=None)
    valor_icms: Optional[Decimal] = Field(default=None)
    valor_total_nota: Optional[Decimal] = Field(default=None)


class NotaFiscal(BaseModel):
    """Estrutura completa de uma NF-e extraída pelo Gemini"""
    numero: str = Field(description="Número da nota fiscal")
    serie: Optional[str] = Field(default=None)
    data_emissao: str = Field(description="Data de emissão no formato YYYY-MM-DD")
    chave_acesso: Optional[str] = Field(default=None, description="Chave de acesso de 44 dígitos")
    natureza_operacao: Optional[str] = Field(default=None)
    tipo_operacao: Optional[str] = Field(default=None, description="Entrada ou Saída")
    fornecedor: Fornecedor
    destinatario: Optional[Destinatario] = Field(default=None)
    itens: list[ItemNotaFiscal] = Field(default_factory=list)
    totais: Optional[Totais] = Field(default=None)
    informacoes_complementares: Optional[str] = Field(default=None)
