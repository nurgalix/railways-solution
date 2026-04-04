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

    <!-- Navigation tabs -->
    <nav class="nav-tabs" role="navigation" aria-label="Основная навигация">
      <RouterLink
        v-for="route in navRoutes"
        :key="route.name"
        :to="route.path"
        class="nav-tab"
        :aria-label="route.meta.label"
      >
        {{ route.meta.label }}
        <!-- Alert badge on Alerts tab -->
        <span
          v-if="route.name === 'alerts' && alertCount > 0"
          class="nav-tab-badge"
          aria-label="`${alertCount} активных алертов`"
        >{{ alertCount }}</span>
      </RouterLink>
    </nav>

    <!-- Right controls -->
    <div class="topbar-controls">

      <!-- Connection status -->
      <div class="topbar-status">
        <span class="status-dot" :class="`status-dot--${store.connectionStatus}`"></span>
        <span class="text-xs">{{ statusLabel }}</span>
        <span v-if="store.connectionStatus === 'mock'" class="mock-badge">СИМУЛЯТОР</span>
      </div>

      <!-- Highload toggle -->
      <button
        class="pill-btn"
        :class="{ 'is-danger': highload }"
        title="Имитация ×10 нагрузки"
        @click="toggleHighload"
      >⚡ ×10</button>

      <!-- Theme -->
      <button
        class="pill-btn pill-btn--icon"
        :title="uiStore.theme === 'dark' ? 'Светлая тема' : 'Тёмная тема'"
        @click="uiStore.toggleTheme()"
      >{{ uiStore.theme === 'dark' ? '☀️' : '🌙' }}</button>

      <!-- Clock -->
      <time class="topbar-clock font-mono" :datetime="isoTime">{{ clock }}</time>

    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useTelemetryStore } from '@/stores/telemetry.js';
import { useUiStore }        from '@/stores/ui.js';
import { telemetryService }  from '@/services/telemetryService.js';

const store   = useTelemetryStore();
const uiStore = useUiStore();
const router  = useRouter();

// Expose only the real route list (skip redirect/catchall entries)
const navRoutes = computed(() =>
  router.getRoutes().filter(r => r.meta?.label)
);

const alertCount = computed(() => store.current?.alerts?.length ?? 0);

const statusLabel = computed(() => ({
  connected:    'Подключено',
  mock:         'Симулятор',
  connecting:   'Подключение…',
  disconnected: 'Нет связи',
}[store.connectionStatus] || store.connectionStatus));

// Highload
const highload = ref(false);
function toggleHighload() {
  highload.value = !highload.value;
  telemetryService.setHighload(highload.value);
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
