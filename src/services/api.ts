/**
 * Serviço de comunicação com o backend FastAPI do AgroContas
 */
import axios, { type AxiosError } from 'axios'
import type { ExtractApiResponse } from '@/types/invoice'
import type {
  Pessoa,
  PessoaCreate,
  Classificacao,
  ClassificacaoCreate,
  MovimentoContas,
  MovimentoCreate,
  ParcelaContas,
  EntityCheckQuery,
  AnalysisCheckResponse,
  LaunchMovementRequest,
  LaunchMovementResponse,
} from '@/types/models'

// Em desenvolvimento: usa '' para que o proxy do Vite (vite.config.ts) resolva /api/* → localhost:8000
// Em produção: define VITE_API_URL com a URL completa do backend
const BASE_URL = import.meta.env.VITE_API_URL ?? ''

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60_000,
})

function handleApiError(error: unknown): never {
  const axiosError = error as AxiosError<{ detail: string }>
  const message =
    axiosError.response?.data?.detail ??
    axiosError.message ??
    'Erro desconhecido ao conectar com o servidor'
  throw new Error(message)
}

// ─── Extração de NF-e via IA Gemini ───────────────────────────────────────
export async function extractInvoiceData(
  file: File,
  onProgress?: (percent: number) => void,
): Promise<ExtractApiResponse> {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await api.post<ExtractApiResponse>('/api/v1/extract', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (event) => {
        if (event.total && onProgress) {
          const percent = Math.round((event.loaded * 100) / event.total)
          onProgress(percent)
        }
      },
    })
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

// ─── 2ª Etapa: Análise de Entidades e Lançamento ──────────────────────────
export async function checkEntities(query: EntityCheckQuery): Promise<AnalysisCheckResponse> {
  try {
    const response = await api.post<AnalysisCheckResponse>('/api/v1/analysis/check-entities', query)
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

export async function launchMovement(data: LaunchMovementRequest): Promise<LaunchMovementResponse> {
  try {
    const response = await api.post<LaunchMovementResponse>('/api/v1/analysis/launch-movement', data)
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

// ─── CRUD: Pessoas (Fornecedores, Faturados, Clientes) ─────────────────────
export async function getPessoas(params?: {
  tipo?: string
  busca?: string
  ativo?: boolean
}): Promise<Pessoa[]> {
  try {
    const response = await api.get<Pessoa[]>('/api/v1/pessoas', { params })
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

export async function createPessoa(data: PessoaCreate): Promise<Pessoa> {
  try {
    const response = await api.post<Pessoa>('/api/v1/pessoas', data)
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

export async function updatePessoa(id: number, data: Partial<PessoaCreate>): Promise<Pessoa> {
  try {
    const response = await api.put<Pessoa>(`/api/v1/pessoas/${id}`, data)
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

export async function inativarPessoa(id: number): Promise<Pessoa> {
  try {
    const response = await api.patch<Pessoa>(`/api/v1/pessoas/${id}/inativar`)
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

export async function reativarPessoa(id: number): Promise<Pessoa> {
  try {
    const response = await api.patch<Pessoa>(`/api/v1/pessoas/${id}/reativar`)
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

// ─── CRUD: Classificações (Despesas e Receitas) ───────────────────────────
export async function getClassificacoes(params?: {
  tipo?: string
  busca?: string
  ativo?: boolean
}): Promise<Classificacao[]> {
  try {
    const response = await api.get<Classificacao[]>('/api/v1/classificacoes', { params })
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

export async function createClassificacao(data: ClassificacaoCreate): Promise<Classificacao> {
  try {
    const response = await api.post<Classificacao>('/api/v1/classificacoes', data)
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

export async function updateClassificacao(
  id: number,
  data: Partial<ClassificacaoCreate>,
): Promise<Classificacao> {
  try {
    const response = await api.put<Classificacao>(`/api/v1/classificacoes/${id}`, data)
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

export async function inativarClassificacao(id: number): Promise<Classificacao> {
  try {
    const response = await api.patch<Classificacao>(`/api/v1/classificacoes/${id}/inativar`)
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

export async function reativarClassificacao(id: number): Promise<Classificacao> {
  try {
    const response = await api.patch<Classificacao>(`/api/v1/classificacoes/${id}/reativar`)
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

// ─── CRUD: Movimentos e Parcelas ──────────────────────────────────────────
export async function getMovimentos(params?: {
  tipo?: string
  status?: string
  ativo?: boolean
}): Promise<MovimentoContas[]> {
  try {
    const response = await api.get<MovimentoContas[]>('/api/v1/movimentos', { params })
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

export async function createMovimento(data: MovimentoCreate): Promise<MovimentoContas> {
  try {
    const response = await api.post<MovimentoContas>('/api/v1/movimentos', data)
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

export async function inativarMovimento(id: number): Promise<MovimentoContas> {
  try {
    const response = await api.patch<MovimentoContas>(`/api/v1/movimentos/${id}/inativar`)
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

export async function reativarMovimento(id: number): Promise<MovimentoContas> {
  try {
    const response = await api.patch<MovimentoContas>(`/api/v1/movimentos/${id}/reativar`)
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

export async function pagarParcela(movimentoId: number, parcelaId: number): Promise<ParcelaContas> {
  try {
    const response = await api.patch<ParcelaContas>(
      `/api/v1/movimentos/${movimentoId}/parcelas/${parcelaId}/pagar`,
    )
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}
