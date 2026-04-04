<template>
  <div class="card" role="region" aria-label="Электрика">
    <div class="card-title">Электрика</div>

    <div class="elec-grid">
      <!-- Voltage -->
      <div class="elec-item">
        <div class="elec-label">Напряжение</div>
        <div class="elec-value font-mono" :class="voltageClass">{{ voltage }} <span class="elec-unit">В</span></div>
        <div class="progress-track mt-1">
          <div class="progress-fill" :style="{ width: voltageRatio + '%', background: voltageColor }"></div>
        </div>
        <div class="elec-range">
          <span>480</span>
          <span class="elec-ok-label">570–640</span>
          <span>720</span>
        </div>
      </div>

      <!-- Current -->
      <div class="elec-item">
        <div class="elec-label">Ток</div>
        <div class="elec-value font-mono" :class="currentClass">{{ current }} <span class="elec-unit">А</span></div>
        <div class="progress-track mt-1">
          <div class="progress-fill" :style="{ width: currentRatio + '%', background: 'var(--color-chart-4)' }"></div>
        </div>
        <div class="elec-range">
          <span>0</span>
          <span class="elec-ok-label">200–1200</span>
          <span>1400</span>
        </div>
      </div>
    </div>

    <!-- Power summary -->
    <div class="power-summary">
      <div class="power-block">
        <span class="power-label">Мощность</span>
        <span class="power-value font-mono">{{ power }} <span class="power-unit">кВт</span></span>
      </div>
      <div class="power-block">
        <span class="power-label">Коэффициент мощн.</span>
        <span class="power-value font-mono">0.92</span>
      </div>
    </div>

    <!-- Circuit diagram (simplified SVG) -->
    <div class="circuit" aria-hidden="true">
      <svg viewBox="0 0 220 60" width="100%">
        <!-- Bus bar -->
        <line x1="10" y1="30" x2="210" y2="30" stroke="var(--color-border)" stroke-width="2"/>
        <!-- Generator symbol -->
        <circle cx="30" cy="30" r="14" fill="none" :stroke="voltageColor" stroke-width="2"/>
        <text x="30" y="34" text-anchor="middle" :fill="voltageColor" style="font-size:8px;font-weight:700">G</text>
        <!-- Load boxes -->
        <g v-for="(load, i) in loads" :key="i">
          <rect :x="70 + i * 40" y="20" width="22" height="18" rx="3"
            fill="var(--color-surface-2)" :stroke="load.color" stroke-width="1.5"/>
          <text :x="81 + i * 40" y="31" text-anchor="middle" :fill="load.color" style="font-size:6px;font-weight:600">
            {{ load.label }}
          </text>
          <line :x1="81 + i * 40" y1="30" :x2="81 + i * 40" y2="38"
            :stroke="load.color" stroke-width="1.5"/>
        </g>
        <!-- Voltage label -->
        <text x="30" y="54" text-anchor="middle" :fill="voltageColor" style="font-size:7px;font-weight:600">
          {{ voltage }}В
        </text>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store = useTelemetryStore();
const t = computed(() => store.current);

const voltage = computed(() => t.value?.voltage ?? 0);
const current = computed(() => t.value?.current ?? 0);
const power   = computed(() => Math.round((voltage.value * current.value) / 1000));

// Voltage: ok 570–640, warn 540–570 or 640–670, crit otherwise
const voltageClass = computed(() => {
  const v = voltage.value;
  if (v >= 570 && v <= 640) return '';
  if (v >= 540 && v <= 670) return 'status-warning';
  return 'status-critical';
});

const voltageColor = computed(() => {
  const v = voltage.value;
  if (v >= 570 && v <= 640) return 'var(--color-normal)';
  if (v >= 540 && v <= 670) return 'var(--color-warning)';
  return 'var(--color-critical)';
});

const voltageRatio = computed(() =>
  Math.min(100, Math.max(0, ((voltage.value - 480) / (720 - 480)) * 100))
);

const currentClass = computed(() =>
  current.value > 1200 ? 'status-critical' : current.value > 1000 ? 'status-warning' : ''
);

const currentRatio = computed(() =>
  Math.min(100, Math.max(0, (current.value / 1400) * 100))
);

// Simplified electrical loads
const loads = computed(() => [
  { label: 'TM',  color: current.value > 1200 ? 'var(--color-critical)' : 'var(--color-chart-1)' },
  { label: 'AUX', color: 'var(--color-chart-2)' },
  { label: 'HVT', color: 'var(--color-chart-3)' },
  { label: 'BRK', color: 'var(--color-chart-4)' },
]);
</script>

<style scoped>
.elec-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.9rem;
}

.elec-item { display: flex; flex-direction: column; }

.elec-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
}

.elec-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--color-text);
  transition: color 0.3s;
  line-height: 1.2;
}

.elec-unit { font-size: 0.75rem; color: var(--color-text-muted); font-weight: 400; }

.elec-range {
  display: flex;
  justify-content: space-between;
  font-size: 0.6rem;
  color: var(--color-text-muted);
  margin-top: 0.15rem;
}

.elec-ok-label { color: var(--color-normal); font-weight: 600; }

.power-summary {
  display: flex;
  justify-content: space-around;
  margin: 0.75rem 0 0.5rem;
  padding: 0.5rem 0;
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}

.power-block { display: flex; flex-direction: column; align-items: center; gap: 0.1rem; }
.power-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--color-text-muted); }
.power-value { font-size: 1.1rem; font-weight: 700; color: var(--color-accent); }
.power-unit  { font-size: 0.7rem; color: var(--color-text-muted); font-weight: 400; }

.circuit {
  margin-top: 0.4rem;
  opacity: 0.85;
}
</style>
