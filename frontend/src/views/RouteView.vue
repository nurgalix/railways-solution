<template>
  <div class="app-content">
    <div class="page-header">
      <div class="page-title">Маршрут</div>
      <div class="page-subtitle">
        Алматы → Тараз · {{ posKm }} км · скорость {{ speed }} км/ч
      </div>
    </div>

    <div class="page-grid page-grid-2">

      <!-- Map placeholder -->
      <div class="card" style="grid-column: 1 / -1">
        <div class="card-title">Карта маршрута</div>
        <!-- TODO: Leaflet map with real coordinates from backend
             See _reference/cabin/RouteMapPanel.vue for SVG fallback
             API: GET /api/route/current-position
             WS:  listen to store.current.position for live updates -->
        <div class="chart-placeholder" style="height:320px">
          <span class="chart-placeholder-icon">🗺</span>
          <span>Интерактивная карта — будет реализована</span>
          <span class="text-xs text-muted">Leaflet / MapLibre с тайлами OpenStreetMap</span>
        </div>
      </div>

      <!-- Station progress -->
      <div class="card">
        <div class="card-title">Станции маршрута</div>
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

      <!-- Segment info -->
      <div class="card">
        <div class="card-title">Текущий участок</div>
        <!-- TODO: fetch segment limits and restrictions from backend
             API: GET /api/route/segment?km=:km -->
        <div class="flex flex-col gap-3">
          <div>
            <div class="label">Позиция</div>
            <div class="font-mono" style="font-size:1.4rem; font-weight:700; color:var(--accent)">{{ posKm }} км</div>
          </div>
          <div>
            <div class="label">Ограничение скорости</div>
            <div style="font-size:1.1rem; font-weight:700">120 км/ч</div>
          </div>
          <div>
            <div class="label">Оставшееся расстояние</div>
            <div style="font-size:1.1rem; font-weight:700">{{ remainingKm }} км</div>
          </div>
          <div>
            <div class="label">Расчётное время прибытия</div>
            <div style="font-size:1.1rem; font-weight:700; color:var(--text-sub)">{{ eta }}</div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';
import { ROUTE_WAYPOINTS, ROUTE_MAX_KM } from '@/services/mockTelemetry.js';

const store  = useTelemetryStore();
const t      = computed(() => store.current);
const posKm  = computed(() => t.value?.position?.km ?? 0);
const speed  = computed(() => Math.round(t.value?.speed ?? 0));

const remainingKm = computed(() => Math.max(0, ROUTE_MAX_KM - posKm.value));

const eta = computed(() => {
  const s = speed.value;
  if (!s) return '–';
  const hours = remainingKm.value / s;
  const h = Math.floor(hours);
  const m = Math.round((hours - h) * 60);
  return `~${h}ч ${m}м`;
});

const stations = computed(() =>
  ROUTE_WAYPOINTS.filter(w => w.name).map(w => ({
    ...w,
    passed:    w.km <= posKm.value,
    isCurrent: Math.abs(w.km - posKm.value) < 20,
  }))
);
</script>
