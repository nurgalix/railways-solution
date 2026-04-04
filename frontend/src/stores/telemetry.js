/**
 * Telemetry store — holds live and historical frames from the backend.
 *
 * Backend WS frame shape (TelemetryFrame):
 * {
 *   type:           "telemetry",
 *   timestamp:      "2024-01-01T12:00:00Z",
 *   locomotive_id:  "LOC-001",
 *   data: {
 *     speed:       87.5,          // km/h
 *     fuel_level:  68.2,          // %
 *     pressure:    5.01,          // bar (combined)
 *     temperature: 81.3,          // °C (combined)
 *     position:    { lat, lng, km_marker }
 *   },
 *   health: {
 *     index:       82.5,          // 0–100
 *     category:    "B",           // A–E
 *     label:       "Attention",
 *     top_factors: [ { parameter, score, weight, impact, status } ]
 *   },
 *   alerts: [ { id, severity, code, message, parameter, value, threshold, recommendation, acknowledged, timestamp } ]
 * }
 *
 * Health, alerts and the index are all computed by the backend.
 * The store does NOT re-calculate them — just stores and exposes.
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

const HISTORY_MAX = 900; // 15 min at 1 Hz

// Alert TTL (time-to-live) in milliseconds - critical alerts last longer
const ALERT_TTL = {
  critical: 120000, // 2 minutes
  warning:   45000, // 45 seconds
  info:      20000, // 20 seconds
};

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const useTelemetryStore = defineStore('telemetry', () => {

  // ─── State ────────────────────────────────────────────────────
  const current          = ref(null);   // latest TelemetryFrame
  const history          = ref([]);     // ring buffer of frames
  const connectionStatus = ref('connecting');
  
  // Persistent alerts with TTL tracking
  const persistentAlerts = ref([]);     // { ...alert, expiresAt: timestamp }

  // ─── Getters ──────────────────────────────────────────────────

  /** Current health object from backend — { index, category, label, top_factors } */
  const health = computed(() =>
    current.value?.health ?? { index: 0, category: 'E', label: 'Нет данных', top_factors: [] }
  );

  /** Derived category key for CSS classes */
  const categoryKey = computed(() => {
    const idx = health.value.index;
    if (idx >= 75) return 'normal';
    if (idx >= 45) return 'warning';
    return 'critical';
  });

  /** Active alerts - includes persistent alerts that haven't expired */
  const alerts = computed(() => {
    const now = Date.now();
    // Filter out expired alerts
    const active = persistentAlerts.value.filter(a => a.expiresAt > now);
    return active;
  });

  /** Shortcut to telemetry data fields */
  const data = computed(() => current.value?.data ?? null);

  // History slices for charts ([ timestamp_ms, value ])
  const speedHistory = computed(() =>
    history.value.map(f => [new Date(f.timestamp).getTime(), f.data?.speed ?? 0])
  );
  const tempHistory = computed(() =>
    history.value.map(f => [new Date(f.timestamp).getTime(), f.data?.temperature ?? 0])
  );
  const fuelHistory = computed(() =>
    history.value.map(f => [new Date(f.timestamp).getTime(), f.data?.fuel_level ?? 0])
  );
  const pressureHistory = computed(() =>
    history.value.map(f => [new Date(f.timestamp).getTime(), f.data?.pressure ?? 0])
  );
  const healthHistory = computed(() =>
    history.value.map(f => [new Date(f.timestamp).getTime(), f.health?.index ?? 0])
  );

  // ─── Actions ──────────────────────────────────────────────────

  function updateTelemetry(frame) {
    current.value = frame;
    history.value.push(frame);
    if (history.value.length > HISTORY_MAX) {
      history.value.splice(0, history.value.length - HISTORY_MAX);
    }
    
    // Process incoming alerts - add to persistent with TTL
    if (frame.alerts && frame.alerts.length > 0) {
      const now = Date.now();
      for (const alert of frame.alerts) {
        const ttl = ALERT_TTL[alert.severity] || ALERT_TTL.info;
        const alertKey = `${alert.code}-${alert.parameter}`;
        
        // Check if this alert already exists (by code+parameter)
        const existingIdx = persistentAlerts.value.findIndex(
          a => `${a.code}-${a.parameter}` === alertKey
        );
        
        if (existingIdx >= 0) {
          // Refresh expiry time for existing alert
          persistentAlerts.value[existingIdx] = {
            ...alert,
            expiresAt: now + ttl,
          };
        } else {
          // Add new alert
          persistentAlerts.value.push({
            ...alert,
            expiresAt: now + ttl,
          });
        }
      }
      
      // Clean up expired alerts periodically
      persistentAlerts.value = persistentAlerts.value.filter(a => a.expiresAt > now);
    }
  }

  function setConnectionStatus(status) {
    connectionStatus.value = status;
  }

  /** Download CSV from backend (includes DB history, not just in-memory buffer). */
  async function exportCsv(minutes = 15) {
    try {
      const url = `${API_BASE}/export/csv?minutes=${minutes}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const blob = await res.blob();
      const a    = document.createElement('a');
      a.href     = URL.createObjectURL(blob);
      a.download = `telemetry_${Date.now()}.csv`;
      a.click();
      URL.revokeObjectURL(a.href);
    } catch (err) {
      console.error('[Store] CSV export failed:', err);
    }
  }

  /** Download PDF report from backend. */
  async function exportPdf(minutes = 15) {
    try {
      const url = `${API_BASE}/export/pdf?minutes=${minutes}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const blob = await res.blob();
      const a    = document.createElement('a');
      a.href     = URL.createObjectURL(blob);
      a.download = `report_${Date.now()}.pdf`;
      a.click();
      URL.revokeObjectURL(a.href);
    } catch (err) {
      console.error('[Store] PDF export failed:', err);
    }
  }

  return {
    // state
    current, history, connectionStatus,
    // getters
    health, categoryKey, alerts, data,
    speedHistory, tempHistory, fuelHistory, pressureHistory, healthHistory,
    // actions
    updateTelemetry, setConnectionStatus, exportCsv, exportPdf,
  };
});
