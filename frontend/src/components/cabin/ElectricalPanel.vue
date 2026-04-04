<template>
  <div class="card">
    <div class="card-title">Электрика</div>

    <div class="elec-grid">
      <div>
        <div class="elec-name">Напряжение</div>
        <div class="elec-value font-mono" :style="{ color: voltageColor }">
          {{ voltage }}<span class="elec-unit"> В</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" :style="{ width: voltageRatio + '%', background: voltageColor }"></div>
        </div>
        <div class="sensor-range-row">
          <span>480</span>
          <span style="color:var(--ok); font-size:0.58rem; font-weight:600">570–640</span>
          <span>720</span>
        </div>
      </div>

      <div>
        <div class="elec-name">Ток</div>
        <div class="elec-value font-mono" :style="{ color: currentColor }">
          {{ current }}<span class="elec-unit"> А</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" :style="{ width: currentRatio + '%', background: currentColor }"></div>
        </div>
        <div class="sensor-range-row">
          <span>0</span>
          <span style="color:var(--ok); font-size:0.58rem; font-weight:600">200–1200</span>
          <span>1400</span>
        </div>
      </div>
    </div>

    <div class="power-row">
      <div class="power-block">
        <span class="power-label">Мощность</span>
        <span class="power-value font-mono">{{ power }} <span style="font-size:0.7rem; color:var(--text-muted); font-weight:400">кВт</span></span>
      </div>
      <div class="power-block">
        <span class="power-label">cosφ</span>
        <span class="power-value font-mono">0.92</span>
      </div>
    </div>

    <!-- TODO: circuit diagram SVG from _reference/cabin/ElectricalPanel.vue -->
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store   = useTelemetryStore();
const t       = computed(() => store.current);

const voltage = computed(() => t.value?.voltage ?? 0);
const current = computed(() => t.value?.current ?? 0);
const power   = computed(() => Math.round((voltage.value * current.value) / 1000));

const voltageColor = computed(() => {
  const v = voltage.value;
  if (v >= 570 && v <= 640) return 'var(--ok)';
  if (v >= 540 && v <= 670) return 'var(--warn)';
  return 'var(--crit)';
});

const currentColor = computed(() =>
  current.value > 1200 ? 'var(--crit)' : current.value > 1000 ? 'var(--warn)' : 'var(--text)'
);

const voltageRatio = computed(() =>
  Math.min(100, Math.max(0, ((voltage.value - 480) / (720 - 480)) * 100))
);

const currentRatio = computed(() =>
  Math.min(100, Math.max(0, (current.value / 1400) * 100))
);
</script>
