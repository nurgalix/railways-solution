<template>
  <div class="card trends-panel">
    <div class="trends-toolbar">
      <div class="card-title" style="margin:0">Тренды</div>
      <div class="trends-controls">
        <button
          v-for="opt in windowOptions" :key="opt.v"
          class="pill-btn" :class="{ 'is-active': windowMin === opt.v }"
          @click="windowMin = opt.v"
        >{{ opt.l }}</button>
        <span class="font-mono text-xs text-muted">{{ replayLabel }}</span>
      </div>
    </div>

    <!-- Metric tabs -->
    <div class="flex gap-1" style="margin-bottom:0.5rem; flex-wrap:wrap">
      <button
        v-for="m in metrics" :key="m.key"
        class="pill-btn"
        :class="{ 'is-active': active === m.key }"
        :style="active === m.key ? { borderColor: m.hex, color: m.hex } : {}"
        @click="active = m.key"
      >{{ m.label }}</button>
    </div>

    <!-- Chart -->
    <div ref="chartEl" class="chart-area"></div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, shallowRef } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';
import { useUiStore }        from '@/stores/ui.js';
import * as echarts from 'echarts/core';
import { LineChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, DataZoomComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([LineChart, GridComponent, TooltipComponent, DataZoomComponent, CanvasRenderer]);

const store   = useTelemetryStore();
const uiStore = useUiStore();

const chartEl   = ref(null);
const chartInst = shallowRef(null);
const windowMin = ref(5);
const active    = ref('speed');

const windowOptions = [
  { l: '1м', v: 1 }, { l: '5м', v: 5 }, { l: '10м', v: 10 },
];

const metrics = [
  { key: 'speed',       label: 'Скорость',    unit: 'км/ч', hex: '#3b82f6' },
  { key: 'temperature', label: 'Темп.',        unit: '°C',   hex: '#f59e0b' },
  { key: 'fuel_level',  label: 'Топливо',      unit: '%',    hex: '#10b981' },
  { key: 'pressure',    label: 'Давление',     unit: 'бар',  hex: '#8b5cf6' },
  { key: 'health',      label: 'Здоровье',     unit: '/100', hex: '#10b981' },
];

const activeMeta   = computed(() => metrics.find(m => m.key === active.value) ?? metrics[0]);
const showCount    = computed(() => Math.min(windowMin.value * 60, store.history.length));

const replayLabel = computed(() => {
  const f = store.history[store.history.length - 1];
  if (!f) return '–';
  return new Date(f.timestamp).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
});

function getSeriesData() {
  const total = store.history.length;
  const slice = store.history.slice(Math.max(0, total - showCount.value));
  const m     = active.value;
  return slice.map(frame => {
    const t = new Date(frame.timestamp).toLocaleTimeString('ru-RU', {
      hour: '2-digit', minute: '2-digit', second: '2-digit',
    });
    const v = m === 'health' ? (frame.health?.index ?? 0) : (frame.data?.[m] ?? 0);
    return [t, +v.toFixed(2)];
  });
}

function buildOption() {
  const dark = uiStore.theme === 'dark';
  const meta = activeMeta.value;
  const data = getSeriesData();
  const gridColor = dark ? '#1e2d45' : '#e2e8f0';
  const labelColor = dark ? '#64748b' : '#94a3b8';

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: dark ? '#1a2235' : '#fff',
      borderColor: gridColor,
      textStyle: { color: dark ? '#e2e8f0' : '#0f172a', fontSize: 11 },
      formatter: p => `<b>${p[0].axisValue}</b><br/>${meta.label}: <b>${Number(p[0].value[1]).toFixed(1)} ${meta.unit}</b>`,
    },
    grid: { left: 42, right: 8, top: 8, bottom: 28 },
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
      axisLabel: { color: labelColor, fontSize: 9, formatter: v => v },
    },
    dataZoom: [{ type: 'inside' }],
    series: [{
      type: 'line',
      data,
      smooth: true,
      symbol: 'none',
      lineStyle: { color: meta.hex, width: 2 },
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: meta.hex + '40' },
            { offset: 1, color: meta.hex + '00' },
          ],
        },
      },
    }],
  };
}

function updateChart() {
  chartInst.value?.setOption(buildOption(), { notMerge: false, lazyUpdate: true });
}

let raf;
watch([() => store.history.length, active, windowMin], () => {
  cancelAnimationFrame(raf);
  raf = requestAnimationFrame(updateChart);
});
watch(() => uiStore.theme, updateChart);

onMounted(() => {
  chartInst.value = echarts.init(chartEl.value);
  updateChart();
  const ro = new ResizeObserver(() => chartInst.value?.resize());
  ro.observe(chartEl.value);
  onUnmounted(() => { ro.disconnect(); chartInst.value?.dispose(); cancelAnimationFrame(raf); });
});
</script>

<style scoped>
.trends-panel { display: flex; flex-direction: column; gap: 0; }
.trends-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 0.5rem;
}
.trends-controls { display: flex; align-items: center; gap: 0.3rem; flex-wrap: wrap; }
.chart-area { width: 100%; height: 200px; }
</style>
