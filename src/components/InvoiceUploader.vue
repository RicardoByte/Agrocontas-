<script setup lang="ts">
import { ref, computed } from 'vue'
import { useInvoiceStore } from '@/stores/invoiceStore'

const store = useInvoiceStore()

const fileInputRef = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)

const MAX_SIZE_MB = 10

// Formata o tamanho do arquivo para exibição
const formattedFileSize = computed(() => {
  if (!store.selectedFile) return ''
  const mb = store.selectedFile.size / 1024 / 1024
  return mb < 1
    ? `${(store.selectedFile.size / 1024).toFixed(0)} KB`
    : `${mb.toFixed(2)} MB`
})

function triggerFileInput(): void {
  fileInputRef.value?.click()
}

function handleFileChange(event: Event): void {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0] ?? null
  processFile(file)
  // Reset input para permitir re-seleção do mesmo arquivo
  if (input) input.value = ''
}

function processFile(file: File | null): void {
  if (!file) return

  if (file.type !== 'application/pdf') {
    alert('❌ Apenas arquivos PDF são aceitos.')
    return
  }

  const sizeMB = file.size / 1024 / 1024
  if (sizeMB > MAX_SIZE_MB) {
    alert(`❌ Arquivo muito grande (${sizeMB.toFixed(1)} MB). Máximo: ${MAX_SIZE_MB} MB.`)
    return
  }

  store.selectFile(file)
}

// Drag & Drop
function onDragOver(e: DragEvent): void {
  e.preventDefault()
  isDragging.value = true
}

function onDragLeave(): void {
  isDragging.value = false
}

function onDrop(e: DragEvent): void {
  e.preventDefault()
  isDragging.value = false
  const file = e.dataTransfer?.files[0] ?? null
  processFile(file)
}
</script>

<template>
  <section class="uploader-section">
    <div class="section-header">
      <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
        />
      </svg>
      <h2 class="section-title">Upload do PDF</h2>
    </div>

    <!-- Drop Zone -->
    <div
      id="drop-zone"
      class="drop-zone"
      :class="{
        'drop-zone--dragging': isDragging,
        'drop-zone--has-file': store.hasFile,
      }"
      @click="triggerFileInput"
      @dragover="onDragOver"
      @dragleave="onDragLeave"
      @drop="onDrop"
    >
      <input
        ref="fileInputRef"
        id="pdf-file-input"
        type="file"
        accept="application/pdf"
        class="file-input-hidden"
        @change="handleFileChange"
      />

      <!-- Estado: nenhum arquivo -->
      <div v-if="!store.hasFile" class="drop-zone__content">
        <div class="drop-zone__icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
        <p class="drop-zone__primary">
          Arraste e solte o PDF aqui
        </p>
        <p class="drop-zone__secondary">
          ou <span class="link">clique para selecionar</span>
        </p>
        <p class="drop-zone__hint">PDF até {{ MAX_SIZE_MB }}MB</p>
      </div>

      <!-- Estado: arquivo selecionado -->
      <div v-else class="drop-zone__file">
        <div class="file-preview">
          <div class="file-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
            </svg>
          </div>
          <div class="file-info">
            <span class="file-name">{{ store.selectedFile?.name }}</span>
            <span class="file-size">{{ formattedFileSize }}</span>
          </div>
          <button
            id="remove-file-btn"
            class="file-remove"
            title="Remover arquivo"
            @click.stop="store.reset()"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <p class="drop-zone__replace">Clique para trocar o arquivo</p>
      </div>
    </div>

    <!-- Botão Extrair Dados -->
    <button
      id="extract-btn"
      class="extract-btn"
      :disabled="!store.hasFile || store.isLoading"
      @click="store.extract()"
    >
      <!-- Loading state -->
      <template v-if="store.isLoading">
        <span class="btn-spinner" />
        <span v-if="store.status === 'uploading'">
          Enviando... {{ store.uploadProgress }}%
        </span>
        <span v-else>Gemini processando...</span>
      </template>

      <!-- Default state -->
      <template v-else>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="btn-icon">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          />
        </svg>
        Extrair Dados com IA
      </template>
    </button>

    <!-- Barra de progresso -->
    <div v-if="store.status === 'uploading'" class="progress-bar">
      <div class="progress-bar__fill" :style="{ width: `${store.uploadProgress}%` }" />
    </div>

    <!-- Indicador de processamento Gemini -->
    <div v-if="store.status === 'processing'" class="processing-indicator">
      <span class="processing-dot" />
      <span class="processing-dot" />
      <span class="processing-dot" />
      <span>Gemini está analisando o documento...</span>
    </div>
  </section>
</template>

<style scoped>
.uploader-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.section-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--color-accent);
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

/* ── Drop Zone ─────────────────────────────────────────── */
.drop-zone {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  padding: 2rem;
  cursor: pointer;
  transition: all 0.25s ease;
  background: var(--color-surface-hover);
  min-height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drop-zone:hover,
.drop-zone--dragging {
  border-color: var(--color-accent);
  background: var(--color-accent-subtle);
  transform: scale(1.005);
}

.drop-zone--has-file {
  border-style: solid;
  border-color: var(--color-accent);
  background: var(--color-accent-subtle);
}

.file-input-hidden {
  display: none;
}

/* ── Drop Zone Content ─────────────────────────────────── */
.drop-zone__content {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
}

.drop-zone__icon {
  width: 3rem;
  height: 3rem;
  color: var(--color-text-muted);
  margin-bottom: 0.25rem;
}

.drop-zone__icon svg {
  width: 100%;
  height: 100%;
}

.drop-zone__primary {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--color-text-primary);
  margin: 0;
}

.drop-zone__secondary {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin: 0;
}

.drop-zone__secondary .link {
  color: var(--color-accent);
  font-weight: 500;
}

.drop-zone__hint {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin: 0;
}

/* ── File Preview ──────────────────────────────────────── */
.drop-zone__file {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.file-preview {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
}

.file-icon {
  width: 2rem;
  height: 2rem;
  color: var(--color-accent);
  flex-shrink: 0;
}

.file-icon svg {
  width: 100%;
  height: 100%;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  min-width: 0;
}

.file-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.file-remove {
  width: 1.75rem;
  height: 1.75rem;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--color-text-muted);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.file-remove:hover {
  background: var(--color-error-subtle);
  color: var(--color-error);
}

.file-remove svg {
  width: 1rem;
  height: 1rem;
}

.drop-zone__replace {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  text-align: center;
  margin: 0;
}

/* ── Extract Button ────────────────────────────────────── */
.extract-btn {
  width: 100%;
  padding: 0.875rem 1.5rem;
  background: var(--color-accent-gradient);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.95rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.625rem;
  transition: all 0.25s ease;
  letter-spacing: 0.025em;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.35);
}

.extract-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5);
}

.extract-btn:active:not(:disabled) {
  transform: translateY(0);
}

.extract-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}

.btn-icon {
  width: 1.125rem;
  height: 1.125rem;
}

/* ── Spinner ───────────────────────────────────────────── */
.btn-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── Progress Bar ──────────────────────────────────────── */
.progress-bar {
  height: 4px;
  background: var(--color-surface-hover);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar__fill {
  height: 100%;
  background: var(--color-accent-gradient);
  border-radius: 2px;
  transition: width 0.3s ease;
}

/* ── Processing Indicator ──────────────────────────────── */
.processing-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: var(--color-text-muted);
  justify-content: center;
}

.processing-dot {
  width: 6px;
  height: 6px;
  background: var(--color-accent);
  border-radius: 50%;
  animation: pulse-dot 1.4s infinite ease-in-out;
}

.processing-dot:nth-child(2) { animation-delay: 0.2s; }
.processing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse-dot {
  0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
  40% { transform: scale(1.2); opacity: 1; }
}
</style>
