<template>
  <div class="app-content">
    <div class="page-header">
      <div class="page-title">Сообщения и диагностика</div>
      <div class="page-subtitle">
        Активные предупреждения · удерживаются {{ STICKY_SEC }} с после исчезновения
      </div>
    </div>

    <div class="page-grid page-grid-2">

      <!-- Active (sticky live) -->
      <div class="card">
        <div class="card-title">
          Активные сообщения (live)
          <span v-if="stickyList.length" class="badge badge-crit">{{ stickyList.length }}</span>
        </div>

        <div v-if="!stickyList.length" class="alerts-empty">
          <span>✓</span> Нарушений не обнаружено
        </div>

        <transition-group name="alert-anim" tag="div" class="alert-list">
          <div
            v-for="a in stickyList"
            :key="a._key"
            class="alert-item"
            :class="[`alert-item--${a.severity}`, a._stale ? 'alert-item--stale' : '']"
          >
            <span class="alert-icon" :class="`alert-icon--${a.severity}`">
              {{ a.severity === 'critical' ? '⚠' : 'ℹ' }}
            </span>
            <div class="alert-body">
              <div class="alert-title">{{ a.code }}</div>
              <div class="alert-message">{{ a.message }}</div>
              <div v-if="a.recommendation" class="alert-rec">
                <span class="alert-rec-arrow">→</span> {{ a.recommendation }}
              </div>
              <div v-if="a.parameter" class="alert-time">
                {{ a.parameter }}: {{ a.value?.toFixed(2) }} / порог {{ a.threshold }}
              </div>
              <div class="alert-time">
                <span v-if="a._stale" style="color:var(--text-muted)">исчез · </span>
                {{ fmt(a.timestamp) }}
              </div>
            </div>
            <span class="badge" :class="severityBadge(a.severity)">
              {{ severityLabel(a.severity) }}
            </span>
          </div>
        </transition-group>
      </div>

      <!-- History from REST API -->
      <div class="card">
        <div class="card-title">
          История событий
          <span v-if="historyAlerts.length" class="badge badge-warn">{{ historyAlerts.length }}</span>
        </div>

        <div class="flex gap-2" style="margin-bottom:0.6rem; flex-wrap:wrap">
          <button
            v-for="m in [15, 30, 60, 120]" :key="m"
            class="pill-btn" :class="{ 'is-active': historyMinutes === m }"
            @click="loadHistory(m)"
          >{{ m }}м</button>
          <button class="pill-btn" :class="{ 'is-active': historySeverity === 'critical' }" @click="toggleSeverity('critical')">⚠ Критично</button>
          <button class="pill-btn" :class="{ 'is-active': historySeverity === 'warning' }"  @click="toggleSeverity('warning')">Внимание</button>
        </div>

        <div v-if="loading"  class="text-sm text-muted" style="padding:0.5rem 0">Загрузка…</div>
        <div v-else-if="error"   class="text-sm" style="color:var(--crit)">{{ error }}</div>
        <div v-else-if="!historyAlerts.length" class="text-sm text-muted" style="padding:0.5rem 0">Событий не найдено</div>

        <div v-else class="alert-list">
          <div
            v-for="a in historyAlerts"
            :key="(a.id ?? a.code) + a.timestamp"
            class="alert-item"
            :class="`alert-item--${a.severity}`"
          >
            <span class="alert-icon" :class="`alert-icon--${a.severity}`">
              {{ a.severity === 'critical' ? '⚠' : 'ℹ' }}
            </span>
            <div class="alert-body">
              <div class="alert-title">{{ a.code }}</div>
              <div class="alert-message">{{ a.message }}</div>
              <div class="alert-time">{{ fmt(a.timestamp) }}</div>
            </div>
            <span class="badge" :class="severityBadge(a.severity)">{{ severityLabel(a.severity) }}</span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';
import { translateAlerts } from '@/utils/alertTranslations.js';

const store = useTelemetryStore();
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// ─── Sticky live alerts ───────────────────────────────────────────────────────
// Alerts are kept for STICKY_SEC seconds after they last appear in the WS frame,
// so brief/intermittent alerts don't flash and disappear.
const STICKY_SEC = 120;
const STICKY_MS  = STICKY_SEC * 1000;

// Map<key, { alert, lastSeen: ms, firstSeen: ms }>
const stickyMap = ref(new Map());

watch(() => store.alerts, (newAlerts) => {
  const now = Date.now();
  const currentKeys = new Set();

  for (const a of newAlerts) {
    const key = a.code ?? String(a.id);
    currentKeys.add(key);
    const existing = stickyMap.value.get(key);
    stickyMap.value.set(key, {
      alert:     a,
      lastSeen:  now,
      firstSeen: existing?.firstSeen ?? now,
    });
  }
// Live alerts from WS (translated)
const liveAlerts = computed(() => translateAlerts(store.alerts));

  // Mark stale but don't delete yet — cleanup timer handles removal
  // (forces re-render so _stale flag updates)
  // Force reactivity: reassign
  stickyMap.value = new Map(stickyMap.value);
}, { deep: true });

// Cleanup stale entries every 10 s
let cleanupTimer;
onMounted(() => {
  cleanupTimer = setInterval(() => {
    const now = Date.now();
    let changed = false;
    for (const [key, entry] of stickyMap.value) {
      if (now - entry.lastSeen > STICKY_MS) {
        stickyMap.value.delete(key);
        changed = true;
      }
    }
    if (changed) stickyMap.value = new Map(stickyMap.value);
  }, 10_000);
  loadHistory();
});
onUnmounted(() => clearInterval(cleanupTimer));

const stickyList = computed(() => {
  const now = Date.now();
  return [...stickyMap.value.entries()]
    .map(([key, e]) => ({ ...e.alert, _key: key, _stale: now - e.lastSeen > 5_000 }))
    .sort((a, b) => {
      const o = { critical: 0, warning: 1, info: 2 };
      return (o[a.severity] ?? 9) - (o[b.severity] ?? 9);
    });
});

// ─── History from REST API ────────────────────────────────────────────────────
const historyAlerts   = ref([]);
const historyMinutes  = ref(30);
const historySeverity = ref(null);
const loading = ref(false);
const error   = ref(null);

async function loadHistory(minutes = historyMinutes.value) {
  historyMinutes.value = minutes;
  loading.value = true;
  error.value   = null;
  try {
    let url = `${API_BASE}/alerts?minutes=${minutes}&limit=200`;
    if (historySeverity.value) url += `&severity=${historySeverity.value}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    historyAlerts.value = translateAlerts(data); // Translate history alerts
  } catch (e) {
    error.value = `Ошибка загрузки: ${e.message}`;
  } finally {
    loading.value = false;
  }
}

function toggleSeverity(s) {
  historySeverity.value = historySeverity.value === s ? null : s;
  loadHistory();
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
const severityBadge = s => ({ critical: 'badge-crit', warning: 'badge-warn', info: 'badge-ok' }[s] ?? 'badge-ok');
const severityLabel = s => ({ critical: 'КРИТИЧНО', warning: 'ВНИМАНИЕ', info: 'ИНФО' }[s] ?? s.toUpperCase());
const fmt = ts => ts ? new Date(ts).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '';
</script>

<style scoped>
.alert-item--stale {
  opacity: 0.55;
  transition: opacity 1s ease;
}
</style>
