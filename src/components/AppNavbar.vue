<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const navItems = [
  { path: '/', label: 'Extração NF-e', icon: '📄' },
  { path: '/pessoas', label: 'Manter Pessoas', icon: '👥' },
  { path: '/classificacoes', label: 'Manter Classificações', icon: '🏷️' },
  { path: '/movimentos', label: 'Contas a Pagar / Receber', icon: '💳' },
]
</script>

<template>
  <nav class="navbar">
    <div class="navbar__inner">
      <RouterLink to="/" class="navbar__brand">
        <span class="brand-icon">🌱</span>
        <span class="brand-text">Agro<span class="brand-text-accent">Contas</span></span>
      </RouterLink>

      <div class="navbar__links">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          :class="{ 'nav-link--active': route.path === item.path }"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </RouterLink>
      </div>

      <div class="navbar__status">
        <span class="status-indicator" title="Banco de Dados Conectado">
          <span class="status-dot" />
          <span class="status-label">DB Ativo</span>
        </span>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  width: 100%;
  background: rgba(19, 22, 30, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 50;
}

.navbar__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.75rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.navbar__brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  font-weight: 800;
  font-size: 1.15rem;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
}

.brand-icon {
  font-size: 1.3rem;
}

.brand-text-accent {
  background: var(--color-accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.navbar__links {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  overflow-x: auto;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.85rem;
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s;
  white-space: nowrap;
}

.nav-link:hover {
  color: var(--color-text-primary);
  background: var(--color-surface-hover);
}

.nav-link--active {
  color: var(--color-accent-light);
  background: var(--color-accent-subtle);
  font-weight: 600;
  border: 1px solid rgba(99, 102, 241, 0.25);
}

.nav-icon {
  font-size: 1rem;
}

.navbar__status {
  display: flex;
  align-items: center;
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(52, 211, 153, 0.1);
  border: 1px solid rgba(52, 211, 153, 0.25);
  padding: 0.25rem 0.6rem;
  border-radius: 100px;
  font-size: 0.75rem;
  color: #34d399;
  font-weight: 600;
}

.status-dot {
  width: 6px;
  height: 6px;
  background: #34d399;
  border-radius: 50%;
  box-shadow: 0 0 6px rgba(52, 211, 153, 0.8);
}
</style>
