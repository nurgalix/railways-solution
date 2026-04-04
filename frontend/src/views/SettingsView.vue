<template>
  <div class="app-content">
    <div class="page-header">
      <div class="page-title">Настройки</div>
      <div class="page-subtitle">Подключение, порог алертов, экспорт</div>
    </div>

    <div class="page-grid page-grid-2">

      <!-- Connection -->
      <div class="card">
        <div class="card-title">Подключение к бэкенду</div>
        <div class="flex flex-col gap-3">
          <div>
            <div class="label">WebSocket URL</div>
            <div class="font-mono text-xs text-sub" style="margin-top:0.3rem; word-break:break-all">
              {{ wsUrl }}
            </div>
            <div class="text-xs text-muted" style="margin-top:0.25rem">
              Задаётся через <code>VITE_WS_URL</code> в <code>.env</code>
            </div>
          </div>
          <div>
            <div class="label">Статус</div>
            <div class="flex items-center gap-2" style="margin-top:0.3rem">
              <span class="status-dot" :class="`status-dot--${store.connectionStatus}`"></span>
              <span class="text-sm">{{ statusLabel }}</span>
            </div>
          </div>
          <div>
            <div class="label">API Base URL</div>
            <div class="font-mono text-xs text-sub" style="margin-top:0.3rem; word-break:break-all">
              {{ apiBase }}
            </div>
          </div>
          <div>
            <div class="label">Буфер истории</div>
            <div class="text-sm">{{ store.history.length }} / 900 фреймов</div>
          </div>
        </div>
      </div>

      <!-- Simulator control -->
      <div class="card">
        <div class="card-title">Симулятор телеметрии</div>
        <div class="flex flex-col gap-3">
          <div class="text-sm text-sub">
            Симулятор управляется бэкендом (переменная окружения <code>SIMULATOR_ENABLED</code>).
          </div>
          <div class="flex gap-2" style="flex-wrap:wrap">
            <button class="pill-btn" @click="toggleHighload(true)">⚡ Highload ×10</button>
            <button class="pill-btn" @click="toggleHighload(false)">✓ Нормальный режим</button>
          </div>
          <div v-if="highloadMsg" class="text-xs" :class="highloadError ? 'c-crit' : 'c-ok'">
            {{ highloadMsg }}
          </div>
          <div class="text-xs text-muted">
            POST /api/simulator/highload?enabled=true|false
          </div>
        </div>
      </div>

      <!-- Thresholds (read-only, managed by backend config) -->
      <div class="card" style="grid-column: 1 / -1">
        <div class="card-title">Пороги алертов (бэкенд)</div>
        <div class="settings-threshold-grid">
          <div v-for="row in thresholds" :key="row.key" class="threshold-row">
            <span class="threshold-name">{{ row.name }}</span>
            <span class="text-xs c-ok">Норма: {{ row.ok }}</span>
            <span class="text-xs c-warn">Внимание: {{ row.warn }}</span>
            <span class="text-xs c-crit">Критично: {{ row.crit }}</span>
          </div>
        </div>
        <div class="text-xs text-muted" style="margin-top:0.6rem">
          Конфигурация — <code>backend/health_config.yaml</code> ·
          API: <code>GET /api/config/thresholds</code>
        </div>
      </div>

      <!-- Export -->
      <div class="card">
        <div class="card-title">Экспорт</div>
        <div class="flex flex-col gap-2">
          <div class="flex gap-2 items-center" style="flex-wrap:wrap">
            <select v-model="exportMinutes" class="settings-input" style="width:auto">
              <option :value="15">15 мин</option>
              <option :value="30">30 мин</option>
              <option :value="60">1 час</option>
              <option :value="1440">24 часа</option>
            </select>
            <button class="pill-btn" @click="store.exportCsv(exportMinutes)">↓ CSV</button>
            <button class="pill-btn" @click="store.exportPdf(exportMinutes)">↓ PDF</button>
          </div>
          <div class="text-xs text-muted">
            Данные берутся из базы данных бэкенда.
          </div>
        </div>
      </div>

      <!-- Interface -->
      <div class="card">
        <div class="card-title">Интерфейс</div>
        <div class="flex flex-col gap-3">
          <div>
            <div class="label">Тема</div>
            <div class="flex gap-2" style="margin-top:0.4rem">
              <button class="pill-btn" :class="{ 'is-active': uiStore.theme === 'dark'  }" @click="uiStore.theme = 'dark'">🌙 Тёмная</button>
              <button class="pill-btn" :class="{ 'is-active': uiStore.theme === 'light' }" @click="uiStore.theme = 'light'">☀️ Светлая</button>
            </div>
          </div>
          <div>
            <div class="label">Версия</div>
            <div class="font-mono text-sm">0.1.0</div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';
import { useUiStore }        from '@/stores/ui.js';

const store   = useTelemetryStore();
const uiStore = useUiStore();

const wsUrl        = import.meta.env.VITE_WS_URL  || 'ws://localhost:8000/api/ws/telemetry';
const apiBase      = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const exportMinutes = ref(15);
const highloadMsg   = ref('');
const highloadError = ref(false);

const statusLabel = computed(() => ({
  connected:    'Подключено к бэкенду',
  disconnected: 'Нет связи — переподключение…',
  connecting:   'Подключение…',
}[store.connectionStatus] || store.connectionStatus));

async function toggleHighload(enabled) {
  highloadMsg.value   = '';
  highloadError.value = false;
  try {
    const res = await fetch(`${apiBase}/simulator/highload?enabled=${enabled}`, { method: 'POST' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    highloadMsg.value = enabled
      ? `Highload включён · ${data.frequency_hz} Гц`
      : 'Нормальный режим · 1 Гц';
  } catch (e) {
    highloadError.value = true;
    highloadMsg.value   = `Ошибка: ${e.message}`;
  }
}

const thresholds = [
  { key: 'temperature', name: 'Температура',  ok: '< 88°C',       warn: '88–100°C',      crit: '> 100°C' },
  { key: 'pressure',    name: 'Давление',     ok: '4.5–5.5 бар',  warn: '4.0–6.0 бар',  crit: '< 4.0 / > 6.0' },
  { key: 'fuel_level',  name: 'Уровень топлива', ok: '> 20%',     warn: '15–20%',         crit: '< 15%' },
  { key: 'speed',       name: 'Скорость',     ok: '< 120 км/ч',   warn: '120–130',        crit: '> 130' },
];
</script>

<style scoped>
.settings-input {
  padding: 0.3rem 0.55rem;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  font-size: 0.8rem;
  outline: none;
}

.settings-threshold-grid { display: flex; flex-direction: column; gap: 0.35rem; }

.threshold-row {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr 1fr;
  gap: 0.5rem;
  align-items: center;
  padding: 0.28rem 0;
  border-bottom: 1px solid var(--border-soft);
  font-size: 0.73rem;
}

.threshold-name { color: var(--text-sub); font-weight: 500; }
</style>
