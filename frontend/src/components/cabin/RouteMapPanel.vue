<template>
  <div class="card">
    <div class="card-title">
      Маршрут
      <span class="font-mono" style="margin-left:auto; color:var(--accent); font-weight:700; text-transform:none; letter-spacing:0">
        {{ displayKm }} км
      </span>
    </div>

    <!-- Progress bar -->
    <div class="bar-track" style="height:6px; margin-bottom:0.25rem; position:relative">
      <!-- Train position marker -->
      <div class="route-train-dot" :style="{ left: routePct + '%' }"></div>
      <div class="bar-fill bar-fill--accent" :style="{ width: routePct + '%' }"></div>
    </div>
    <div class="flex justify-between text-xs text-muted" style="margin-bottom:0.6rem">
      <span>Алматы</span>
      <span>{{ ROUTE_MAX_KM }} км</span>
      <span>Тараз</span>
    </div>

    <!-- Station list -->
    <div class="station-list">
      <div v-for="s in namedStations" :key="s.name"
        class="station-row"
        :class="{ 'is-passed': s.passed, 'is-current': s.isCurrent }">
        <span class="station-dot" :class="{ 'is-passed': s.passed }"></span>
        <span>{{ s.name }}</span>
        <span class="station-km font-mono">{{ s.km }} км</span>
        <span v-if="s.isCurrent" class="here-label">◀ здесь</span>
      </div>
    </div>

    <!-- ETA row -->
    <div v-if="eta" class="card-divider" style="margin:0.5rem 0"></div>
    <div v-if="eta" class="flex justify-between text-xs">
      <span class="text-muted">Оставшееся</span>
      <span class="font-mono" style="font-weight:600">{{ remainKm }} км · ~{{ eta }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';
import { ROUTE_WAYPOINTS, ROUTE_MAX_KM } from '@/constants/route.js';

const store = useTelemetryStore();

// Backend km_marker is 0–100 (simulated). Scale to real 350 km.
const rawKm     = computed(() => store.data?.position?.km_marker ?? 0);
const displayKm = computed(() => Math.round((rawKm.value / 100) * ROUTE_MAX_KM));
const routePct  = computed(() => (rawKm.value / 100) * 100);
const remainKm  = computed(() => Math.max(0, ROUTE_MAX_KM - displayKm.value));

const namedStations = computed(() =>
  ROUTE_WAYPOINTS.filter(w => w.name).map(w => ({
    ...w,
    passed:    w.km < displayKm.value,
    isCurrent: Math.abs(w.km - displayKm.value) < 25,
  }))
);

const eta = computed(() => {
  const s = store.data?.speed ?? 0;
  if (s < 1) return null;
  const h = Math.floor(remainKm.value / s);
  const m = Math.round(((remainKm.value / s) - h) * 60);
  return `${h}ч ${m}м`;
});
</script>

<style scoped>
.route-train-dot {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--accent);
  border: 2px solid var(--surface);
  box-shadow: 0 0 0 2px var(--accent);
  z-index: 1;
  transition: left 0.5s ease;
}
</style>
