<script setup lang="ts">
import { ref, computed } from 'vue'
import { useInvoiceStore } from '@/stores/invoiceStore'

const store = useInvoiceStore()

type ViewMode = 'formatted' | 'json'
const viewMode = ref<ViewMode>('formatted')

const copySuccess = ref(false)

async function copyJson(): Promise<void> {
  if (!store.extractedJson) return
  try {
    await navigator.clipboard.writeText(store.extractedJson)
    copySuccess.value = true
    setTimeout(() => (copySuccess.value = false), 2000)
  } catch {
    // Fallback para browsers sem Clipboard API
    const el = document.createElement('textarea')
    el.value = store.extractedJson
    document.body.appendChild(el)
    el.select()
    document.execCommand('copy')
    document.body.removeChild(el)
    copySuccess.value = true
    setTimeout(() => (copySuccess.value = false), 2000)
  }
}

// Formata valor monetário em BRL
function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—'
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value)
}

function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—'
  return new Intl.NumberFormat('pt-BR').format(value)
}

// Highlight de JSON (coloração por tipo)
const highlightedJson = computed(() => {
  if (!store.extractedJson) return ''
  return store.extractedJson
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(
      /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)/g,
      (match) => {
        let cls = 'json-number'
        if (/^"/.test(match)) {
          cls = /:$/.test(match) ? 'json-key' : 'json-string'
        } else if (/true|false/.test(match)) {
          cls = 'json-boolean'
        } else if (/null/.test(match)) {
          cls = 'json-null'
        }
        return `<span class="${cls}">${match}</span>`
      },
    )
})
</script>

<template>
  <section v-if="store.hasData" class="viewer-section">
    <div class="viewer-header">
      <h2 class="section-title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="section-icon">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Dados Extraídos
      </h2>

      <!-- Toggle de visualização -->
      <div class="view-toggle" role="tablist">
        <button
          id="view-formatted-btn"
          role="tab"
          class="toggle-btn"
          :class="{ 'toggle-btn--active': viewMode === 'formatted' }"
          @click="viewMode = 'formatted'"
        >
          Visualização Formatada
        </button>
        <button
          id="view-json-btn"
          role="tab"
          class="toggle-btn"
          :class="{ 'toggle-btn--active': viewMode === 'json' }"
          @click="viewMode = 'json'"
        >
          JSON
        </button>
      </div>
    </div>

    <!-- ── Visualização Formatada ─────────────────────── -->
    <div v-if="viewMode === 'formatted'" class="formatted-view">
      <div v-if="store.extractedData" class="nfe-data">
        <!-- Cabeçalho da NF -->
        <div class="data-card">
          <h3 class="card-title">📄 Informações da Nota</h3>
          <div class="data-grid">
            <div class="data-field">
              <span class="field-label">Número</span>
              <span class="field-value highlight">{{ store.extractedData.numero }}</span>
            </div>
            <div class="data-field">
              <span class="field-label">Série</span>
              <span class="field-value">{{ store.extractedData.serie ?? '—' }}</span>
            </div>
            <div class="data-field">
              <span class="field-label">Data de Emissão</span>
              <span class="field-value">{{ store.extractedData.data_emissao }}</span>
            </div>
            <div class="data-field">
              <span class="field-label">Natureza da Operação</span>
              <span class="field-value">{{ store.extractedData.natureza_operacao ?? '—' }}</span>
            </div>
            <div v-if="store.extractedData.chave_acesso" class="data-field data-field--full">
              <span class="field-label">Chave de Acesso</span>
              <span class="field-value field-value--mono">{{ store.extractedData.chave_acesso }}</span>
            </div>
          </div>
        </div>

        <!-- Fornecedor -->
        <div class="data-card">
          <h3 class="card-title">🏭 Fornecedor</h3>
          <div class="data-grid">
            <div class="data-field data-field--full">
              <span class="field-label">Razão Social</span>
              <span class="field-value highlight">{{ store.extractedData.fornecedor.nome }}</span>
            </div>
            <div class="data-field">
              <span class="field-label">CNPJ</span>
              <span class="field-value field-value--mono">{{ store.extractedData.fornecedor.cnpj }}</span>
            </div>
            <div class="data-field">
              <span class="field-label">Inscrição Estadual</span>
              <span class="field-value">{{ store.extractedData.fornecedor.ie ?? '—' }}</span>
            </div>
            <div v-if="store.extractedData.fornecedor.endereco" class="data-field data-field--full">
              <span class="field-label">Endereço</span>
              <span class="field-value">{{ store.extractedData.fornecedor.endereco }}</span>
            </div>
          </div>
        </div>

        <!-- Destinatário -->
        <div v-if="store.extractedData.destinatario" class="data-card">
          <h3 class="card-title">🏢 Destinatário</h3>
          <div class="data-grid">
            <div class="data-field data-field--full">
              <span class="field-label">Nome/Razão Social</span>
              <span class="field-value highlight">{{ store.extractedData.destinatario.nome }}</span>
            </div>
            <div class="data-field">
              <span class="field-label">CNPJ/CPF</span>
              <span class="field-value field-value--mono">{{ store.extractedData.destinatario.cnpj_cpf }}</span>
            </div>
          </div>
        </div>

        <!-- Itens -->
        <div v-if="store.extractedData.itens.length > 0" class="data-card">
          <h3 class="card-title">📦 Itens ({{ store.extractedData.itens.length }})</h3>
          <div class="items-table-wrapper">
            <table class="items-table">
              <thead>
                <tr>
                  <th>Descrição</th>
                  <th>Qtd</th>
                  <th>Un.</th>
                  <th>Vl. Unit.</th>
                  <th>Vl. Total</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, idx) in store.extractedData.itens" :key="idx">
                  <td>{{ item.descricao }}</td>
                  <td>{{ formatNumber(item.quantidade) }}</td>
                  <td>{{ item.unidade ?? '—' }}</td>
                  <td>{{ formatCurrency(item.valor_unitario) }}</td>
                  <td class="value-col">{{ formatCurrency(item.valor_total) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Totais -->
        <div v-if="store.extractedData.totais" class="data-card">
          <h3 class="card-title">💰 Totais</h3>
          <div class="totals-grid">
            <div class="total-row">
              <span>Valor dos Produtos</span>
              <span>{{ formatCurrency(store.extractedData.totais.valor_produtos) }}</span>
            </div>
            <div v-if="store.extractedData.totais.valor_frete" class="total-row">
              <span>Frete</span>
              <span>{{ formatCurrency(store.extractedData.totais.valor_frete) }}</span>
            </div>
            <div v-if="store.extractedData.totais.valor_desconto" class="total-row total-row--discount">
              <span>Desconto</span>
              <span>- {{ formatCurrency(store.extractedData.totais.valor_desconto) }}</span>
            </div>
            <div v-if="store.extractedData.totais.valor_icms" class="total-row">
              <span>ICMS</span>
              <span>{{ formatCurrency(store.extractedData.totais.valor_icms) }}</span>
            </div>
            <div class="total-row total-row--total">
              <span>TOTAL DA NOTA</span>
              <span>{{ formatCurrency(store.extractedData.totais.valor_total_nota) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Visualização JSON ───────────────────────────── -->
    <div v-else class="json-view">
      <div class="json-toolbar">
        <div class="json-toolbar__left">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="json-icon">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
          <span>Dados em JSON</span>
        </div>
        <button
          id="copy-json-btn"
          class="copy-btn"
          :class="{ 'copy-btn--success': copySuccess }"
          @click="copyJson"
        >
          <svg v-if="!copySuccess" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          {{ copySuccess ? 'Copiado!' : 'Copiar JSON' }}
        </button>
      </div>

      <div class="json-code-wrapper">
        <pre class="json-code" v-html="highlightedJson" />
      </div>

      <p class="json-hint">
        Este JSON contém todos os dados extraídos da nota fiscal e pode ser usado
        para integração com outros sistemas.
      </p>
    </div>
  </section>
</template>

<style scoped>
.viewer-section {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  animation: slide-up 0.4s ease;
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.viewer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.section-icon {
  width: 1.125rem;
  height: 1.125rem;
  color: var(--color-accent);
}

/* ── Toggle ──────────────────────────────────────────────── */
.view-toggle {
  display: flex;
  background: var(--color-surface-hover);
  border-radius: var(--radius-md);
  padding: 3px;
  gap: 3px;
}

.toggle-btn {
  padding: 0.375rem 0.875rem;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  font-size: 0.8rem;
  font-weight: 500;
  font-family: inherit;
  border-radius: calc(var(--radius-md) - 2px);
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn--active {
  background: var(--color-surface);
  color: var(--color-text-primary);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

/* ── Formatted View ─────────────────────────────────────── */
.formatted-view {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.data-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
}

.card-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.875rem;
}

.data-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.data-field--full {
  grid-column: 1 / -1;
}

.field-label {
  font-size: 0.7rem;
  font-weight: 500;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.field-value {
  font-size: 0.875rem;
  color: var(--color-text-primary);
  line-height: 1.4;
}

.field-value.highlight {
  font-weight: 600;
  color: var(--color-accent-light);
}

.field-value--mono {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.8rem;
  word-break: break-all;
}

/* ── Tabela de Itens ────────────────────────────────────── */
.items-table-wrapper {
  overflow-x: auto;
  border-radius: var(--radius-md);
}

.items-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}

.items-table th {
  background: var(--color-surface-hover);
  color: var(--color-text-muted);
  font-weight: 600;
  text-align: left;
  padding: 0.5rem 0.75rem;
  white-space: nowrap;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.items-table td {
  padding: 0.625rem 0.75rem;
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-border);
}

.items-table tr:last-child td {
  border-bottom: none;
}

.items-table tr:hover td {
  background: var(--color-surface-hover);
}

.value-col {
  font-weight: 600;
  color: var(--color-accent-light) !important;
}

/* ── Totais ─────────────────────────────────────────────── */
.totals-grid {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  font-size: 0.875rem;
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-border);
}

.total-row:last-child { border-bottom: none; }

.total-row--discount {
  color: var(--color-error);
}

.total-row--total {
  font-weight: 700;
  font-size: 1rem;
  color: var(--color-accent-light);
  padding-top: 0.75rem;
  border-top: 2px solid var(--color-accent);
  border-bottom: none;
}

/* ── JSON View ──────────────────────────────────────────── */
.json-view {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.json-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.json-toolbar__left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.json-icon {
  width: 1rem;
  height: 1rem;
  color: var(--color-accent);
}

.copy-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.375rem 0.875rem;
  background: var(--color-surface-hover);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: 0.8rem;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.copy-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.copy-btn--success {
  border-color: var(--color-success);
  color: var(--color-success);
  background: var(--color-success-subtle);
}

.copy-btn svg {
  width: 0.875rem;
  height: 0.875rem;
}

.json-code-wrapper {
  background: #0d1117;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg);
  overflow: hidden;
  max-height: 420px;
  overflow-y: auto;
}

.json-code {
  margin: 0;
  padding: 1.25rem 1.5rem;
  font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
  font-size: 0.8rem;
  line-height: 1.7;
  white-space: pre;
  overflow-x: auto;
  color: #e6edf3;
}

/* JSON Syntax Colors */
:deep(.json-key) { color: #79c0ff; }
:deep(.json-string) { color: #a5d6a7; }
:deep(.json-number) { color: #ffa657; }
:deep(.json-boolean) { color: #ff7b72; }
:deep(.json-null) { color: #8b949e; }

.json-hint {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin: 0;
  text-align: center;
}
</style>
