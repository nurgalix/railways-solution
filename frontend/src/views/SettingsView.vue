<template>
  <div class="app-content">
    <div class="page-header">
      <div class="page-title">Настройки</div>
      <div class="page-subtitle">Конфигурация порогов, подключения и интерфейса</div>
    </div>

    <div class="page-grid page-grid-2">

      <!-- Connection -->
      <div class="card">
        <div class="card-title">Подключение к бэкенду</div>
        <div class="flex flex-col gap-3">
          <div>
            <div class="label">WebSocket URL</div>
            <div style="margin-top:0.3rem; display:flex; gap:0.4rem;">
              <input
                v-model="wsUrl"
                type="text"
                class="settings-input"
                placeholder="ws://localhost:8000/ws/telemetry"
                aria-label="WebSocket URL"
              />
            </div>
            <div class="text-xs text-muted" style="margin-top:0.3rem">
              Задаётся через <code>VITE_WS_URL</code> в <code>.env</code>
            </div>
          </div>

          <div>
            <div class="label">Статус</div>
            <div class="flex items-center gap-2" style="margin-top:0.3rem">
              <span class="status-dot" :class="`status-dot--${store.connectionStatus}`"></span>
              <span class="text-sm">{{ statusLabel }}</span>
              <span v-if="store.connectionStatus === 'mock'" class="mock-badge">СИМУЛЯТОР</span>
            </div>
          </div>

          <div>
            <div class="label">Частота обновления (симулятор)</div>
            <div class="text-sm text-sub" style="margin-top:0.2rem">1 Гц (1 сообщение/сек)</div>
          </div>
        </div>
      </div>

      <!-- Theme -->
      <div class="card">
        <div class="card-title">Интерфейс</div>
        <div class="flex flex-col gap-3">
          <div>
            <div class="label">Тема</div>
            <div class="flex gap-2" style="margin-top:0.4rem">
              <button
                class="pill-btn"
                :class="{ 'is-active': uiStore.theme === 'dark' }"
                @click="uiStore.theme = 'dark'"
              >🌙 Тёмная</button>
              <button
                class="pill-btn"
                :class="{ 'is-active': uiStore.theme === 'light' }"
                @click="uiStore.theme = 'light'"
              >☀️ Светлая</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Alert thresholds -->
      <div class="card" style="grid-column: 1 / -1">
        <div class="card-title">Пороги алертов</div>
        <!-- TODO: load thresholds from backend API: GET /api/config/thresholds
             Save via: PUT /api/config/thresholds
             Currently hardcoded in src/services/mockTelemetry.js (ALERT_TYPES)
             and in src/stores/telemetry.js (calcHealthIndex) -->
        <div class="settings-threshold-grid">
          <div v-for="row in thresholds" :key="row.key" class="threshold-row">
            <span class="threshold-name">{{ row.name }}</span>
            <span class="threshold-ok text-xs" style="color:var(--ok)">OK: {{ row.ok }}</span>
            <span class="threshold-warn text-xs" style="color:var(--warn)">Внимание: {{ row.warn }}</span>
            <span class="threshold-crit text-xs" style="color:var(--crit)">Критично: {{ row.crit }}</span>
          </div>
        </div>
        <div class="text-xs text-muted" style="margin-top:0.75rem">
          Редактирование порогов будет доступно после подключения бэкенда.
        </div>
      </div>

      <!-- Data export -->
      <div class="card">
        <div class="card-title">Экспорт данных</div>
        <div class="flex flex-col gap-2">
          <button class="pill-btn" style="width:fit-content" @click="store.exportCsv()">
            ↓ Экспорт истории (CSV)
          </button>
          <div class="text-xs text-muted">
            Экспортирует последние {{ store.history.length }} записей (до 15 мин)
          </div>
        </div>
      </div>

      <!-- About -->
      <div class="card">
        <div class="card-title">О системе</div>
        <div class="flex flex-col gap-1">
          <div class="flex justify-between text-sm">
            <span class="text-muted">Версия</span>
            <span class="font-mono">0.1.0</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-muted">Стек</span>
            <span>Vue 3 · Pinia · Vue Router</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-muted">WebSocket</span>
            <span class="font-mono text-xs">{{ wsUrl || 'не задан' }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-muted">Буфер истории</span>
            <span>{{ store.history.length }} / 900 записей</span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';
import { useUiStore } from '@/stores/ui.js';

const store   = useTelemetryStore();
const uiStore = useUiStore();

const wsUrl = ref(import.meta.env.VITE_WS_URL || '');

const statusLabel = computed(() => ({
  connected:    'Подключено к бэкенду',
  mock:         'Работает симулятор (бэкенд недоступен)',
  connecting:   'Подключение…',
  disconnected: 'Нет связи',
}[store.connectionStatus] || store.connectionStatus));

// Thresholds shown as read-only reference (edit in mockTelemetry.js / store)
const thresholds = [
  { key: 'temp_engine',    name: 'Температура двигателя', ok: '< 88°C',    warn: '88–100°C', crit: '> 100°C' },
  { key: 'pressure_brake', name: 'Давление тормозов',     ok: '4.5–5.5 бар', warn: '4.0–6.0 бар', crit: '< 4.0 / > 6.0' },
  { key: 'fuel_level',     name: 'Уровень топлива',       ok: '> 20%',     warn: '15–20%',   crit: '< 15%' },
  { key: 'voltage',        name: 'Напряжение',            ok: '570–640 В', warn: '540–670 В', crit: '< 540 / > 670' },
  { key: 'speed',          name: 'Скорость',              ok: '< 120 км/ч', warn: '120–130', crit: '> 130' },
];
</script>

<style scoped>
.settings-input {
  flex: 1;
  padding: 0.35rem 0.6rem;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  font-size: 0.8rem;
  font-family: monospace;
  outline: none;
  transition: border-color 0.15s;
}
.settings-input:focus { border-color: var(--accent); }

.settings-threshold-grid {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.threshold-row {
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr 1fr;
  gap: 0.5rem;
  align-items: center;
  padding: 0.3rem 0;
  border-bottom: 1px solid var(--border-soft);
  font-size: 0.75rem;
}

.threshold-name { color: var(--text-sub); font-weight: 500; }
</style>
