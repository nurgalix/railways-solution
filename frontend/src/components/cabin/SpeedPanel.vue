<template>
  <div class="card speed-card">
    <div class="card-title">
      Скорость
      <span v-if="overLimit" class="badge badge-crit" style="margin-left:auto">⚠ ПРЕВЫШЕНИЕ</span>
    </div>

    <div class="gauge-wrap">
      <svg viewBox="0 0 120 112" class="gauge-svg" aria-hidden="true">

        <!-- Zone tints (static, 270° arc, rotate(135,60,65)) -->
        <!-- green 0–100 = 168.3 of 235.62 -->
        <circle cx="60" cy="65" r="50" fill="none"
          stroke="#10b981" stroke-width="8" stroke-linecap="butt" opacity="0.18"
          stroke-dasharray="168.3 314.16"
          transform="rotate(135 60 65)"/>
        <!-- yellow 100–120: offset 168.3, length 33.62 -->
        <circle cx="60" cy="65" r="50" fill="none"
          stroke="#f59e0b" stroke-width="8" stroke-linecap="butt" opacity="0.18"
          stroke-dasharray="33.62 314.16"
          stroke-dashoffset="-168.3"
          transform="rotate(135 60 65)"/>
        <!-- red 120–140: offset 201.9, length 33.72 -->
        <circle cx="60" cy="65" r="50" fill="none"
          stroke="#ef4444" stroke-width="8" stroke-linecap="butt" opacity="0.18"
          stroke-dasharray="33.72 314.16"
          stroke-dashoffset="-201.9"
          transform="rotate(135 60 65)"/>

        <!-- Track (270° arc) -->
        <circle cx="60" cy="65" r="50" fill="none"
          stroke="var(--border)" stroke-width="10" stroke-linecap="round"
          stroke-dasharray="235.62 78.54"
          transform="rotate(135 60 65)"/>

        <!-- Fill arc — uses stroke-dasharray, smooth via CSS transition -->
        <circle cx="60" cy="65" r="50" fill="none"
          :stroke="speedColor"
          stroke-width="10" stroke-linecap="round"
          :stroke-dasharray="`${fillLen} 314.16`"
          transform="rotate(135 60 65)"
          class="gauge-fill"/>

        <!-- 120 km/h tick mark (position pre-computed) -->
        <line x1="99.7" y1="69.4" x2="111.6" y2="70.7"
          stroke="var(--crit)" stroke-width="2.5" stroke-linecap="round"/>

        <!-- Value -->
        <text x="60" y="63" text-anchor="middle"
          font-family="'JetBrains Mono',monospace"
          font-size="34" font-weight="800"
          :fill="speedColor">{{ Math.round(speed) }}</text>
        <text x="60" y="79" text-anchor="middle"
          font-size="11" fill="var(--text-muted)">км/ч</text>

        <!-- Axis labels -->
        <text x="14"  y="107" text-anchor="middle" font-size="9" fill="var(--text-muted)">0</text>
        <text x="61"  y="9"  text-anchor="middle" font-size="9" fill="var(--text-muted)">70</text>
        <text x="110" y="107" text-anchor="middle" font-size="9" fill="var(--text-muted)">140</text>
        <text x="114" y="68"  text-anchor="end"    font-size="8" fill="var(--crit)">120</text>
      </svg>
    </div>

    <div class="speed-meta">
      <div>
        <div class="label">Позиция</div>
        <div class="font-mono" style="font-weight:600">{{ posKm }} км</div>
      </div>
      <div>
        <div class="label">Лимит</div>
        <div style="font-weight:600; color:var(--crit)">120 км/ч</div>
      </div>
      <div>
        <div class="label">→ Тараз</div>
        <div class="text-xs text-muted">{{ remainKm }} км</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';
import { ROUTE_MAX_KM } from '@/constants/route.js';

const store     = useTelemetryStore();
const speed     = computed(() => store.data?.speed ?? 0);
const posKm     = computed(() => Math.round(store.data?.position?.km_marker ?? 0));
const overLimit = computed(() => speed.value > 120);

// Scale simulated 0-100km to real 0-350km for display
const remainKm = computed(() =>
  Math.round(ROUTE_MAX_KM - (posKm.value / 100) * ROUTE_MAX_KM)
);

const speedColor = computed(() =>
  speed.value > 120 ? 'var(--crit)'
  : speed.value > 100 ? 'var(--warn)'
  : 'var(--ok)'
);

// stroke-dasharray gauge: r=50, 270° arc = 235.62 of circumference 314.16
// transform="rotate(135, 60, 65)" starts arc at bottom-left (7:30)
const FULL_ARC = 235.619;
const fillLen = computed(() =>
  Math.max(0, Math.min(speed.value, 140) / 140 * FULL_ARC)
);
</script>

<style scoped>
.speed-card { display: flex; flex-direction: column; }

.gauge-wrap { display: flex; justify-content: center; }

.gauge-svg {
  width: 100%;
  max-width: 210px;
  height: auto;
  overflow: visible;
}

.gauge-fill {
  transition: stroke-dasharray 0.3s ease, stroke 0.3s ease;
}
</style>
