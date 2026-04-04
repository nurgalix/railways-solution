<template>
  <div class="card">
    <div class="card-title">Топливо / Энергия</div>

    <!-- Fuel level -->
    <div class="metric-row">
      <div class="metric-header">
        <span class="metric-name">Уровень топлива</span>
        <span class="metric-value font-mono" :style="{ color: fuelColor }">{{ fuelLevel }}%</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" :style="{ width: fuelLevel + '%', background: fuelColor }"></div>
      </div>
      <div class="metric-sub">
        <span>Расход: <b>{{ fuelConsumption }} л/ч</b></span>
        <span>Запас: <b>{{ fuelRange }} км</b></span>
      </div>
    </div>

    <div class="card-divider"></div>

    <!-- Electrical -->
    <div class="flex justify-between gap-2">
      <div class="metric-row" style="flex:1; margin-bottom:0">
        <div class="metric-header">
          <span class="metric-name">Ток</span>
          <span class="metric-value font-mono">{{ current }} А</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill bar-fill--accent" :style="{ width: Math.min(current / 14, 100) + '%' }"></div>
        </div>
      </div>
      <div class="metric-row" style="flex:1; margin-bottom:0">
        <div class="metric-header">
          <span class="metric-name">Мощность</span>
          <span class="metric-value font-mono c-accent">{{ power }} кВт</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill bar-fill--accent" :style="{ width: Math.min(power / 35, 100) + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- TODO: fuel tank graphic from _reference/cabin/FuelEnergyPanel.vue -->
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store = useTelemetryStore();
const t     = computed(() => store.current);

const fuelLevel       = computed(() => t.value?.fuel_level       ?? 0);
const fuelConsumption = computed(() => t.value?.fuel_consumption ?? 0);
const current         = computed(() => t.value?.current          ?? 0);
const voltage         = computed(() => t.value?.voltage          ?? 0);
const power           = computed(() => Math.round((voltage.value * current.value) / 1000));

const fuelRange = computed(() => {
  const c = fuelConsumption.value;
  const v = t.value?.speed ?? 0;
  if (!c || !v) return '–';
  return Math.round(((fuelLevel.value / 100) * 5000 / c) * v);
});

const fuelColor = computed(() =>
  fuelLevel.value < 15 ? 'var(--crit)'
  : fuelLevel.value < 25 ? 'var(--warn)'
  : 'var(--ok)'
);
</script>
