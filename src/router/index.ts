import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        title: 'Extração de NF-e | AgroContas',
      },
    },
    // Futuros módulos do AgroContas:
    // { path: '/invoices', name: 'invoices', component: () => import('@/views/InvoiceListView.vue') },
    // { path: '/dashboard', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
  ],
})

// Atualiza o <title> da página de acordo com a rota
router.beforeEach((to) => {
  const title = to.meta.title as string | undefined
  if (title) document.title = title
})

export default router
