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
    items: [
      { path: '/', label: 'Extração de Notas', icon: 'file-text' },
      { path: '/pessoas', label: 'Fornecedores', icon: 'truck' },
      { path: '/classificacoes', label: 'Operações', icon: 'layers' },
    ],
  },
  {
    label: 'Relatórios',
    items: [
      { path: '/pessoas', label: 'Fornecedores', icon: 'bar-chart' },
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
      <div class="brand-logo">
        <svg viewBox="0 0 24 24" fill="none" class="brand-icon">
          <path d="M12 2L2 7l10 5 10-5-10-5z" fill="currentColor" opacity="0.9"/>
          <path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" fill="none"/>
        </svg>
      </div>
      <div class="brand-text">
        <span class="brand-name">Agrotech</span>
        <span class="brand-tagline">Precision System</span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <template v-for="(section, idx) in navSections" :key="section.label ?? idx">
        <div v-if="section.label" class="nav-section-label">
          {{ section.label }}
          <button class="nav-section-action" title="Adicionar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="12" height="12">
              <path stroke-linecap="round" stroke-width="2" d="M12 5v14M5 12h14"/>
            </svg>
          </button>
        </div>
        <RouterLink
          v-for="item in section.items"
          :key="item.path + item.label"
          :to="item.path"
          class="nav-item"
          :class="{ 'nav-item--active': route.path === item.path && item.path !== '/' || route.path === item.path }"
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
            <path stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" d="M19 7H5a2 2 0 00-2 2v8a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2zM3 7l9-4 9 4"/>
            <circle cx="17" cy="13" r="1" fill="currentColor"/>
          </svg>
          <!-- File-text icon -->
          <svg v-else-if="item.icon === 'file-text'" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-icon">
            <path stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
            <path stroke-width="1.75" stroke-linecap="round" d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>
          </svg>
          <!-- Truck icon -->
          <svg v-else-if="item.icon === 'truck'" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-icon">
            <path stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" d="M1 3h15v13H1zM16 8h4l3 4v5h-7V8zM5.5 21a1.5 1.5 0 100-3 1.5 1.5 0 000 3zM18.5 21a1.5 1.5 0 100-3 1.5 1.5 0 000 3z"/>
          </svg>
          <!-- Layers icon -->
          <svg v-else-if="item.icon === 'layers'" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-icon">
            <path stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
          <!-- Bar-chart icon -->
          <svg v-else-if="item.icon === 'bar-chart'" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-icon">
            <path stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" d="M18 20V10M12 20V4M6 20v-6"/>
          </svg>
          <!-- Pie-chart icon -->
          <svg v-else-if="item.icon === 'pie-chart'" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="nav-icon">
            <path stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" d="M21.21 15.89A10 10 0 118.11 2.79M22 12A10 10 0 0012 2v10z"/>
          </svg>

          <span class="nav-label">{{ item.label }}</span>
        </RouterLink>
      </template>
    </nav>

    <!-- User profile footer -->
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar">{{ authStore.iniciaisUsuario }}</div>
        <div class="user-meta">
          <span class="user-name">{{ authStore.nomeUsuario || authStore.loginUsuario }}</span>
          <span class="user-role">
            <span class="user-dot" />
            {{ authStore.perfilUsuario }}
          </span>
        </div>
        <button class="user-action" title="Sair do sistema" @click="handleLogout">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
          </svg>
        </button>
      </div>
    </div>
  </aside>
</template>

<style scoped>
/* ── Sidebar Shell ─────────────────────────────────────── */
.sidebar {
  width: var(--sidebar-width);
  min-height: 100vh;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--sidebar-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

/* ── Brand ─────────────────────────────────────────────── */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 1rem 1rem 0.75rem;
  border-bottom: 1px solid var(--sidebar-border);
}

.brand-logo {
  width: 34px;
  height: 34px;
  background: linear-gradient(135deg, #2d5a3d, #4ade80);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-icon {
  width: 18px;
  height: 18px;
  color: #fff;
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 0;
  line-height: 1.1;
}

.brand-name {
  font-size: 0.9rem;
  font-weight: 800;
  color: #e8f5eb;
  letter-spacing: -0.02em;
  text-transform: uppercase;
}

.brand-tagline {
  font-size: 0.6rem;
  font-weight: 500;
  color: var(--sidebar-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

/* ── Navigation ────────────────────────────────────────── */
.sidebar-nav {
  flex: 1;
  padding: 0.75rem 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.nav-section-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 0.6rem 0.3rem;
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--sidebar-text-muted);
}

.nav-section-action {
  background: none;
  border: none;
  color: var(--sidebar-text-muted);
  cursor: pointer;
  padding: 2px;
  border-radius: 3px;
  display: flex;
  align-items: center;
  transition: color 0.15s, background 0.15s;
}

.nav-section-action:hover {
  color: var(--sidebar-text);
  background: var(--sidebar-hover);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.5rem 0.7rem;
  border-radius: 7px;
  text-decoration: none;
  color: var(--sidebar-text);
  font-size: 0.815rem;
  font-weight: 500;
  transition: all 0.15s ease;
  border: 1px solid transparent;
}

.nav-item:hover {
  background: var(--sidebar-hover);
  color: #d4edd7;
}

.nav-item--active {
  background: var(--sidebar-active-bg);
  color: var(--sidebar-active-text);
  border-color: rgba(74, 222, 128, 0.15);
  font-weight: 600;
}

.nav-icon {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
  opacity: 0.85;
}

.nav-item--active .nav-icon { opacity: 1; }

.nav-label { flex: 1; line-height: 1; }

/* ── Footer / User ─────────────────────────────────────── */
.sidebar-footer {
  border-top: 1px solid var(--sidebar-border);
  padding: 0.75rem 0.75rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2d5a3d, #4ade80);
  color: #fff;
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-meta {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 0.775rem;
  font-weight: 600;
  color: var(--sidebar-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.65rem;
  color: var(--sidebar-text-muted);
}

.user-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #4ade80;
  box-shadow: 0 0 4px rgba(74, 222, 128, 0.6);
  animation: pulse-dot 2s ease infinite;
}

.user-action {
  background: none;
  border: none;
  color: var(--sidebar-text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.15s;
  display: flex;
}

.user-action:hover {
  background: var(--sidebar-hover);
  color: var(--sidebar-text);
}
</style>
