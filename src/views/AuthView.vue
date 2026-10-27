<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

// ─── Aba ativa ─────────────────────────────────────────────────────────────
const activeTab = ref<'login' | 'register'>('login')

// ─── Formulário Login ───────────────────────────────────────────────────────
const loginForm = reactive({
  login: '',
  senha: '',
})

// ─── Formulário Cadastro ────────────────────────────────────────────────────
const registerForm = reactive({
  nome: '',
  login: '',
  cpf_cnpj: '',
  senha: '',
  confirmarSenha: '',
})

const mostrarSenhaLogin = ref(false)
const mostrarSenhaRegister = ref(false)
const mostrarConfirmarSenha = ref(false)

// ─── Validações ─────────────────────────────────────────────────────────────
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

const loginFormValid = computed(() => loginForm.login.trim() && loginForm.senha.trim())
const registerFormValid = computed(() =>
  registerForm.nome.trim() &&
  registerForm.login.trim() &&
  registerForm.senha.trim() &&
  registerForm.confirmarSenha.trim() &&
  Object.keys(registerErrors.value).length === 0
)

// ─── Submits ─────────────────────────────────────────────────────────────────
async function handleLogin() {
  if (!loginFormValid.value) return
  try {
    await authStore.login({ login: loginForm.login, senha: loginForm.senha })
    router.push('/')
  } catch {
    // erro já está em authStore.error
  }
}

async function handleRegister() {
  if (!registerFormValid.value) return
  try {
    await authStore.register({
      login: registerForm.login,
      senha: registerForm.senha,
      nome: registerForm.nome,
      cpf_cnpj: registerForm.cpf_cnpj || null,
      perfil_id: 2,
    })
    router.push('/')
  } catch {
    // erro já está em authStore.error
  }
}

function switchTab(tab: 'login' | 'register') {
  activeTab.value = tab
  authStore.clearError()
}
</script>

<template>
  <div class="auth-page">
    <!-- Background decorativo -->
    <div class="auth-bg">
      <div class="auth-bg-orb auth-bg-orb--1" />
      <div class="auth-bg-orb auth-bg-orb--2" />
      <div class="auth-bg-orb auth-bg-orb--3" />
      <div class="auth-bg-grid" />
    </div>

    <!-- Coluna esquerda — Branding -->
    <div class="auth-branding">
      <div class="auth-branding-inner">
        <!-- Logo -->
        <div class="auth-logo">
          <div class="auth-logo-icon">
            <svg viewBox="0 0 24 24" fill="none" class="auth-logo-svg">
              <path d="M12 2L2 7l10 5 10-5-10-5z" fill="currentColor" opacity="0.9"/>
              <path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" fill="none"/>
            </svg>
          </div>
          <div class="auth-logo-text">
            <span class="auth-logo-name">AgroContas</span>
            <span class="auth-logo-tagline">Precision System</span>
          </div>
        </div>

        <!-- Headline -->
        <div class="auth-headline">
          <h1 class="auth-headline-title">Gestão financeira<br/><span class="auth-headline-accent">para o campo</span></h1>
          <p class="auth-headline-desc">
            Controle suas contas a pagar e receber, extraia notas fiscais com IA e tenha uma visão completa das suas finanças rurais.
          </p>
        </div>

        <!-- Features -->
        <ul class="auth-features">
          <li class="auth-feature-item">
            <div class="auth-feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <span>Extração automática de NF-e com IA Gemini</span>
          </li>
          <li class="auth-feature-item">
            <div class="auth-feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <span>Contas a pagar e receber por safra</span>
          </li>
          <li class="auth-feature-item">
            <div class="auth-feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <span>Relatórios completos de despesas e receitas</span>
          </li>
          <li class="auth-feature-item">
            <div class="auth-feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <span>Segurança com criptografia bcrypt + JWT</span>
          </li>
        </ul>

        <!-- Safra badge -->
        <div class="auth-safra-badge">
          <span class="auth-safra-dot" />
          SAFRA 2024/25 ATIVA
        </div>
      </div>
    </div>

    <!-- Coluna direita — Formulário -->
    <div class="auth-form-col">
      <div class="auth-card">
        <!-- Tabs -->
        <div class="auth-tabs" role="tablist">
          <button
            id="tab-login"
            role="tab"
            :aria-selected="activeTab === 'login'"
            class="auth-tab"
            :class="{ 'auth-tab--active': activeTab === 'login' }"
            @click="switchTab('login')"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="15" height="15">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4M10 17l5-5-5-5M15 12H3"/>
            </svg>
            Entrar
          </button>
          <button
            id="tab-register"
            role="tab"
            :aria-selected="activeTab === 'register'"
            class="auth-tab"
            :class="{ 'auth-tab--active': activeTab === 'register' }"
            @click="switchTab('register')"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="15" height="15">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M12.5 3.5a4 4 0 110 8 4 4 0 010-8zM20 8v6M23 11h-6"/>
            </svg>
            Cadastrar
          </button>
          <div class="auth-tab-indicator" :class="{ 'auth-tab-indicator--right': activeTab === 'register' }" />
        </div>

        <!-- ── PAINEL LOGIN ── -->
        <div v-show="activeTab === 'login'" class="auth-panel" role="tabpanel" aria-labelledby="tab-login">
          <div class="auth-panel-header">
            <h2 class="auth-panel-title">Bem-vindo de volta</h2>
            <p class="auth-panel-desc">Acesse sua conta para continuar</p>
          </div>

          <!-- Alerta de erro -->
          <div v-if="authStore.error && activeTab === 'login'" class="auth-alert auth-alert--error">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
              <circle cx="12" cy="12" r="10" stroke-width="1.75"/>
              <path stroke-linecap="round" stroke-width="1.75" d="M12 8v4M12 16h.01"/>
            </svg>
            {{ authStore.error }}
          </div>

          <form id="form-login" class="auth-form" @submit.prevent="handleLogin">
            <div class="form-field">
              <label for="login-username" class="form-label">Usuário</label>
              <div class="form-input-wrap">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="form-input-icon" width="16" height="16">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 11a4 4 0 100-8 4 4 0 000 8z"/>
                </svg>
                <input
                  id="login-username"
                  v-model.trim="loginForm.login"
                  type="text"
                  class="form-input"
                  placeholder="Seu nome de usuário"
                  autocomplete="username"
                  required
                />
              </div>
            </div>

            <div class="form-field">
              <div class="form-label-row">
                <label for="login-senha" class="form-label">Senha</label>
              </div>
              <div class="form-input-wrap">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="form-input-icon" width="16" height="16">
                  <rect x="3" y="11" width="18" height="11" rx="2" stroke-width="1.75"/>
                  <path stroke-linecap="round" stroke-width="1.75" d="M7 11V7a5 5 0 0110 0v4"/>
                </svg>
                <input
                  id="login-senha"
                  v-model="loginForm.senha"
                  :type="mostrarSenhaLogin ? 'text' : 'password'"
                  class="form-input form-input--padded-right"
                  placeholder="Sua senha"
                  autocomplete="current-password"
                  required
                />
                <button
                  type="button"
                  class="form-input-toggle"
                  :title="mostrarSenhaLogin ? 'Ocultar senha' : 'Mostrar senha'"
                  @click="mostrarSenhaLogin = !mostrarSenhaLogin"
                >
                  <svg v-if="!mostrarSenhaLogin" viewBox="0 0 24 24" fill="none" stroke="currentColor" width="15" height="15">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3" stroke-width="1.75"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" width="15" height="15">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24M1 1l22 22"/>
                  </svg>
                </button>
              </div>
            </div>

            <button
              id="btn-login-submit"
              type="submit"
              class="auth-btn-primary"
              :disabled="!loginFormValid || authStore.loading"
            >
              <span v-if="authStore.loading" class="auth-btn-spinner" />
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4M10 17l5-5-5-5M15 12H3"/>
              </svg>
              {{ authStore.loading ? 'Entrando...' : 'Entrar no Sistema' }}
            </button>
          </form>

          <p class="auth-switch-hint">
            Não tem conta?
            <button class="auth-link" @click="switchTab('register')">Cadastre-se gratuitamente</button>
          </p>
        </div>

        <!-- ── PAINEL CADASTRO ── -->
        <div v-show="activeTab === 'register'" class="auth-panel" role="tabpanel" aria-labelledby="tab-register">
          <div class="auth-panel-header">
            <h2 class="auth-panel-title">Criar sua conta</h2>
            <p class="auth-panel-desc">Preencha os dados para começar a usar</p>
          </div>

          <!-- Alerta de erro -->
          <div v-if="authStore.error && activeTab === 'register'" class="auth-alert auth-alert--error">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
              <circle cx="12" cy="12" r="10" stroke-width="1.75"/>
              <path stroke-linecap="round" stroke-width="1.75" d="M12 8v4M12 16h.01"/>
            </svg>
            {{ authStore.error }}
          </div>

          <form id="form-register" class="auth-form" @submit.prevent="handleRegister">
            <div class="form-field">
              <label for="reg-nome" class="form-label">Nome Completo <span class="form-required">*</span></label>
              <div class="form-input-wrap">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="form-input-icon" width="16" height="16">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 11a4 4 0 100-8 4 4 0 000 8z"/>
                </svg>
                <input
                  id="reg-nome"
                  v-model.trim="registerForm.nome"
                  type="text"
                  class="form-input"
                  placeholder="Seu nome completo"
                  autocomplete="name"
                  required
                />
              </div>
            </div>

            <div class="form-row-2">
              <div class="form-field">
                <label for="reg-login" class="form-label">Usuário <span class="form-required">*</span></label>
                <div class="form-input-wrap">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="form-input-icon" width="16" height="16">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"/>
                  </svg>
                  <input
                    id="reg-login"
                    v-model.trim="registerForm.login"
                    type="text"
                    class="form-input"
                    placeholder="Nome de usuário"
                    autocomplete="username"
                    required
                  />
                </div>
              </div>

              <div class="form-field">
                <label for="reg-cpf" class="form-label">CPF / CNPJ</label>
                <div class="form-input-wrap">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="form-input-icon" width="16" height="16">
                    <rect x="5" y="2" width="14" height="20" rx="2" stroke-width="1.75"/>
                    <path stroke-linecap="round" stroke-width="1.75" d="M9 7h6M9 11h6M9 15h4"/>
                  </svg>
                  <input
                    id="reg-cpf"
                    v-model.trim="registerForm.cpf_cnpj"
                    type="text"
                    class="form-input"
                    placeholder="Opcional"
                    autocomplete="off"
                  />
                </div>
              </div>
            </div>

            <div class="form-field">
              <label for="reg-senha" class="form-label">Senha <span class="form-required">*</span></label>
              <div class="form-input-wrap">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="form-input-icon" width="16" height="16">
                  <rect x="3" y="11" width="18" height="11" rx="2" stroke-width="1.75"/>
                  <path stroke-linecap="round" stroke-width="1.75" d="M7 11V7a5 5 0 0110 0v4"/>
                </svg>
                <input
                  id="reg-senha"
                  v-model="registerForm.senha"
                  :type="mostrarSenhaRegister ? 'text' : 'password'"
                  class="form-input form-input--padded-right"
                  :class="{ 'form-input--error': registerErrors.senha }"
                  placeholder="Mínimo 4 caracteres"
                  autocomplete="new-password"
                  required
                />
                <button
                  type="button"
                  class="form-input-toggle"
                  @click="mostrarSenhaRegister = !mostrarSenhaRegister"
                >
                  <svg v-if="!mostrarSenhaRegister" viewBox="0 0 24 24" fill="none" stroke="currentColor" width="15" height="15">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3" stroke-width="1.75"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" width="15" height="15">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24M1 1l22 22"/>
                  </svg>
                </button>
              </div>
              <span v-if="registerErrors.senha" class="form-error-msg">{{ registerErrors.senha }}</span>
            </div>

            <div class="form-field">
              <label for="reg-confirmar" class="form-label">Confirmar Senha <span class="form-required">*</span></label>
              <div class="form-input-wrap">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="form-input-icon" width="16" height="16">
                  <rect x="3" y="11" width="18" height="11" rx="2" stroke-width="1.75"/>
                  <path stroke-linecap="round" stroke-width="1.75" d="M7 11V7a5 5 0 0110 0v4"/>
                </svg>
                <input
                  id="reg-confirmar"
                  v-model="registerForm.confirmarSenha"
                  :type="mostrarConfirmarSenha ? 'text' : 'password'"
                  class="form-input form-input--padded-right"
                  :class="{ 'form-input--error': registerErrors.confirmarSenha }"
                  placeholder="Repita a senha"
                  autocomplete="new-password"
                  required
                />
                <button
                  type="button"
                  class="form-input-toggle"
                  @click="mostrarConfirmarSenha = !mostrarConfirmarSenha"
                >
                  <svg v-if="!mostrarConfirmarSenha" viewBox="0 0 24 24" fill="none" stroke="currentColor" width="15" height="15">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3" stroke-width="1.75"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" width="15" height="15">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24M1 1l22 22"/>
                  </svg>
                </button>
              </div>
              <span v-if="registerErrors.confirmarSenha" class="form-error-msg">{{ registerErrors.confirmarSenha }}</span>
            </div>

            <button
              id="btn-register-submit"
              type="submit"
              class="auth-btn-primary"
              :disabled="!registerFormValid || authStore.loading"
            >
              <span v-if="authStore.loading" class="auth-btn-spinner" />
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M12.5 3.5a4 4 0 110 8 4 4 0 010-8zM20 8v6M23 11h-6"/>
              </svg>
              {{ authStore.loading ? 'Criando conta...' : 'Criar Conta Gratuita' }}
            </button>
          </form>

          <p class="auth-switch-hint">
            Já tem conta?
            <button class="auth-link" @click="switchTab('login')">Fazer login</button>
          </p>
        </div>
      </div>

      <!-- Footer -->
      <p class="auth-footer">
        © 2025 AgroContas · Todos os direitos reservados
      </p>
    </div>
  </div>
</template>

<style scoped>
/* ── Layout Principal ────────────────────────────────────────────────── */
.auth-page {
  min-height: 100vh;
  display: flex;
  position: relative;
  overflow: hidden;
  background: #0d1a0f;
}

/* ── Background decorativo ────────────────────────────────────────────── */
.auth-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.auth-bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.25;
}

.auth-bg-orb--1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, #1d6f37, transparent);
  top: -150px;
  left: -100px;
  animation: orb-float 8s ease-in-out infinite;
}

.auth-bg-orb--2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #0a4a1e, transparent);
  bottom: -80px;
  left: 300px;
  animation: orb-float 11s ease-in-out infinite reverse;
}

.auth-bg-orb--3 {
  width: 350px;
  height: 350px;
  background: radial-gradient(circle, #4ade80, transparent);
  opacity: 0.1;
  top: 40%;
  right: 15%;
  animation: orb-float 9s ease-in-out infinite;
}

.auth-bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(74, 222, 128, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(74, 222, 128, 0.04) 1px, transparent 1px);
  background-size: 40px 40px;
}

@keyframes orb-float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-30px) scale(1.05); }
}

/* ── Coluna Branding (esquerda) ─────────────────────────────────────── */
.auth-branding {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem 3rem 3rem;
  position: relative;
  z-index: 1;
}

.auth-branding-inner {
  max-width: 440px;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

/* Logo */
.auth-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.auth-logo-icon {
  width: 46px;
  height: 46px;
  background: linear-gradient(135deg, #1d6f37, #4ade80);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(29, 111, 55, 0.4);
}

.auth-logo-svg {
  width: 24px;
  height: 24px;
  color: #fff;
}

.auth-logo-text {
  display: flex;
  flex-direction: column;
  gap: 0;
  line-height: 1.1;
}

.auth-logo-name {
  font-size: 1.2rem;
  font-weight: 800;
  color: #e8f5eb;
  letter-spacing: -0.03em;
  text-transform: uppercase;
}

.auth-logo-tagline {
  font-size: 0.65rem;
  font-weight: 500;
  color: #4ade80;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

/* Headline */
.auth-headline-title {
  font-size: clamp(2rem, 3vw, 2.8rem);
  font-weight: 800;
  color: #e8f5eb;
  line-height: 1.15;
  letter-spacing: -0.03em;
}

.auth-headline-accent {
  color: #4ade80;
}

.auth-headline-desc {
  margin-top: 1rem;
  font-size: 0.95rem;
  color: #7a9b7e;
  line-height: 1.7;
}

/* Features */
.auth-features {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.auth-feature-item {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  font-size: 0.875rem;
  color: #c8d8c9;
}

.auth-feature-icon {
  width: 26px;
  height: 26px;
  background: rgba(74, 222, 128, 0.12);
  border: 1px solid rgba(74, 222, 128, 0.25);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4ade80;
  flex-shrink: 0;
}

/* Safra badge */
.auth-safra-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.72rem;
  font-weight: 700;
  color: #4ade80;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.25);
  border-radius: 99px;
  padding: 0.4rem 0.9rem;
  width: fit-content;
}

.auth-safra-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #4ade80;
  box-shadow: 0 0 8px rgba(74, 222, 128, 0.7);
  animation: pulse-dot 2s ease infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.8); }
}

/* ── Coluna Formulário (direita) ─────────────────────────────────────── */
.auth-form-col {
  width: 480px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 2.5rem;
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.02);
  border-left: 1px solid rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(20px);
  gap: 1.25rem;
}

/* Card do formulário */
.auth-card {
  width: 100%;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35), 0 0 0 1px rgba(255,255,255,0.05);
  overflow: hidden;
}

/* ── Tabs ─────────────────────────────────────────────────────────────── */
.auth-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  position: relative;
  background: #f7faf7;
  border-bottom: 1px solid #e0e8e1;
}

.auth-tab {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  padding: 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b8a6f;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
  font-family: inherit;
  position: relative;
  z-index: 1;
}

.auth-tab--active {
  color: #1d6f37;
}

.auth-tab-indicator {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 50%;
  height: 2.5px;
  background: linear-gradient(90deg, #1d6f37, #4ade80);
  border-radius: 2px 2px 0 0;
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.auth-tab-indicator--right {
  transform: translateX(100%);
}

/* ── Painéis ─────────────────────────────────────────────────────────── */
.auth-panel {
  padding: 1.75rem 2rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.auth-panel-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.auth-panel-title {
  font-size: 1.3rem;
  font-weight: 800;
  color: #1a2e1e;
  letter-spacing: -0.02em;
}

.auth-panel-desc {
  font-size: 0.85rem;
  color: #6b8a6f;
}

/* ── Alert ─────────────────────────────────────────────────────────── */
.auth-alert {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  padding: 0.8rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
  line-height: 1.5;
  animation: slide-down 0.2s ease;
}

.auth-alert--error {
  background: rgba(220, 38, 38, 0.07);
  border: 1px solid rgba(220, 38, 38, 0.25);
  color: #b91c1c;
}

@keyframes slide-down {
  from { opacity: 0; transform: translateY(-6px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── Formulário ──────────────────────────────────────────────────────── */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #3d5c42;
  display: flex;
  align-items: center;
  gap: 0.2rem;
}

.form-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.form-required {
  color: #dc2626;
}

.form-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.form-input-icon {
  position: absolute;
  left: 0.75rem;
  color: #9ab09d;
  pointer-events: none;
  flex-shrink: 0;
}

.form-input {
  width: 100%;
  height: 42px;
  padding: 0 0.85rem 0 2.35rem;
  border: 1.5px solid #e0e8e1;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #1a2e1e;
  background: #f7faf7;
  font-family: inherit;
  transition: border-color 0.15s, box-shadow 0.15s, background 0.15s;
  outline: none;
}

.form-input::placeholder {
  color: #b0c4b2;
}

.form-input:focus {
  border-color: #1d6f37;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(29, 111, 55, 0.1);
}

.form-input--padded-right {
  padding-right: 2.5rem;
}

.form-input--error {
  border-color: #dc2626 !important;
  background: rgba(220, 38, 38, 0.03);
}

.form-input--error:focus {
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}

.form-input-toggle {
  position: absolute;
  right: 0.6rem;
  background: none;
  border: none;
  color: #9ab09d;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  transition: color 0.15s;
}

.form-input-toggle:hover {
  color: #3d5c42;
}

.form-error-msg {
  font-size: 0.76rem;
  color: #dc2626;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

/* ── Botão Principal ─────────────────────────────────────────────────── */
.auth-btn-primary {
  width: 100%;
  height: 46px;
  background: linear-gradient(135deg, #1d6f37, #2d9e50);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  font-family: inherit;
  letter-spacing: 0.01em;
  transition: all 0.2s;
  box-shadow: 0 4px 16px rgba(29, 111, 55, 0.3);
  margin-top: 0.25rem;
}

.auth-btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #16562b, #27894a);
  box-shadow: 0 6px 24px rgba(29, 111, 55, 0.4);
  transform: translateY(-1px);
}

.auth-btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.auth-btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Spinner */
.auth-btn-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── Links de troca de aba ─────────────────────────────────────────────── */
.auth-switch-hint {
  font-size: 0.82rem;
  color: #6b8a6f;
  text-align: center;
}

.auth-link {
  background: none;
  border: none;
  color: #1d6f37;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  font-size: inherit;
  padding: 0;
  text-decoration: underline;
  text-underline-offset: 2px;
  transition: color 0.15s;
}

.auth-link:hover {
  color: #2d9e50;
}

/* ── Footer ────────────────────────────────────────────────────────────── */
.auth-footer {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.2);
  text-align: center;
}

/* ── Responsividade ───────────────────────────────────────────────────── */
@media (max-width: 900px) {
  .auth-page {
    flex-direction: column;
  }

  .auth-branding {
    padding: 2.5rem 2rem 1.5rem;
    justify-content: flex-start;
  }

  .auth-branding-inner {
    gap: 1.5rem;
  }

  .auth-features,
  .auth-safra-badge {
    display: none;
  }

  .auth-form-col {
    width: 100%;
    border-left: none;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    padding: 1.5rem 1.25rem 2.5rem;
  }
}

@media (max-width: 480px) {
  .form-row-2 {
    grid-template-columns: 1fr;
  }
}
</style>
