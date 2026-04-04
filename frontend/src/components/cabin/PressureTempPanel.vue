<template>
  <div class="card">
    <div class="card-title">Давление / Температура</div>

    <div class="sensor-grid">

      <!-- Pressure -->
      <div class="sensor-item">
        <div class="sensor-header">
          <span class="sensor-name">Давление</span>
          <span class="sensor-value font-mono" :style="{ color: pressureColor }">
            {{ pressure.toFixed(2) }} бар
          </span>
        </div>
        <div class="bar-track" style="position:relative">
          <div :style="okZone(4.5, 5.5, 0, 10)"></div>
          <div class="bar-fill" :style="{ width: Math.min(pressure / 10 * 100, 100) + '%', background: pressureColor }"></div>
        </div>
        <div class="sensor-range-row">
          <span>0</span>
          <span :style="{ color: pressureColor, fontSize:'0.58rem', fontWeight:600 }">{{ pressureStatus }}</span>
          <span>10</span>
        </div>
      </div>

      <!-- Temperature -->
      <div class="sensor-item">
        <div class="sensor-header">
          <span class="sensor-name">Температура</span>
          <span class="sensor-value font-mono" :style="{ color: tempColor }">
            {{ temperature.toFixed(1) }} °C
          </span>
        </div>
        <div class="bar-track" style="position:relative">
          <div :style="okZone(60, 88, 0, 120)"></div>
          <div class="bar-fill" :style="{ width: Math.min(temperature / 120 * 100, 100) + '%', background: tempColor }"></div>
        </div>
        <div class="sensor-range-row">
          <span>0</span>
          <span :style="{ color: tempColor, fontSize:'0.58rem', fontWeight:600 }">{{ tempStatus }}</span>
          <span>120</span>
        </div>
      </div>

    </div>

    <!-- Active alerts from backend related to these params -->
    <div v-if="relatedAlerts.length" style="margin-top:0.75rem">
      <div class="label" style="margin-bottom:0.3rem">Связанные алерты</div>
      <div v-for="a in relatedAlerts" :key="a.id ?? a.code" class="alert-item" :class="`alert-item--${a.severity}`">
        <span class="alert-icon" :class="`alert-icon--${a.severity}`">{{ a.severity === 'critical' ? '⚠' : 'ℹ' }}</span>
        <div class="alert-body">
          <div class="alert-title">{{ a.code }}</div>
          <div class="alert-message">{{ a.message }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store = useTelemetryStore();

const pressure    = computed(() => store.data?.pressure    ?? 0);
const temperature = computed(() => store.data?.temperature ?? 0);

// Status labels
const pressureStatus = computed(() => {
  const p = pressure.value;
  if (p >= 4.5 && p <= 5.5) return 'норма';
  if (p >= 4.0 && p <= 6.0) return 'внимание';
  return 'критично';
});

const tempStatus = computed(() => {
  const t = temperature.value;
  if (t >= 60 && t <= 88) return 'норма';
  if (t >= 50 && t <= 100) return 'внимание';
  return 'критично';
});

// Colors
const pressureColor = computed(() => {
  const p = pressure.value;
  if (p >= 4.5 && p <= 5.5) return 'var(--ok)';
  if (p >= 4.0 && p <= 6.0) return 'var(--warn)';
  return 'var(--crit)';
});

const tempColor = computed(() => {
  const t = temperature.value;
  if (t > 100) return 'var(--crit)';
  if (t > 88)  return 'var(--warn)';
  return 'var(--ok)';
});

// OK zone style helper (position:absolute overlay on bar-track)
function okZone(okMin, okMax, rangeMin, rangeMax) {
  const total = rangeMax - rangeMin;
  const left  = ((okMin - rangeMin) / total * 100).toFixed(1);
  const width = ((okMax - okMin)    / total * 100).toFixed(1);
  return {
    position: 'absolute', top: 0, bottom: 0, borderRadius: '3px',
    background: 'rgba(16,185,129,0.15)',
    left: left + '%', width: width + '%',
  };
}

// Filter alerts relevant to pressure/temperature
const relatedAlerts = computed(() =>
  (store.alerts ?? []).filter(a =>
    a.parameter === 'pressure' || a.parameter === 'temperature'
  )
);
</script>
