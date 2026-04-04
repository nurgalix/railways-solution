<template>
  <div class="app-content">
    <div class="page-header">
      <div class="page-title">Алерты и диагностика</div>
      <div class="page-subtitle">Активные предупреждения · история за {{ historyMinutes }} мин</div>
    </div>

    <div class="page-grid page-grid-2">

      <!-- Active (live from WS) -->
      <div class="card">
        <div class="card-title">
          Активные алерты (live)
          <span v-if="liveAlerts.length" class="badge badge-crit">{{ liveAlerts.length }}</span>
        </div>

        <div v-if="!liveAlerts.length" class="alerts-empty">
          <span>✓</span> Нарушений не обнаружено
        </div>

        <transition-group name="alert-anim" tag="div" class="alert-list">
          <div
            v-for="a in liveAlerts"
            :key="a.id ?? a.code"
            class="alert-item anim-fade-in"
            :class="`alert-item--${a.severity}`"
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
              <div v-if="a.parameter" class="text-xs text-muted" style="margin-top:0.2rem">
                {{ a.parameter }}: {{ a.value?.toFixed(2) }} / порог {{ a.threshold }}
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
          <button class="pill-btn" :class="{ 'is-active': historySeverity === 'warning'  }" @click="toggleSeverity('warning')">Внимание</button>
        </div>

        <div v-if="loading" class="text-sm text-muted" style="padding:0.5rem 0">Загрузка…</div>
        <div v-else-if="error"  class="text-sm" style="color:var(--crit)">{{ error }}</div>
        <div v-else-if="!historyAlerts.length" class="text-sm text-muted" style="padding:0.5rem 0">Событий не найдено</div>

        <div v-else class="alert-list">
          <div
            v-for="a in historyAlerts"
            :key="a.id ?? a.code + a.timestamp"
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
import { ref, computed, onMounted } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';
import { translateAlerts } from '@/utils/alertTranslations.js';

const store = useTelemetryStore();

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Live alerts from WS (translated)
const liveAlerts = computed(() => translateAlerts(store.alerts));

// History from REST
const historyAlerts  = ref([]);
const historyMinutes = ref(30);
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
    const res  = await fetch(url);
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

onMounted(() => loadHistory());

const severityBadge = s => ({ critical: 'badge-crit', warning: 'badge-warn', info: 'badge-ok' }[s] ?? 'badge-ok');
const severityLabel = s => ({ critical: 'КРИТИЧНО', warning: 'ВНИМАНИЕ', info: 'ИНФО' }[s] ?? s.toUpperCase());
const fmt = ts => ts ? new Date(ts).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '';
</script>
