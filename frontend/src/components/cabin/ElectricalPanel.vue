<template>
  <div class="card">
    <div class="card-title">Электрика</div>

    <!-- Health factor breakdown for electrical params from backend -->
    <div v-if="electricalFactors.length">
      <div v-for="f in electricalFactors" :key="f.parameter" class="sensor-item" style="margin-bottom:0.7rem">
        <div class="sensor-header">
          <span class="sensor-name">{{ f.parameter }}</span>
          <span class="sensor-value font-mono" :style="{ color: scoreColor(f.score) }">
            {{ Math.round(f.score) }}/100
          </span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" :style="{ width: f.score + '%', background: scoreColor(f.score) }"></div>
        </div>
        <div class="sensor-range-row">
          <span class="text-xs" :style="{ color: statusColor(f.status) }">{{ statusLabel(f.status) }}</span>
          <span class="text-xs text-muted">вес {{ (f.weight * 100).toFixed(0) }}%</span>
        </div>
      </div>
    </div>

    <!-- No electrical factors in current frame -->
    <div v-else class="text-sm text-muted" style="padding:0.5rem 0">
      Электрические параметры включены в индекс здоровья.
    </div>

    <div class="card-divider"></div>

    <!-- Overall electrical health contribution -->
    <div class="flex justify-between items-center">
      <span class="label">Влияние на индекс</span>
      <span class="font-mono text-sm" :style="{ color: impactColor }">
        {{ totalImpact > 0 ? '−' : '' }}{{ totalImpact.toFixed(1) }}
      </span>
    </div>

    <!-- Backend alerts for electrical params -->
    <div v-if="electricalAlerts.length" style="margin-top:0.6rem">
      <div v-for="a in electricalAlerts" :key="a.id ?? a.code" class="alert-item" :class="`alert-item--${a.severity}`">
        <span class="alert-icon" :class="`alert-icon--${a.severity}`">⚠</span>
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

const ELECTRICAL_PARAMS = new Set(['voltage', 'current', 'power', 'electric', 'traction']);

const electricalFactors = computed(() =>
  (store.health.top_factors ?? []).filter(f =>
    ELECTRICAL_PARAMS.has(f.parameter.toLowerCase()) ||
    f.parameter.toLowerCase().includes('volt') ||
    f.parameter.toLowerCase().includes('curr') ||
    f.parameter.toLowerCase().includes('trac')
  )
);

const totalImpact = computed(() =>
  electricalFactors.value.reduce((s, f) => s + (f.impact ?? 0), 0)
);

const impactColor = computed(() =>
  totalImpact.value > 5 ? 'var(--crit)'
  : totalImpact.value > 2 ? 'var(--warn)'
  : 'var(--ok)'
);

const electricalAlerts = computed(() =>
  (store.alerts ?? []).filter(a =>
    ELECTRICAL_PARAMS.has((a.parameter ?? '').toLowerCase())
  )
);

function scoreColor(s)  { return s >= 75 ? 'var(--ok)' : s >= 45 ? 'var(--warn)' : 'var(--crit)'; }
function statusColor(s) { return s === 'normal' ? 'var(--ok)' : s === 'warning' ? 'var(--warn)' : 'var(--crit)'; }
function statusLabel(s) { return { normal: 'норма', warning: 'внимание', critical: 'критично' }[s] ?? s; }
</script>
