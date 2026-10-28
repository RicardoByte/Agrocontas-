<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

// ─── Controle de Aba Ativa ──────────────────────────────────
const activeTab = ref<'login' | 'register'>('login')

// ─── Formulário Login ───────────────────────────────────────
const loginForm = reactive({
  login: '',
  senha: '',
  lembrar: true,
})

// ─── Formulário Cadastro ────────────────────────────────────
const registerForm = reactive({
  nome: '',
  login: '',
  email: '',
  cpf_cnpj: '',
  senha: '',
  confirmarSenha: '',
})

// Visibilidade de senhas
const mostrarSenhaLogin = ref(false)
const mostrarSenhaRegister = ref(false)
const mostrarConfirmarSenha = ref(false)

// ─── Validações Reativas ────────────────────────────────────
const registerErrors = computed(() => {
  const erros: Record<string, string> = {}
  if (registerForm.senha && registerForm.confirmarSenha && registerForm.senha !== registerForm.confirmarSenha) {
    erros.confirmarSenha = 'As senhas não coincidem'
  }
  if (registerForm.senha && registerForm.senha.length < 4) {
    erros.senha = 'A senha deve ter no mínimo 4 caracteres'
  }
  return erros
})

const loginFormValid = computed(() => loginForm.login.trim().length > 0 && loginForm.senha.trim().length > 0)

const registerFormValid = computed(() =>
  registerForm.nome.trim().length > 0 &&
  registerForm.login.trim().length > 0 &&
  registerForm.senha.trim().length >= 4 &&
  registerForm.senha === registerForm.confirmarSenha &&
  Object.keys(registerErrors.value).length === 0
)

// ─── Handlers de Submissão ──────────────────────────────────
async function handleLogin() {
  if (!loginFormValid.value) return
  try {
    await authStore.login({
      login: loginForm.login.trim(),
      senha: loginForm.senha,
    })
    router.push('/')
  } catch {
    // erro exibido através de authStore.error
  }
}

async function handleRegister() {
  if (!registerFormValid.value) return
  try {
    await authStore.register({
      login: registerForm.login.trim(),
      senha: registerForm.senha,
      nome: registerForm.nome.trim(),
      cpf_cnpj: registerForm.cpf_cnpj.trim() || null,
      perfil_id: 2,
    })
    router.push('/')
  } catch {
    // erro exibido através de authStore.error
  }
}

function switchTab(tab: 'login' | 'register') {
  activeTab.value = tab
  authStore.clearError()
}

function handleForgotPassword() {
  alert('Para redefinir sua senha, entre em contato com o suporte ou administrador do sistema.')
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-container">
      <!-- ── Painel Esquerdo: Identidade Institucional Floresta (#154326) ── -->
      <aside class="auth-brand-side">
        <!-- Topo da Marca -->
        <div class="auth-brand-top">
          <div class="auth-brand-logo">
            <div class="auth-logo-badge">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="auth-logo-badge-icon" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z" />
                <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
              </svg>
            </div>
            <div class="auth-brand-text">
              <h1 class="auth-brand-title">AGROTECH</h1>
              <span class="auth-brand-subtitle">PRECISION SYSTEM</span>
            </div>
          </div>

          <div class="auth-brand-safra">
            <span class="auth-brand-safra-dot" />
            <span>SAFRA 2024/25</span>
          </div>
        </div>

        <!-- Conteúdo Central -->
        <div class="auth-brand-body">
          <div class="auth-brand-tag">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 2v20m0-20L3 11m9-9l9 9"/>
            </svg>
            <span>Gestão Familiar Rural Consolidada</span>
          </div>

          <h2 class="auth-brand-headline">
            Gestão Financeira &amp; Fiscal Inteligente para o Produtor Rural.
          </h2>

          <p class="auth-brand-desc">
            Controle unificado de receitas, despesas, maquinários e cruzamento tributário automatizado em tempo real da Fazenda Bela Vista.
          </p>
        </div>

        <!-- Rodapé do Card Esquerdo -->
        <div class="auth-brand-footer">
          <div class="auth-brand-accent-dot" />
        </div>
      </aside>

      <!-- ── Painel Direito: Formulário com Abas (Branco) ── -->
      <main class="auth-form-side">
        <div>
          <!-- Navegação por Abas -->
          <div class="auth-nav-tabs" role="tablist">
            <button
              id="tab-btn-login"
              type="button"
              role="tab"
              :aria-selected="activeTab === 'login'"
              class="auth-tab-btn"
              :class="{ 'auth-tab-btn--active': activeTab === 'login' }"
              @click="switchTab('login')"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>
                <polyline points="10 17 15 12 10 7"/>
                <line x1="15" y1="12" x2="3" y2="12"/>
              </svg>
              <span>Entrar</span>
            </button>

            <button
              id="tab-btn-register"
              type="button"
              role="tab"
              :aria-selected="activeTab === 'register'"
              class="auth-tab-btn"
              :class="{ 'auth-tab-btn--active': activeTab === 'register' }"
              @click="switchTab('register')"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <line x1="19" y1="8" x2="19" y2="14"/>
                <line x1="22" y1="11" x2="16" y2="11"/>
              </svg>
              <span>Cadastrar</span>
            </button>
          </div>

          <!-- ══════════════ ABA LOGIN ══════════════ -->
          <div v-show="activeTab === 'login'" role="tabpanel" aria-labelledby="tab-btn-login">
            <header class="auth-section-header">
              <div class="auth-section-subline">
                <span class="auth-pre-title">PAINEL ADMINISTRATIVO DA FAZENDA</span>
                <span class="auth-safra-hint">Safra Corrente</span>
              </div>
              <h2 class="auth-form-title">Entrar na sua Conta</h2>
              <p class="auth-form-desc">
                Informe suas credenciais registradas ou use avaliação direta de campo via WhatsApp.
              </p>
            </header>

            <!-- Alerta de Erro -->
            <div v-if="authStore.error && activeTab === 'login'" class="auth-error-banner" role="alert">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="18" height="18" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <span>{{ authStore.error }}</span>
            </div>

            <form id="form-login" class="auth-form-body" @submit.prevent="handleLogin">
              <!-- Usuário / CPF / E-mail -->
              <div class="auth-field-group">
                <div class="auth-field-header">
                  <label for="login-id" class="auth-label">CPF, E-mail ou Nome de Usuário</label>
                  <span class="auth-label-hint">000.000.000-00</span>
                </div>
                <div class="auth-input-container">
                  <span class="auth-input-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" stroke-width="1.8">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                      <circle cx="12" cy="7" r="4"/>
                    </svg>
                  </span>
                  <input
                    id="login-id"
                    v-model.trim="loginForm.login"
                    type="text"
                    class="auth-input"
                    placeholder="000.000.000-00 ou fiscal@fazendabelavista.agro.br"
                    autocomplete="username"
                    required
                  />
                </div>
              </div>

              <!-- Senha de Acesso -->
              <div class="auth-field-group">
                <div class="auth-field-header">
                  <label for="login-pwd" class="auth-label">Senha de Acesso</label>
                  <span class="auth-label-hint">Mínimo de 8 caracteres</span>
                </div>
                <div class="auth-input-container">
                  <span class="auth-input-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" stroke-width="1.8">
                      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                      <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                    </svg>
                  </span>
                  <input
                    id="login-pwd"
                    v-model="loginForm.senha"
                    :type="mostrarSenhaLogin ? 'text' : 'password'"
                    class="auth-input auth-input--has-toggle"
                    placeholder="••••••••••••"
                    autocomplete="current-password"
                    required
                  />
                  <button
                    type="button"
                    class="auth-input-eye"
                    :title="mostrarSenhaLogin ? 'Ocultar senha' : 'Exibir senha'"
                    @click="mostrarSenhaLogin = !mostrarSenhaLogin"
                  >
                    <svg v-if="!mostrarSenhaLogin" viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" stroke-width="1.8">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" stroke-width="1.8">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24M1 1l22 22"/>
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Opções: Lembrar e Recuperar Senha -->
              <div class="auth-options-row">
                <label class="auth-checkbox-label">
                  <input
                    v-model="loginForm.lembrar"
                    type="checkbox"
                    class="auth-checkbox"
                  />
                  <span>Lembrar neste computador da sede</span>
                </label>

                <a href="#recuperar" class="auth-forgot-link" @click.prevent="handleForgotPassword">
                  <span>Esqueceu sua senha?</span>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="12" height="12" stroke-width="2.2">
                    <line x1="7" y1="17" x2="17" y2="7"/>
                    <polyline points="7 7 17 7 17 17"/>
                  </svg>
                </a>
              </div>

              <!-- Botão Principal -->
              <button
                id="btn-login-submit"
                type="submit"
                class="auth-submit-btn"
                :disabled="!loginFormValid || authStore.loading"
              >
                <span v-if="authStore.loading" class="auth-btn-spinner" />
                <template v-else>
                  <span>ACESSAR O SISTEMA</span>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="15" height="15" stroke-width="2.4">
                    <line x1="7" y1="7" x2="17" y2="17"/>
                    <polyline points="7 17 17 17 17 7"/>
                  </svg>
                </template>
              </button>
            </form>

            <div class="auth-switch-box">
              <span>Não tem conta?</span>
              <button type="button" class="auth-switch-btn" @click="switchTab('register')">
                <span>Cadastre-se gratuitamente</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="12" height="12" stroke-width="2.2">
                  <line x1="7" y1="17" x2="17" y2="7"/>
                  <polyline points="7 7 17 7 17 17"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- ══════════════ ABA CADASTRAR ══════════════ -->
          <div v-show="activeTab === 'register'" role="tabpanel" aria-labelledby="tab-btn-register">
            <header class="auth-section-header">
              <div class="auth-section-subline">
                <span class="auth-pre-title">PAINEL ADMINISTRATIVO DA FAZENDA</span>
                <span class="auth-safra-hint">Safra Corrente</span>
              </div>
              <h2 class="auth-form-title">Criar Conta na Fazenda</h2>
              <p class="auth-form-desc">
                Campos estruturados para cadastro rural e controle de acesso institucional.
              </p>
            </header>

            <!-- Alerta de Erro -->
            <div v-if="authStore.error && activeTab === 'register'" class="auth-error-banner" role="alert">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="18" height="18" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <span>{{ authStore.error }}</span>
            </div>

            <form id="form-register" class="auth-form-body" @submit.prevent="handleRegister">
              <!-- Nome Completo -->
              <div class="auth-field-group">
                <div class="auth-field-header">
                  <label for="reg-nome" class="auth-label">
                    <span>Nome Completo</span>
                    <span class="auth-req-star">*</span>
                  </label>
                </div>
                <div class="auth-input-container">
                  <span class="auth-input-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" stroke-width="1.8">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                      <circle cx="12" cy="7" r="4"/>
                    </svg>
                  </span>
                  <input
                    id="reg-nome"
                    v-model.trim="registerForm.nome"
                    type="text"
                    class="auth-input"
                    placeholder="Ex: Beltrano da Silva"
                    autocomplete="name"
                    required
                  />
                </div>
              </div>

              <!-- Linha dupla: CPF/CNPJ e E-mail Institucional -->
              <div class="auth-field-group auth-field-group--row">
                <div>
                  <div class="auth-field-header">
                    <label for="reg-cpf" class="auth-label">CPF ou CNPJ</label>
                  </div>
                  <div class="auth-input-container">
                    <span class="auth-input-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" stroke-width="1.8">
                        <rect x="3" y="4" width="18" height="16" rx="2"/>
                        <line x1="7" y1="8" x2="17" y2="8"/>
                        <line x1="7" y1="12" x2="17" y2="12"/>
                        <line x1="7" y1="16" x2="12" y2="16"/>
                      </svg>
                    </span>
                    <input
                      id="reg-cpf"
                      v-model.trim="registerForm.cpf_cnpj"
                      type="text"
                      class="auth-input"
                      placeholder="000.000.000-00"
                    />
                  </div>
                </div>

                <div>
                  <div class="auth-field-header">
                    <label for="reg-email" class="auth-label">E-mail Institucional</label>
                  </div>
                  <div class="auth-input-container">
                    <span class="auth-input-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" stroke-width="1.8">
                        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                        <polyline points="22,6 12,13 2,6"/>
                      </svg>
                    </span>
                    <input
                      id="reg-email"
                      v-model.trim="registerForm.email"
                      type="email"
                      class="auth-input"
                      placeholder="fiscal@fazenda.agro.br"
                    />
                  </div>
                </div>
              </div>

              <!-- Nome de Usuário -->
              <div class="auth-field-group">
                <div class="auth-field-header">
                  <label for="reg-login" class="auth-label">
                    <span>Nome de Usuário</span>
                    <span class="auth-req-star">*</span>
                  </label>
                  <span class="auth-label-hint">Login no sistema</span>
                </div>
                <div class="auth-input-container">
                  <span class="auth-input-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" stroke-width="1.8">
                      <circle cx="12" cy="12" r="4"/>
                      <path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-3.92 7.94"/>
                    </svg>
                  </span>
                  <input
                    id="reg-login"
                    v-model.trim="registerForm.login"
                    type="text"
                    class="auth-input"
                    placeholder="beltrano.silva"
                    autocomplete="username"
                    required
                  />
                </div>
              </div>

              <!-- Linha dupla: Senha e Confirmação -->
              <div class="auth-field-group auth-field-group--row">
                <div>
                  <div class="auth-field-header">
                    <label for="reg-pwd" class="auth-label">
                      <span>Senha</span>
                      <span class="auth-req-star">*</span>
                    </label>
                  </div>
                  <div class="auth-input-container" :class="{ 'auth-input-container--error': registerErrors.senha }">
                    <span class="auth-input-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" stroke-width="1.8">
                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                      </svg>
                    </span>
                    <input
                      id="reg-pwd"
                      v-model="registerForm.senha"
                      :type="mostrarSenhaRegister ? 'text' : 'password'"
                      class="auth-input auth-input--has-toggle"
                      placeholder="Mínimo 4 caracteres"
                      autocomplete="new-password"
                      required
                    />
                    <button
                      type="button"
                      class="auth-input-eye"
                      @click="mostrarSenhaRegister = !mostrarSenhaRegister"
                    >
                      <svg v-if="!mostrarSenhaRegister" viewBox="0 0 24 24" fill="none" stroke="currentColor" width="15" height="15" stroke-width="1.8">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                      </svg>
                      <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" width="15" height="15" stroke-width="1.8">
                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24M1 1l22 22"/>
                      </svg>
                    </button>
                  </div>
                  <span v-if="registerErrors.senha" class="auth-field-error">{{ registerErrors.senha }}</span>
                </div>

                <div>
                  <div class="auth-field-header">
                    <label for="reg-pwd-conf" class="auth-label">
                      <span>Confirmar</span>
                      <span class="auth-req-star">*</span>
                    </label>
                  </div>
                  <div class="auth-input-container" :class="{ 'auth-input-container--error': registerErrors.confirmarSenha }">
                    <span class="auth-input-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" stroke-width="1.8">
                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                      </svg>
                    </span>
                    <input
                      id="reg-pwd-conf"
                      v-model="registerForm.confirmarSenha"
                      :type="mostrarConfirmarSenha ? 'text' : 'password'"
                      class="auth-input auth-input--has-toggle"
                      placeholder="Repita a senha"
                      autocomplete="new-password"
                      required
                    />
                    <button
                      type="button"
                      class="auth-input-eye"
                      @click="mostrarConfirmarSenha = !mostrarConfirmarSenha"
                    >
                      <svg v-if="!mostrarConfirmarSenha" viewBox="0 0 24 24" fill="none" stroke="currentColor" width="15" height="15" stroke-width="1.8">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                      </svg>
                      <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" width="15" height="15" stroke-width="1.8">
                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24M1 1l22 22"/>
                      </svg>
                    </button>
                  </div>
                  <span v-if="registerErrors.confirmarSenha" class="auth-field-error">{{ registerErrors.confirmarSenha }}</span>
                </div>
              </div>

              <!-- Botão Principal de Cadastro -->
              <button
                id="btn-register-submit"
                type="submit"
                class="auth-submit-btn"
                :disabled="!registerFormValid || authStore.loading"
              >
                <span v-if="authStore.loading" class="auth-btn-spinner" />
                <template v-else>
                  <span>CRIAR CONTA NA FAZENDA</span>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="15" height="15" stroke-width="2.4">
                    <line x1="7" y1="7" x2="17" y2="17"/>
                    <polyline points="7 17 17 17 17 7"/>
                  </svg>
                </template>
              </button>
            </form>

            <div class="auth-switch-box">
              <span>Já possui conta?</span>
              <button type="button" class="auth-switch-btn" @click="switchTab('login')">
                <span>Fazer login</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="12" height="12" stroke-width="2.2">
                  <line x1="7" y1="17" x2="17" y2="7"/>
                  <polyline points="7 7 17 7 17 17"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- ── Rodapé de Segurança e Versão (Preservado fiel ao design) ── -->
        <footer class="auth-security-footer">
          <div class="auth-security-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            <span>Ambiente seguro e criptografado</span>
          </div>

          <span class="auth-version-badge">V2.5 AGROTECH • VUE3 + FASTAPI</span>
        </footer>
      </main>
    </div>
  </div>
</template>

<style src="@/assets/styles/auth.css"></style>
