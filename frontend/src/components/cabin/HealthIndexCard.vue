<template>
  <div class="card" :class="borderClass">
    <div class="card-title">Индекс здоровья</div>

    <!-- Main value -->
    <div class="flex items-baseline gap-3">
      <span class="health-index-value" :style="{ color: catColor }">
        {{ Math.round(health.index) }}
      </span>
      <span class="badge" :class="badgeClass">{{ health.label }}</span>
    </div>

    <!-- Progress bar -->
    <div class="bar-track" style="margin-top:0.6rem; height:8px">
      <div class="bar-fill" :style="{ width: health.index + '%', background: catColor }"></div>
    </div>
    <div class="flex justify-between text-xs text-muted" style="margin-top:0.2rem">
      <span>0</span><span>50</span><span>100</span>
    </div>

    <!-- Category label row -->
    <div class="health-status-row">
      <span class="label">Категория</span>
      <span class="font-mono" style="font-weight:700" :style="{ color: catColor }">
        {{ health.category }}
      </span>
    </div>

    <div class="card-divider"></div>

    <!-- Top factors from backend -->
    <div class="label" style="margin-bottom:0.5rem">Факторы влияния</div>

    <div v-if="!health.top_factors.length" class="text-sm text-muted">
      Ожидание данных…
    </div>

    <div
      v-for="f in health.top_factors.slice(0, 5)"
      :key="f.parameter"
      class="health-factor-row"
    >
      <span class="health-factor-name">{{ f.parameter }}</span>
      <div class="health-factor-bar">
        <div class="bar-track">
          <div class="bar-fill" :style="{ width: f.score + '%', background: scoreColor(f.score) }"></div>
        </div>
      </div>
      <span class="health-factor-score" :style="{ color: scoreColor(f.score) }">
        {{ Math.round(f.score) }}
      </span>
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
}[store.categoryKey] || 'var(--text)'));

const borderClass = computed(() => ({
  normal:   'health-card--ok',
  warning:  'health-card--warn',
  critical: 'health-card--crit',
}[store.categoryKey] || ''));

const badgeClass = computed(() => ({
  normal:   'badge-ok',
  warning:  'badge-warn',
  critical: 'badge-crit',
}[store.categoryKey] || 'badge-ok'));

function scoreColor(s) {
  if (s >= 75) return 'var(--ok)';
  if (s >= 45) return 'var(--warn)';
  return 'var(--crit)';
}
</script>
