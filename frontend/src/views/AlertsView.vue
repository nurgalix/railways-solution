<template>
  <div class="app-content">
    <div class="page-header">
      <div class="page-title">Алерты и диагностика</div>
      <div class="page-subtitle">Активные предупреждения и история событий</div>
    </div>

    <div class="page-grid page-grid-2">

      <!-- Active alerts -->
      <div class="card">
        <div class="card-title">
          Активные алерты
          <span v-if="activeAlerts.length" class="badge badge-crit">{{ activeAlerts.length }}</span>
        </div>
        <!-- TODO: replace with full AlertsPanel or dedicated AlertsFeed component -->
        <div v-if="!activeAlerts.length" class="alerts-empty">
          <span>✓</span> Нарушений не обнаружено
        </div>
        <transition-group name="alert-anim" tag="div" class="alert-list">
          <div
            v-for="a in activeAlerts"
            :key="a.id"
            class="alert-item anim-fade-in"
            :class="`alert-item--${a.severity}`"
          >
            <span class="alert-icon" :class="`alert-icon--${a.severity}`">
              {{ a.severity === 'critical' ? '⚠' : 'ℹ' }}
            </span>
            <div class="alert-body">
              <div class="alert-title">{{ a.title }}</div>
              <div class="alert-message">{{ a.message }}</div>
              <div v-if="a.recommendation" class="alert-rec">
                <span class="alert-rec-arrow">→</span> {{ a.recommendation }}
              </div>
              <div class="alert-time">{{ formatTime(a.timestamp) }}</div>
            </div>
            <span class="badge" :class="a.severity === 'critical' ? 'badge-crit' : 'badge-warn'">
              {{ a.severity === 'critical' ? 'КРИТИЧНО' : 'ВНИМАНИЕ' }}
            </span>
          </div>
        </transition-group>
      </div>

      <!-- Alert history log -->
      <div class="card">
        <div class="card-title">История событий</div>
        <!-- TODO: implement event log with timestamps from backend history API -->
        <div class="chart-placeholder">
          <span class="chart-placeholder-icon">📋</span>
          <span>История событий — будет реализована</span>
          <span class="text-xs text-muted">GET /api/alerts/history</span>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store = useTelemetryStore();
const activeAlerts = computed(() => store.current?.alerts ?? []);

function formatTime(ts) {
  if (!ts) return '';
  return new Date(ts).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
</script>
