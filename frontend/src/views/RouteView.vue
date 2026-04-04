<template>
  <div class="app-content">
    <div class="page-header">
      <div class="page-title">Маршрут</div>
      <div class="page-subtitle">
        Алматы → Тараз · {{ posKm }} км · скорость {{ speed }} км/ч
      </div>
    </div>

    <div class="page-grid page-grid-2">

      <!-- Map placeholder (full width) -->
      <div class="card" style="grid-column: 1 / -1">
        <div class="card-title">Карта маршрута</div>
        <!-- TODO: Leaflet map — see _reference/cabin/RouteMapPanel.vue for SVG fallback
             Live position: store.data.position → { lat, lng, km_marker }
             API: GET /api/telemetry/latest for initial position -->
        <div class="chart-placeholder" style="height:300px">
          <span class="chart-placeholder-icon">🗺</span>
          <span>Интерактивная карта — реализовать с Leaflet</span>
          <span class="text-xs text-muted">
            Live: {{ store.data?.position?.lat?.toFixed(4) }}, {{ store.data?.position?.lng?.toFixed(4) }}
          </span>
        </div>
      </div>

      <!-- Station progress -->
      <div class="card">
        <div class="card-title">Станции маршрута</div>

        <!-- Route progress bar -->
        <div class="bar-track" style="height:6px; margin-bottom:0.75rem">
          <div class="bar-fill bar-fill--accent" :style="{ width: routeProgress + '%' }"></div>
        </div>

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
        <div class="flex flex-col gap-3">
          <div>
            <div class="label">Позиция</div>
            <div class="font-mono" style="font-size:1.4rem; font-weight:700; color:var(--accent)">
              {{ posKm }} км
            </div>
          </div>
          <div>
            <div class="label">Координаты</div>
            <div class="font-mono text-sm text-sub">
              {{ store.data?.position?.lat?.toFixed(5) ?? '–' }},
              {{ store.data?.position?.lng?.toFixed(5) ?? '–' }}
            </div>
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
import { ROUTE_WAYPOINTS, ROUTE_MAX_KM } from '@/constants/route.js';

const store  = useTelemetryStore();
const posKm  = computed(() => Math.round(store.data?.position?.km_marker ?? 0));
const speed  = computed(() => Math.round(store.data?.speed ?? 0));

const remainingKm   = computed(() => Math.max(0, ROUTE_MAX_KM - posKm.value));
const routeProgress = computed(() => Math.min(100, (posKm.value / ROUTE_MAX_KM) * 100));

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
