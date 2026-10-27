<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  getClassificacoes,
  createClassificacao,
  updateClassificacao,
  inativarClassificacao,
  reativarClassificacao,
} from '@/services/api'
import type { Classificacao, ClassificacaoCreate, TipoClassificacao } from '@/types/models'

const classificacoes = ref<Classificacao[]>([])
const isLoading = ref(false)
const errorMessage = ref<string | null>(null)
const successMessage = ref<string | null>(null)

// Filtros
const selectedTipo = ref<string>('')
const buscaTexto = ref<string>('')
const statusFiltro = ref<string>('todos')

// Modal
const isModalOpen = ref(false)
const editingClassificacao = ref<Classificacao | null>(null)
const form = ref<ClassificacaoCreate>({
  tipo: 'DESPESA',
  descricao: '',
})

async function fetchClassificacoes() {
  isLoading.value = true
  errorMessage.value = null
  try {
    const params: { tipo?: string; busca?: string; ativo?: boolean } = {}
    if (selectedTipo.value) params.tipo = selectedTipo.value
    if (buscaTexto.value) params.busca = buscaTexto.value
    if (statusFiltro.value === 'ativos') params.ativo = true
    if (statusFiltro.value === 'inativos') params.ativo = false

    classificacoes.value = await getClassificacoes(params)
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro ao buscar classificações'
  } finally {
    isLoading.value = false
  }
}

function openCreateModal() {
  editingClassificacao.value = null
  form.value = {
    tipo: 'DESPESA',
    descricao: '',
  }
  isModalOpen.value = true
}

function openEditModal(c: Classificacao) {
  editingClassificacao.value = c
  form.value = {
    tipo: c.tipo,
    descricao: c.descricao,
  }
  isModalOpen.value = true
}

async function handleSave() {
  if (!form.value.descricao.trim()) {
    alert('Descrição é obrigatória!')
    return
  }

  isLoading.value = true
  try {
    if (editingClassificacao.value) {
      await updateClassificacao(editingClassificacao.value.id, form.value)
      showNotification('Classificação atualizada com sucesso!')
    } else {
      await createClassificacao(form.value)
      showNotification('Classificação criada com sucesso!')
    }
    isModalOpen.value = false
    await fetchClassificacoes()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro ao salvar'
  } finally {
    isLoading.value = false
  }
}

async function handleInativar(c: Classificacao) {
  if (!confirm(`Deseja inativar a classificação "${c.descricao}"?\n\n(Regra de negócio: Cadastros não são excluídos, ficam inativados e podem ser reativados a qualquer momento).`)) {
    return
  }
  try {
    await inativarClassificacao(c.id)
    showNotification(`"${c.descricao}" foi inativada.`)
    await fetchClassificacoes()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro ao inativar'
  }
}

async function handleReativar(c: Classificacao) {
  try {
    await reativarClassificacao(c.id)
    showNotification(`"${c.descricao}" foi reativada com sucesso!`)
    await fetchClassificacoes()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro ao reativar'
  }
}

function showNotification(msg: string) {
  successMessage.value = msg
  setTimeout(() => (successMessage.value = null), 4000)
}

onMounted(() => {
  fetchClassificacoes()
})
</script>

<template>
  <div class="view-page">
    <div class="view-page__inner">
      <!-- Cabeçalho -->
      <div class="page-header">
        <div>
          <span class="page-badge">Módulo Financeiro</span>
          <h1 class="page-title">Manter Classificações</h1>
          <p class="page-desc">Gerenciamento de Tipos de Despesas e Receitas para rateio financeiro.</p>
        </div>
        <button class="primary-btn" @click="openCreateModal">
          <span>+</span> Nova Classificação
        </button>
      </div>

      <!-- Feedback -->
      <div v-if="successMessage" class="banner banner--success">
        ✓ {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="banner banner--error">
        ⚠️ {{ errorMessage }}
      </div>

      <!-- Barra de Filtros -->
      <div class="filters-bar">
        <div class="filter-group">
          <label>Tipo:</label>
          <select v-model="selectedTipo" class="select-input" @change="fetchClassificacoes">
            <option value="">Todos os tipos</option>
            <option value="DESPESA">DESPESA</option>
            <option value="RECEITA">RECEITA</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Status:</label>
          <select v-model="statusFiltro" class="select-input" @change="fetchClassificacoes">
            <option value="todos">Todos</option>
            <option value="ativos">Apenas Ativos</option>
            <option value="inativos">Apenas Inativos</option>
          </select>
        </div>

        <div class="filter-group search-group">
          <label>Buscar:</label>
          <input
            v-model="buscaTexto"
            type="text"
            class="search-input"
            placeholder="Descrição da classificação..."
            @keyup.enter="fetchClassificacoes"
          />
        </div>

        <button class="filter-btn" @click="fetchClassificacoes">
          Filtrar
        </button>
      </div>

      <!-- Tabela -->
      <div class="table-card">
        <div v-if="isLoading" class="loading-state">
          Carregando dados...
        </div>
        <div v-else-if="classificacoes.length === 0" class="empty-state">
          Nenhuma classificação encontrada.
        </div>
        <div v-else class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Tipo</th>
                <th>Descrição</th>
                <th>Status</th>
                <th class="actions-col">Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in classificacoes" :key="c.id" :class="{ 'row--inactive': !c.ativo }">
                <td class="id-col">#{{ c.id }}</td>
                <td>
                  <span class="tipo-tag" :class="c.tipo === 'DESPESA' ? 'tipo-tag--despesa' : 'tipo-tag--receita'">
                    {{ c.tipo }}
                  </span>
                </td>
                <td class="name-col">{{ c.descricao }}</td>
                <td>
                  <span class="status-badge" :class="c.ativo ? 'status-badge--active' : 'status-badge--inactive'">
                    {{ c.ativo ? 'Ativo' : 'Inativo' }}
                  </span>
                </td>
                <td class="actions-col">
                  <div class="action-buttons">
                    <button class="icon-btn" title="Editar" @click="openEditModal(c)">
                      ✏️
                    </button>
                    <!-- Regra: Inativação / Reativação -->
                    <button
                      v-if="c.ativo"
                      class="inactivate-btn"
                      title="Inativar cadastro"
                      @click="handleInativar(c)"
                    >
                      Inativar
                    </button>
                    <button
                      v-else
                      class="reactivate-btn"
                      title="Reativar cadastro"
                      @click="handleReativar(c)"
                    >
                      Reativar
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="isModalOpen" class="modal-backdrop" @click.self="isModalOpen = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3>{{ editingClassificacao ? 'Editar Classificação' : 'Nova Classificação' }}</h3>
          <button class="modal-close" @click="isModalOpen = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-field">
              <label>Tipo de Classificação *</label>
              <select v-model="form.tipo" class="select-input">
                <option value="DESPESA">DESPESA</option>
                <option value="RECEITA">RECEITA</option>
              </select>
            </div>

            <div class="form-field form-field--full">
              <label>Descrição *</label>
              <input
                v-model="form.descricao"
                type="text"
                class="text-input"
                placeholder="Ex: MANUTENÇÃO E OPERAÇÃO"
              />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="isModalOpen = false">Cancelar</button>
          <button class="save-btn" :disabled="isLoading" @click="handleSave">
            {{ isLoading ? 'Salvando...' : 'Salvar Classificação' }}
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
  max-width: 1000px;
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

.filters-bar {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.825rem;
  color: var(--color-text-muted);
}

.search-group {
  flex: 1;
  min-width: 200px;
}

.select-input, .text-input, .search-input {
  background: var(--color-surface-hover);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  border-radius: var(--radius-md);
  padding: 0.45rem 0.75rem;
  font-size: 0.85rem;
  outline: none;
  font-family: inherit;
}

.select-input:focus, .text-input:focus, .search-input:focus {
  border-color: var(--color-accent);
}

.search-input {
  width: 100%;
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
}

.filter-btn:hover {
  border-color: var(--color-accent);
}

.table-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  text-align: left;
}

.data-table th {
  background: var(--color-surface-hover);
  color: var(--color-text-muted);
  font-weight: 600;
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--color-border);
}

.data-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-primary);
}

.data-table tr:last-child td {
  border-bottom: none;
}

.row--inactive {
  opacity: 0.6;
  background: rgba(0, 0, 0, 0.15);
}

.id-col {
  color: var(--color-text-muted);
  font-weight: 600;
  font-size: 0.8rem;
}

.tipo-tag {
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.72rem;
  font-weight: 700;
}

.tipo-tag--despesa {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

.tipo-tag--receita {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
}

.name-col {
  font-weight: 600;
}

.status-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 100px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
}

.status-badge--active {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
}

.status-badge--inactive {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

.actions-col {
  text-align: right;
}

.action-buttons {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.icon-btn {
  background: none;
  border: 1px solid var(--color-border);
  padding: 0.3rem 0.5rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: var(--color-surface-hover);
}

.inactivate-btn {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #f87171;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.3rem 0.65rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
}

.inactivate-btn:hover {
  background: rgba(239, 68, 68, 0.2);
}

.reactivate-btn {
  background: rgba(52, 211, 153, 0.1);
  border: 1px solid rgba(52, 211, 153, 0.3);
  color: #34d399;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.3rem 0.65rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
}

.reactivate-btn:hover {
  background: rgba(52, 211, 153, 0.2);
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
  max-width: 480px;
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
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
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
