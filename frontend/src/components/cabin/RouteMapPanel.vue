<template>
  <div class="card">
    <div class="card-title">Маршрут</div>

    <!-- Route progress bar -->
    <div style="margin-bottom:0.5rem">
      <div class="bar-track" style="height:6px">
        <div class="bar-fill bar-fill--accent" :style="{ width: routeProgress + '%' }"></div>
      </div>
      <div class="flex justify-between text-xs text-muted" style="margin-top:0.2rem">
        <span>Алматы</span>
        <span class="font-mono">{{ posKm }} / {{ ROUTE_MAX_KM }} км</span>
        <span>Тараз</span>
      </div>
    </div>

    <!-- Station list -->
    <div class="station-list">
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
import { ROUTE_WAYPOINTS, ROUTE_MAX_KM } from '@/constants/route.js';

const store  = useTelemetryStore();
// Backend sends position.km_marker
const posKm  = computed(() => Math.round(store.data?.position?.km_marker ?? 0));

const routeProgress = computed(() =>
  Math.min(100, (posKm.value / ROUTE_MAX_KM) * 100)
);

const stations = computed(() =>
  ROUTE_WAYPOINTS.filter(w => w.name).map(w => ({
    ...w,
    passed:    w.km <= posKm.value,
    isCurrent: Math.abs(w.km - posKm.value) < 20,
  }))
);
</script>
