<template>
  <div class="card alerts-panel" role="region" aria-label="Сообщения и рекомендации" aria-live="polite">
    <div class="card-title">
      Сообщения
      <span v-if="alerts.length" class="alert-count" :class="countClass">
        {{ alerts.length }}
      </span>
    </div>

    <!-- No alerts -->
    <div v-if="!alerts.length" class="no-alerts">
      <span class="no-alerts-icon" aria-hidden="true">✓</span>
      <span>Нарушений не обнаружено</span>
    </div>

    <!-- Alert list -->
    <transition-group name="alert-anim" tag="div" class="alert-list">
      <div
        v-for="alert in sortedAlerts"
        :key="alert.id"
        class="alert-item animate-fade-in"
        :class="`alert-item--${alert.severity}`"
        :role="alert.severity === 'critical' ? 'alert' : 'status'"
      >
        <div class="alert-icon" :class="`alert-icon--${alert.severity}`" aria-hidden="true">
          {{ alert.severity === 'critical' ? '⚠' : 'ℹ' }}
        </div>
        <div class="alert-body">
          <div class="alert-title">{{ alert.title }}</div>
          <div class="alert-message">{{ alert.message }}</div>
          <div class="alert-rec" v-if="alert.recommendation">
            <span class="rec-prefix">→</span> {{ alert.recommendation }}
          </div>
          <div class="alert-time">{{ formatTime(alert.timestamp) }}</div>
        </div>
        <div class="alert-badge">
          <span class="badge" :class="`badge-${alert.severity}`">
            {{ severityLabel(alert.severity) }}
          </span>
        </div>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store = useTelemetryStore();

const alerts = computed(() => store.current?.alerts ?? []);

const sortedAlerts = computed(() =>
  [...alerts.value].sort((a, b) => {
    const order = { critical: 0, warning: 1, info: 2 };
    return (order[a.severity] ?? 9) - (order[b.severity] ?? 9);
  })
);

const countClass = computed(() => {
  const hasCrit = alerts.value.some(a => a.severity === 'critical');
  return hasCrit ? 'count-critical' : 'count-warning';
});

function severityLabel(s) {
  return { critical: 'КРИТИЧНО', warning: 'ВНИМАНИЕ', info: 'ИНФО' }[s] || s.toUpperCase();
}

function formatTime(ts) {
  if (!ts) return '';
  return new Date(ts).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
</script>

<style scoped>
.alerts-panel {}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.alert-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  border-radius: 999px;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0 4px;
}

.count-critical { background: var(--color-critical-bg); color: var(--color-critical); }
.count-warning  { background: var(--color-warning-bg);  color: var(--color-warning);  }

.no-alerts {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 0;
  color: var(--color-normal);
  font-size: 0.82rem;
  font-weight: 500;
}

.no-alerts-icon { font-size: 1.1rem; }

.alert-list { display: flex; flex-direction: column; gap: 0.5rem; }

.alert-item {
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  border-left: 3px solid transparent;
}

.alert-item--critical {
  background: var(--color-critical-bg);
  border-left-color: var(--color-critical);
}

.alert-item--warning {
  background: var(--color-warning-bg);
  border-left-color: var(--color-warning);
}

.alert-item--info {
  background: var(--color-accent-glow);
  border-left-color: var(--color-accent);
}

.alert-icon {
  font-size: 1rem;
  flex-shrink: 0;
  line-height: 1.3;
}

.alert-icon--critical { color: var(--color-critical); }
.alert-icon--warning  { color: var(--color-warning);  }
.alert-icon--info     { color: var(--color-accent);   }

.alert-body { flex: 1; min-width: 0; }

.alert-title {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 0.15rem;
}

.alert-message {
  font-size: 0.7rem;
  color: var(--color-text-sub);
  line-height: 1.4;
}

.alert-rec {
  font-size: 0.68rem;
  color: var(--color-text-muted);
  margin-top: 0.2rem;
  font-style: italic;
}

.rec-prefix { color: var(--color-accent); font-style: normal; font-weight: 600; }

.alert-time {
  font-size: 0.6rem;
  color: var(--color-text-muted);
  margin-top: 0.25rem;
  font-family: monospace;
}

.alert-badge { flex-shrink: 0; }

/* Transitions */
.alert-anim-enter-active { transition: all 0.3s ease; }
.alert-anim-leave-active { transition: all 0.25s ease; }
.alert-anim-enter-from   { opacity: 0; transform: translateY(-6px); }
.alert-anim-leave-to     { opacity: 0; transform: translateX(10px); }
</style>
