<template>
  <div class="card">
    <div class="card-title">Топливо</div>

    <!-- Fuel level -->
    <div class="metric-row">
      <div class="metric-header">
        <span class="metric-name">Уровень топлива</span>
        <span class="metric-value font-mono" :style="{ color: fuelColor }">{{ fuelLevel.toFixed(1) }}%</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" :style="{ width: fuelLevel + '%', background: fuelColor }"></div>
      </div>
      <div class="metric-sub">
        <span>Ёмкость: <b>5000 л</b></span>
        <span>Остаток: <b>{{ fuelLiters }} л</b></span>
      </div>
    </div>

    <div class="card-divider"></div>

    <!-- Temperature & Pressure summary -->
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem">
      <div>
        <div class="label">Температура</div>
        <div class="font-mono" style="font-size:1.1rem; font-weight:700" :style="{ color: tempColor }">
          {{ temperature.toFixed(1) }} °C
        </div>
        <div class="bar-track" style="margin-top:0.25rem">
          <div class="bar-fill" :style="{ width: Math.min(temperature / 120 * 100, 100) + '%', background: tempColor }"></div>
        </div>
      </div>
      <div>
        <div class="label">Давление</div>
        <div class="font-mono" style="font-size:1.1rem; font-weight:700" :style="{ color: pressureColor }">
          {{ pressure.toFixed(2) }} бар
        </div>
        <div class="bar-track" style="margin-top:0.25rem">
          <div class="bar-fill" :style="{ width: Math.min(pressure / 10 * 100, 100) + '%', background: pressureColor }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store = useTelemetryStore();

const fuelLevel   = computed(() => store.data?.fuel_level   ?? 0);
const temperature = computed(() => store.data?.temperature  ?? 0);
const pressure    = computed(() => store.data?.pressure     ?? 0);
const fuelLiters  = computed(() => Math.round((fuelLevel.value / 100) * 5000));

const fuelColor = computed(() =>
  fuelLevel.value < 15 ? 'var(--crit)'
  : fuelLevel.value < 25 ? 'var(--warn)'
  : 'var(--ok)'
);

const tempColor = computed(() =>
  temperature.value > 100 ? 'var(--crit)'
  : temperature.value > 88  ? 'var(--warn)'
  : 'var(--ok)'
);

const pressureColor = computed(() => {
  const p = pressure.value;
  if (p >= 4.5 && p <= 5.5) return 'var(--ok)';
  if (p >= 4.0 && p <= 6.0) return 'var(--warn)';
  return 'var(--crit)';
});
</script>
