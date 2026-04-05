<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
        <span class="login-brand-icon">🚂</span>
        <div>
          <div class="login-brand-title">Цифровой двойник</div>
          <div class="login-brand-sub">ВЛ80 · Алматы–Тараз</div>
        </div>
      </div>

      <form class="login-form" @submit.prevent="submit">
        <div class="login-field">
          <label class="login-label" for="username">Логин</label>
          <input
            id="username"
            v-model="username"
            class="login-input"
            type="text"
            autocomplete="username"
            placeholder="Введите логин"
            required
          />
        </div>

        <div class="login-field">
          <label class="login-label" for="password">Пароль</label>
          <input
            id="password"
            v-model="password"
            class="login-input"
            type="password"
            autocomplete="current-password"
            placeholder="Введите пароль"
            required
          />
        </div>

        <p v-if="auth.error" class="login-error">{{ auth.error }}</p>

        <button class="login-btn" type="submit" :disabled="loading">
          {{ loading ? 'Вход…' : 'Войти' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth.js';

const auth     = useAuthStore();
const router   = useRouter();
const username = ref('');
const password = ref('');
const loading  = ref(false);

async function submit() {
  loading.value = true;
  const ok = await auth.login(username.value, password.value);
  loading.value = false;
  if (ok) router.replace('/dashboard');
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
}

.login-card {
  width: 100%;
  max-width: 380px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 2rem;
  box-shadow: var(--shadow-card);
}

.login-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.login-brand-icon {
  font-size: 2rem;
}

.login-brand-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-text);
}

.login-brand-sub {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-top: 2px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.login-field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.login-label {
  font-size: 0.8rem;
  color: var(--color-text-sub);
  font-weight: 500;
}

.login-input {
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 0.6rem 0.8rem;
  color: var(--color-text);
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.15s;
}

.login-input:focus {
  border-color: var(--color-accent);
}

.login-error {
  font-size: 0.82rem;
  color: var(--color-critical);
  margin: 0;
}

.login-btn {
  margin-top: 0.5rem;
  padding: 0.65rem;
  background: var(--color-accent);
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-btn:not(:disabled):hover {
  opacity: 0.85;
}
</style>
