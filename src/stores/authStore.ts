/**
 * Store Pinia para autenticação — estado do usuário logado e ações de sessão
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UsuarioDTO } from '@/types/auth'
import {
  authLogin,
  authRegister,
  authGetMe,
  saveSession,
  clearSession,
  getStoredToken,
  getStoredUser,
} from '@/services/auth'
import type { UserLoginRequest, UserRegisterRequest } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // ─── State ──────────────────────────────────────────────────────────────
  const token = ref<string | null>(getStoredToken())
  const usuario = ref<UsuarioDTO | null>(getStoredUser())
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ─── Getters ─────────────────────────────────────────────────────────────
  const isAuthenticated = computed(() => !!token.value && !!usuario.value)
  const nomeUsuario = computed(() => usuario.value?.nome ?? '')
  const loginUsuario = computed(() => usuario.value?.login ?? '')
  const perfilUsuario = computed(() => usuario.value?.perfil ?? 'COMUM')
  const iniciaisUsuario = computed(() => {
    const nome = nomeUsuario.value
    if (!nome) return '?'
    const partes = nome.trim().split(/\s+/)
    if (partes.length === 1) return partes[0][0].toUpperCase()
    return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase()
  })

  // ─── Actions ─────────────────────────────────────────────────────────────
  async function login(data: UserLoginRequest): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const resp = await authLogin(data)
      token.value = resp.access_token
      usuario.value = resp.usuario
      saveSession(resp.access_token, resp.usuario)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Erro ao fazer login'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function register(data: UserRegisterRequest): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const resp = await authRegister(data)
      token.value = resp.access_token
      usuario.value = resp.usuario
      saveSession(resp.access_token, resp.usuario)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Erro ao cadastrar'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchMe(): Promise<void> {
    if (!token.value) return
    try {
      const me = await authGetMe()
      usuario.value = me
      saveSession(token.value, me)
    } catch {
      // Token inválido — limpa sessão
      logout()
    }
  }

  function logout(): void {
    token.value = null
    usuario.value = null
    error.value = null
    clearSession()
  }

  function clearError(): void {
    error.value = null
  }

  return {
    token,
    usuario,
    loading,
    error,
    isAuthenticated,
    nomeUsuario,
    loginUsuario,
    perfilUsuario,
    iniciaisUsuario,
    login,
    register,
    fetchMe,
    logout,
    clearError,
  }
})
