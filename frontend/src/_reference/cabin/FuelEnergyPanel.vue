<template>
  <div class="card" role="region" aria-label="Топливо и энергия">
    <div class="card-title">Топливо / Энергия</div>

    <!-- Fuel Level -->
    <div class="metric-row">
      <div class="metric-header">
        <span class="metric-name">Уровень топлива</span>
        <span class="metric-val font-mono" :class="fuelClass">{{ fuelLevel }}%</span>
      </div>
      <div class="progress-track mt-1">
        <div class="progress-fill" :style="{ width: fuelLevel + '%', background: fuelBarColor }"></div>
      </div>
      <div class="metric-sub">
        <span>Расход: <b>{{ fuelConsumption }} л/ч</b></span>
        <span>Запас: <b>{{ fuelRange }} км</b></span>
      </div>
    </div>

    <div class="divider"></div>

    <!-- Tank Graphic -->
    <div class="tank-graphic" aria-hidden="true">
      <svg viewBox="0 0 120 60" width="100%" style="max-width:140px">
        <!-- Tank outline -->
        <rect x="8" y="5" width="104" height="50" rx="6" fill="none"
          stroke="var(--color-border)" stroke-width="2" />
        <!-- Fuel fill (right to left) -->
        <rect :x="fuelFillX" y="7" :width="fuelFillW" height="46" rx="4"
          :fill="fuelBarColor" opacity="0.4" class="tank-fill" />
        <rect :x="fuelFillX" y="7" :width="fuelFillW" height="46" rx="4"
          :fill="fuelBarColor" opacity="0.15" />
        <!-- Level lines -->
        <line v-for="(pct, i) in [25, 50, 75]" :key="i"
          :x1="8 + pct" y1="5" :x2="8 + pct" y2="55"
          stroke="var(--color-border)" stroke-width="0.8" stroke-dasharray="2 2" />
        <!-- Label -->
        <text x="60" y="33" text-anchor="middle" fill="var(--color-text)"
          style="font-size:13px;font-weight:700;font-family:monospace">
          {{ fuelLevel }}%
        </text>
      </svg>
    </div>

    <div class="divider"></div>

    <!-- Current & Power -->
    <div class="metrics-grid">
      <div class="mg-item">
        <span class="mg-label">Ток</span>
        <span class="mg-value font-mono">{{ current }} А</span>
        <div class="progress-track mt-1">
          <div class="progress-fill"
            :style="{ width: Math.min(current / 14, 100) + '%', background: 'var(--color-chart-4)' }"></div>
        </div>
      </div>
      <div class="mg-item">
        <span class="mg-label">Мощность (расч.)</span>
        <span class="mg-value font-mono">{{ power }} кВт</span>
        <div class="progress-track mt-1">
          <div class="progress-fill"
            :style="{ width: Math.min(power / 35, 100) + '%', background: 'var(--color-chart-2)' }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store = useTelemetryStore();
const t = computed(() => store.current);

const fuelLevel       = computed(() => t.value?.fuel_level ?? 0);
const fuelConsumption = computed(() => t.value?.fuel_consumption ?? 0);
const current         = computed(() => t.value?.current ?? 0);
const voltage         = computed(() => t.value?.voltage ?? 0);

// Estimated range: tank capacity ~5000 L, consumption in L/h, speed in km/h
const fuelRange = computed(() => {
  const c = fuelConsumption.value;
  const v = t.value?.speed ?? 0;
  if (!c || !v) return '–';
  const litersLeft = (fuelLevel.value / 100) * 5000;
  return Math.round((litersLeft / c) * v);
});

const power = computed(() => Math.round((voltage.value * current.value) / 1000));

const fuelClass = computed(() =>
  fuelLevel.value < 15 ? 'status-critical'
  : fuelLevel.value < 25 ? 'status-warning'
  : ''
);

const fuelBarColor = computed(() =>
  fuelLevel.value < 15 ? 'var(--color-critical)'
  : fuelLevel.value < 25 ? 'var(--color-warning)'
  : 'var(--color-normal)'
);

// Tank SVG geometry: fill spans from right, width = fuelLevel% of 100px
const fuelFillW = computed(() => Math.max(0, fuelLevel.value));
const fuelFillX = computed(() => 10 + (100 - fuelFillW.value));
</script>

<style scoped>
.metric-row { margin-bottom: 0.5rem; }

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-name { font-size: 0.78rem; color: var(--color-text-sub); }
.metric-val  { font-size: 1.1rem; font-weight: 700; color: var(--color-text); }

.metric-sub {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: var(--color-text-muted);
  margin-top: 0.25rem;
}

.metric-sub b { color: var(--color-text-sub); }

.divider {
  height: 1px;
  background: var(--color-border);
  margin: 0.6rem 0;
}

.tank-graphic {
  display: flex;
  justify-content: center;
  margin: 0.25rem 0;
}

.tank-fill { transition: x 0.4s ease, width 0.4s ease; }

.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.mg-item { display: flex; flex-direction: column; gap: 0.15rem; }
.mg-label { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--color-text-muted); }
.mg-value { font-size: 0.95rem; font-weight: 700; color: var(--color-text); }
</style>
