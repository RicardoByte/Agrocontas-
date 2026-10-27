/**
 * Serviços de autenticação — login, cadastro e gestão de sessão JWT
 */
import { api } from './api'
import type { AuthResponse, UserLoginRequest, UserRegisterRequest, UsuarioDTO } from '@/types/auth'
import type { AxiosError } from 'axios'

const TOKEN_KEY = 'agrocontas_token'
const USER_KEY = 'agrocontas_user'

// ─── Token helpers ────────────────────────────────────────────────────────
export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function getStoredUser(): UsuarioDTO | null {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as UsuarioDTO
  } catch {
    return null
  }
}

export function saveSession(token: string, usuario: UsuarioDTO): void {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(usuario))
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

// ─── Injeção do token no header Authorization ─────────────────────────────
api.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token) {
    config.headers = config.headers ?? {}
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

function handleApiError(error: unknown): never {
  const axiosError = error as AxiosError<{ detail: string }>
  const message =
    axiosError.response?.data?.detail ??
    axiosError.message ??
    'Erro desconhecido ao conectar com o servidor'
  throw new Error(message)
}

// ─── Auth API calls ────────────────────────────────────────────────────────
export async function authLogin(data: UserLoginRequest): Promise<AuthResponse> {
  try {
    const response = await api.post<AuthResponse>('/api/v1/auth/login', data)
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

export async function authRegister(data: UserRegisterRequest): Promise<AuthResponse> {
  try {
    const response = await api.post<AuthResponse>('/api/v1/auth/register', data)
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}

export async function authGetMe(): Promise<UsuarioDTO> {
  try {
    const response = await api.get<UsuarioDTO>('/api/v1/auth/me')
    return response.data
  } catch (error) {
    handleApiError(error)
  }
}
