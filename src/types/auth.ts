/**
 * Tipos TypeScript para Autenticação e Usuários do AgroContas
 */

export interface UsuarioDTO {
  id: number
  login: string
  nome: string
  perfil: string
  pessoa_id: number
  ativo: boolean
  created_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  usuario: UsuarioDTO
}

export interface UserLoginRequest {
  login: string
  senha: string
}

export interface UserRegisterRequest {
  login: string
  senha: string
  nome: string
  cpf_cnpj?: string | null
  perfil_id?: number
}
