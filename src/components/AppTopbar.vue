<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const route = useRoute()
const authStore = useAuthStore()

const routeLabels: Record<string, { section: string; page: string }> = {
  '/':               { section: 'Cadastros', page: 'Processamento de Documentos Fiscais' },
  '/pessoas':        { section: 'Cadastros', page: 'Manter Pessoas' },
  '/classificacoes': { section: 'Cadastros', page: 'Manter Classificações' },
  '/movimentos':     { section: 'Financeiro', page: 'Contas a Pagar / Receber' },
}

const current = () => routeLabels[route.path] ?? { section: 'Sistema', page: 'Página' }
</script>

<template>
  <header class="topbar">
    <!-- Titular selector -->
    <div class="topbar-titular">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="titular-icon">
        <rect x="3" y="4" width="18" height="18" rx="2" stroke-width="1.75"/>
        <path stroke-linecap="round" stroke-width="1.75" d="M16 2v4M8 2v4M3 10h18"/>
      </svg>
      <span class="titular-label">Titular:</span>
      <button class="titular-btn">
        Beltrano (Pai)
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="10" height="10">
          <path stroke-linecap="round" stroke-width="2" d="M6 9l6 6 6-6"/>
        </svg>
      </button>
    </div>

    <!-- Safra pill -->
    <div class="topbar-safra">
      <span class="safra-dot" />
      <span>SAFRA 2024/25 ATIVA</span>
    </div>

    <div class="topbar-spacer" />

    <!-- Ajuda button -->
    <button class="btn-ajuda">
      <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
        <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
      </svg>
      AJUDA SIMPLES
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="10" height="10">
        <path stroke-linecap="round" stroke-width="2" d="M7 17L17 7M7 7h10v10"/>
      </svg>
    </button>

    <!-- Notification bell -->
    <button class="topbar-icon-btn" title="Notificações">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="17" height="17">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75"
          d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0"/>
      </svg>
      <span class="notif-badge">3</span>
    </button>

    <!-- Avatar -->
    <div
      class="topbar-avatar"
      :title="authStore.nomeUsuario || authStore.loginUsuario"
    >{{ authStore.iniciaisUsuario }}</div>
  </header>
</template>

<style scoped>
.topbar {
  height: var(--topbar-height);
  background: var(--topbar-bg);
  border-bottom: 1px solid var(--topbar-border);
  display: flex;
  align-items: center;
  padding: 0 1.25rem;
  gap: 0.65rem;
  position: sticky;
  top: 0;
  z-index: 100;
  flex-shrink: 0;
}

/* Titular */
.topbar-titular {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.3rem 0.65rem;
}

.titular-icon {
  width: 14px;
  height: 14px;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.titular-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--color-text-faint);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.titular-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: none;
  border: none;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-primary);
  cursor: pointer;
  padding: 0;
  font-family: inherit;
  transition: color 0.15s;
}

.titular-btn:hover { color: var(--color-accent); }

/* Safra */
.topbar-safra {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--color-success);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: var(--color-success-bg);
  border: 1px solid var(--color-success-border);
  border-radius: 99px;
  padding: 0.28rem 0.7rem;
}

.safra-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-success);
  box-shadow: 0 0 5px rgba(22, 163, 74, 0.6);
  animation: pulse-dot 2s ease infinite;
}

.topbar-spacer { flex: 1; }

/* Ajuda */
.btn-ajuda {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--sidebar-bg);
  color: #d4edd7;
  border: none;
  border-radius: var(--radius-md);
  padding: 0.4rem 0.85rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}

.btn-ajuda:hover { background: var(--sidebar-bg-deeper); }

/* Icon buttons */
.topbar-icon-btn {
  position: relative;
  width: 34px;
  height: 34px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-surface-2);
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.topbar-icon-btn:hover {
  background: var(--color-border);
  color: var(--color-text-primary);
}

.notif-badge {
  position: absolute;
  top: -3px;
  right: -3px;
  background: var(--color-error);
  color: #fff;
  font-size: 0.55rem;
  font-weight: 800;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1.5px solid var(--color-surface);
}

/* Avatar */
.topbar-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2d5a3d, #4ade80);
  color: #fff;
  font-size: 0.8rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: box-shadow 0.15s;
}

.topbar-avatar:hover {
  box-shadow: 0 0 0 3px rgba(74, 222, 128, 0.3);
}
</style>
