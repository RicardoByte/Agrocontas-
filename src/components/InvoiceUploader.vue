<script setup lang="ts">
import { ref, computed } from 'vue'
import { useInvoiceStore } from '@/stores/invoiceStore'

const store = useInvoiceStore()
const fileInputRef = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)

const MAX_SIZE_MB = 25

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
  if (input) input.value = ''
}

function processFile(file: File | null): void {
  if (!file) return

  // Validação: PDF ou XML ou Imagem
  const validTypes = ['application/pdf', 'text/xml', 'application/xml', 'image/jpeg', 'image/png']
  const isXml = file.name.endsWith('.xml')
  if (!validTypes.includes(file.type) && !isXml) {
    alert('❌ Por favor, envie um arquivo fiscal válido (PDF, XML da SEFAZ, DANFE ou imagem).')
    return
  }

  const sizeMB = file.size / 1024 / 1024
  if (sizeMB > MAX_SIZE_MB) {
    alert(`❌ Arquivo excede o tamanho máximo permitido de ${MAX_SIZE_MB}MB.`)
    return
  }

  store.selectFile(file)
}

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
    <!-- Precision Dropzone com Cantoneiras Arquiteturais -->
    <div
      id="precision-drop-zone"
      class="precision-dropzone-wrap"
      :class="{
        'precision-dropzone-wrap--dragging': isDragging,
        'precision-dropzone-wrap--has-file': store.hasFile,
      }"
      @click="triggerFileInput"
      @dragover="onDragOver"
      @dragleave="onDragLeave"
      @drop="onDrop"
    >
      <!-- Corner Markers (Cantoneiras Precisão) -->
      <span class="corner-marker corner-marker--tl" />
      <span class="corner-marker corner-marker--tr" />
      <span class="corner-marker corner-marker--bl" />
      <span class="corner-marker corner-marker--br" />

      <input
        ref="fileInputRef"
        id="pdf-file-input"
        type="file"
        accept="application/pdf,application/xml,text/xml,image/*"
        class="file-input-hidden"
        @change="handleFileChange"
      />

      <!-- Sem arquivo selecionado -->
      <template v-if="!store.hasFile">
        <div class="dropzone-icon-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="30" height="30" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="16 16 12 12 8 16"/>
            <line x1="12" y1="12" x2="12" y2="21"/>
            <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/>
          </svg>
        </div>

        <h3 class="dropzone-title">ARRASTE E SOLTE O ARQUIVO AQUI</h3>
        <p class="dropzone-desc">
          Suporta <strong>PDF (DANFE)</strong>, <strong>XML da SEFAZ</strong>, ou fotos nítidas de recibos, fretes e canhotos de entrega agrícola.
        </p>

        <button type="button" class="btn-select-file" @click.stop="triggerFileInput">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
          <span>ESCOLHER ARQUIVO DO COMPUTADOR</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14" stroke-width="2.2">
            <line x1="7" y1="7" x2="17" y2="17"/>
            <polyline points="7 17 17 17 17 7"/>
          </svg>
        </button>

        <span class="dropzone-caption">
          TAMANHO MÁXIMO: 25MB • PROCESSAMENTO CRIPTOGRAFADO PONTA A PONTA
        </span>
      </template>

      <!-- Arquivo Selecionado -->
      <template v-else>
        <div class="file-preview-card" @click.stop>
          <div class="file-preview-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="22" height="22" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
          </div>
          <div class="file-preview-meta">
            <span class="file-preview-name">{{ store.selectedFile?.name }}</span>
            <span class="file-preview-size">{{ formattedFileSize }}</span>
          </div>
          <button
            type="button"
            class="file-preview-remove"
            title="Remover arquivo"
            @click.stop="store.reset()"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" stroke-width="2.2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <span class="dropzone-change-hint">Clique para selecionar outro documento</span>
      </template>
    </div>

    <!-- Botão de Ação: Extrair Dados com IA -->
    <div v-if="store.hasFile">
      <button
        id="extract-btn"
        type="button"
        class="btn-extract-action"
        :disabled="store.isLoading"
        @click="store.extract()"
      >
        <template v-if="store.isLoading">
          <span class="btn-extract-spinner" />
          <span>Gemini AI Processando Documento...</span>
        </template>
        <template v-else>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="18" height="18" stroke-width="2">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
          </svg>
          <span>INICIAR PROCESSAMENTO &amp; EXTRAÇÃO OCR</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14" stroke-width="2.2">
            <line x1="7" y1="7" x2="17" y2="17"/>
            <polyline points="7 17 17 17 17 7"/>
          </svg>
        </template>
      </button>
    </div>

    <!-- Feedback de processamento -->
    <div v-if="store.isLoading" class="processing-status-bar">
      <div class="processing-dots">
        <span />
        <span />
        <span />
      </div>
      <span>Extraindo campos tributários, itens e emitente via IA Gemini...</span>
    </div>
  </section>
</template>

<style src="@/assets/styles/uploader.css"></style>
