<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  getMovimentos,
  createMovimento,
  inativarMovimento,
  reativarMovimento,
  pagarParcela,
  getPessoas,
  getClassificacoes,
} from '@/services/api'
import type {
  MovimentoContas,
  MovimentoCreate,
  Pessoa,
  Classificacao,
  TipoMovimento,
} from '@/types/models'

const movimentos = ref<MovimentoContas[]>([])
const isLoading = ref(false)
const errorMessage = ref<string | null>(null)
const successMessage = ref<string | null>(null)

// Filtros
const selectedTipo = ref<TipoMovimento>('APAGAR')
const statusFiltro = ref<string>('')
const statusAtivo = ref<string>('todos')

// Modal de Criação Manual
const isModalOpen = ref(false)
const pessoasFornecedores = ref<Pessoa[]>([])
const pessoasFaturados = ref<Pessoa[]>([])
const classificacoesDisponiveis = ref<Classificacao[]>([])

// Form simples para criação manual
const form = ref<{
  tipo: TipoMovimento
  fornecedor_id: number | null
  faturado_id: number | null
  numero_documento: string
  data_emissao: string
  valor_total: number
  classificacao_id: number | null
  data_vencimento: string
  identificacao_parcela: string
  observacao: string
}>({
  tipo: 'APAGAR' as TipoMovimento,
  fornecedor_id: null,
  faturado_id: null,
  numero_documento: '',
  data_emissao: new Date().toISOString().split('T')[0]!,
  valor_total: 0,
  classificacao_id: null,
  data_vencimento: new Date().toISOString().split('T')[0]!,
  identificacao_parcela: 'ÚNICA',
  observacao: '',
})

async function fetchMovimentos() {
  isLoading.value = true
  errorMessage.value = null
  try {
    const params: { tipo?: string; status?: string; ativo?: boolean } = {}
    if (selectedTipo.value) params.tipo = selectedTipo.value
    if (statusFiltro.value) params.status = statusFiltro.value
    if (statusAtivo.value === 'ativos') params.ativo = true
    if (statusAtivo.value === 'inativos') params.ativo = false

    movimentos.value = await getMovimentos(params)
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro ao buscar movimentos'
  } finally {
    isLoading.value = false
  }
}

async function loadDependencies() {
  try {
    pessoasFornecedores.value = await getPessoas({ tipo: 'CLIENTE-FORNECEDOR', ativo: true })
    pessoasFaturados.value = await getPessoas({ tipo: 'FATURADO', ativo: true })
    classificacoesDisponiveis.value = await getClassificacoes({ tipo: 'DESPESA', ativo: true })
  } catch (err) {
    console.error('Erro ao carregar pessoas/classificações:', err)
  }
}

function openCreateModal() {
  form.value = {
    tipo: selectedTipo.value,
    fornecedor_id: pessoasFornecedores.value[0]?.id ?? null,
    faturado_id: pessoasFaturados.value[0]?.id ?? null,
    numero_documento: '',
    data_emissao: new Date().toISOString().split('T')[0]!,
    valor_total: 0,
    classificacao_id: classificacoesDisponiveis.value[0]?.id ?? null,
    data_vencimento: new Date().toISOString().split('T')[0]!,
    identificacao_parcela: 'ÚNICA',
    observacao: '',
  }
  isModalOpen.value = true
}

async function handleSave() {
  if (form.value.valor_total <= 0) {
    alert('O valor total deve ser maior que zero!')
    return
  }

  isLoading.value = true
  try {
    const payload: MovimentoCreate = {
      tipo: form.value.tipo,
      fornecedor_id: form.value.fornecedor_id,
      faturado_id: form.value.faturado_id,
      numero_documento: form.value.numero_documento || null,
      data_emissao: form.value.data_emissao || null,
      valor_total: form.value.valor_total,
      observacao: form.value.observacao || null,
      classificacoes: form.value.classificacao_id
        ? [{ classificacao_id: form.value.classificacao_id, valor: form.value.valor_total }]
        : [],
      parcelas: [
        {
          identificacao: form.value.identificacao_parcela || 'ÚNICA',
          numero_parcela: 1,
          data_vencimento: form.value.data_vencimento,
          valor: form.value.valor_total,
          status: 'PENDENTE',
        },
      ],
    }

    await createMovimento(payload)
    showNotification('Movimento registrado com sucesso!')
    isModalOpen.value = false
    await fetchMovimentos()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro ao registrar movimento'
  } finally {
    isLoading.value = false
  }
}

async function handleInativar(m: MovimentoContas) {
  if (!confirm(`Deseja inativar este movimento de contas (ID: ${m.id})?`)) return
  try {
    await inativarMovimento(m.id)
    showNotification(`Movimento #${m.id} inativado.`)
    await fetchMovimentos()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro ao inativar'
  }
}

async function handleReativar(m: MovimentoContas) {
  try {
    await reativarMovimento(m.id)
    showNotification(`Movimento #${m.id} reativado!`)
    await fetchMovimentos()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro ao reativar'
  }
}

async function handlePagarParcela(movimentoId: number, parcelaId: number) {
  try {
    await pagarParcela(movimentoId, parcelaId)
    showNotification(`Parcela marcada como PAGA!`)
    await fetchMovimentos()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro ao pagar parcela'
  }
}

function showNotification(msg: string) {
  successMessage.value = msg
  setTimeout(() => (successMessage.value = null), 4000)
}

function formatCurrency(val: number | null | undefined): string {
  if (val === null || val === undefined) return 'R$ 0,00'
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val)
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '—'
  const [y, m, d] = dateStr.split('-')
  return `${d}/${m}/${y}`
}

onMounted(() => {
  fetchMovimentos()
  loadDependencies()
})
</script>

<template>
  <div class="view-page">
    <div class="view-page__inner">
      <!-- Cabeçalho -->
      <div class="page-header">
        <div>
          <span class="page-badge">Módulo Financeiro</span>
          <h1 class="page-title">Movimento de Contas & Parcelas</h1>
          <p class="page-desc">Registros de Contas a Pagar e a Receber com classificação por despesa/receita e gestão de parcelas.</p>
        </div>
        <button class="primary-btn" @click="openCreateModal">
          <span>+</span> Novo Lançamento
        </button>
      </div>

      <!-- Feedback -->
      <div v-if="successMessage" class="banner banner--success">
        ✓ {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="banner banner--error">
        ⚠️ {{ errorMessage }}
      </div>

      <!-- Toggle de Tipo: Contas a Pagar vs Contas a Receber -->
      <div class="type-toggle-bar">
        <button
          class="type-btn"
          :class="{ 'type-btn--active': selectedTipo === 'APAGAR' }"
          @click="selectedTipo = 'APAGAR'; fetchMovimentos()"
        >
          💳 Contas a Pagar (Despesas)
        </button>
        <button
          class="type-btn"
          :class="{ 'type-btn--active': selectedTipo === 'ARECEBER' }"
          @click="selectedTipo = 'ARECEBER'; fetchMovimentos()"
        >
          💰 Contas a Receber (Receitas)
        </button>
      </div>

      <!-- Barra de Filtros -->
      <div class="filters-bar">
        <div class="filter-group">
          <label>Status Movimento:</label>
          <select v-model="statusFiltro" class="select-input" @change="fetchMovimentos">
            <option value="">Todos</option>
            <option value="PENDENTE">PENDENTE</option>
            <option value="PAGO">PAGO</option>
            <option value="RECEBIDO">RECEBIDO</option>
            <option value="CANCELADO">CANCELADO</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Ativo/Inativo:</label>
          <select v-model="statusAtivo" class="select-input" @change="fetchMovimentos">
            <option value="todos">Todos</option>
            <option value="ativos">Apenas Ativos</option>
            <option value="inativos">Apenas Inativos</option>
          </select>
        </div>

        <button class="filter-btn" @click="fetchMovimentos">
          Atualizar
        </button>
      </div>

      <!-- Lista de Movimentos -->
      <div class="movements-container">
        <div v-if="isLoading" class="loading-state">
          Carregando lançamentos...
        </div>
        <div v-else-if="movimentos.length === 0" class="empty-state">
          Nenhum movimento registrado com os filtros selecionados.
        </div>
        <div v-else class="movements-list">
          <div
            v-for="m in movimentos"
            :key="m.id"
            class="movement-card"
            :class="{ 'movement-card--inactive': !m.ativo }"
          >
            <!-- Topo do Card -->
            <div class="movement-card__header">
              <div class="header-left">
                <span class="movement-id">#{{ m.id }}</span>
                <span class="movement-doc" v-if="m.numero_documento">
                  Doc / NF: <strong>{{ m.numero_documento }}</strong>
                </span>
                <span class="date-badge">Emissão: {{ formatDate(m.data_emissao) }}</span>
              </div>
              <div class="header-right">
                <span class="value-highlight">{{ formatCurrency(m.valor_total) }}</span>
                <span class="status-pill" :class="m.status === 'PAGO' || m.status === 'RECEBIDO' ? 'status-pill--success' : 'status-pill--pending'">
                  {{ m.status }}
                </span>
                <button
                  v-if="m.ativo"
                  class="inactivate-btn"
                  title="Inativar movimento"
                  @click="handleInativar(m)"
                >
                  Inativar
                </button>
                <button
                  v-else
                  class="reactivate-btn"
                  title="Reativar movimento"
                  @click="handleReativar(m)"
                >
                  Reativar
                </button>
              </div>
            </div>

            <!-- Dados das Entidades Vinculadas -->
            <div class="entities-info-grid">
              <!-- Fornecedor ou Cliente -->
              <div class="info-block" v-if="m.fornecedor">
                <span class="info-label">FORNECEDOR (PESSOA ID: {{ m.fornecedor.id }})</span>
                <span class="info-val font-semibold">{{ m.fornecedor.razao_social }}</span>
                <span class="info-sub" v-if="m.fornecedor.cpf_cnpj">CNPJ: {{ m.fornecedor.cpf_cnpj }}</span>
              </div>
              <div class="info-block" v-else-if="m.cliente">
                <span class="info-label">CLIENTE (PESSOA ID: {{ m.cliente.id }})</span>
                <span class="info-val font-semibold">{{ m.cliente.razao_social }}</span>
              </div>

              <!-- Faturado -->
              <div class="info-block" v-if="m.faturado">
                <span class="info-label">FATURADO (PESSOA ID: {{ m.faturado.id }})</span>
                <span class="info-val font-semibold">{{ m.faturado.razao_social }}</span>
                <span class="info-sub" v-if="m.faturado.cpf_cnpj">CPF/CNPJ: {{ m.faturado.cpf_cnpj }}</span>
              </div>

              <!-- Classificação -->
              <div class="info-block">
                <span class="info-label">CLASSIFICAÇÃO / DESPESA</span>
                <div v-if="m.classificacoes && m.classificacoes.length > 0" class="classif-tags">
                  <span
                    v-for="mc in m.classificacoes"
                    :key="mc.id"
                    class="classif-tag"
                  >
                    🏷️ {{ mc.classificacao?.descricao }} ({{ formatCurrency(mc.valor) }})
                  </span>
                </div>
                <span v-else class="info-sub">Sem classificação</span>
              </div>
            </div>

            <!-- Parcelas do Movimento -->
            <div class="parcels-section">
              <h5 class="parcels-title">
                <span>🗓️ Parcelas ({{ m.parcelas?.length || 0 }})</span>
              </h5>
              <div class="parcels-grid">
                <div
                  v-for="p in m.parcelas"
                  :key="p.id"
                  class="parcel-card"
                  :class="{ 'parcel-card--paid': p.status === 'PAGO' }"
                >
                  <div class="parcel-info">
                    <span class="parcel-ident">{{ p.identificacao }}</span>
                    <span class="parcel-due">Venc: <strong>{{ formatDate(p.data_vencimento) }}</strong></span>
                    <span class="parcel-value">{{ formatCurrency(p.valor) }}</span>
                  </div>
                  <div class="parcel-status-wrap">
                    <span class="status-pill" :class="p.status === 'PAGO' ? 'status-pill--success' : 'status-pill--warn'">
                      {{ p.status }}
                    </span>
                    <button
                      v-if="p.status === 'PENDENTE'"
                      class="pay-btn"
                      @click="handlePagarParcela(m.id, p.id)"
                    >
                      ✓ Marcar Pago
                    </button>
                    <span v-else-if="p.data_pagamento" class="paid-date">
                      Pago em {{ formatDate(p.data_pagamento) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Criação Manual -->
    <div v-if="isModalOpen" class="modal-backdrop" @click.self="isModalOpen = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3>Novo Lançamento — {{ form.tipo === 'APAGAR' ? 'Contas a Pagar' : 'Contas a Receber' }}</h3>
          <button class="modal-close" @click="isModalOpen = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-field">
              <label>Fornecedor (Pessoa) *</label>
              <select v-model="form.fornecedor_id" class="select-input">
                <option v-for="p in pessoasFornecedores" :key="p.id" :value="p.id">
                  {{ p.razao_social }} (ID: {{ p.id }})
                </option>
              </select>
            </div>

            <div class="form-field">
              <label>Faturado (Pessoa) *</label>
              <select v-model="form.faturado_id" class="select-input">
                <option v-for="p in pessoasFaturados" :key="p.id" :value="p.id">
                  {{ p.razao_social }} (ID: {{ p.id }})
                </option>
              </select>
            </div>

            <div class="form-field">
              <label>Classificação (Tipo de Despesa) *</label>
              <select v-model="form.classificacao_id" class="select-input">
                <option v-for="c in classificacoesDisponiveis" :key="c.id" :value="c.id">
                  {{ c.descricao }}
                </option>
              </select>
            </div>

            <div class="form-field">
              <label>Nº do Documento / Nota</label>
              <input v-model="form.numero_documento" type="text" class="text-input" placeholder="000123" />
            </div>

            <div class="form-field">
              <label>Data de Emissão</label>
              <input v-model="form.data_emissao" type="date" class="text-input" />
            </div>

            <div class="form-field">
              <label>Valor Total (R$) *</label>
              <input v-model.number="form.valor_total" type="number" step="0.01" class="text-input" />
            </div>

            <div class="form-field">
              <label>Identificação da Parcela</label>
              <input v-model="form.identificacao_parcela" type="text" class="text-input" placeholder="ÚNICA" />
            </div>

            <div class="form-field">
              <label>Vencimento da Parcela</label>
              <input v-model="form.data_vencimento" type="date" class="text-input" />
            </div>

            <div class="form-field form-field--full">
              <label>Observação</label>
              <input v-model="form.observacao" type="text" class="text-input" placeholder="Observações do lançamento..." />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="isModalOpen = false">Cancelar</button>
          <button class="save-btn" :disabled="isLoading" @click="handleSave">
            {{ isLoading ? 'Salvando...' : 'Registrar Movimento' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.view-page {
  padding: 2rem 1.25rem 4rem;
  min-height: calc(100vh - 60px);
}

.view-page__inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-badge {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 600;
  color: #a5b4fc;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.25);
  padding: 0.2rem 0.6rem;
  border-radius: 100px;
  margin-bottom: 0.4rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--color-text-primary);
  margin: 0;
}

.page-desc {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin: 0.25rem 0 0;
}

.primary-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--color-accent-gradient);
  color: #fff;
  border: none;
  font-weight: 600;
  font-size: 0.875rem;
  padding: 0.6rem 1.25rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
  transition: all 0.2s;
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45);
}

.banner {
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
}

.banner--success {
  background: rgba(52, 211, 153, 0.1);
  border: 1px solid rgba(52, 211, 153, 0.3);
  color: #34d399;
}

.banner--error {
  background: var(--color-error-subtle);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: var(--color-error);
}

/* Toggle Bar */
.type-toggle-bar {
  display: flex;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 4px;
  gap: 4px;
}

.type-btn {
  flex: 1;
  padding: 0.75rem 1.25rem;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  font-size: 0.9rem;
  font-weight: 600;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.type-btn--active {
  background: var(--color-surface-hover);
  color: var(--color-text-primary);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
}

/* Filters */
.filters-bar {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 0.85rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.825rem;
  color: var(--color-text-muted);
}

.select-input, .text-input {
  background: var(--color-surface-hover);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  border-radius: var(--radius-md);
  padding: 0.45rem 0.75rem;
  font-size: 0.85rem;
  outline: none;
  font-family: inherit;
}

.filter-btn {
  background: var(--color-surface-hover);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  font-size: 0.825rem;
  font-weight: 500;
  padding: 0.45rem 1rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  margin-left: auto;
}

/* Movements List */
.movements-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.movement-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: var(--shadow-sm);
}

.movement-card--inactive {
  opacity: 0.6;
  background: rgba(0, 0, 0, 0.2);
}

.movement-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.movement-id {
  font-weight: 800;
  font-size: 0.9rem;
  color: #a5b4fc;
}

.movement-doc {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.movement-doc strong {
  color: var(--color-text-primary);
}

.date-badge {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  background: var(--color-surface-hover);
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-sm);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.value-highlight {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--color-accent-light);
}

.status-pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 100px;
  text-transform: uppercase;
}

.status-pill--success {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
}

.status-pill--pending {
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
}

.status-pill--warn {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

.inactivate-btn {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #f87171;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.reactivate-btn {
  background: rgba(52, 211, 153, 0.1);
  border: 1px solid rgba(52, 211, 153, 0.3);
  color: #34d399;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

/* Entities Info */
.entities-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.info-block {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.info-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--color-text-muted);
  letter-spacing: 0.05em;
}

.info-val {
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.info-sub {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.classif-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.classif-tag {
  background: rgba(99, 102, 241, 0.1);
  color: #a5b4fc;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-sm);
}

/* Parcels */
.parcels-section {
  background: var(--color-surface-hover);
  border-radius: var(--radius-md);
  padding: 0.85rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.parcels-title {
  margin: 0;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.parcels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 0.75rem;
}

.parcel-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.65rem 0.85rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.parcel-card--paid {
  border-color: rgba(52, 211, 153, 0.3);
}

.parcel-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.parcel-ident {
  font-size: 0.72rem;
  font-weight: 700;
  color: #a5b4fc;
}

.parcel-due {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.parcel-value {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.parcel-status-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.3rem;
}

.pay-btn {
  background: rgba(52, 211, 153, 0.15);
  border: 1px solid rgba(52, 211, 153, 0.35);
  color: #34d399;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
}

.pay-btn:hover {
  background: rgba(52, 211, 153, 0.25);
}

.paid-date {
  font-size: 0.7rem;
  color: #34d399;
}

.loading-state, .empty-state {
  padding: 3rem 1rem;
  text-align: center;
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
}

.modal-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 600px;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--color-text-primary);
}

.modal-close {
  background: none;
  border: none;
  color: var(--color-text-muted);
  font-size: 1.1rem;
  cursor: pointer;
}

.modal-body {
  padding: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-field--full {
  grid-column: 1 / -1;
}

.form-field label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.cancel-btn {
  background: var(--color-surface-hover);
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  cursor: pointer;
}

.save-btn {
  background: var(--color-accent-gradient);
  border: none;
  color: #fff;
  font-weight: 600;
  padding: 0.5rem 1.25rem;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  cursor: pointer;
}
</style>
