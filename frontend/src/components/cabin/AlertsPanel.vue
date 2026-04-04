<template>
  <div class="card">
    <div class="card-title">
      Алерты
      <span v-if="alerts.length" class="badge badge-crit">{{ alerts.length }}</span>
    </div>

    <div v-if="!alerts.length" class="alerts-empty">
      <span>✓</span> Нарушений не обнаружено
    </div>

    <transition-group name="alert-anim" tag="div" class="alert-list" role="list">
      <div
        v-for="a in sorted"
        :key="a.id ?? a.code"
        class="alert-item"
        :class="`alert-item--${a.severity}`"
        :role="a.severity === 'critical' ? 'alert' : 'status'"
      >
        <span class="alert-icon" :class="`alert-icon--${a.severity}`">
          {{ a.severity === 'critical' ? '⚠' : 'ℹ' }}
        </span>
        <div class="alert-body">
          <div class="alert-title">{{ a.code }}</div>
          <div class="alert-message">{{ a.message }}</div>
          <div v-if="a.recommendation" class="alert-rec">
            <span class="alert-rec-arrow">→</span> {{ a.recommendation }}
          </div>
          <div v-if="a.parameter" class="alert-time">
            {{ a.parameter }}: {{ a.value?.toFixed(2) }} (порог {{ a.threshold }})
          </div>
          <div class="alert-time">{{ fmt(a.timestamp) }}</div>
        </div>
        <span class="badge" :class="a.severity === 'critical' ? 'badge-crit' : a.severity === 'warning' ? 'badge-warn' : 'badge-ok'">
          {{ severityLabel(a.severity) }}
        </span>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store  = useTelemetryStore();
const alerts = computed(() => store.alerts);

const sorted = computed(() =>
  [...alerts.value].sort((a, b) => {
    const o = { critical: 0, warning: 1, info: 2 };
    return (o[a.severity] ?? 9) - (o[b.severity] ?? 9);
  })
);

const severityLabel = s => ({ critical: 'КРИТИЧНО', warning: 'ВНИМАНИЕ', info: 'ИНФО' }[s] ?? s.toUpperCase());

function fmt(ts) {
  if (!ts) return '';
  return new Date(ts).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
</script>
