<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from '@/components/AppSidebar.vue'
import AppTopbar from '@/components/AppTopbar.vue'

const route = useRoute()

// Exibe o shell completo (sidebar + topbar) apenas em rotas autenticadas
const showShell = computed(() => !route.meta.public)
</script>

<template>
  <!-- Layout com shell (rotas protegidas) -->
  <div v-if="showShell" class="app-shell">
    <AppSidebar />
    <div class="app-main">
      <AppTopbar />
      <RouterView />
    </div>
  </div>

  <!-- Layout limpo (rotas públicas: login/cadastro) -->
  <RouterView v-else />
</template>

<style scoped>
.app-shell {
  display: flex;
  min-height: 100vh;
}

.app-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
</style>
