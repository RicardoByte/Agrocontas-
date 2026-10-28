<script setup lang="ts">
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const commitHash = typeof __APP_COMMIT_HASH__ !== 'undefined' ? __APP_COMMIT_HASH__ : '4da785c'
</script>

<template>
  <header class="topbar">
    <!-- Lado Esquerdo: Safra -->
    <div class="topbar-left">
      <div class="topbar-safra-pill">
        <span class="safra-dot" />
        <span>SAFRA 2024/25 ATIVA</span>
      </div>

      <div class="topbar-commit-pill" title="Código da Última Atualização no GitHub">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="11" height="11" stroke-width="2">
          <circle cx="12" cy="12" r="4"/>
          <line x1="1.05" y1="12" x2="7" y2="12"/>
          <line x1="17.01" y1="12" x2="22.96" y2="12"/>
        </svg>
        <span>GitHub: <code>{{ commitHash }}</code></span>
      </div>
    </div>

    <!-- Lado Direito: Ajuda, Notificação e Avatar -->
    <div class="topbar-right">
      <button class="topbar-btn-ajuda" type="button">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14" stroke-width="2">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
        </svg>
        <span>AJUDA SIMPLES</span>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="10" height="10" stroke-width="2.5">
          <line x1="7" y1="17" x2="17" y2="7"/>
          <polyline points="7 7 17 7 17 17"/>
        </svg>
      </button>

      <button class="topbar-notif-btn" type="button" title="Notificações">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" stroke-width="1.8">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
        </svg>
        <span class="topbar-notif-dot" />
      </button>

      <div
        class="topbar-avatar-btn"
        :title="authStore.nomeUsuario || authStore.loginUsuario"
      >
        {{ authStore.iniciaisUsuario }}
      </div>
    </div>
  </header>
</template>
