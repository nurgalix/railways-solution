<template>
  <div class="card health-card" :class="`health-card--${store.category.key}`" role="region" aria-label="Индекс здоровья локомотива">
    <div class="card-title">Индекс здоровья</div>

    <!-- SVG Arc Gauge -->
    <div class="gauge-wrap">
      <svg viewBox="0 0 200 130" class="gauge-svg" aria-hidden="true">
        <!-- Track arc -->
        <path
          d="M 20 110 A 90 90 0 0 1 180 110"
          fill="none"
          stroke="var(--color-border)"
          stroke-width="14"
          stroke-linecap="round"
        />
        <!-- Value arc -->
        <path
          d="M 20 110 A 90 90 0 0 1 180 110"
          fill="none"
          :stroke="store.category.color"
          stroke-width="14"
          stroke-linecap="round"
          :stroke-dasharray="arcDashArray"
          class="gauge-arc"
        />
        <!-- Center value -->
        <text x="100" y="96" text-anchor="middle" class="gauge-value" :fill="store.category.color">
          {{ displayIndex }}
        </text>
        <text x="100" y="114" text-anchor="middle" class="gauge-label" fill="var(--color-text-muted)">
          {{ store.category.label }}
        </text>
        <!-- Min / Max labels -->
        <text x="18"  y="128" text-anchor="middle" class="gauge-tick" fill="var(--color-text-muted)">0</text>
        <text x="182" y="128" text-anchor="middle" class="gauge-tick" fill="var(--color-text-muted)">100</text>
      </svg>
    </div>

    <!-- Top-5 contributing factors -->
    <div class="factors" aria-label="Факторы влияния">
      <div class="factors-title">Факторы (топ-5)</div>
      <div
        v-for="f in (store.health.factors || []).slice(0, 5)"
        :key="f.key"
        class="factor-row"
      >
        <span class="factor-label truncate">{{ f.label }}</span>
        <div class="factor-bar-wrap">
          <div class="progress-track" style="flex:1">
            <div
              class="progress-fill"
              :style="{
                width: f.score + '%',
                background: factorColor(f.score),
              }"
            ></div>
          </div>
          <span class="factor-score" :style="{ color: factorColor(f.score) }">
            {{ Math.round(f.score) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Alert penalty badge -->
    <div v-if="store.health.alertPenalty > 0" class="penalty-row">
      <span class="badge badge-critical">−{{ store.health.alertPenalty }} за алерты</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store = useTelemetryStore();

// Animate to current value
const displayIndex = computed(() => store.health.index);

// Arc: full arc length ≈ π*90 ≈ 282.7 (semicircle)
const ARC_LEN = Math.PI * 90;
const arcDashArray = computed(() => {
  const filled = (store.health.index / 100) * ARC_LEN;
  return `${filled} ${ARC_LEN}`;
});

function factorColor(score) {
  if (score >= 75) return 'var(--color-normal)';
  if (score >= 45) return 'var(--color-warning)';
  return 'var(--color-critical)';
}
</script>

<style scoped>
.health-card {
  transition: box-shadow 0.4s ease;
}

.health-card--normal   { box-shadow: var(--shadow-glow-normal); }
.health-card--warning  { box-shadow: var(--shadow-glow-warn);   }
.health-card--critical { box-shadow: var(--shadow-glow-crit);   }

.gauge-wrap {
  display: flex;
  justify-content: center;
  margin: 0.25rem 0;
}

.gauge-svg { width: 100%; max-width: 200px; }

.gauge-arc {
  transition: stroke-dasharray 0.5s ease, stroke 0.5s ease;
}

.gauge-value {
  font-size: 36px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  transition: fill 0.4s;
}

.gauge-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.gauge-tick { font-size: 9px; }

/* Factors */
.factors { margin-top: 0.75rem; }

.factors-title {
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  margin-bottom: 0.5rem;
}

.factor-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}

.factor-label {
  font-size: 0.72rem;
  color: var(--color-text-sub);
  width: 45%;
  flex-shrink: 0;
}

.factor-bar-wrap {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex: 1;
}

.factor-score {
  font-size: 0.7rem;
  font-weight: 600;
  font-family: monospace;
  width: 24px;
  text-align: right;
  flex-shrink: 0;
}

.penalty-row {
  margin-top: 0.6rem;
  display: flex;
  justify-content: flex-end;
}
</style>
