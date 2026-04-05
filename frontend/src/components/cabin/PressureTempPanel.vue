<template>
  <div class="card">
    <div class="card-title">Датчики</div>

    <div class="sensor-grid">

      <!-- Pressure -->
      <div class="sensor-item">
        <div class="sensor-header">
          <span class="sensor-name">Давление</span>
          <span class="sensor-value font-mono" :style="{ color: pressureColor }">
            {{ pressure.toFixed(2) }} бар
          </span>
        </div>
        <div class="bar-track" style="position:relative; margin-top:0.35rem">
          <div :style="okZone(4.5, 5.5, 0, 10)"></div>
          <div class="bar-fill" :style="{ width: Math.min(pressure / 10 * 100, 100) + '%', background: pressureColor }"></div>
        </div>
        <div class="sensor-range-row">
          <span>0</span>
          <span :style="{ color: pressureColor, fontSize:'0.6rem', fontWeight:700 }">{{ pressureStatus }}</span>
          <span>10 бар</span>
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
        <div class="bar-track" style="position:relative; margin-top:0.35rem">
          <div :style="okZone(60, 88, 0, 120)"></div>
          <div class="bar-fill" :style="{ width: Math.min(temperature / 120 * 100, 100) + '%', background: tempColor }"></div>
        </div>
        <div class="sensor-range-row">
          <span>0</span>
          <span :style="{ color: tempColor, fontSize:'0.6rem', fontWeight:700 }">{{ tempStatus }}</span>
          <span>120 °C</span>
        </div>
      </div>

    </div>

    
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store       = useTelemetryStore();
const pressure    = computed(() => store.data?.pressure    ?? 0);
const temperature = computed(() => store.data?.temperature ?? 0);

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

const pressureColor = computed(() => {
  const p = pressure.value;
  if (p >= 4.5 && p <= 5.5) return 'var(--ok)';
  if (p >= 4.0 && p <= 6.0) return 'var(--warn)';
  return 'var(--crit)';
});

const tempColor = computed(() =>
  temperature.value > 100 ? 'var(--crit)'
  : temperature.value > 88 ? 'var(--warn)'
  : 'var(--ok)'
);

function okZone(okMin, okMax, rangeMin, rangeMax) {
  const total = rangeMax - rangeMin;
  return {
    position: 'absolute', top: 0, bottom: 0, borderRadius: '3px',
    background: 'rgba(16,185,129,0.15)',
    left:  ((okMin - rangeMin) / total * 100).toFixed(1) + '%',
    width: ((okMax - okMin)    / total * 100).toFixed(1) + '%',
  };
}

</script>
