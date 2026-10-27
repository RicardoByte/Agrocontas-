<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
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
  tipo: 'APAGAR',
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

// Estatísticas Computadas
const totalGeral = computed(() =>
  movimentos.value.reduce((acc, m) => acc + (m.valor_total || 0), 0)
)
const totalPago = computed(() =>
  movimentos.value
    .filter((m) => m.status === 'PAGO' || m.status === 'RECEBIDO')
    .reduce((acc, m) => acc + (m.valor_total || 0), 0)
)
const totalPendente = computed(() =>
  movimentos.value
    .filter((m) => m.status === 'PENDENTE')
    .reduce((acc, m) => acc + (m.valor_total || 0), 0)
)

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
      <!-- ── Cabeçalho ─────────────────────────────────────────── -->
      <div class="page-header">
        <div>
          <span class="page-badge">Módulo Financeiro</span>
          <h1 class="page-title">Movimento de Contas &amp; Parcelas</h1>
          <p class="page-desc">
            Registros de Contas a Pagar e a Receber com classificação contábil, centro de custo e gestão de vencimentos.
          </p>
        </div>
        <button class="primary-btn" @click="openCreateModal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
            <path stroke-linecap="round" stroke-width="2.5" d="M12 5v14M5 12h14" />
          </svg>
          Novo Lançamento
        </button>
      </div>

      <!-- ── Alertas ───────────────────────────────────────────── -->
      <div v-if="successMessage" class="alert alert-success">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="15" height="15" style="flex-shrink:0">
          <path stroke-linecap="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
        </svg>
        {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="alert alert-error">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="15" height="15" style="flex-shrink:0;margin-top:1px">
          <path stroke-linecap="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
        {{ errorMessage }}
      </div>

      <!-- ── Cards de Métricas / Resumo ───────────────────────── -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-card__icon stat-card__icon--accent">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="18" height="18">
              <path stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <span class="stat-card__label">Volume Total</span>
            <div class="stat-card__val">{{ formatCurrency(totalGeral) }}</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-card__icon stat-card__icon--warn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="18" height="18">
              <path stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <span class="stat-card__label">Pendente / Em Aberto</span>
            <div class="stat-card__val stat-card__val--warn">{{ formatCurrency(totalPendente) }}</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-card__icon stat-card__icon--success">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="18" height="18">
              <path stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div>
            <span class="stat-card__label">Liquidado</span>
            <div class="stat-card__val stat-card__val--success">{{ formatCurrency(totalPago) }}</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-card__icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="18" height="18">
              <path stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <div>
            <span class="stat-card__label">Lançamentos</span>
            <div class="stat-card__val">{{ movimentos.length }}</div>
          </div>
        </div>
      </div>

      <!-- ── Filtros e Navegação por Tipo ─────────────────────── -->
      <div class="filters-card">
        <div class="type-toggle-pills">
          <button
            class="type-pill"
            :class="{ 'type-pill--active': selectedTipo === 'APAGAR' }"
            @click="selectedTipo = 'APAGAR'; fetchMovimentos()"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
              <path stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            Contas a Pagar (Despesas)
          </button>
          <button
            class="type-pill"
            :class="{ 'type-pill--active': selectedTipo === 'ARECEBER' }"
            @click="selectedTipo = 'ARECEBER'; fetchMovimentos()"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
              <path stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Contas a Receber (Receitas)
          </button>
        </div>

        <div class="filters-divider" />

        <div class="filter-group">
          <label class="filter-label">Status</label>
          <select v-model="statusFiltro" class="form-select" @change="fetchMovimentos">
            <option value="">Todos os status</option>
            <option value="PENDENTE">PENDENTE</option>
            <option value="PAGO">PAGO</option>
            <option value="RECEBIDO">RECEBIDO</option>
            <option value="CANCELADO">CANCELADO</option>
          </select>
        </div>

        <div class="filter-group">
          <label class="filter-label">Ativo / Inativo</label>
          <select v-model="statusAtivo" class="form-select" @change="fetchMovimentos">
            <option value="todos">Todos</option>
            <option value="ativos">Apenas Ativos</option>
            <option value="inativos">Apenas Inativos</option>
          </select>
        </div>

        <button class="filter-btn" @click="fetchMovimentos">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="13" height="13">
            <path stroke-linecap="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          Atualizar
        </button>
      </div>

      <!-- ── Lista de Movimentos ───────────────────────────────── -->
      <div class="movements-container">
        <div v-if="isLoading" class="state-box">
          <span class="state-icon">⏳</span>
          Carregando lançamentos...
        </div>
        <div v-else-if="movimentos.length === 0" class="state-box">
          <span class="state-icon">🔍</span>
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
                <span v-if="m.numero_documento" class="movement-doc">
                  Doc / NF: <strong>{{ m.numero_documento }}</strong>
                </span>
                <span class="date-badge">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="11" height="11">
                    <rect x="3" y="4" width="18" height="18" rx="2" stroke-width="2"/>
                    <path stroke-linecap="round" stroke-width="2" d="M16 2v4M8 2v4M3 10h18"/>
                  </svg>
                  Emissão: {{ formatDate(m.data_emissao) }}
                </span>
              </div>

              <div class="header-right">
                <span class="value-highlight">{{ formatCurrency(m.valor_total) }}</span>
                <span
                  class="badge"
                  :class="m.status === 'PAGO' || m.status === 'RECEBIDO' ? 'badge-success' : 'badge-warning'"
                >
                  {{ m.status }}
                </span>
                <button
                  v-if="m.ativo"
                  class="action-pill action-pill--danger"
                  title="Inativar movimento"
                  @click="handleInativar(m)"
                >
                  Inativar
                </button>
                <button
                  v-else
                  class="action-pill action-pill--success"
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
              <div v-if="m.fornecedor" class="info-block">
                <span class="info-label">FORNECEDOR (PESSOA ID: {{ m.fornecedor.id }})</span>
                <span class="info-val font-semibold">{{ m.fornecedor.razao_social }}</span>
                <span v-if="m.fornecedor.cpf_cnpj" class="info-sub font-mono">CNPJ: {{ m.fornecedor.cpf_cnpj }}</span>
              </div>
              <div v-else-if="m.cliente" class="info-block">
                <span class="info-label">CLIENTE (PESSOA ID: {{ m.cliente.id }})</span>
                <span class="info-val font-semibold">{{ m.cliente.razao_social }}</span>
              </div>

              <!-- Faturado -->
              <div v-if="m.faturado" class="info-block">
                <span class="info-label">FATURADO (PESSOA ID: {{ m.faturado.id }})</span>
                <span class="info-val font-semibold">{{ m.faturado.razao_social }}</span>
                <span v-if="m.faturado.cpf_cnpj" class="info-sub font-mono">CPF/CNPJ: {{ m.faturado.cpf_cnpj }}</span>
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
                    <span
                      class="badge"
                      :class="p.status === 'PAGO' ? 'badge-success' : 'badge-warning'"
                    >
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

    <!-- ── Modal de Criação Manual ─────────────────────────────── -->
    <div v-if="isModalOpen" class="modal-backdrop" @click.self="isModalOpen = false">
      <div class="modal-box">
        <div class="modal-head">
          <h3>Novo Lançamento — {{ form.tipo === 'APAGAR' ? 'Contas a Pagar' : 'Contas a Receber' }}</h3>
          <button class="modal-x" @click="isModalOpen = false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
              <path stroke-linecap="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-field">
              <label class="form-label">Fornecedor (Pessoa) *</label>
              <select v-model="form.fornecedor_id" class="form-select">
                <option v-for="p in pessoasFornecedores" :key="p.id" :value="p.id">
                  {{ p.razao_social }} (ID: {{ p.id }})
                </option>
              </select>
            </div>

            <div class="form-field">
              <label class="form-label">Faturado (Pessoa) *</label>
              <select v-model="form.faturado_id" class="form-select">
                <option v-for="p in pessoasFaturados" :key="p.id" :value="p.id">
                  {{ p.razao_social }} (ID: {{ p.id }})
                </option>
              </select>
            </div>

            <div class="form-field">
              <label class="form-label">Classificação (Tipo de Despesa) *</label>
              <select v-model="form.classificacao_id" class="form-select">
                <option v-for="c in classificacoesDisponiveis" :key="c.id" :value="c.id">
                  {{ c.descricao }}
                </option>
              </select>
            </div>

            <div class="form-field">
              <label class="form-label">Nº do Documento / Nota</label>
              <input v-model="form.numero_documento" type="text" class="form-input" placeholder="000123" />
            </div>

            <div class="form-field">
              <label class="form-label">Data de Emissão</label>
              <input v-model="form.data_emissao" type="date" class="form-input" />
            </div>

            <div class="form-field">
              <label class="form-label">Valor Total (R$) *</label>
              <input v-model.number="form.valor_total" type="number" step="0.01" class="form-input" />
            </div>

            <div class="form-field">
              <label class="form-label">Identificação da Parcela</label>
              <input v-model="form.identificacao_parcela" type="text" class="form-input" placeholder="ÚNICA" />
            </div>

            <div class="form-field">
              <label class="form-label">Vencimento da Parcela</label>
              <input v-model="form.data_vencimento" type="date" class="form-input" />
            </div>

            <div class="form-field form-field--full">
              <label class="form-label">Observação</label>
              <input v-model="form.observacao" type="text" class="form-input" placeholder="Observações do lançamento..." />
            </div>
          </div>
        </div>
        <div class="modal-foot">
          <button class="btn btn-secondary" @click="isModalOpen = false">Cancelar</button>
          <button class="btn btn-primary" :disabled="isLoading" @click="handleSave">
            {{ isLoading ? 'Salvando...' : 'Registrar Movimento' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style src="@/assets/styles/movimentos.css"></style>
