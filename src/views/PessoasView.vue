<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getPessoas, createPessoa, updatePessoa, inativarPessoa, reativarPessoa } from '@/services/api'
import type { Pessoa, PessoaCreate } from '@/types/models'

const pessoas = ref<Pessoa[]>([])
const isLoading = ref(false)
const errorMessage = ref<string | null>(null)
const successMessage = ref<string | null>(null)

// Filtros
const selectedTipo = ref<string>('')
const buscaTexto = ref<string>('')
const statusFiltro = ref<string>('todos') // 'todos', 'ativos', 'inativos'

// Modal de Criação / Edição
const isModalOpen = ref(false)
const editingPessoa = ref<Pessoa | null>(null)
const form = ref<PessoaCreate>({
  tipo: 'CLIENTE-FORNECEDOR',
  razao_social: '',
  cpf_cnpj: '',
  inscricao_estadual: '',
  endereco: '',
  telefone: '',
})

async function fetchPessoas() {
  isLoading.value = true
  errorMessage.value = null
  try {
    const params: { tipo?: string; busca?: string; ativo?: boolean } = {}
    if (selectedTipo.value) params.tipo = selectedTipo.value
    if (buscaTexto.value) params.busca = buscaTexto.value
    if (statusFiltro.value === 'ativos') params.ativo = true
    if (statusFiltro.value === 'inativos') params.ativo = false

    pessoas.value = await getPessoas(params)
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro ao buscar pessoas'
  } finally {
    isLoading.value = false
  }
}

function openCreateModal() {
  editingPessoa.value = null
  form.value = {
    tipo: 'CLIENTE-FORNECEDOR',
    razao_social: '',
    cpf_cnpj: '',
    inscricao_estadual: '',
    endereco: '',
    telefone: '',
  }
  isModalOpen.value = true
}

function openEditModal(p: Pessoa) {
  editingPessoa.value = p
  form.value = {
    tipo: p.tipo,
    razao_social: p.razao_social,
    cpf_cnpj: p.cpf_cnpj ?? '',
    inscricao_estadual: p.inscricao_estadual ?? '',
    endereco: p.endereco ?? '',
    telefone: p.telefone ?? '',
  }
  isModalOpen.value = true
}

async function handleSave() {
  if (!form.value.razao_social.trim()) {
    alert('Razão Social / Nome é obrigatório!')
    return
  }

  isLoading.value = true
  try {
    if (editingPessoa.value) {
      await updatePessoa(editingPessoa.value.id, form.value)
      showNotification('Cadastro atualizado com sucesso!')
    } else {
      await createPessoa(form.value)
      showNotification('Pessoa cadastrada com sucesso!')
    }
    isModalOpen.value = false
    await fetchPessoas()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro ao salvar'
  } finally {
    isLoading.value = false
  }
}

async function handleInativar(p: Pessoa) {
  if (!confirm(`Deseja inativar o cadastro "${p.razao_social}"?\n\n(Regra de negócio: Cadastros não são excluídos, ficam inativados e podem ser reativados a qualquer momento).`)) {
    return
  }
  try {
    await inativarPessoa(p.id)
    showNotification(`"${p.razao_social}" foi inativado.`)
    await fetchPessoas()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro ao inativar'
  }
}

async function handleReativar(p: Pessoa) {
  try {
    await reativarPessoa(p.id)
    showNotification(`"${p.razao_social}" foi reativado com sucesso!`)
    await fetchPessoas()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro ao reativar'
  }
}

function showNotification(msg: string) {
  successMessage.value = msg
  setTimeout(() => (successMessage.value = null), 4000)
}

onMounted(() => {
  fetchPessoas()
})
</script>

<template>
  <div class="view-page">
    <div class="view-page__inner">
      <!-- Cabeçalho -->
      <div class="page-header">
        <div>
          <span class="page-badge">Módulo de Cadastros</span>
          <h1 class="page-title">Manter Pessoas</h1>
          <p class="page-desc">Gerenciamento de Fornecedores, Faturados e Clientes com controle de inativação e reativação.</p>
        </div>
        <button class="primary-btn" @click="openCreateModal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
            <path stroke-linecap="round" stroke-width="2.5" d="M12 5v14M5 12h14"/>
          </svg>
          Novo Cadastro
        </button>
      </div>

      <!-- Alertas -->
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

      <!-- Barra de Filtros -->
      <div class="filters-card">
        <div class="filter-group">
          <label class="filter-label">Tipo</label>
          <select v-model="selectedTipo" class="form-select" style="min-width:180px" @change="fetchPessoas">
            <option value="">Todos os tipos</option>
            <option value="CLIENTE-FORNECEDOR">CLIENTE-FORNECEDOR</option>
            <option value="FORNECEDOR">FORNECEDOR</option>
            <option value="FATURADO">FATURADO</option>
            <option value="CLIENTE">CLIENTE</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">Status</label>
          <select v-model="statusFiltro" class="form-select" @change="fetchPessoas">
            <option value="todos">Todos</option>
            <option value="ativos">Apenas Ativos</option>
            <option value="inativos">Apenas Inativos</option>
          </select>
        </div>
        <div class="filter-group" style="flex:1;min-width:200px">
          <label class="filter-label">Buscar</label>
          <input
            v-model="buscaTexto"
            type="text"
            class="form-input"
            placeholder="Nome ou CPF/CNPJ..."
            @keyup.enter="fetchPessoas"
          />
        </div>
        <button class="filter-btn" style="align-self:flex-end" @click="fetchPessoas">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="13" height="13">
            <path stroke-linecap="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          Filtrar
        </button>
      </div>

      <!-- Tabela de Pessoas -->
      <div class="table-card">
        <div v-if="isLoading" class="state-box">
          <span class="state-icon">⏳</span>
          Carregando dados...
        </div>
        <div v-else-if="pessoas.length === 0" class="state-box">
          <span class="state-icon">🔍</span>
          Nenhuma pessoa encontrada com os filtros informados.
        </div>
        <div v-else class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Tipo</th>
                <th>Razão Social / Nome</th>
                <th>CPF / CNPJ</th>
                <th>Telefone</th>
                <th>Status</th>
                <th style="text-align:right">Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in pessoas" :key="p.id" :class="{ 'row--inactive': !p.ativo }">
                <td class="id-col">#{{ p.id }}</td>
                <td>
                  <span class="tipo-tag">{{ p.tipo }}</span>
                </td>
                <td style="font-weight:600">{{ p.razao_social }}</td>
                <td class="mono">{{ p.cpf_cnpj || '—' }}</td>
                <td>{{ p.telefone || '—' }}</td>
                <td>
                  <span class="badge" :class="p.ativo ? 'badge-success' : 'badge-error'">
                    {{ p.ativo ? 'Ativo' : 'Inativo' }}
                  </span>
                </td>
                <td style="text-align:right">
                  <div class="action-buttons">
                    <button class="btn-icon" title="Editar" @click="openEditModal(p)">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="13" height="13">
                        <path stroke-linecap="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                      </svg>
                    </button>
                    <button
                      v-if="p.ativo"
                      class="action-pill action-pill--danger"
                      title="Inativar cadastro"
                      @click="handleInativar(p)"
                    >Inativar</button>
                    <button
                      v-else
                      class="action-pill action-pill--success"
                      title="Reativar cadastro"
                      @click="handleReativar(p)"
                    >Reativar</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal de Criação / Edição -->
    <div v-if="isModalOpen" class="modal-backdrop" @click.self="isModalOpen = false">
      <div class="modal-box">
        <div class="modal-head">
          <h3>{{ editingPessoa ? 'Editar Pessoa' : 'Nova Pessoa' }}</h3>
          <button class="modal-x" @click="isModalOpen = false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
              <path stroke-linecap="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-field">
              <label class="form-label">Tipo de Pessoa *</label>
              <select v-model="form.tipo" class="form-select">
                <option value="CLIENTE-FORNECEDOR">CLIENTE-FORNECEDOR</option>
                <option value="FORNECEDOR">FORNECEDOR</option>
                <option value="FATURADO">FATURADO</option>
                <option value="CLIENTE">CLIENTE</option>
              </select>
            </div>

            <div class="form-field form-field--full">
              <label class="form-label">Razão Social / Nome Completo *</label>
              <input v-model="form.razao_social" type="text" class="form-input" placeholder="Ex: IGUAÇU MAQUINAS LTDA" />
            </div>

            <div class="form-field">
              <label class="form-label">CPF ou CNPJ</label>
              <input v-model="form.cpf_cnpj" type="text" class="form-input" placeholder="00.000.000/0000-00" />
            </div>

            <div class="form-field">
              <label class="form-label">Inscrição Estadual</label>
              <input v-model="form.inscricao_estadual" type="text" class="form-input" placeholder="Inscrição Estadual" />
            </div>

            <div class="form-field form-field--full">
              <label class="form-label">Endereço Completo</label>
              <input v-model="form.endereco" type="text" class="form-input" placeholder="Rua, Número, Bairro, Cidade - UF" />
            </div>

            <div class="form-field">
              <label class="form-label">Telefone</label>
              <input v-model="form.telefone" type="text" class="form-input" placeholder="(00) 00000-0000" />
            </div>
          </div>
        </div>
        <div class="modal-foot">
          <button class="btn btn-secondary" @click="isModalOpen = false">Cancelar</button>
          <button class="btn btn-primary" :disabled="isLoading" @click="handleSave">
            {{ isLoading ? 'Salvando...' : 'Salvar Cadastro' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.view-page {
  min-height: calc(100vh - var(--topbar-height));
  background: var(--color-bg);
}

.view-page__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.75rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* ── Header ───────────────────────────────────────────── */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding-bottom: 1.1rem;
  border-bottom: 1px solid var(--color-border);
}

.page-badge {
  display: inline-block;
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--color-accent);
  background: var(--color-accent-subtle);
  border: 1px solid rgba(29, 111, 55, 0.2);
  padding: 0.18rem 0.55rem;
  border-radius: 99px;
  margin-bottom: 0.35rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 900;
  color: var(--color-text-primary);
  margin: 0;
  letter-spacing: -0.03em;
  text-transform: uppercase;
  line-height: 1.15;
}

.page-desc {
  font-size: 0.825rem;
  color: var(--color-text-muted);
  margin: 0.3rem 0 0;
}

.primary-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--color-accent);
  color: #fff;
  border: none;
  font-weight: 700;
  font-size: 0.825rem;
  padding: 0.6rem 1.1rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(29, 111, 55, 0.3);
  transition: all 0.15s;
  font-family: inherit;
  white-space: nowrap;
  margin-top: 0.25rem;
}

.primary-btn:hover {
  background: #185c2d;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(29, 111, 55, 0.4);
}

/* ── Alerts ───────────────────────────────────────────── */
.alert {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.835rem;
  font-weight: 500;
  animation: slide-down 0.2s ease;
}

.alert-success {
  background: var(--color-success-bg);
  border: 1px solid var(--color-success-border);
  color: var(--color-success);
}

.alert-error {
  background: var(--color-error-bg);
  border: 1px solid var(--color-error-border);
  color: var(--color-error);
}

@keyframes slide-down {
  from { opacity: 0; transform: translateY(-6px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── Filters ──────────────────────────────────────────── */
.filters-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1rem 1.25rem;
  display: flex;
  align-items: flex-end;
  gap: 0.9rem;
  flex-wrap: wrap;
  box-shadow: var(--shadow-xs);
}

.filter-group { display: flex; flex-direction: column; gap: 0.25rem; }

.filter-label {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--color-text-faint);
}

.filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border-strong);
  color: var(--color-text-secondary);
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.52rem 1rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}

.filter-btn:hover {
  background: var(--color-accent-subtle);
  border-color: var(--color-accent-mid);
  color: var(--color-accent);
}

/* ── Table ────────────────────────────────────────────── */
.table-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-xs);
}

.table-wrapper { overflow-x: auto; }

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.835rem;
  text-align: left;
}

.data-table th {
  background: var(--color-surface-2);
  color: var(--color-text-muted);
  font-weight: 700;
  padding: 0.7rem 1rem;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.data-table td {
  padding: 0.8rem 1rem;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-primary);
  vertical-align: middle;
}

.data-table tr:last-child td { border-bottom: none; }
.data-table tbody tr { transition: background 0.12s; }
.data-table tbody tr:hover { background: var(--color-surface-2); }
.row--inactive { opacity: 0.5; }

.id-col {
  color: var(--color-text-faint);
  font-weight: 600;
  font-size: 0.78rem;
  font-family: 'JetBrains Mono', monospace;
}

.tipo-tag {
  background: var(--color-accent-subtle);
  color: var(--color-accent);
  border: 1px solid rgba(29, 111, 55, 0.2);
  padding: 0.18rem 0.55rem;
  border-radius: 99px;
  font-size: 0.67rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.67rem;
  font-weight: 700;
  padding: 0.18rem 0.55rem;
  border-radius: 99px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge-success {
  background: var(--color-success-bg);
  color: var(--color-success);
  border: 1px solid var(--color-success-border);
}

.badge-error {
  background: var(--color-error-bg);
  color: var(--color-error);
  border: 1px solid var(--color-error-border);
}

.mono {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  color: var(--color-text-muted);
}

.action-buttons {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  justify-content: flex-end;
}

.btn-icon {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--color-surface-2);
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.btn-icon:hover {
  background: var(--color-border);
  color: var(--color-text-primary);
}

.action-pill {
  display: inline-flex;
  align-items: center;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.28rem 0.65rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
  border: 1px solid;
}

.action-pill--danger {
  background: var(--color-error-bg);
  border-color: var(--color-error-border);
  color: var(--color-error);
}

.action-pill--danger:hover { background: rgba(220, 38, 38, 0.14); }

.action-pill--success {
  background: var(--color-success-bg);
  border-color: var(--color-success-border);
  color: var(--color-success);
}

.action-pill--success:hover { background: rgba(22, 163, 74, 0.14); }

.state-box {
  padding: 3.5rem 1rem;
  text-align: center;
  color: var(--color-text-faint);
  font-size: 0.875rem;
}

.state-box .state-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 0.75rem;
}

/* ── Modal ────────────────────────────────────────────── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(10, 20, 12, 0.5);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 1rem;
}

.modal-box {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 560px;
  overflow: hidden;
  box-shadow: var(--shadow-xl);
  animation: pop-in 0.22s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes pop-in {
  from { transform: scale(0.93); opacity: 0; }
  to   { transform: scale(1);    opacity: 1; }
}

.modal-head {
  padding: 1.1rem 1.4rem;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--color-surface-2);
}

.modal-head h3 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 800;
  color: var(--color-text-primary);
  text-transform: uppercase;
  letter-spacing: -0.01em;
}

.modal-x {
  background: none;
  border: none;
  color: var(--color-text-faint);
  cursor: pointer;
  padding: 0.2rem;
  border-radius: var(--radius-sm);
  transition: color 0.15s;
  display: flex;
  align-items: center;
}

.modal-x:hover { color: var(--color-text-primary); }

.modal-body { padding: 1.4rem; }

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.form-field { display: flex; flex-direction: column; gap: 0.3rem; }
.form-field--full { grid-column: 1 / -1; }

.modal-foot {
  padding: 1rem 1.4rem;
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
  background: var(--color-surface-2);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  font-family: inherit;
  font-size: 0.825rem;
  font-weight: 600;
  border-radius: var(--radius-md);
  border: none;
  cursor: pointer;
  transition: all 0.15s;
  padding: 0.55rem 1.1rem;
}

.btn-primary {
  background: var(--color-accent);
  color: #fff;
  box-shadow: 0 2px 8px rgba(29, 111, 55, 0.3);
}

.btn-primary:hover { background: #185c2d; transform: translateY(-1px); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

.btn-secondary {
  background: var(--color-surface-2);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover { background: var(--color-border); }
</style>
