<template>
  <div class="card">
    <div class="trends-toolbar">
      <div class="card-title" style="margin:0">Тренды</div>
      <div class="trends-controls">
        <button
          v-for="opt in windowOptions" :key="opt.v"
          class="pill-btn" :class="{ 'is-active': windowMin === opt.v }"
          @click="windowMin = opt.v"
        >{{ opt.l }}</button>
      </div>
    </div>

    <!-- Metric tabs -->
    <div class="flex gap-1" style="margin-bottom:0.5rem; flex-wrap:wrap">
      <button
        v-for="m in metrics" :key="m.key"
        class="pill-btn"
        :class="{ 'is-active': active === m.key }"
        :style="active === m.key ? { borderColor: m.color, color: m.color } : {}"
        @click="active = m.key"
      >{{ m.label }}</button>
    </div>

    <!-- Chart area — implement ECharts using _reference/cabin/TrendsPanel.vue -->
    <div class="chart-placeholder">
      <span class="chart-placeholder-icon">📈</span>
      <span>{{ activeMeta.label }} · последние {{ windowMin }} мин ({{ displayCount }} точек)</span>
    </div>

    <!-- Replay scrubber -->
    <div class="flex items-center gap-2" style="margin-top:0.5rem; flex-wrap:wrap">
      <input
        type="range" min="0" :max="Math.max(0, store.history.length - 1)"
        v-model="replayPos"
        style="flex:1; min-width:80px; accent-color:var(--accent)"
        aria-label="Перемотка"
      />
      <span class="font-mono text-xs text-sub">{{ replayLabel }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store     = useTelemetryStore();
const windowMin = ref(5);
const active    = ref('speed');
const replayPos = ref(0);

const windowOptions = [
  { l: '1м', v: 1 }, { l: '5м', v: 5 }, { l: '10м', v: 10 }, { l: '15м', v: 15 },
];

// Metrics map directly to store history computed arrays
const metrics = [
  { key: 'speed',       label: 'Скорость',     color: 'var(--chart-1)' },
  { key: 'temperature', label: 'Температура',  color: 'var(--chart-3)' },
  { key: 'fuel_level',  label: 'Топливо',      color: 'var(--chart-2)' },
  { key: 'pressure',    label: 'Давление',     color: 'var(--chart-4)' },
  { key: 'health',      label: 'Здоровье',     color: 'var(--ok)' },
];

const activeMeta   = computed(() => metrics.find(m => m.key === active.value) || metrics[0]);
const displayCount = computed(() => Math.min(windowMin.value * 60, store.history.length));

const replayLabel = computed(() => {
  const idx = Math.min(Number(replayPos.value), store.history.length - 1);
  const frame = store.history[idx];
  if (!frame) return '–';
  return new Date(frame.timestamp).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
});
</script>
