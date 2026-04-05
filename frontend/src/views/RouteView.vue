<template>
  <div class="app-content app-content--map route-page">

    <!-- Map fills the page -->
    <div ref="mapEl" class="route-leaflet-map"></div>

    <!-- Overlay info bar -->
    <div class="route-info-bar">

      <div class="route-info-card">
        <div class="label">Позиция</div>
        <div class="font-mono route-info-val" style="color:var(--accent)">{{ displayKm }} км</div>
      </div>

      <div class="route-info-card">
        <div class="label">Скорость</div>
        <div class="font-mono route-info-val" :style="{ color: speedColor }">{{ speed }} км/ч</div>
      </div>

      <div class="route-info-card">
        <div class="label">Осталось</div>
        <div class="font-mono route-info-val">{{ remainKm }} км</div>
      </div>

      <div class="route-info-card">
        <div class="label">Прибытие</div>
        <div class="font-mono route-info-val">{{ eta }}</div>
      </div>

      <div class="route-info-card">
        <div class="label">Прогресс</div>
        <div style="width:120px; margin-top:0.2rem">
          <div class="bar-track" style="height:5px">
            <div class="bar-fill bar-fill--accent" :style="{ width: routePct + '%' }"></div>
          </div>
          <div class="flex justify-between text-xs text-muted" style="margin-top:0.1rem">
            <span>Алматы</span><span>Тараз</span>
          </div>
        </div>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useTelemetryStore } from '@/stores/telemetry.js';
import { useUiStore }        from '@/stores/ui.js';
import { ROUTE_WAYPOINTS, ROUTE_MAX_KM } from '@/constants/route.js';

// Fix Leaflet bundler icon path issue
import iconUrl       from 'leaflet/dist/images/marker-icon.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import shadowUrl     from 'leaflet/dist/images/marker-shadow.png';
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({ iconUrl, iconRetinaUrl, shadowUrl });

const store   = useTelemetryStore();
const uiStore = useUiStore();

// ── Computed telemetry values ────────────────────────────────────────
const rawKm     = computed(() => store.data?.position?.km_marker ?? 0);
const displayKm = computed(() => Math.round((rawKm.value / 100) * ROUTE_MAX_KM));
const routePct  = computed(() => rawKm.value);                          // 0–100
const speed     = computed(() => Math.round(store.data?.speed ?? 0));
const remainKm  = computed(() => Math.max(0, ROUTE_MAX_KM - displayKm.value));

const speedColor = computed(() =>
  speed.value > 120 ? 'var(--crit)' : speed.value > 100 ? 'var(--warn)' : 'var(--ok)'
);

const eta = computed(() => {
  if (speed.value < 1) return '–';
  const h = Math.floor(remainKm.value / speed.value);
  const m = Math.round(((remainKm.value / speed.value) - h) * 60);
  return `~${h}ч ${m}м`;
});

// ── Interpolate lat/lng from displayKm along ROUTE_WAYPOINTS ────────
function kmToLatLng(km) {
  const pts = ROUTE_WAYPOINTS;
  if (km <= pts[0].km)                      return [pts[0].lat, pts[0].lng];
  if (km >= pts[pts.length - 1].km)         return [pts[pts.length - 1].lat, pts[pts.length - 1].lng];
  for (let i = 0; i < pts.length - 1; i++) {
    if (km >= pts[i].km && km <= pts[i + 1].km) {
      const t = (km - pts[i].km) / (pts[i + 1].km - pts[i].km);
      return [
        pts[i].lat + t * (pts[i + 1].lat - pts[i].lat),
        pts[i].lng + t * (pts[i + 1].lng - pts[i].lng),
      ];
    }
  }
  return [pts[0].lat, pts[0].lng];
}

// ── Leaflet ──────────────────────────────────────────────────────────
const mapEl       = ref(null);
let   mapInst     = null;
let   trainMarker = null;
let   tileLayer   = null;
let   routeLine   = null;

const TILES = {
  dark:  'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
  light: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
};

const trainIcon = L.divIcon({
  className: '',
  html: `<div style="
    width:28px; height:28px;
    background:#3b82f6; border:3px solid #fff;
    border-radius:50%;
    box-shadow:0 0 0 2px #3b82f6, 0 3px 12px rgba(0,0,0,0.5);
    display:flex; align-items:center; justify-content:center;
    font-size:14px; line-height:1;
  ">🚂</div>`,
  iconSize:   [28, 28],
  iconAnchor: [14, 14],
  popupAnchor:[0, -14],
});

function buildStationIcon(passed) {
  return L.divIcon({
    className: '',
    html: `<div style="
      width:12px; height:12px;
      background:${passed ? '#3b82f6' : '#fff'};
      border:2.5px solid #3b82f6;
      border-radius:50%;
    "></div>`,
    iconSize:   [12, 12],
    iconAnchor: [6, 6],
  });
}

let stationMarkers = [];

function initMap() {
  if (!mapEl.value || mapInst) return;

  const bounds = L.latLngBounds(ROUTE_WAYPOINTS.map(w => [w.lat, w.lng]));

  mapInst = L.map(mapEl.value, {
    zoomControl: true,
    attributionControl: true,
    scrollWheelZoom: true,
    doubleClickZoom: true,
  });

  mapInst.fitBounds(bounds, { padding: [30, 30] });

  tileLayer = L.tileLayer(TILES[uiStore.theme] ?? TILES.dark, {
    attribution: '&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://openstreetmap.org">OSM</a>',
    maxZoom: 18,
  }).addTo(mapInst);

  // Route line
  routeLine = L.polyline(
    ROUTE_WAYPOINTS.map(w => [w.lat, w.lng]),
    { color: '#3b82f6', weight: 4, opacity: 0.9 }
  ).addTo(mapInst);

  // Passed route line (accent coloring, updated live)
  // Station markers
  ROUTE_WAYPOINTS.filter(w => w.name).forEach(w => {
    const passed = w.km < displayKm.value;
    const m = L.marker([w.lat, w.lng], { icon: buildStationIcon(passed) })
      .bindPopup(`<b>${w.name}</b><br/>${w.km} км`, { className: 'map-popup' })
      .addTo(mapInst);
    stationMarkers.push({ marker: m, km: w.km, name: w.name });
  });

  // Train marker
  const pos = kmToLatLng(displayKm.value);
  trainMarker = L.marker(pos, { icon: trainIcon, zIndexOffset: 1000 })
    .bindPopup(`<b>ВЛ80</b><br/>${displayKm.value} км · ${speed.value} км/ч`, { className: 'map-popup' })
    .addTo(mapInst);
}

// Update train + station marker states on new telemetry
watch(displayKm, (km) => {
  if (!trainMarker) return;
  trainMarker.setLatLng(kmToLatLng(km));
  trainMarker.setPopupContent(`<b>ВЛ80</b><br/>${km} км · ${speed.value} км/ч`);

  // Update station icons passed/unpassed
  stationMarkers.forEach(({ marker, km: skm }) => {
    marker.setIcon(buildStationIcon(skm < km));
  });
});

watch(() => uiStore.theme, (theme) => {
  tileLayer?.setUrl(TILES[theme] ?? TILES.dark);
});

onMounted(() => requestAnimationFrame(initMap));
onUnmounted(() => { mapInst?.remove(); mapInst = null; });
</script>

<style scoped>
.route-page {
  position: relative;
}

.route-leaflet-map {
  flex: 1;
  min-height: 0;
  z-index: 0;
}

.route-info-bar {
  display: flex;
  align-items: center;
  gap: 0;
  background: var(--topbar-bg);
  border-top: 1px solid var(--border);
  backdrop-filter: blur(12px);
  padding: 0.5rem 1rem;
  flex-wrap: wrap;
  gap: 0.75rem;
  flex-shrink: 0;
  z-index: 1;
}

.route-info-card {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  padding-right: 0.75rem;
  border-right: 1px solid var(--border);
}
.route-info-card:last-child { border-right: none; }

.route-info-val {
  font-size: 1.1rem;
  font-weight: 700;
  transition: color 0.3s;
}
</style>

<style>
.map-popup .leaflet-popup-content-wrapper {
  background: var(--surface, #111827) !important;
  border: 1px solid var(--border, #1e2d45) !important;
  color: var(--text, #e2e8f0) !important;
  font-family: inherit !important;
  font-size: 0.8rem !important;
  border-radius: 6px !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.5) !important;
}
.map-popup .leaflet-popup-tip {
  background: var(--surface, #111827) !important;
}
.map-popup .leaflet-popup-close-button {
  color: var(--text-muted, #64748b) !important;
}
</style>
