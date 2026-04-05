<template>
  <div class="card fuel-card">
    <div class="card-title">
      {{ isElectric ? 'Заряд батареи' : 'Топливо' }}
    </div>

    <!-- Semi-circle gauge (180°, opens downward) -->
    <div class="gauge-wrap">
      <svg viewBox="0 0 120 75" class="fuel-svg" aria-hidden="true">

        <!-- Track (top semicircle, rotate 180 → starts at left, ends at right) -->
        <circle cx="60" cy="70" r="48" fill="none"
          stroke="var(--border)" stroke-width="10" stroke-linecap="round"
          stroke-dasharray="150.8 150.8"
          transform="rotate(180 60 70)"/>

        <!-- Fill arc -->
        <circle cx="60" cy="70" r="48" fill="none"
          :stroke="levelColor"
          stroke-width="10" stroke-linecap="round"
          :stroke-dasharray="`${fillLen} 301.6`"
          transform="rotate(180 60 70)"
          class="fuel-fill"/>

        <!-- E / F labels at arc endpoints -->
        <text x="8"   y="72" text-anchor="middle" font-size="10" font-weight="700" fill="var(--crit)">E</text>
        <text x="112" y="72" text-anchor="middle" font-size="10" font-weight="700" fill="var(--ok)">F</text>

        <!-- Value -->
        <text x="60" y="46" text-anchor="middle"
          font-family="'JetBrains Mono',monospace"
          font-size="26" font-weight="800"
          :fill="levelColor">{{ Math.round(level) }}</text>
        <text x="60" y="60" text-anchor="middle" font-size="10" fill="var(--text-muted)">%</text>
      </svg>
    </div>

    <!-- Stats -->
    <div class="fuel-stats">
      <div class="fuel-stat">
        <div class="label">Остаток</div>
        <div class="font-mono" style="font-weight:700; font-size:0.85rem" :style="{ color: levelColor }">
          {{ reserve }}
        </div>
      </div>
      <div class="fuel-stat">
        <div class="label">Ёмкость</div>
        <div class="font-mono" style="font-weight:600; font-size:0.85rem">{{ capacity }}</div>
      </div>
      <div class="fuel-stat">
        <div class="label">Тип</div>
        <div style="font-weight:600; font-size:0.85rem">{{ isElectric ? '⚡ Эл.' : '⛽ Диз.' }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

// Flip to true for an electric locomotive
const isElectric = false;
const TANK_L   = 5000;  // diesel litres
const BATT_KWH = 800;   // electric kWh

const store = useTelemetryStore();
const level = computed(() => store.data?.fuel_level ?? 0);

const reserve  = computed(() =>
  isElectric
    ? (level.value / 100 * BATT_KWH).toFixed(0) + ' кВт·ч'
    : Math.round(level.value / 100 * TANK_L) + ' л'
);
const capacity = computed(() =>
  isElectric ? BATT_KWH + ' кВт·ч' : TANK_L + ' л'
);

const levelColor = computed(() =>
  level.value < 15 ? 'var(--crit)'
  : level.value < 25 ? 'var(--warn)'
  : 'var(--ok)'
);

// Gauge math:
//   r=48, C = 2π*48 = 301.593
//   HALF_ARC = π*48 = 150.796  (180° = top semicircle)
//   transform="rotate(180, 60, 62)": original 3-o'clock → left endpoint
//   Fill goes left → top → right as level 0→100%
const HALF_ARC = 150.796;
const fillLen  = computed(() =>
  Math.max(0, level.value / 100 * HALF_ARC)
);
</script>

<style scoped>
.fuel-card { display: flex; flex-direction: column; }

.gauge-wrap { display: flex; justify-content: center; }

.fuel-svg {
  width: 100%;
  max-width: 200px;
  height: auto;
  overflow: visible;
}

.fuel-fill {
  transition: stroke-dasharray 0.4s ease, stroke 0.4s ease;
}

.fuel-stats {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 0.25rem;
  text-align: center;
}

.fuel-stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}
</style>
