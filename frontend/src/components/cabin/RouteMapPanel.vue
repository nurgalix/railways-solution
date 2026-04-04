<template>
  <div class="card">
    <div class="card-title">Маршрут</div>

    <!-- Map placeholder — implement with Leaflet or SVG from _reference -->
    <div class="route-map-wrap" style="height:120px; display:flex; align-items:center; justify-content:center">
      <span style="font-size:0.72rem; color:var(--text-muted)">
        Карта — см. _reference/cabin/RouteMapPanel.vue
      </span>
    </div>

    <!-- Progress bar along route -->
    <div style="margin:0.5rem 0 0.25rem">
      <div class="bar-track" style="height:6px">
        <div class="bar-fill bar-fill--accent" :style="{ width: routeProgress + '%' }"></div>
      </div>
      <div class="flex justify-between text-xs text-muted" style="margin-top:0.2rem">
        <span>Алматы</span>
        <span class="font-mono">{{ posKm }} / {{ routeMaxKm }} км</span>
        <span>Тараз</span>
      </div>
    </div>

    <!-- Station list -->
    <div class="station-list" style="margin-top:0.5rem">
      <div
        v-for="s in stations" :key="s.name"
        class="station-row"
        :class="{ 'is-passed': s.passed, 'is-current': s.isCurrent }"
      >
        <span class="station-dot" :class="{ 'is-passed': s.passed }"></span>
        <span>{{ s.name }}</span>
        <span class="station-km">{{ s.km }} км</span>
        <span v-if="s.isCurrent" class="here-label">здесь</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';
import { ROUTE_WAYPOINTS, ROUTE_MAX_KM } from '@/services/mockTelemetry.js';

const store      = useTelemetryStore();
const posKm      = computed(() => store.current?.position?.km ?? 0);
const routeMaxKm = ROUTE_MAX_KM;

const routeProgress = computed(() =>
  Math.min(100, (posKm.value / routeMaxKm) * 100)
);

const stations = computed(() =>
  ROUTE_WAYPOINTS.filter(w => w.name).map(w => ({
    ...w,
    passed:    w.km <= posKm.value,
    isCurrent: Math.abs(w.km - posKm.value) < 20,
  }))
);
</script>
