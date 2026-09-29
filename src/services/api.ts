/**
 * Serviço de comunicação com o backend FastAPI
 */
import axios, { type AxiosError } from 'axios'
import type { ExtractApiResponse } from '@/types/invoice'

// URL base do backend — usa variável de ambiente (Vite expõe VITE_* vars)
const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60_000, // 60 segundos — PDFs grandes podem demorar
})

/**
 * Envia um PDF para extração de dados via Gemini AI
 *
 * @param file - Arquivo PDF selecionado pelo usuário
 * @param onProgress - Callback opcional de progresso de upload (0-100)
 * @returns Dados extraídos da nota fiscal
 */
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
    const axiosError = error as AxiosError<{ detail: string }>
    const message =
      axiosError.response?.data?.detail ??
      axiosError.message ??
      'Erro desconhecido ao conectar com o servidor'
    throw new Error(message)
  }
}
