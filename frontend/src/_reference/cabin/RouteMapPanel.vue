<template>
  <div class="card route-panel" role="region" aria-label="Карта маршрута">
    <div class="card-title">Маршрут</div>

    <!-- SVG Route Map -->
    <div class="map-wrap">
      <svg ref="svgEl" viewBox="0 0 260 160" class="route-svg" aria-label="Схема маршрута Алматы–Тараз">
        <!-- Background -->
        <rect x="0" y="0" width="260" height="160" rx="8" fill="var(--color-bg-elevated)"/>

        <!-- Grid lines -->
        <g opacity="0.3">
          <line v-for="x in [65, 130, 195]" :key="'gx' + x" :x1="x" y1="0" :x2="x" y2="160"
            stroke="var(--color-border)" stroke-width="0.5" />
          <line v-for="y in [40, 80, 120]" :key="'gy' + y" x1="0" :y1="y" x2="260" :y2="y"
            stroke="var(--color-border)" stroke-width="0.5" />
        </g>

        <!-- Route track (thick rail) -->
        <polyline
          :points="trackPoints"
          fill="none"
          stroke="var(--color-border)"
          stroke-width="5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <!-- Traveled portion -->
        <polyline
          :points="traveledPoints"
          fill="none"
          stroke="var(--color-accent)"
          stroke-width="5"
          stroke-linecap="round"
          stroke-linejoin="round"
          opacity="0.85"
        />

        <!-- Station markers -->
        <g v-for="s in stations" :key="s.name">
          <circle :cx="s.x" :cy="s.y" r="5"
            fill="var(--color-surface)" :stroke="s.passed ? 'var(--color-accent)' : 'var(--color-border)'"
            stroke-width="2" />
          <text :x="s.x" :y="s.y - 9" text-anchor="middle"
            fill="var(--color-text-sub)" style="font-size:7px;font-weight:600">{{ s.name }}</text>
          <text :x="s.x" :y="s.y + 18" text-anchor="middle"
            fill="var(--color-text-muted)" style="font-size:6px">{{ s.km }} км</text>
        </g>

        <!-- Train position marker -->
        <g :transform="`translate(${trainX}, ${trainY})`" class="train-marker">
          <circle r="8" fill="var(--color-accent)" opacity="0.25" class="train-pulse" />
          <circle r="5" fill="var(--color-accent)" />
          <text y="4" text-anchor="middle" fill="#fff" style="font-size:6px;font-weight:700">🚂</text>
        </g>

        <!-- Speed overlay -->
        <rect x="2" y="2" width="68" height="22" rx="4" fill="var(--color-surface)" opacity="0.9" />
        <text x="7" y="10" fill="var(--color-text-muted)" style="font-size:6px">СКОРОСТЬ</text>
        <text x="7" y="20" :fill="speedColor" style="font-size:10px;font-weight:700;font-family:monospace">
          {{ speed }} км/ч
        </text>

        <!-- Position overlay -->
        <rect x="190" y="2" width="68" height="22" rx="4" fill="var(--color-surface)" opacity="0.9" />
        <text x="195" y="10" fill="var(--color-text-muted)" style="font-size:6px">ПОЗИЦИЯ</text>
        <text x="195" y="20" fill="var(--color-text-sub)" style="font-size:10px;font-weight:700;font-family:monospace">
          {{ posKm }} км
        </text>
      </svg>
    </div>

    <!-- Station list -->
    <div class="station-list">
      <div v-for="s in stations" :key="s.name + '_list'" class="station-row" :class="{ passed: s.passed, current: s.isCurrent }">
        <span class="station-dot" :class="{ passed: s.passed }"></span>
        <span class="station-name">{{ s.name }}</span>
        <span class="station-km">{{ s.km }} км</span>
        <span v-if="s.isCurrent" class="here-badge">здесь</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';
import { ROUTE_WAYPOINTS } from '@/services/mockTelemetry.js';

const store = useTelemetryStore();
const t = computed(() => store.current);
const speed  = computed(() => Math.round(t.value?.speed ?? 0));
const posKm  = computed(() => t.value?.position?.km ?? 0);

const speedColor = computed(() =>
  speed.value > 120 ? 'var(--color-critical)'
  : speed.value > 100 ? 'var(--color-warning)'
  : 'var(--color-normal)'
);

// Map waypoints to SVG coordinates
// Lat range: ~43.23 → ~42.18 (top to bottom slightly)
// Lng range: ~76.89 → ~73.60 (left to right)
const MAP_W = 260, MAP_H = 160;
const LAT_MAX = 43.30, LAT_MIN = 42.10;
const LNG_MIN = 73.40, LNG_MAX = 77.10;
const PAD_X = 18, PAD_Y = 25;

function toSvg(lat, lng) {
  const x = PAD_X + ((lng - LNG_MIN) / (LNG_MAX - LNG_MIN)) * (MAP_W - PAD_X * 2);
  const y = PAD_Y + ((LAT_MAX - lat) / (LAT_MAX - LAT_MIN)) * (MAP_H - PAD_Y * 2);
  return { x: Math.round(x * 10) / 10, y: Math.round(y * 10) / 10 };
}

const svgPoints = ROUTE_WAYPOINTS.map(w => toSvg(w.lat, w.lng));

const trackPoints = computed(() =>
  svgPoints.map(p => `${p.x},${p.y}`).join(' ')
);

// Current position in SVG coords
const trainPos = computed(() => {
  const pos = t.value?.position;
  if (!pos) return svgPoints[0];
  return toSvg(pos.lat, pos.lng);
});
const trainX = computed(() => trainPos.value.x);
const trainY = computed(() => trainPos.value.y);

// Traveled portion: all points before current + current pos
const traveledPoints = computed(() => {
  const km = posKm.value;
  const pts = [];
  for (let i = 0; i < ROUTE_WAYPOINTS.length; i++) {
    if (ROUTE_WAYPOINTS[i].km <= km) {
      pts.push(svgPoints[i]);
    } else {
      break;
    }
  }
  pts.push(trainPos.value);
  return pts.map(p => `${p.x},${p.y}`).join(' ');
});

// Named stations only
const stations = computed(() => {
  const km = posKm.value;
  return ROUTE_WAYPOINTS.filter(w => w.name).map(w => {
    const sv = toSvg(w.lat, w.lng);
    return {
      ...w,
      x: sv.x,
      y: sv.y,
      passed:    w.km <= km,
      isCurrent: Math.abs(w.km - km) < 15,
    };
  });
});
</script>

<style scoped>
.route-panel {}

.map-wrap {
  margin: 0.25rem 0;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.route-svg { width: 100%; display: block; }

@keyframes train-pulse {
  0%, 100% { r: 8; opacity: 0.25; }
  50%       { r: 12; opacity: 0.1; }
}
.train-pulse { animation: train-pulse 1.5s ease-in-out infinite; }

.station-list {
  margin-top: 0.6rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.station-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.72rem;
  color: var(--color-text-muted);
  padding: 0.15rem 0;
}

.station-row.passed { color: var(--color-text-sub); }
.station-row.current { color: var(--color-text); font-weight: 600; }

.station-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  border: 1.5px solid var(--color-border);
  flex-shrink: 0;
}
.station-dot.passed { background: var(--color-accent); border-color: var(--color-accent); }

.station-name { flex: 1; }
.station-km   { font-family: monospace; font-size: 0.65rem; }

.here-badge {
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0.1rem 0.35rem;
  background: var(--color-accent-glow);
  color: var(--color-accent);
  border-radius: 4px;
}
</style>
