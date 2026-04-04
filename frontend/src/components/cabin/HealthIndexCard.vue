<template>
  <div class="card" :class="borderClass">
    <div class="card-title">Индекс здоровья</div>

    <!-- Main value -->
    <div class="flex items-baseline gap-3">
      <span class="health-index-value" :style="{ color: catColor }">
        {{ health.index }}
      </span>
      <span class="badge" :class="badgeClass">{{ store.category.label }}</span>
    </div>

    <!-- Simple bar representing overall score -->
    <div class="bar-track" style="margin-top:0.6rem; height:8px">
      <div class="bar-fill" :style="{ width: health.index + '%', background: catColor }"></div>
    </div>
    <div class="flex justify-between text-xs text-muted" style="margin-top:0.2rem">
      <span>0</span><span>50</span><span>100</span>
    </div>

    <div class="card-divider"></div>

    <!-- Top factors -->
    <div class="label" style="margin-bottom:0.5rem">Факторы влияния</div>
    <div v-if="!health.factors.length" class="text-sm text-muted">Ожидание данных…</div>
    <div
      v-for="f in health.factors.slice(0, 5)" :key="f.key"
      class="health-factor-row"
    >
      <span class="health-factor-name">{{ f.label }}</span>
      <div class="health-factor-bar">
        <div class="bar-track">
          <div class="bar-fill" :style="{ width: f.score + '%', background: scoreColor(f.score) }"></div>
        </div>
      </div>
      <span class="health-factor-score" :style="{ color: scoreColor(f.score) }">
        {{ Math.round(f.score) }}
      </span>
    </div>

    <!-- Alert penalty -->
    <div v-if="health.alertPenalty > 0" style="margin-top:0.5rem; text-align:right">
      <span class="badge badge-crit">−{{ health.alertPenalty }} алерты</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store  = useTelemetryStore();
const health = computed(() => store.health);

const catColor = computed(() => ({
  normal:   'var(--ok)',
  warning:  'var(--warn)',
  critical: 'var(--crit)',
}[store.category.key] || 'var(--text)'));

const borderClass = computed(() => ({
  normal:   'health-card--ok',
  warning:  'health-card--warn',
  critical: 'health-card--crit',
}[store.category.key] || ''));

const badgeClass = computed(() => ({
  normal:   'badge-ok',
  warning:  'badge-warn',
  critical: 'badge-crit',
}[store.category.key] || 'badge-ok'));

function scoreColor(s) {
  if (s >= 75) return 'var(--ok)';
  if (s >= 45) return 'var(--warn)';
  return 'var(--crit)';
}
</script>
