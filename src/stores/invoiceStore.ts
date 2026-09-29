/**
 * Pinia Store — gerencia o estado global de extração de notas fiscais
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { NotaFiscal, ExtractionStatus } from '@/types/invoice'
import { extractInvoiceData } from '@/services/api'

export const useInvoiceStore = defineStore('invoice', () => {
  // ─── State ────────────────────────────────────────────────────────────────
  const selectedFile = ref<File | null>(null)
  const extractedData = ref<NotaFiscal | null>(null)
  const status = ref<ExtractionStatus>('idle')
  const errorMessage = ref<string | null>(null)
  const uploadProgress = ref<number>(0)
  const filename = ref<string | null>(null)
  const fileSizeKb = ref<number | null>(null)

  // ─── Getters ──────────────────────────────────────────────────────────────
  const hasFile = computed(() => selectedFile.value !== null)
  const hasData = computed(() => extractedData.value !== null)
  const isLoading = computed(
    () => status.value === 'uploading' || status.value === 'processing',
  )
  const isSuccess = computed(() => status.value === 'success')
  const isError = computed(() => status.value === 'error')

  const extractedJson = computed(() =>
    extractedData.value ? JSON.stringify(extractedData.value, null, 2) : null,
  )

  // ─── Actions ──────────────────────────────────────────────────────────────

  function selectFile(file: File | null): void {
    selectedFile.value = file
    // Limpa dados anteriores ao selecionar novo arquivo
    extractedData.value = null
    errorMessage.value = null
    status.value = 'idle'
    uploadProgress.value = 0
  }

  async function extract(): Promise<void> {
    if (!selectedFile.value) return

    status.value = 'uploading'
    errorMessage.value = null
    uploadProgress.value = 0
    extractedData.value = null

    try {
      const response = await extractInvoiceData(selectedFile.value, (percent) => {
        uploadProgress.value = percent
        if (percent === 100) {
          // Upload concluído, agora o Gemini está processando
          status.value = 'processing'
        }
      })

      extractedData.value = response.data
      filename.value = response.filename
      fileSizeKb.value = response.size_kb
      status.value = 'success'
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : 'Erro inesperado'
      status.value = 'error'
    }
  }

  /** Fecha apenas o banner de erro, mantendo o arquivo selecionado */
  function clearError(): void {
    errorMessage.value = null
    status.value = 'idle'
  }

  function reset(): void {
    selectedFile.value = null
    extractedData.value = null
    status.value = 'idle'
    errorMessage.value = null
    uploadProgress.value = 0
    filename.value = null
    fileSizeKb.value = null
  }

  return {
    // State
    selectedFile,
    extractedData,
    status,
    errorMessage,
    uploadProgress,
    filename,
    fileSizeKb,
    // Getters
    hasFile,
    hasData,
    isLoading,
    isSuccess,
    isError,
    extractedJson,
    // Actions
    selectFile,
    extract,
    clearError,
    reset,
  }
})
