<script setup lang="ts">
import { useInvoiceStore } from '@/stores/invoiceStore'
import InvoiceUploader from '@/components/InvoiceUploader.vue'
import JsonViewer from '@/components/JsonViewer.vue'

const store = useInvoiceStore()
</script>

<template>
  <main class="page">
    <!-- ── Hero / Header ─────────────────────────────────── -->
    <header class="hero">
      <div class="hero__badge">
        <span class="badge-dot" />
        Powered by Gemini AI
      </div>
      <h1 class="hero__title">Extração de Dados de<br /><span class="hero__title-accent">Nota Fiscal</span></h1>
      <p class="hero__subtitle">
        Carregue um PDF de nota fiscal e extraia os dados automaticamente usando IA
      </p>
    </header>

    <!-- ── Card Principal ────────────────────────────────── -->
    <div class="card">
      <!-- Uploader -->
      <InvoiceUploader />

      <!-- Divisor (só aparece quando há dados) -->
      <div v-if="store.hasData" class="divider" />

      <!-- Mensagem de erro -->
      <div v-if="store.isError" class="error-banner">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="error-icon">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <div>
          <strong>Erro na extração</strong>
          <p>{{ store.errorMessage }}</p>
        </div>
        <button class="error-close" @click="store.reset()">✕</button>
      </div>

      <!-- Viewer de dados extraídos -->
      <JsonViewer />
    </div>

    <!-- ── Footer ─────────────────────────────────────────── -->
    <footer class="page-footer">
      <span>AgroContas</span>
      <span class="footer-sep">·</span>
      <span>Sprint 1 — Extração de NF-e</span>
    </footer>
  </main>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem 1.25rem 2rem;
  gap: 1.75rem;
}

/* ── Hero ─────────────────────────────────────────────── */
.hero {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  max-width: 560px;
}

.hero__badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.25);
  color: #a5b4fc;
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.3rem 0.875rem;
  border-radius: 100px;
  letter-spacing: 0.025em;
}

.badge-dot {
  width: 6px;
  height: 6px;
  background: #6366f1;
  border-radius: 50%;
  box-shadow: 0 0 6px rgba(99, 102, 241, 0.8);
  animation: glow 2s ease-in-out infinite;
}

@keyframes glow {
  0%, 100% { box-shadow: 0 0 6px rgba(99, 102, 241, 0.8); }
  50% { box-shadow: 0 0 12px rgba(99, 102, 241, 1); }
}

.hero__title {
  font-size: clamp(1.75rem, 5vw, 2.5rem);
  font-weight: 800;
  line-height: 1.2;
  color: var(--color-text-primary);
  margin: 0;
  letter-spacing: -0.02em;
}

.hero__title-accent {
  background: var(--color-accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero__subtitle {
  font-size: 0.95rem;
  color: var(--color-text-muted);
  margin: 0;
  line-height: 1.6;
}

/* ── Card ─────────────────────────────────────────────── */
.card {
  width: 100%;
  max-width: 680px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 20px 60px rgba(0, 0, 0, 0.4);
}

/* ── Divider ─────────────────────────────────────────── */
.divider {
  height: 1px;
  background: var(--color-border);
}

/* ── Error Banner ────────────────────────────────────── */
.error-banner {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  background: var(--color-error-subtle);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-md);
  padding: 1rem;
  animation: slide-up 0.3s ease;
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

.error-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--color-error);
  flex-shrink: 0;
  margin-top: 1px;
}

.error-banner strong {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-error);
  margin-bottom: 0.25rem;
}

.error-banner p {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  margin: 0;
}

.error-close {
  margin-left: auto;
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 0.875rem;
  padding: 0 0.25rem;
  flex-shrink: 0;
}

.error-close:hover { color: var(--color-error); }

/* ── Footer ──────────────────────────────────────────── */
.page-footer {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.footer-sep { opacity: 0.4; }
</style>
