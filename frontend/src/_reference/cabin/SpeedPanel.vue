<template>
  <div class="card speed-panel" role="region" aria-label="Скорость локомотива">
    <div class="card-title">Скорость</div>

    <div class="speed-display">
      <!-- Large speed number -->
      <div class="speed-main">
        <span class="speed-value font-mono" :class="speedClass">{{ speedDisplay }}</span>
        <span class="speed-unit">км/ч</span>
      </div>

      <!-- Speed limit indicator -->
      <div class="speed-limit-row">
        <span class="limit-label">Лимит: <strong>120 км/ч</strong></span>
        <span v-if="overLimit" class="badge badge-critical">ПРЕВЫШЕНИЕ</span>
      </div>
    </div>

    <!-- Speedometer arc (SVG) -->
    <div class="speedo-wrap" aria-hidden="true">
      <svg viewBox="0 0 200 115" class="speedo-svg">
        <!-- Background arc 0–140 km/h span 200° -->
        <path d="M 14 108 A 90 90 0 0 1 186 108"
          fill="none" stroke="var(--color-border)" stroke-width="12" stroke-linecap="round" />
        <!-- Danger zone 120–140 -->
        <path d="M 14 108 A 90 90 0 0 1 186 108"
          fill="none" stroke="rgba(239,68,68,0.2)" stroke-width="12" stroke-linecap="round"
          :stroke-dasharray="dangerDash" />
        <!-- Speed fill -->
        <path d="M 14 108 A 90 90 0 0 1 186 108"
          fill="none" :stroke="speedFillColor" stroke-width="12" stroke-linecap="round"
          :stroke-dasharray="speedDash" class="speedo-arc" />
        <!-- Needle -->
        <line
          :x1="100" :y1="108"
          :x2="needleX" :y2="needleY"
          stroke="var(--color-text)" stroke-width="2.5" stroke-linecap="round"
          class="speedo-needle"
        />
        <circle cx="100" cy="108" r="5" fill="var(--color-text)" />
        <!-- Tick marks -->
        <g v-for="tick in ticks" :key="tick.v">
          <line
            :x1="tick.x1" :y1="tick.y1" :x2="tick.x2" :y2="tick.y2"
            stroke="var(--color-text-muted)" stroke-width="1.5"
          />
          <text :x="tick.tx" :y="tick.ty" text-anchor="middle"
            fill="var(--color-text-muted)" style="font-size:7px">{{ tick.v }}</text>
        </g>
      </svg>
    </div>

    <!-- Secondary metrics -->
    <div class="speed-meta">
      <div class="meta-item">
        <span class="meta-label">Текущий ПК</span>
        <span class="meta-value font-mono">{{ posKm }} км</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Направление</span>
        <span class="meta-value">→ Тараз</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store = useTelemetryStore();
const t = computed(() => store.current);

const speed     = computed(() => t.value?.speed ?? 0);
const overLimit = computed(() => speed.value > 120);

const speedDisplay = computed(() => Math.round(speed.value).toString().padStart(3, '\u2007'));
const speedClass   = computed(() => overLimit.value ? 'speed-over' : '');
const posKm        = computed(() => t.value?.position?.km ?? '–');

// Speedo arc: 0–140 km/h mapped to 0–π (180°), starts at left (200°)
const MAX_KM   = 140;
const ARC_FULL = Math.PI * 90; // semicircle circumference

const speedRatio    = computed(() => Math.min(speed.value / MAX_KM, 1));
const speedDash     = computed(() => {
  const filled = speedRatio.value * ARC_FULL;
  return `${filled} ${ARC_FULL}`;
});
const dangerDash    = computed(() => {
  const dangerStart = (120 / MAX_KM) * ARC_FULL;
  const dangerLen   = ARC_FULL - dangerStart;
  return `0 ${dangerStart} ${dangerLen} 0`;
});
const speedFillColor = computed(() =>
  speed.value > 120 ? 'var(--color-critical)'
  : speed.value > 100 ? 'var(--color-warning)'
  : 'var(--color-accent)'
);

// Needle angle: from 200° to 340° (left to right), 140° span = 140 km/h
function toNeedle(kmh) {
  const angleDeg = 200 + (kmh / MAX_KM) * 140;
  const rad = (angleDeg * Math.PI) / 180;
  const r   = 72;
  return {
    x: 100 + r * Math.cos(rad),
    y: 108 + r * Math.sin(rad),
  };
}
const needle  = computed(() => toNeedle(speed.value));
const needleX = computed(() => needle.value.x);
const needleY = computed(() => needle.value.y);

// Tick marks every 20 km/h
const ticks = [0, 20, 40, 60, 80, 100, 120, 140].map(v => {
  const angleDeg = 200 + (v / MAX_KM) * 140;
  const rad = (angleDeg * Math.PI) / 180;
  const r1 = 82, r2 = 90, rt = 97;
  return {
    v,
    x1: 100 + r1 * Math.cos(rad), y1: 108 + r1 * Math.sin(rad),
    x2: 100 + r2 * Math.cos(rad), y2: 108 + r2 * Math.sin(rad),
    tx: 100 + rt * Math.cos(rad), ty: 108 + rt * Math.sin(rad) + 1,
  };
});
</script>

<style scoped>
.speed-panel {}

.speed-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0.25rem 0;
}

.speed-main {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
}

.speed-value {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1;
  color: var(--color-text);
  transition: color 0.3s;
  letter-spacing: -0.02em;
}

.speed-value.speed-over { color: var(--color-critical); }
.speed-unit { font-size: 1rem; color: var(--color-text-muted); margin-bottom: 0.3rem; }

.speed-limit-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-text-sub);
  margin-top: 0.2rem;
}

.limit-label strong { color: var(--color-text); }

.speedo-wrap { display: flex; justify-content: center; }
.speedo-svg  { width: 100%; max-width: 220px; }

.speedo-arc    { transition: stroke-dasharray 0.3s ease, stroke 0.3s; }
.speedo-needle { transition: x2 0.3s ease, y2 0.3s ease; }

.speed-meta {
  display: flex;
  justify-content: space-around;
  margin-top: 0.5rem;
  border-top: 1px solid var(--color-border);
  padding-top: 0.6rem;
}

.meta-item { display: flex; flex-direction: column; align-items: center; gap: 0.15rem; }
.meta-label { font-size: 0.68rem; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.meta-value { font-size: 0.85rem; font-weight: 600; color: var(--color-text); }
</style>
