/**
 * Tipos TypeScript para os modelos do AgroContas (Pessoas, Classificações, Movimentos, Parcelas)
 * e para a 2ª Etapa de Análise e Lançamento
 */

export type TipoPessoa = 'CLIENTE-FORNECEDOR' | 'FORNECEDOR' | 'FATURADO' | 'CLIENTE'
export type TipoClassificacao = 'DESPESA' | 'RECEITA'
export type TipoMovimento = 'APAGAR' | 'ARECEBER'
export type StatusMovimento = 'PENDENTE' | 'PAGO' | 'RECEBIDO' | 'CANCELADO'
export type StatusParcela = 'PENDENTE' | 'PAGO' | 'CANCELADO'

export interface Pessoa {
  id: number
  tipo: string
  razao_social: string
  cpf_cnpj: string | null
  inscricao_estadual: string | null
  endereco: string | null
  telefone: string | null
  ativo: boolean
  created_at: string
  updated_at: string
}

export interface PessoaCreate {
  tipo: string
  razao_social: string
  cpf_cnpj?: string | null
  inscricao_estadual?: string | null
  endereco?: string | null
  telefone?: string | null
}

export interface Classificacao {
  id: number
  tipo: TipoClassificacao
  descricao: string
  ativo: boolean
  created_at: string
  updated_at: string
}

export interface ClassificacaoCreate {
  tipo: TipoClassificacao
  descricao: string
}

export interface ParcelaContas {
  id: number
  movimento_id: number
  identificacao: string
  numero_parcela: number
  data_vencimento: string
  valor: number
  status: StatusParcela
  data_pagamento: string | null
  ativo: boolean
  created_at: string
}

export interface ParcelaCreate {
  identificacao: string
  numero_parcela: number
  data_vencimento: string
  valor: number
  status?: StatusParcela
  data_pagamento?: string | null
}

export interface MovimentoClassificacao {
  id: number
  classificacao_id: number
  valor: number
  classificacao?: Classificacao
}

export interface MovimentoContas {
  id: number
  tipo: TipoMovimento
  fornecedor_id: number | null
  faturado_id: number | null
  cliente_id: number | null
  numero_documento: string | null
  serie: string | null
  chave_acesso: string | null
  data_emissao: string | null
  valor_total: number
  observacao: string | null
  status: StatusMovimento
  ativo: boolean
  created_at: string
  updated_at: string

  fornecedor?: Pessoa | null
  faturado?: Pessoa | null
  cliente?: Pessoa | null
  classificacoes: MovimentoClassificacao[]
  parcelas: ParcelaContas[]
}

export interface MovimentoCreate {
  tipo: TipoMovimento
  fornecedor_id?: number | null
  faturado_id?: number | null
  cliente_id?: number | null
  numero_documento?: string | null
  serie?: string | null
  chave_acesso?: string | null
  data_emissao?: string | null
  valor_total: number
  observacao?: string | null
  status?: StatusMovimento
  classificacoes: { classificacao_id: number; valor: number }[]
  parcelas: ParcelaCreate[]
}

// ─── 2ª Etapa: Análise e Lançamento ───────────────────────────────────────

export interface EntitySearchResult {
  existe: boolean
  id: number | null
  nome_razao_social: string | null
  documento: string | null
  detalhes: string | null
  ativo: boolean | null
}

export interface AnalysisCheckResponse {
  fornecedor: EntitySearchResult
  faturado: EntitySearchResult
  despesa: EntitySearchResult
}

export interface EntityCheckQuery {
  fornecedor_nome?: string | null
  fornecedor_cnpj?: string | null
  faturado_nome?: string | null
  faturado_cpf_cnpj?: string | null
  despesa_descricao?: string | null
  tipo_classificacao?: string
}

export interface LaunchMovementRequest {
  fornecedor_id?: number | null
  fornecedor_nome?: string | null
  fornecedor_cnpj?: string | null
  fornecedor_ie?: string | null
  fornecedor_endereco?: string | null

  faturado_id?: number | null
  faturado_nome?: string | null
  faturado_cpf_cnpj?: string | null

  classificacao_id?: number | null
  classificacao_descricao?: string | null
  classificacao_tipo?: string

  numero_documento?: string | null
  serie?: string | null
  chave_acesso?: string | null
  data_emissao?: string | null
  valor_total: number
  tipo_movimento?: TipoMovimento
  observacao?: string | null

  parcelas?: ParcelaCreate[]
}

export interface LaunchMovementResponse {
  sucesso: boolean
  mensagem: string
  movimento_id: number
  fornecedor: EntitySearchResult
  faturado: EntitySearchResult
  despesa: EntitySearchResult
  total_parcelas: number
  valor_total: number
}
