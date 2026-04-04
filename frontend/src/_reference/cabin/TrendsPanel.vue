<template>
  <div class="card trends-panel" role="region" aria-label="Тренды телеметрии">
    <div class="trends-header">
      <div class="card-title" style="margin:0">Тренды</div>
      <div class="trend-controls">
        <button
          v-for="opt in windowOptions"
          :key="opt.value"
          class="win-btn"
          :class="{ active: windowMin === opt.value }"
          @click="windowMin = opt.value"
          :aria-pressed="windowMin === opt.value"
        >{{ opt.label }}</button>

        <!-- Replay scrubber -->
        <template v-if="history.length > 0">
          <input
            type="range"
            class="replay-slider"
            :min="0"
            :max="history.length - 1"
            v-model="replayPos"
            :title="`Перемотка: ${replayTimeLabel}`"
            aria-label="Перемотка истории"
          />
          <span class="replay-time font-mono">{{ replayTimeLabel }}</span>
        </template>
      </div>
    </div>

    <!-- Active metric tabs -->
    <div class="metric-tabs">
      <button
        v-for="m in metrics"
        :key="m.key"
        class="tab-btn"
        :class="{ active: activeMetric === m.key }"
        :style="activeMetric === m.key ? { borderColor: m.color, color: m.color } : {}"
        @click="activeMetric = m.key"
      >{{ m.label }}</button>
    </div>

    <!-- Chart area (pure canvas via ECharts option) -->
    <div ref="chartEl" class="chart-area" aria-hidden="true"></div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, shallowRef } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';
import { useUiStore } from '@/stores/ui.js';
import * as echarts from 'echarts/core';
import { LineChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, DataZoomComponent, LegendComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([LineChart, GridComponent, TooltipComponent, DataZoomComponent, LegendComponent, CanvasRenderer]);

const store   = useTelemetryStore();
const uiStore = useUiStore();

const chartEl    = ref(null);
const chartInst  = shallowRef(null);
const windowMin  = ref(5);
const replayPos  = ref(0);
const activeMetric = ref('speed');

const windowOptions = [
  { label: '1м',  value: 1  },
  { label: '5м',  value: 5  },
  { label: '10м', value: 10 },
  { label: '15м', value: 15 },
];

const metrics = [
  { key: 'speed',       label: 'Скорость',   unit: 'км/ч', color: 'var(--color-chart-1)' },
  { key: 'temp_engine', label: 'Темп. двиг', unit: '°C',   color: 'var(--color-chart-3)' },
  { key: 'fuel_level',  label: 'Топливо',    unit: '%',    color: 'var(--color-chart-2)' },
  { key: 'voltage',     label: 'Напряжение', unit: 'В',    color: 'var(--color-chart-4)' },
  { key: 'health',      label: 'Здоровье',   unit: '/100', color: 'var(--color-normal)'  },
];

const history = computed(() => store.history);

// How many data points to show
const showCount = computed(() => Math.min(windowMin.value * 60, history.value.length));

// Replay position label
const replayTimeLabel = computed(() => {
  const idx = Math.min(Number(replayPos.value), history.value.length - 1);
  if (!history.value[idx]) return '–';
  return new Date(history.value[idx].timestamp)
    .toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
});

// Get the slice of data for the chart
function getSeriesData() {
  const total = history.value.length;
  const count = showCount.value;
  const slice = history.value.slice(Math.max(0, total - count));
  const m = activeMetric.value;

  return slice.map(s => {
    const time = new Date(s.timestamp).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    let val;
    if (m === 'health') {
      // Re-use healthHistory if possible
      val = s._health ?? s.speed; // fallback until we compute it
    } else {
      val = s[m] ?? 0;
    }
    return [time, val];
  });
}

const activeMeta = computed(() => metrics.find(m => m.key === activeMetric.value) || metrics[0]);

function buildOption() {
  const dark = uiStore.theme === 'dark';
  const data = getSeriesData();
  const meta = activeMeta.value;

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: dark ? '#1a2235' : '#fff',
      borderColor: dark ? '#1e2d45' : '#e2e8f0',
      textStyle: { color: dark ? '#e2e8f0' : '#0f172a', fontSize: 11 },
      formatter: params => {
        const p = params[0];
        return `<b>${p.axisValue}</b><br/>${meta.label}: <b>${Number(p.value[1]).toFixed(1)} ${meta.unit}</b>`;
      },
    },
    grid: { left: 44, right: 12, top: 10, bottom: 36 },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      axisLine:  { lineStyle: { color: dark ? '#1e2d45' : '#e2e8f0' } },
      axisLabel: { color: dark ? '#64748b' : '#94a3b8', fontSize: 9 },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value',
      axisLine:  { show: false },
      splitLine: { lineStyle: { color: dark ? '#1e2d45' : '#e2e8f0', type: 'dashed' } },
      axisLabel: { color: dark ? '#64748b' : '#94a3b8', fontSize: 9, formatter: v => v + ' ' + meta.unit },
    },
    dataZoom: [{
      type: 'inside',
      start: 0,
      end: 100,
    }],
    series: [{
      type: 'line',
      data,
      smooth: true,
      symbol: 'none',
      lineStyle: { color: meta.color, width: 2 },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: meta.color + '40' },
            { offset: 1, color: meta.color + '00' },
          ],
        },
      },
    }],
  };
}

function updateChart() {
  if (chartInst.value) {
    chartInst.value.setOption(buildOption(), { notMerge: false, lazyUpdate: true });
  }
}

// Watch history for live updates
let updateRaf;
watch([() => store.history.length, activeMetric, windowMin], () => {
  cancelAnimationFrame(updateRaf);
  updateRaf = requestAnimationFrame(updateChart);
});

// Re-theme on theme change
watch(() => uiStore.theme, updateChart);

onMounted(() => {
  chartInst.value = echarts.init(chartEl.value);
  updateChart();

  const ro = new ResizeObserver(() => chartInst.value?.resize());
  ro.observe(chartEl.value);
  onUnmounted(() => {
    ro.disconnect();
    chartInst.value?.dispose();
    cancelAnimationFrame(updateRaf);
  });
});
</script>

<style scoped>
.trends-panel { display: flex; flex-direction: column; }

.trends-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.6rem;
}

.trend-controls {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  flex-wrap: wrap;
}

.win-btn {
  padding: 0.2rem 0.45rem;
  font-size: 0.7rem;
  font-weight: 600;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-muted);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
}
.win-btn.active, .win-btn:hover {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: #fff;
}

.replay-slider {
  width: 100px;
  accent-color: var(--color-accent);
}

.replay-time {
  font-size: 0.65rem;
  color: var(--color-text-muted);
  min-width: 60px;
}

.metric-tabs {
  display: flex;
  gap: 0.3rem;
  flex-wrap: wrap;
  margin-bottom: 0.5rem;
}

.tab-btn {
  padding: 0.2rem 0.55rem;
  font-size: 0.7rem;
  font-weight: 500;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-muted);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
}
.tab-btn.active { font-weight: 700; background: transparent; }
.tab-btn:hover  { color: var(--color-text); }

.chart-area {
  flex: 1;
  min-height: 180px;
  height: 220px;
}
</style>
