import { createRouter, createWebHistory } from 'vue-router'
import { getStoredToken } from '@/services/auth'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ── Rota pública: Login / Cadastro ──────────────────────────────────────
    {
      path: '/auth',
      name: 'auth',
      component: () => import('@/views/AuthView.vue'),
      meta: {
        title: 'Entrar | AgroContas',
        public: true,
      },
    },

    // ── Rotas protegidas ─────────────────────────────────────────────────────
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        title: 'Extração de NF-e | AgroContas',
        requiresAuth: true,
      },
    },
    {
      path: '/pessoas',
      name: 'pessoas',
      component: () => import('@/views/PessoasView.vue'),
      meta: {
        title: 'Manter Pessoas | AgroContas',
        requiresAuth: true,
      },
    },
    {
      path: '/classificacoes',
      name: 'classificacoes',
      component: () => import('@/views/ClassificacoesView.vue'),
      meta: {
        title: 'Manter Classificações | AgroContas',
        requiresAuth: true,
      },
    },
    {
      path: '/movimentos',
      name: 'movimentos',
      component: () => import('@/views/MovimentosView.vue'),
      meta: {
        title: 'Movimento de Contas | AgroContas',
        requiresAuth: true,
      },
    },
  ],
})

// ── Navigation Guard ─────────────────────────────────────────────────────────
router.beforeEach((to, _from, next) => {
  // Atualiza título da página
  const title = to.meta.title as string | undefined
  if (title) document.title = title

  const isAuthenticated = !!getStoredToken()
  const requiresAuth = to.meta.requiresAuth as boolean | undefined
  const isPublic = to.meta.public as boolean | undefined

  if (requiresAuth && !isAuthenticated) {
    // Rota protegida sem autenticação → redireciona para login
    next({ name: 'auth' })
  } else if (isPublic && isAuthenticated) {
    // Usuário já logado tentando acessar /auth → redireciona para home
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router
