<script setup lang="ts">
import { ref, onMounted } from 'vue'
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

<style src="@/assets/styles/pessoas.css"></style>
