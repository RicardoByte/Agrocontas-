<script setup lang="ts">
import { useInvoiceStore } from '@/stores/invoiceStore'
import InvoiceUploader from '@/components/InvoiceUploader.vue'
import JsonViewer from '@/components/JsonViewer.vue'
import InvoiceAnalysis from '@/components/InvoiceAnalysis.vue'

const store = useInvoiceStore()
</script>

<template>
  <div class="page-content">
    <!-- ── Page Header ──────────────────────────────────────── -->
    <div class="page-inner-header">
      <div class="page-breadcrumb">
        <a href="#">Cadastros</a>
        <span class="breadcrumb-sep">/</span>
        <span>Processamento de Documentos Fiscais</span>
        <span class="breadcrumb-sep">/</span>
      </div>
      <div class="page-title-row">
        <div>
          <h1 class="page-title">Extração de Notas &amp; Documentos</h1>
          <p class="page-subtitle">
            Importe arquivos fiscais (PDF, XML da SEFAZ, DANFE ou fotos de canhotos) para leitura
            inteligente via OCR e confronto cadastral automático com o banco de dados.
          </p>
        </div>
        <div class="header-badge">
          <span class="ai-badge">
            <span class="ai-badge-dot" />
            Powered by Gemini AI
          </span>
        </div>
      </div>
    </div>

    <!-- ── Page Body ────────────────────────────────────────── -->
    <div class="page-body">

      <!-- Step 1 — Extração -->
      <div class="precision-card extraction-card">
        <div class="extraction-card__inner">
          <InvoiceUploader />
        </div>

        <!-- Padrões suportados (rodapé do card) -->
        <div class="supported-formats">
          <span class="formats-label">PADRÕES:</span>
          <span class="format-tag format-tag--green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="10" height="10">
              <path stroke-linecap="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
            </svg>
            NF-e Mod. 55
          </span>
          <span class="format-tag format-tag--green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="10" height="10">
              <path stroke-linecap="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
            </svg>
            NFC-e Mod. 65
          </span>
          <span class="format-tag format-tag--green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="10" height="10">
              <path stroke-linecap="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
            </svg>
            NFS-e de Serviços
          </span>
          <span class="format-tag format-tag--code">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="10" height="10">
              <path stroke-linecap="round" stroke-width="2" d="M16 18l6-6-6-6M8 6l-6 6 6 6"/>
            </svg>
            XML Completo SEFAZ
          </span>
          <span class="format-tag format-tag--orange">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="10" height="10">
              <path stroke-linecap="round" stroke-width="2" d="M12 8v4l3 3M12 2a10 10 0 100 20A10 10 0 0012 2z"/>
            </svg>
            Contrato Futuro
          </span>
        </div>
      </div>

      <!-- Error banner -->
      <div v-if="store.isError" class="alert alert-error">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" style="flex-shrink:0;margin-top:1px">
          <path stroke-linecap="round" stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
        <div>
          <strong>Erro na extração:</strong> {{ store.errorMessage }}
        </div>
        <button
          style="margin-left:auto;background:none;border:none;cursor:pointer;font-size:0.85rem;color:inherit;opacity:0.6"
          @click="store.clearError()"
        >✕</button>
      </div>

      <!-- JSON Viewer -->
      <div v-if="store.hasData" class="precision-card">
        <div class="card-header">
          <span class="card-title">Dados Extraídos — JSON</span>
          <span class="badge badge-success">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="9" height="9">
              <path stroke-linecap="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
            </svg>
            Extração concluída
          </span>
        </div>
        <div class="card-body" style="padding:0">
          <JsonViewer />
        </div>
      </div>

      <!-- Step 2 — Análise -->
      <div v-if="store.hasData" class="precision-card">
        <div class="card-header">
          <span class="card-title">
            <span class="step-tag">2ª Etapa</span>
            Consulta e Lançamento Automático
          </span>
        </div>
        <div class="card-body" style="padding:0">
          <InvoiceAnalysis />
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* ── Extraction card overrides ─────────────────────────── */
.extraction-card {
  overflow: hidden;
}

.extraction-card__inner {
  padding: 0;
}

/* ── AI Badge ──────────────────────────────────────────── */
.ai-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--color-accent-subtle);
  border: 1px solid rgba(29, 111, 55, 0.2);
  color: var(--color-accent);
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.3rem 0.7rem;
  border-radius: 99px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
  margin-top: 0.25rem;
}

.ai-badge-dot {
  width: 6px;
  height: 6px;
  background: var(--color-accent-mid);
  border-radius: 50%;
  box-shadow: 0 0 5px rgba(45, 158, 80, 0.6);
}

/* ── Supported formats bar ─────────────────────────────── */
.supported-formats {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-2);
  flex-wrap: wrap;
}

.formats-label {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text-faint);
}

.format-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: 99px;
}

.format-tag--green {
  background: var(--color-success-bg);
  color: var(--color-success);
  border: 1px solid var(--color-success-border);
}

.format-tag--code {
  background: rgba(3, 105, 161, 0.08);
  color: var(--color-info);
  border: 1px solid rgba(3, 105, 161, 0.2);
}

.format-tag--orange {
  background: var(--color-warning-bg);
  color: var(--color-warning);
  border: 1px solid rgba(217, 119, 6, 0.2);
}

/* ── Step tag ──────────────────────────────────────────── */
.step-tag {
  background: var(--color-accent);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 0.15rem 0.45rem;
  border-radius: var(--radius-xs);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-right: 0.3rem;
}
</style>
