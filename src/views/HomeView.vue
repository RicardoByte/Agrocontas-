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
        <span style="color: var(--color-agro-forest); font-weight: 700;">Processamento de Documentos Fiscais</span>
        <span class="breadcrumb-sep">/</span>
      </div>
      <div class="page-title-row">
        <div>
          <h1 class="page-title">EXTRAÇÃO DE NOTAS &amp; DOCUMENTOS</h1>
          <p class="page-subtitle">
            Importe arquivos fiscais (PDF, XML da SEFAZ, DANFE ou fotos de canhotos) para leitura inteligente via OCR e confronto cadastral automático com o banco de dados.
          </p>
        </div>
        <div class="header-badge">
          <span class="ai-badge">
            <span class="ai-badge-dot" />
            POWERED BY GEMINI AI
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

        <!-- Padrões suportados (rodapé do card exatamente como Image 1) -->
        <div class="supported-formats">
          <span class="formats-label">PADRÕES:</span>
          <span class="format-tag format-tag--green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="12" height="12" stroke-width="2.5">
              <path stroke-linecap="round" d="M20 6L9 17l-5-5"/>
            </svg>
            NF-e Mod. 55
          </span>
          <span class="format-tag format-tag--green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="12" height="12" stroke-width="2.5">
              <path stroke-linecap="round" d="M20 6L9 17l-5-5"/>
            </svg>
            NFC-e Mod. 65
          </span>
          <span class="format-tag format-tag--green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="12" height="12" stroke-width="2.5">
              <path stroke-linecap="round" d="M20 6L9 17l-5-5"/>
            </svg>
            NFS-e de Serviços
          </span>
          <span class="format-tag format-tag--code">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="12" height="12" stroke-width="2">
              <polyline points="16 18 22 12 16 6"/>
              <polyline points="8 6 2 12 8 18"/>
            </svg>
            XML Completo SEFAZ
          </span>
          <span class="format-tag format-tag--orange">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="12" height="12" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            Contrato Futuro
          </span>
        </div>
      </div>

      <!-- Error banner -->
      <div v-if="store.isError" class="alert alert-error">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" style="flex-shrink:0;margin-top:1px">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
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

<style src="@/assets/styles/home.css"></style>
