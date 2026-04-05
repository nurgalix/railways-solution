<template>
  <div class="card health-card" :class="borderClass">
    <div class="card-title">Индекс здоровья</div>

    <!-- Big index with ring gauge -->
    <div class="health-main">
      <svg class="health-ring" viewBox="0 0 120 120">
        <!-- Track -->
        <circle cx="60" cy="60" r="50" fill="none" stroke="var(--border)" stroke-width="10"
          stroke-dasharray="235.6 78.5" transform="rotate(135 60 60)" stroke-linecap="round"/>
        <!-- Fill -->
        <circle cx="60" cy="60" r="50" fill="none" :stroke="catColor" stroke-width="10"
          :stroke-dasharray="`${indexDash} 1000`"
          transform="rotate(135 60 60)" stroke-linecap="round"
          style="transition: stroke-dasharray 0.5s ease, stroke 0.5s ease"/>
        <!-- Value text -->
        <text x="60" y="56" text-anchor="middle" font-family="'JetBrains Mono',monospace"
          font-size="30" font-weight="800" :fill="catColor">
          {{ Math.round(health.index) }}
        </text>
        <text x="60" y="72" text-anchor="middle" font-size="10" fill="var(--text-muted)">/100</text>
      </svg>

      <div class="health-info">
        <div class="health-category" :style="{ color: catColor }">{{ healthLabel }}</div>
        <div class="health-cat-code">Категория <b :style="{ color: catColor }">{{ health.category }}</b></div>
        <!-- Compact bar -->
        <div class="bar-track" style="margin-top:0.5rem; height:6px">
          <div class="bar-fill" :style="{ width: health.index + '%', background: catColor }"></div>
        </div>
        <div class="flex justify-between" style="margin-top:0.2rem">
          <span class="text-xs text-muted">0</span>
          <span class="text-xs text-muted">100</span>
        </div>
      </div>
    </div>

    <div class="card-divider"></div>

    <!-- Top factors -->
    <div class="label" style="margin-bottom:0.45rem">Факторы влияния</div>

    <div v-if="!health.top_factors.length" class="text-sm text-muted">
      Ожидание данных…
    </div>

    <div
      v-for="f in health.top_factors.slice(0, 5)"
      :key="f.parameter"
      class="health-factor-row"
    >
      <span class="health-factor-name">{{ factorsLabelrus(f.parameter) }}</span>
      <div class="health-factor-bar">
        <div class="bar-track">
          <div class="bar-fill" :style="{ width: f.score + '%', background: scoreColor(f.score) }"></div>
        </div>
      </div>
      <span class="health-factor-score" :style="{ color: scoreColor(f.score) }">
        {{ Math.round(f.score) }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store  = useTelemetryStore();
const health = computed(() => store.health);

const catColor = computed(() => ({
  normal:   'var(--ok)',
  warning:  'var(--warn)',
  critical: 'var(--crit)',
}[store.categoryKey] ?? 'var(--text)'));

const borderClass = computed(() => ({
  normal:   'health-card--ok',
  warning:  'health-card--warn',
  critical: 'health-card--crit',
}[store.categoryKey] ?? ''));

// Ring arc: r=50, 270° sweep = 2πr * 0.75 ≈ 235.6; gap=78.5
const RING_ARC = 235.6;
const indexDash = computed(() =>
  ((health.value.index / 100) * RING_ARC).toFixed(2)
);

const healthLabel = computed(() => ({
  normal:   'Норма',
  warning:  'Внимание',
  critical: 'Критично',
}[store.categoryKey] ?? store.categoryKey));

function scoreColor(s) {
  if (s >= 75) return 'var(--ok)';
  if (s >= 45) return 'var(--warn)';
  return 'var(--crit)';
}
function factorsLabelrus(factor){
  return ({
    speed: 'Скорость',
    pressure: 'Давление',
    temperature: 'Температура',
    fuel_level: 'Топливо',
    sensor_reliability: 'Датчики',
  }[factor] ?? factor);
}
</script>

<style scoped>
.health-main {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.health-ring {
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}

.health-info {
  flex: 1;
  min-width: 0;
}

.health-category {
  font-size: 1.1rem;
  font-weight: 700;
  line-height: 1.2;
  transition: color 0.4s;
}

.health-cat-code {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.2rem;
}
</style>
