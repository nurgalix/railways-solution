<template>
  <header class="topbar" role="banner">
    <!-- Left: Branding -->
    <div class="topbar__brand">
      <span class="topbar__icon" aria-hidden="true">🚂</span>
      <div>
        <div class="topbar__title">Цифровой двойник</div>
        <div class="topbar__subtitle">Локомотив ВЛ80 · Маршрут Алматы–Тараз</div>
      </div>
    </div>

    <!-- Center: Connection status -->
    <div class="topbar__status">
      <span
        class="status-dot"
        :class="`status-dot--${connectionClass}`"
        aria-label="`Статус подключения: ${connectionLabel}`"
      ></span>
      <span class="status-label">{{ connectionLabel }}</span>
      <span v-if="store.connectionStatus === 'mock'" class="mock-badge">МОКЕР</span>
    </div>

    <!-- Right: Controls -->
    <div class="topbar__controls">
      <!-- Highload toggle -->
      <button
        class="ctrl-btn"
        :class="{ active: highload }"
        title="Имитация высокой нагрузки (×10 событий)"
        aria-pressed="highload"
        @click="toggleHighload"
      >
        ⚡ Highload
      </button>

      <!-- Export CSV -->
      <button class="ctrl-btn" title="Экспорт данных в CSV" @click="store.exportCsv()">
        ↓ CSV
      </button>

      <!-- Theme toggle -->
      <button
        class="ctrl-btn ctrl-btn--icon"
        :title="uiStore.theme === 'dark' ? 'Светлая тема' : 'Тёмная тема'"
        :aria-label="uiStore.theme === 'dark' ? 'Переключить на светлую тему' : 'Переключить на тёмную тему'"
        @click="uiStore.toggleTheme()"
      >
        {{ uiStore.theme === 'dark' ? '☀️' : '🌙' }}
      </button>

      <!-- Live clock -->
      <time class="topbar__clock font-mono" :datetime="isoTime">{{ displayTime }}</time>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';
import { useUiStore } from '@/stores/ui.js';
import { telemetryService } from '@/services/telemetryService.js';

const store   = useTelemetryStore();
const uiStore = useUiStore();

const highload = ref(false);
function toggleHighload() {
  highload.value = !highload.value;
  telemetryService.setHighload(highload.value);
}

const connectionLabel = computed(() => ({
  connected:    'Подключено',
  mock:         'Симулятор активен',
  connecting:   'Подключение…',
  disconnected: 'Нет связи',
}[store.connectionStatus] || store.connectionStatus));

const connectionClass = computed(() => ({
  connected:    'connected',
  mock:         'mock',
  connecting:   'connecting',
  disconnected: 'disconnected',
}[store.connectionStatus] || 'disconnected'));

// Live clock
const now = ref(new Date());
let clockTimer;
onMounted(()  => { clockTimer = setInterval(() => { now.value = new Date(); }, 1000); });
onUnmounted(() => clearInterval(clockTimer));

const displayTime = computed(() =>
  now.value.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
);
const isoTime = computed(() => now.value.toISOString());
</script>

<style scoped>
.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 1.25rem;
  background: var(--topbar-bg);
  border-bottom: 1px solid var(--topbar-border);
  backdrop-filter: blur(12px);
  gap: 1rem;
}

.topbar__brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-shrink: 0;
}

.topbar__icon { font-size: 1.5rem; line-height: 1; }

.topbar__title {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: 0.02em;
}

.topbar__subtitle {
  font-size: 0.68rem;
  color: var(--color-text-muted);
  margin-top: 1px;
}

.topbar__status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.78rem;
  color: var(--color-text-sub);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot--connected    { background: var(--color-normal);  animation: pulse-dot 2s ease-in-out infinite; }
.status-dot--mock         { background: var(--color-warning); animation: pulse-dot 1.5s ease-in-out infinite; }
.status-dot--connecting   { background: var(--color-accent);  animation: pulse-dot 1s ease-in-out infinite; }
.status-dot--disconnected { background: var(--color-critical); }

.status-label { color: var(--color-text-sub); }

.mock-badge {
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0.1rem 0.4rem;
  background: var(--color-warning-bg);
  color: var(--color-warning);
  border-radius: 4px;
  letter-spacing: 0.06em;
}

.topbar__controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.ctrl-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem 0.7rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-sub);
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  white-space: nowrap;
}

.ctrl-btn:hover {
  background: var(--color-border);
  color: var(--color-text);
}

.ctrl-btn.active {
  background: var(--color-warning-bg);
  color: var(--color-warning);
  border-color: var(--color-warning);
}

.ctrl-btn--icon { padding: 0.3rem 0.5rem; font-size: 1rem; }

.topbar__clock {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-text-sub);
  letter-spacing: 0.04em;
  padding-left: 0.5rem;
  border-left: 1px solid var(--color-border);
}
</style>
