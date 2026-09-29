/**
 * Tipos TypeScript para Notas Fiscais (NF-e)
 * Espelha os modelos Pydantic do backend
 */

export interface Fornecedor {
  nome: string
  cnpj: string
  endereco: string | null
  ie: string | null
  telefone: string | null
}

export interface Destinatario {
  nome: string
  cnpj_cpf: string
  endereco: string | null
  ie: string | null
}

export interface ItemNotaFiscal {
  codigo: string | null
  descricao: string
  ncm: string | null
  cfop: string | null
  unidade: string | null
  quantidade: number | null
  valor_unitario: number | null
  valor_total: number | null
  icms_aliquota: number | null
}

export interface Totais {
  valor_produtos: number | null
  valor_frete: number | null
  valor_seguro: number | null
  valor_desconto: number | null
  valor_ipi: number | null
  valor_icms: number | null
  valor_total_nota: number | null
}

export interface NotaFiscal {
  numero: string
  serie: string | null
  data_emissao: string
  chave_acesso: string | null
  natureza_operacao: string | null
  tipo_operacao: string | null
  fornecedor: Fornecedor
  destinatario: Destinatario | null
  itens: ItemNotaFiscal[]
  totais: Totais | null
  informacoes_complementares: string | null
}

export interface ExtractApiResponse {
  success: boolean
  filename: string
  size_kb: number
  data: NotaFiscal
}

export interface ApiError {
  detail: string
}

/** Estados possíveis do processo de extração */
export type ExtractionStatus = 'idle' | 'uploading' | 'processing' | 'success' | 'error'
