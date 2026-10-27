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
          <p class="page-desc">Categorias de Despesas e Receitas usadas no lançamento de contas a pagar e receber.</p>
        </div>
        <button class="primary-btn" @click="openCreateModal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
            <path stroke-linecap="round" stroke-width="2.5" d="M12 5v14M5 12h14"/>
          </svg>
          Nova Classificação
        </button>
      </div>

      <!-- Alertas -->
      <div v-if="successMessage" class="alert alert-success">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="15" height="15" style="flex-shrink:0">
          <path stroke-linecap="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
        </svg>
        {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="alert alert-error">⚠️ {{ errorMessage }}</div>

      <!-- Filtros -->
      <div class="filters-card">
        <div class="filter-group">
          <label class="filter-label">Tipo</label>
          <select v-model="selectedTipo" class="form-select" style="min-width:150px" @change="fetchClassificacoes">
            <option value="">Todos os tipos</option>
            <option value="DESPESA">DESPESA</option>
            <option value="RECEITA">RECEITA</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">Status</label>
          <select v-model="statusFiltro" class="form-select" @change="fetchClassificacoes">
            <option value="todos">Todos</option>
            <option value="ativos">Apenas Ativos</option>
            <option value="inativos">Apenas Inativos</option>
          </select>
        </div>
        <div class="filter-group" style="flex:1;min-width:180px">
          <label class="filter-label">Buscar</label>
          <input v-model="buscaTexto" type="text" class="form-input" placeholder="Descrição..." @keyup.enter="fetchClassificacoes" />
        </div>
        <button class="filter-btn" style="align-self:flex-end" @click="fetchClassificacoes">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="13" height="13">
            <path stroke-linecap="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          Filtrar
        </button>
      </div>

      <!-- Tabela -->
      <div class="table-card">
        <div v-if="isLoading" class="state-box"><span class="state-icon">⏳</span>Carregando dados...</div>
        <div v-else-if="classificacoes.length === 0" class="state-box"><span class="state-icon">🔍</span>Nenhuma classificação encontrada.</div>
        <div v-else class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th><th>Tipo</th><th>Descrição</th><th>Status</th>
                <th style="text-align:right">Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in classificacoes" :key="c.id" :class="{ 'row--inactive': !c.ativo }">
                <td class="id-col">#{{ c.id }}</td>
                <td>
                  <span class="tipo-tag" :class="c.tipo === 'DESPESA' ? 'tipo-despesa' : 'tipo-receita'">{{ c.tipo }}</span>
                </td>
                <td style="font-weight:600">{{ c.descricao }}</td>
                <td>
                  <span class="badge" :class="c.ativo ? 'badge-success' : 'badge-error'">
                    {{ c.ativo ? 'Ativo' : 'Inativo' }}
                  </span>
                </td>
                <td style="text-align:right">
                  <div class="action-buttons">
                    <button class="btn-icon" title="Editar" @click="openEditModal(c)">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="13" height="13">
                        <path stroke-linecap="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                      </svg>
                    </button>
                    <button v-if="c.ativo" class="action-pill action-pill--danger" @click="handleInativar(c)">Inativar</button>
                    <button v-else class="action-pill action-pill--success" @click="handleReativar(c)">Reativar</button>
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
      <div class="modal-box">
        <div class="modal-head">
          <h3>{{ editingClassificacao ? 'Editar Classificação' : 'Nova Classificação' }}</h3>
          <button class="modal-x" @click="isModalOpen = false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
              <path stroke-linecap="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-field">
              <label class="form-label">Tipo *</label>
              <select v-model="form.tipo" class="form-select">
                <option value="DESPESA">DESPESA</option>
                <option value="RECEITA">RECEITA</option>
              </select>
            </div>
            <div class="form-field form-field--full">
              <label class="form-label">Descrição *</label>
              <input v-model="form.descricao" type="text" class="form-input" placeholder="Ex: Combustível, Manutenção, Vendas..." />
            </div>
          </div>
        </div>
        <div class="modal-foot">
          <button class="btn btn-secondary" @click="isModalOpen = false">Cancelar</button>
          <button class="btn btn-primary" :disabled="isLoading" @click="handleSave">
            {{ isLoading ? 'Salvando...' : 'Salvar Classificação' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style src="@/assets/styles/classificacoes.css"></style>
