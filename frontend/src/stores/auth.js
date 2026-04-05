import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const TOKEN_KEY = 'railways_token';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || null);
  const user  = ref(null);
  const error = ref(null);

  const isAuthenticated = computed(() => !!token.value);

  function _authHeaders() {
    return { Authorization: `Bearer ${token.value}` };
  }

  async function login(username, password) {
    error.value = null;
    const body = new URLSearchParams({ username, password });
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body,
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      error.value = data.detail || 'Неверный логин или пароль';
      return false;
    }
    const data = await res.json();
    token.value = data.access_token;
    localStorage.setItem(TOKEN_KEY, token.value);
    await fetchMe();
    return true;
  }

  async function fetchMe() {
    if (!token.value) return;
    try {
      const res = await fetch(`${API_BASE}/auth/me`, { headers: _authHeaders() });
      if (res.ok) {
        user.value = await res.json();
      } else {
        // Token invalid or expired — clear it
        logout();
      }
    } catch {
      // Network error — keep token, try again later
    }
  }

  function logout() {
    token.value = null;
    user.value  = null;
    localStorage.removeItem(TOKEN_KEY);
  }

  return { token, user, error, isAuthenticated, login, logout, fetchMe };
});
