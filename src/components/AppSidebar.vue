<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const navSections = [
  {
    label: null,
    items: [
      { path: '/', label: 'Dashboard', icon: 'grid' },
      { path: '/movimentos', label: 'Contas a Pagar/Receber', icon: 'wallet' },
    ],
  },
  {
    label: 'Cadastros',
    iconHeader: 'folder',
    items: [
      { path: '/', label: 'Extração de Notas', icon: 'file-text' },
      { path: '/pessoas', label: 'Fornecedores/Faturados', icon: 'truck' },
      { path: '/classificacoes', label: 'Operações', icon: 'layers' },
    ],
  },
  {
    label: 'Relatórios',
    iconHeader: 'chart',
    items: [
      { path: '/pessoas', label: 'Fornecedores/Faturados', icon: 'bar-chart' },
      { path: '/movimentos', label: 'Operações', icon: 'pie-chart' },
    ],
  },
]

function handleLogout() {
  authStore.logout()
  router.push({ name: 'auth' })
}
</script>

<template>
  <aside class="sidebar">
    <!-- Brand -->
    <div class="sidebar-brand">
      <div class="brand-logo-box">
        <span>A</span>
      </div>
      <div class="brand-text">
        <span class="brand-name">AGROTECH</span>
        <span class="brand-tagline">PRECISION SYSTEM</span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <template v-for="(section, idx) in navSections" :key="section.label ?? idx">
        <div v-if="section.label" class="nav-section-header">
          <span>{{ section.label }}</span>
          <svg v-if="section.iconHeader === 'folder'" viewBox="0 0 24 24" fill="none" stroke="currentColor" width="13" height="13" class="nav-section-icon" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
          <svg v-else-if="section.iconHeader === 'chart'" viewBox="0 0 24 24" fill="none" stroke="currentColor" width="13" height="13" class="nav-section-icon" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
            <polyline points="17 6 23 6 23 12"/>
          </svg>
        </div>

        <RouterLink
          v-for="item in section.items"
          :key="item.path + item.label"
          :to="item.path"
          class="nav-item"
          :class="{ 'nav-item--active': route.path === item.path }"
        >
          <!-- Grid icon -->
          <svg v-if="item.icon === 'grid'" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-icon">
            <rect x="3" y="3" width="7" height="7" rx="1" stroke-width="1.75"/>
            <rect x="14" y="3" width="7" height="7" rx="1" stroke-width="1.75"/>
            <rect x="14" y="14" width="7" height="7" rx="1" stroke-width="1.75"/>
            <rect x="3" y="14" width="7" height="7" rx="1" stroke-width="1.75"/>
          </svg>
          <!-- Wallet icon -->
          <svg v-else-if="item.icon === 'wallet'" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-icon">
            <rect x="2" y="6" width="20" height="12" rx="2" stroke-width="1.75"/>
            <circle cx="12" cy="12" r="2.5" stroke-width="1.75"/>
          </svg>
          <!-- File-text icon -->
          <svg v-else-if="item.icon === 'file-text'" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-icon">
            <path stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
            <polyline points="14 2 14 8 20 8" stroke-width="1.75"/>
            <line x1="16" y1="13" x2="8" y2="13" stroke-width="1.75"/>
            <line x1="16" y1="17" x2="8" y2="17" stroke-width="1.75"/>
          </svg>
          <!-- Truck icon -->
          <svg v-else-if="item.icon === 'truck'" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-icon">
            <rect x="1" y="3" width="15" height="13" stroke-width="1.75"/>
            <polygon points="16 8 20 8 23 11 23 16 16 16 16 8" stroke-width="1.75"/>
            <circle cx="5.5" cy="18.5" r="2.5" stroke-width="1.75"/>
            <circle cx="18.5" cy="18.5" r="2.5" stroke-width="1.75"/>
          </svg>
          <!-- Layers icon -->
          <svg v-else-if="item.icon === 'layers'" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-icon">
            <polygon points="12 2 2 7 12 12 22 7 12 2" stroke-width="1.75"/>
            <polyline points="2 17 12 22 22 17" stroke-width="1.75"/>
            <polyline points="2 12 12 17 22 12" stroke-width="1.75"/>
          </svg>
          <!-- Bar-chart icon -->
          <svg v-else-if="item.icon === 'bar-chart'" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-icon">
            <line x1="18" y1="20" x2="18" y2="10" stroke-width="1.75"/>
            <line x1="12" y1="20" x2="12" y2="4" stroke-width="1.75"/>
            <line x1="6" y1="20" x2="6" y2="14" stroke-width="1.75"/>
          </svg>
          <!-- Pie-chart icon -->
          <svg v-else-if="item.icon === 'pie-chart'" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-icon">
            <circle cx="12" cy="12" r="10" stroke-width="1.75"/>
            <line x1="12" y1="2" x2="12" y2="12" stroke-width="1.75"/>
            <line x1="12" y1="12" x2="20" y2="16" stroke-width="1.75"/>
          </svg>

          <span class="nav-label">{{ item.label }}</span>
        </RouterLink>
      </template>
    </nav>

    <!-- User profile card footer -->
    <div class="sidebar-footer">
      <div class="user-card">
        <div class="user-avatar-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <div class="user-meta-box">
          <span class="user-display-name">{{ authStore.nomeUsuario || 'Beltrano da Silva' }}</span>
          <div class="user-display-role">
            <span>Produtor Rural</span>
            <span class="user-active-dot" />
          </div>
        </div>
        <button class="user-logout-btn" title="Alternar usuário / Sair" @click="handleLogout">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14" stroke-width="2">
            <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
          </svg>
        </button>
      </div>
    </div>
  </aside>
</template>
