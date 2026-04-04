<template>
  <div class="app-content">
    <div class="page-header">
      <div class="page-title">Тренды и аналитика</div>
      <div class="page-subtitle">Временные ряды телеметрии · последние {{ windowMin }} мин</div>
    </div>

    <!-- Window selector -->
    <div class="flex gap-2 mb" style="margin-bottom:0.75rem">
      <button
        v-for="opt in windowOptions" :key="opt.v"
        class="pill-btn"
        :class="{ 'is-active': windowMin === opt.v }"
        @click="windowMin = opt.v"
      >{{ opt.l }}</button>
    </div>

    <div class="page-grid page-grid-2">

      <div class="card">
        <div class="card-title">Скорость (км/ч)</div>
        <!-- TODO: ECharts line chart — see _reference/cabin/TrendsPanel.vue -->
        <div class="chart-placeholder">
          <span class="chart-placeholder-icon">📈</span>
          <span>График скорости</span>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Температура двигателя (°C)</div>
        <!-- TODO: ECharts line chart -->
        <div class="chart-placeholder">
          <span class="chart-placeholder-icon">🌡</span>
          <span>График температуры</span>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Уровень топлива (%)</div>
        <!-- TODO: ECharts area chart -->
        <div class="chart-placeholder">
          <span class="chart-placeholder-icon">⛽</span>
          <span>График топлива</span>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Напряжение (В)</div>
        <!-- TODO: ECharts line chart -->
        <div class="chart-placeholder">
          <span class="chart-placeholder-icon">⚡</span>
          <span>График напряжения</span>
        </div>
      </div>

      <div class="card" style="grid-column: 1 / -1">
        <div class="card-title">Индекс здоровья</div>
        <!-- TODO: ECharts area chart with threshold bands -->
        <div class="chart-placeholder">
          <span class="chart-placeholder-icon">💚</span>
          <span>График индекса здоровья</span>
        </div>
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
        <span class="font-mono text-sm text-sub">{{ replayTimeLabel }}</span>
        <button class="pill-btn" @click="store.exportCsv()">↓ Экспорт CSV</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store = useTelemetryStore();
const windowMin = ref(5);
const replayPos = ref(0);

const windowOptions = [
  { l: '1м', v: 1 }, { l: '5м', v: 5 }, { l: '10м', v: 10 }, { l: '15м', v: 15 },
];

const replayTimeLabel = computed(() => {
  const idx = Math.min(Number(replayPos.value), store.history.length - 1);
  if (!store.history[idx]) return '–';
  return new Date(store.history[idx].timestamp)
    .toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
});
</script>
