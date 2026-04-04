<template>
  <div class="app-content">
    <div class="page-header">
      <div class="page-title">Тренды и аналитика</div>
      <div class="page-subtitle">Телеметрия · последние {{ windowMin }} мин</div>
    </div>

    <!-- Controls -->
    <div class="flex gap-2" style="margin-bottom:0.75rem; flex-wrap:wrap; align-items:center">
      <button
        v-for="opt in windowOptions" :key="opt.v"
        class="pill-btn" :class="{ 'is-active': windowMin === opt.v }"
        @click="setWindow(opt.v)"
      >{{ opt.l }}</button>

      <span class="text-xs text-muted" style="margin-left:auto">
        {{ store.history.length }} точек в буфере ·
        <button class="pill-btn" @click="fetchHistory">↻ История из БД</button>
      </span>
    </div>

    <div class="page-grid page-grid-2">

      <div class="card">
        <div class="card-title">Скорость (км/ч)</div>
        <!-- ECharts: source = store.speedHistory, slice last windowMin*60 points -->
        <div class="chart-placeholder">
          <span class="chart-placeholder-icon">📈</span>
          <span>{{ sliceCount }} точек · {{ store.data?.speed?.toFixed(1) ?? '–' }} км/ч (сейчас)</span>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Температура (°C)</div>
        <div class="chart-placeholder">
          <span class="chart-placeholder-icon">🌡</span>
          <span>{{ store.data?.temperature?.toFixed(1) ?? '–' }} °C (сейчас)</span>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Уровень топлива (%)</div>
        <div class="chart-placeholder">
          <span class="chart-placeholder-icon">⛽</span>
          <span>{{ store.data?.fuel_level?.toFixed(1) ?? '–' }} % (сейчас)</span>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Давление (бар)</div>
        <div class="chart-placeholder">
          <span class="chart-placeholder-icon">🔵</span>
          <span>{{ store.data?.pressure?.toFixed(2) ?? '–' }} бар (сейчас)</span>
        </div>
      </div>

      <div class="card" style="grid-column: 1 / -1">
        <div class="card-title">Индекс здоровья</div>
        <div class="chart-placeholder">
          <span class="chart-placeholder-icon">💚</span>
          <span>{{ store.health.index?.toFixed(1) ?? '–' }} / 100 (сейчас) · категория {{ store.health.category }}</span>
        </div>
      </div>

    </div>

    <!-- DB history stats -->
    <div v-if="dbHistory.length" class="card" style="margin-top:0.75rem">
      <div class="card-title">Данные из БД (GET /api/telemetry/history)</div>
      <div class="flex gap-3 text-sm" style="flex-wrap:wrap">
        <span>Записей: <b>{{ dbHistory.length }}</b></span>
        <span>Период: <b>{{ dbHistory[0]?.timestamp?.slice(0,16) }}</b> → <b>{{ dbHistory[dbHistory.length-1]?.timestamp?.slice(0,16) }}</b></span>
        <span v-if="dbError" style="color:var(--crit)">{{ dbError }}</span>
      </div>
    </div>

    <!-- Replay & export -->
    <div class="card" style="margin-top:0.75rem">
      <div class="card-title">Перемотка и экспорт</div>
      <div class="flex gap-2 items-center" style="flex-wrap:wrap">
        <input
          type="range" min="0" :max="Math.max(0, store.history.length - 1)"
          v-model="replayPos"
          style="flex:1; min-width:120px; accent-color:var(--accent)"
          aria-label="Перемотка истории"
        />
        <span class="font-mono text-sm text-sub">{{ replayLabel }}</span>
        <button class="pill-btn" @click="store.exportCsv(windowMin)">↓ CSV ({{ windowMin }}м)</button>
        <button class="pill-btn" @click="store.exportPdf(windowMin)">↓ PDF ({{ windowMin }}м)</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store     = useTelemetryStore();
const windowMin = ref(5);
const replayPos = ref(0);
const dbHistory = ref([]);
const dbError   = ref(null);

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const windowOptions = [
  { l: '1м', v: 1 }, { l: '5м', v: 5 }, { l: '10м', v: 10 }, { l: '15м', v: 15 },
];

const sliceCount = computed(() => Math.min(windowMin.value * 60, store.history.length));

function setWindow(v) {
  windowMin.value = v;
}

async function fetchHistory() {
  dbError.value = null;
  try {
    const res = await fetch(`${API_BASE}/telemetry/history?minutes=${windowMin.value}&limit=500`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    dbHistory.value = json.items ?? [];
  } catch (e) {
    dbError.value = `Ошибка: ${e.message}`;
  }
}

const replayLabel = computed(() => {
  const idx   = Math.min(Number(replayPos.value), store.history.length - 1);
  const frame = store.history[idx];
  if (!frame) return '–';
  return new Date(frame.timestamp).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
});
</script>
