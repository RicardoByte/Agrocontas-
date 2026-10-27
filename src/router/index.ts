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
    {
      path: '/pessoas',
      name: 'pessoas',
      component: () => import('@/views/PessoasView.vue'),
      meta: {
        title: 'Manter Pessoas | AgroContas',
      },
    },
    {
      path: '/classificacoes',
      name: 'classificacoes',
      component: () => import('@/views/ClassificacoesView.vue'),
      meta: {
        title: 'Manter Classificações | AgroContas',
      },
    },
    {
      path: '/movimentos',
      name: 'movimentos',
      component: () => import('@/views/MovimentosView.vue'),
      meta: {
        title: 'Movimento de Contas | AgroContas',
      },
    },
  ],
})

// Atualiza o <title> da página de acordo com a rota
router.beforeEach((to) => {
  const title = to.meta.title as string | undefined
  if (title) document.title = title
})

export default router
