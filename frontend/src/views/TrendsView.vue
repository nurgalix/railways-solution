<template>
  <div class="app-content">
    <div class="page-header">
      <div class="page-title">Тренды и аналитика</div>
      <div class="page-subtitle">Телеметрия · последние {{ windowMin }} мин · {{ store.history.length }} точек в буфере</div>
    </div>

    <!-- Time window + export controls -->
    <div class="flex gap-2" style="margin-bottom:0.75rem; flex-wrap:wrap; align-items:center">
      <button
        v-for="opt in windowOptions" :key="opt.v"
        class="pill-btn" :class="{ 'is-active': windowMin === opt.v }"
        @click="windowMin = opt.v"
      >{{ opt.l }}</button>
      <span style="margin-left:auto" class="flex gap-2">
        <button class="pill-btn" @click="store.exportCsv(windowMin)">↓ CSV</button>
        <button class="pill-btn" @click="store.exportPdf(windowMin)">↓ PDF</button>
      </span>
    </div>

    <!-- Charts grid -->
    <div class="trends-grid">
      <div v-for="m in metrics" :key="m.key"
        class="card trends-chart-card"
        :style="m.full ? 'grid-column: 1 / -1' : ''"
      >
        <div class="card-title" style="margin-bottom:0.4rem">
          {{ m.label }}
          <span class="text-muted" style="font-weight:400; text-transform:none; letter-spacing:0">{{ m.unit }}</span>
          <span class="font-mono" style="margin-left:auto; font-weight:700" :style="{ color: m.hex }">
            {{ currentVal(m) }}
          </span>
        </div>
        <div :ref="el => chartEls[m.key] = el" class="trends-chart-area"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';
import { useUiStore }        from '@/stores/ui.js';
import * as echarts from 'echarts/core';
import { LineChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, DataZoomComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([LineChart, GridComponent, TooltipComponent, DataZoomComponent, CanvasRenderer]);

const store   = useTelemetryStore();
const uiStore = useUiStore();

const windowMin = ref(5);
const windowOptions = [
  { l: '1м', v: 1 }, { l: '5м', v: 5 }, { l: '10м', v: 10 }, { l: '15м', v: 15 },
];

const metrics = [
  { key: 'speed',       label: 'Скорость',     unit: 'км/ч', hex: '#3b82f6' },
  { key: 'temperature', label: 'Температура',  unit: '°C',   hex: '#f59e0b' },
  { key: 'fuel_level',  label: 'Уровень топлива', unit: '%', hex: '#10b981' },
  { key: 'pressure',    label: 'Давление',     unit: 'бар',  hex: '#8b5cf6' },
  { key: 'health',      label: 'Индекс здоровья', unit: '/ 100', hex: '#10b981', full: true },
];

function currentVal(m) {
  if (!store.data && m.key !== 'health') return '–';
  const v = m.key === 'health'
    ? store.health.index
    : store.data?.[m.key];
  return v != null ? (+v).toFixed(1) + ' ' + m.unit : '–';
}

const chartEls  = reactive({});
const chartInsts = {};
const ros = {};

function getSlice(key) {
  const count = Math.min(windowMin.value * 60, store.history.length);
  const slice = store.history.slice(Math.max(0, store.history.length - count));
  return slice.map(frame => {
    const t = new Date(frame.timestamp).toLocaleTimeString('ru-RU', {
      hour: '2-digit', minute: '2-digit', second: '2-digit',
    });
    const v = key === 'health' ? (frame.health?.index ?? 0) : (frame.data?.[key] ?? 0);
    return [t, +v.toFixed(2)];
  });
}

function buildOption(m) {
  const dark = uiStore.theme === 'dark';
  const gridColor  = dark ? '#1e2d45' : '#e2e8f0';
  const labelColor = dark ? '#64748b' : '#94a3b8';
  const data = getSlice(m.key);

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: dark ? '#1a2235' : '#fff',
      borderColor: gridColor,
      textStyle: { color: dark ? '#e2e8f0' : '#0f172a', fontSize: 11 },
      formatter: p => `<b>${p[0].axisValue}</b><br/>${m.label}: <b>${Number(p[0].value[1]).toFixed(2)} ${m.unit}</b>`,
    },
    grid: { left: 46, right: 10, top: 8, bottom: 30 },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      axisLine:  { lineStyle: { color: gridColor } },
      axisLabel: { color: labelColor, fontSize: 9 },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value',
      axisLine:  { show: false },
      splitLine: { lineStyle: { color: gridColor, type: 'dashed' } },
      axisLabel: { color: labelColor, fontSize: 9 },
    },
    dataZoom: [{ type: 'inside' }],
    series: [{
      type: 'line',
      data,
      smooth: true,
      symbol: 'none',
      lineStyle: { color: m.hex, width: 2 },
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: m.hex + '50' },
            { offset: 1, color: m.hex + '00' },
          ],
        },
      },
    }],
  };
}

function updateAll() {
  for (const m of metrics) {
    if (chartInsts[m.key]) {
      chartInsts[m.key].setOption(buildOption(m), { notMerge: false, lazyUpdate: true });
    }
  }
}

let raf;
watch([() => store.history.length, windowMin], () => {
  cancelAnimationFrame(raf);
  raf = requestAnimationFrame(updateAll);
});
watch(() => uiStore.theme, updateAll);

onMounted(() => {
  for (const m of metrics) {
    const el = chartEls[m.key];
    if (!el) continue;
    chartInsts[m.key] = echarts.init(el);
    chartInsts[m.key].setOption(buildOption(m));
    ros[m.key] = new ResizeObserver(() => chartInsts[m.key]?.resize());
    ros[m.key].observe(el);
  }
});

onUnmounted(() => {
  cancelAnimationFrame(raf);
  for (const m of metrics) {
    ros[m.key]?.disconnect();
    chartInsts[m.key]?.dispose();
  }
});
</script>

<style scoped>
.trends-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

@media (max-width: 768px) {
  .trends-grid { grid-template-columns: 1fr; }
}

.trends-chart-card { display: flex; flex-direction: column; }
.trends-chart-area { width: 100%; height: 220px; }
</style>
