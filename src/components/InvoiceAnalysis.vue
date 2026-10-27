<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { useInvoiceStore } from '@/stores/invoiceStore'
import { checkEntities, launchMovement, getClassificacoes } from '@/services/api'
import type {
  AnalysisCheckResponse,
  Classificacao,
  LaunchMovementResponse,
} from '@/types/models'

const store = useInvoiceStore()

// Estados da análise
const isChecking = ref(false)
const isLaunching = ref(false)
const checkResult = ref<AnalysisCheckResponse | null>(null)
const launchResult = ref<LaunchMovementResponse | null>(null)
const launchError = ref<string | null>(null)

// Campos editáveis antes de lançar
const despesaDescricao = ref('MANUTENÇÃO E OPERAÇÃO')
const vencimentoData = ref<string>(new Date().toISOString().split('T')[0]!)
const identificacaoParcela = ref('ÚNICA')
const availableClassificacoes = ref<Classificacao[]>([])

// Carrega classificações existentes para autocomplete / dropdown
async function loadClassificacoes() {
  try {
    availableClassificacoes.value = await getClassificacoes({ tipo: 'DESPESA', ativo: true })
  } catch (err) {
    console.error('Erro ao carregar classificações:', err)
  }
}

// Executa a checagem no banco de dados (Atividade 2ª Etapa)
async function runAnalysis() {
  if (!store.extractedData) return

  isChecking.value = true
  launchResult.value = null
  launchError.value = null

  try {
    const fornecedor = store.extractedData.fornecedor
    const destinatario = store.extractedData.destinatario

    // Se a NF-e tem data de emissão, usa como base para vencimento (ex: 30 dias após)
    if (store.extractedData.data_emissao) {
      try {
        const d = new Date(store.extractedData.data_emissao)
        d.setDate(d.getDate() + 30)
        vencimentoData.value = d.toISOString().split('T')[0]!
      } catch {
        vencimentoData.value = new Date().toISOString().split('T')[0]!
      }
    }

    const res = await checkEntities({
      fornecedor_nome: fornecedor?.nome ?? null,
      fornecedor_cnpj: fornecedor?.cnpj ?? null,
      faturado_nome: destinatario?.nome ?? null,
      faturado_cpf_cnpj: destinatario?.cnpj_cpf ?? null,
      despesa_descricao: despesaDescricao.value,
      tipo_classificacao: 'DESPESA',
    })

    checkResult.value = res
  } catch (err) {
    console.error('Erro ao checar entidades no banco:', err)
  } finally {
    isChecking.value = false
  }
}

// Executa o lançamento automático no banco de dados (Passos 1 a 5 do PDF)
async function handleLaunch() {
  if (!store.extractedData) return

  isLaunching.value = true
  launchError.value = null

  try {
    const fornecedor = store.extractedData.fornecedor
    const destinatario = store.extractedData.destinatario
    const valorNota = store.extractedData.totais?.valor_total_nota ?? 0

    const res = await launchMovement({
      // Fornecedor
      fornecedor_id: checkResult.value?.fornecedor.id ?? null,
      fornecedor_nome: fornecedor?.nome,
      fornecedor_cnpj: fornecedor?.cnpj,
      fornecedor_ie: fornecedor?.ie,
      fornecedor_endereco: fornecedor?.endereco,

      // Faturado
      faturado_id: checkResult.value?.faturado.id ?? null,
      faturado_nome: destinatario?.nome ?? 'CONSUMIDOR FINAL',
      faturado_cpf_cnpj: destinatario?.cnpj_cpf ?? null,

      // Despesa
      classificacao_id: checkResult.value?.despesa.id ?? null,
      classificacao_descricao: despesaDescricao.value,
      classificacao_tipo: 'DESPESA',

      // Movimento Contas (APAGAR)
      tipo_movimento: 'APAGAR',
      numero_documento: store.extractedData.numero,
      serie: store.extractedData.serie,
      chave_acesso: store.extractedData.chave_acesso,
      data_emissao: store.extractedData.data_emissao,
      valor_total: valorNota,
      observacao: `Importação automática NF-e nº ${store.extractedData.numero}`,

      // Parcela Contas
      parcelas: [
        {
          identificacao: identificacaoParcela.value,
          numero_parcela: 1,
          data_vencimento: vencimentoData.value,
          valor: valorNota,
          status: 'PENDENTE' as const,
        },
      ],
    })

    launchResult.value = res
    // Atualiza checagem após criação
    await runAnalysis()
  } catch (err) {
    launchError.value = err instanceof Error ? err.message : 'Erro ao lançar movimento no banco'
  } finally {
    isLaunching.value = false
  }
}

// Dispara análise automaticamente quando a nota for extraída
watch(
  () => store.extractedData,
  (newData) => {
    if (newData) {
      runAnalysis()
    } else {
      checkResult.value = null
      launchResult.value = null
    }
  },
  { immediate: true },
)

onMounted(() => {
  loadClassificacoes()
})

function formatCurrency(val: number | null | undefined): string {
  if (val === null || val === undefined) return 'R$ 0,00'
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val)
}
</script>

<template>
  <div v-if="store.hasData" class="analysis-container">
    <!-- Header da Etapa -->
    <div class="analysis-header">
      <div class="step-indicator">
        <span class="step-badge">2ª ETAPA</span>
        <span class="step-title">Análise dos Dados & Consulta ao Banco de Dados</span>
      </div>
      <button class="refresh-btn" :disabled="isChecking" @click="runAnalysis">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="btn-icon" :class="{ rotating: isChecking }">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        {{ isChecking ? 'Consultando...' : 'Reconsultar Banco' }}
      </button>
    </div>

    <!-- Cards de Consulta: Exatamente como pedido no PDF -->
    <div v-if="checkResult" class="query-results-grid">
      <!-- 1. FORNECEDOR -->
      <div class="query-card" :class="{ 'query-card--exists': checkResult.fornecedor.existe, 'query-card--not-exists': !checkResult.fornecedor.existe }">
        <div class="query-card__header">
          <span class="entity-tag">FORNECEDOR</span>
          <span class="status-pill" :class="checkResult.fornecedor.existe ? 'status-pill--success' : 'status-pill--warn'">
            {{ checkResult.fornecedor.existe ? `EXISTE – ID: ${checkResult.fornecedor.id}` : 'NÃO EXISTE' }}
          </span>
        </div>
        <div class="query-card__body">
          <h4 class="entity-name">{{ checkResult.fornecedor.nome_razao_social || 'Nome não identificado' }}</h4>
          <p class="entity-doc">
            <strong>CNPJ:</strong> {{ checkResult.fornecedor.documento || 'Não informado' }}
          </p>
          <div v-if="!checkResult.fornecedor.existe" class="card-action-hint">
            ⚡ Será cadastrado automaticamente como Pessoa (Tipo: <code>CLIENTE-FORNECEDOR</code>)
          </div>
        </div>
      </div>

      <!-- 2. FATURADO -->
      <div class="query-card" :class="{ 'query-card--exists': checkResult.faturado.existe, 'query-card--not-exists': !checkResult.faturado.existe }">
        <div class="query-card__header">
          <span class="entity-tag">FATURADO</span>
          <span class="status-pill" :class="checkResult.faturado.existe ? 'status-pill--success' : 'status-pill--warn'">
            {{ checkResult.faturado.existe ? `EXISTE – ID: ${checkResult.faturado.id}` : 'NÃO EXISTE' }}
          </span>
        </div>
        <div class="query-card__body">
          <h4 class="entity-name">{{ checkResult.faturado.nome_razao_social || 'Consumidor / Destinatário' }}</h4>
          <p class="entity-doc">
            <strong>CPF/CNPJ:</strong> {{ checkResult.faturado.documento || 'Não informado' }}
          </p>
          <div v-if="!checkResult.faturado.existe" class="card-action-hint">
            ⚡ Será cadastrado automaticamente como Pessoa (Tipo: <code>FATURADO</code>)
          </div>
        </div>
      </div>

      <!-- 3. DESPESA / CLASSIFICAÇÃO -->
      <div class="query-card" :class="{ 'query-card--exists': checkResult.despesa.existe, 'query-card--not-exists': !checkResult.despesa.existe }">
        <div class="query-card__header">
          <span class="entity-tag">DESPESA</span>
          <span class="status-pill" :class="checkResult.despesa.existe ? 'status-pill--success' : 'status-pill--warn'">
            {{ checkResult.despesa.existe ? `EXISTE – ID: ${checkResult.despesa.id}` : 'NÃO EXISTE' }}
          </span>
        </div>
        <div class="query-card__body">
          <h4 class="entity-name">{{ despesaDescricao }}</h4>
          <div class="classif-picker">
            <label class="input-label">Alterar Classificação da Despesa:</label>
            <input
              v-model="despesaDescricao"
              type="text"
              class="text-input"
              list="classificacoes-list"
              placeholder="Digite ou escolha uma classificação"
              @change="runAnalysis"
            />
            <datalist id="classificacoes-list">
              <option v-for="c in availableClassificacoes" :key="c.id" :value="c.descricao" />
            </datalist>
          </div>
          <div v-if="!checkResult.despesa.existe" class="card-action-hint">
            ⚡ Será cadastrada automaticamente como Classificação (Tipo: <code>DESPESA</code>)
          </div>
        </div>
      </div>
    </div>

    <!-- Parâmetros de Movimento e Parcela -->
    <div class="movement-settings-card">
      <h3 class="settings-title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="settings-icon">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        Entidades e Registro a Serem Lançados
      </h3>

      <div class="settings-grid">
        <div class="field-group">
          <label class="field-label">Tipo do Movimento</label>
          <div class="fixed-badge">APAGAR (Contas a Pagar)</div>
        </div>

        <div class="field-group">
          <label class="field-label">Identificação da Parcela</label>
          <input v-model="identificacaoParcela" type="text" class="text-input" placeholder="Ex: ÚNICA" />
        </div>

        <div class="field-group">
          <label class="field-label">Data de Vencimento</label>
          <input v-model="vencimentoData" type="date" class="text-input" />
        </div>

        <div class="field-group">
          <label class="field-label">Valor Total</label>
          <div class="fixed-badge highlight">
            {{ formatCurrency(store.extractedData?.totais?.valor_total_nota) }}
          </div>
        </div>
      </div>

      <!-- Erro de lançamento se houver -->
      <div v-if="launchError" class="launch-error">
        <span>⚠️ {{ launchError }}</span>
      </div>

      <!-- Botão de Ação Principal -->
      <div class="action-footer">
        <button
          id="launch-movement-btn"
          class="launch-btn"
          :disabled="isLaunching || isChecking"
          @click="handleLaunch"
        >
          <svg v-if="!isLaunching" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="btn-icon">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" class="btn-icon rotating">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {{ isLaunching ? 'Lançando no Banco de Dados...' : 'Lançar Registro no Banco de Dados' }}
        </button>
      </div>
    </div>

    <!-- Banner de Sucesso pós Lançamento -->
    <div v-if="launchResult" class="success-banner">
      <div class="success-header">
        <div class="success-icon-wrap">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="success-icon">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div>
          <h4 class="success-title">Registro Lançado com Sucesso!</h4>
          <p class="success-sub">Todas as entidades foram criadas/vinculadas no banco de dados.</p>
        </div>
      </div>

      <div class="success-details-grid">
        <div class="success-item">
          <span class="item-lbl">MOVIMENTO CONTAS</span>
          <span class="item-val">ID: {{ launchResult.movimento_id }} (Tipo APAGAR)</span>
        </div>
        <div class="success-item">
          <span class="item-lbl">PARCELA CONTAS</span>
          <span class="item-val">{{ launchResult.total_parcelas }}x ({{ identificacaoParcela }}) - {{ formatCurrency(launchResult.valor_total) }}</span>
        </div>
        <div class="success-item">
          <span class="item-lbl">FORNECEDOR (PESSOA)</span>
          <span class="item-val">ID: {{ launchResult.fornecedor.id }} — {{ launchResult.fornecedor.nome_razao_social }}</span>
        </div>
        <div class="success-item">
          <span class="item-lbl">FATURADO (PESSOA)</span>
          <span class="item-val">ID: {{ launchResult.faturado.id }} — {{ launchResult.faturado.nome_razao_social }}</span>
        </div>
        <div class="success-item">
          <span class="item-lbl">CLASSIFICAÇÃO (DESPESA)</span>
          <span class="item-val">ID: {{ launchResult.despesa.id }} — {{ launchResult.despesa.nome_razao_social }}</span>
        </div>
      </div>

      <div class="success-actions">
        <RouterLink to="/movimentos" class="link-btn">
          Ver no Contas a Pagar →
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.analysis-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 1rem;
  animation: fade-in 0.3s ease;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Header */
.analysis-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.step-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.step-badge {
  background: var(--color-accent-gradient);
  color: #fff;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.65rem;
  border-radius: var(--radius-sm);
  letter-spacing: 0.05em;
}

.step-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--color-surface-hover);
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  font-size: 0.8rem;
  font-weight: 500;
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  color: var(--color-text-primary);
  border-color: var(--color-accent);
}

.btn-icon {
  width: 0.95rem;
  height: 0.95rem;
}

.rotating {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Query Grid */
.query-results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.query-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  transition: all 0.2s;
  box-shadow: var(--shadow-sm);
}

.query-card--exists {
  border-color: rgba(52, 211, 153, 0.35);
  background: linear-gradient(180deg, rgba(52, 211, 153, 0.03) 0%, var(--color-surface) 100%);
}

.query-card--not-exists {
  border-color: rgba(251, 191, 36, 0.35);
  background: linear-gradient(180deg, rgba(251, 191, 36, 0.03) 0%, var(--color-surface) 100%);
}

.query-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.entity-tag {
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: var(--color-text-muted);
}

.status-pill {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 100px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.status-pill--success {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
  border: 1px solid rgba(52, 211, 153, 0.3);
}

.status-pill--warn {
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.3);
}

.entity-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 0.25rem;
}

.entity-doc {
  font-size: 0.825rem;
  color: var(--color-text-muted);
}

.card-action-hint {
  font-size: 0.72rem;
  color: #fbbf24;
  background: rgba(251, 191, 36, 0.08);
  border-radius: var(--radius-sm);
  padding: 0.4rem 0.6rem;
  margin-top: 0.5rem;
}

.card-action-hint code {
  font-weight: 700;
  color: #fef08a;
}

.classif-picker {
  margin-top: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.input-label {
  font-size: 0.72rem;
  color: var(--color-text-muted);
}

.text-input {
  background: var(--color-surface-hover);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  border-radius: var(--radius-sm);
  padding: 0.4rem 0.6rem;
  font-size: 0.825rem;
  outline: none;
  transition: border-color 0.2s;
}

.text-input:focus {
  border-color: var(--color-accent);
}

/* Movement Settings */
.movement-settings-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.settings-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.settings-icon {
  width: 1.1rem;
  height: 1.1rem;
  color: var(--color-accent);
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.field-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
}

.fixed-badge {
  background: var(--color-surface-hover);
  border: 1px solid var(--color-border);
  padding: 0.45rem 0.65rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.fixed-badge.highlight {
  color: var(--color-accent-light);
  font-size: 1rem;
}

.launch-error {
  background: var(--color-error-subtle);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: var(--color-error);
  padding: 0.75rem;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
}

.action-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.5rem;
}

.launch-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--color-accent-gradient);
  color: #fff;
  border: none;
  font-size: 0.9rem;
  font-weight: 600;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
  transition: all 0.2s;
}

.launch-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45);
}

.launch-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Success Banner */
.success-banner {
  background: rgba(52, 211, 153, 0.08);
  border: 1px solid rgba(52, 211, 153, 0.35);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  animation: slide-up 0.3s ease;
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.success-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.success-icon-wrap {
  width: 2.2rem;
  height: 2.2rem;
  background: rgba(52, 211, 153, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.success-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: #34d399;
}

.success-title {
  font-size: 1rem;
  font-weight: 700;
  color: #34d399;
  margin: 0;
}

.success-sub {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  margin: 0;
}

.success-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1rem;
}

.success-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.item-lbl {
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--color-text-muted);
  letter-spacing: 0.04em;
}

.item-val {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.success-actions {
  display: flex;
  justify-content: flex-end;
}

.link-btn {
  display: inline-flex;
  align-items: center;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.35);
  color: #a5b4fc;
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  text-decoration: none;
  transition: all 0.2s;
}

.link-btn:hover {
  background: rgba(99, 102, 241, 0.25);
  color: #fff;
}
</style>
