<template>
  <header class="topbar" role="banner">

    <!-- Brand -->
    <RouterLink to="/dashboard" class="topbar-brand">
      <span class="topbar-brand-icon" aria-hidden="true">🚂</span>
      <div>
        <div class="topbar-brand-title">Цифровой двойник</div>
        <div class="topbar-brand-sub">ВЛ80 · Алматы–Тараз</div>
      </div>
    </RouterLink>

    <!-- Navigation -->
    <nav class="nav-tabs" role="navigation" aria-label="Основная навигация">
      <RouterLink
        v-for="r in navRoutes"
        :key="r.name"
        :to="r.path"
        class="nav-tab"
        :aria-label="r.meta.label"
      >
        {{ r.meta.label }}
        <span
          v-if="r.name === 'alerts' && alertCount > 0"
          class="nav-tab-badge"
        >{{ alertCount }}</span>
      </RouterLink>
    </nav>

    <!-- Right controls -->
    <div class="topbar-controls">

      <!-- Connection status -->
      <div class="topbar-status">
        <span class="status-dot" :class="`status-dot--${store.connectionStatus}`"></span>
        <span class="text-xs">{{ statusLabel }}</span>
      </div>

      <!-- Highload toggle — calls backend API -->
      <button
        class="pill-btn"
        :class="{ 'is-danger': highload }"
        :title="highload ? 'Отключить highload' : 'Включить ×10 нагрузку'"
        @click="toggleHighload"
      >⚡ ×10</button>

      <!-- Theme -->
      <button
        class="pill-btn pill-btn--icon"
        :title="uiStore.theme === 'dark' ? 'Светлая тема' : 'Тёмная тема'"
        @click="uiStore.toggleTheme()"
      >{{ uiStore.theme === 'dark' ? '☀️' : '🌙' }}</button>

      <!-- Live clock -->
      <time class="topbar-clock font-mono" :datetime="isoTime">{{ clock }}</time>

      <!-- User + logout -->
      <div v-if="auth.user" class="topbar-user">
        <span class="topbar-username">{{ auth.user.username }}</span>
        <button class="pill-btn" title="Выйти" @click="handleLogout">⎋ Выйти</button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useTelemetryStore } from '@/stores/telemetry.js';
import { useUiStore }        from '@/stores/ui.js';
import { useAuthStore }      from '@/stores/auth.js';
import { telemetryService }  from '@/services/telemetryService.js';

const store   = useTelemetryStore();
const uiStore = useUiStore();
const auth    = useAuthStore();
const router  = useRouter();

function handleLogout() {
  auth.logout();
  router.replace('/login');
}

const navRoutes = computed(() => router.getRoutes().filter(r => r.meta?.label));

const alertCount  = computed(() => store.alerts.length);

const statusLabel = computed(() => ({
  connected:    'Подключено',
  disconnected: 'Нет связи',
  connecting:   'Подключение…',
}[store.connectionStatus] || store.connectionStatus));

// Highload — delegates to telemetryService which calls POST /api/simulator/highload
const highload = ref(false);
async function toggleHighload() {
  highload.value = !highload.value;
  await telemetryService.setHighload(highload.value);
}

// Live clock
const now = ref(new Date());
let timer;
onMounted(()  => { timer = setInterval(() => { now.value = new Date(); }, 1000); });
onUnmounted(() => clearInterval(timer));

const clock   = computed(() =>
  now.value.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
);
const isoTime = computed(() => now.value.toISOString());
</script>
