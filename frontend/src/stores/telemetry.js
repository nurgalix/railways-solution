import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

// ─── Health Index Formula ──────────────────────────────────────────
// Each sub-factor is normalized 0–100, then weighted and combined.
// Alerts apply multiplicative penalties.

function normalize(value, okMin, okMax, worstMin, worstMax) {
  if (value >= okMin && value <= okMax) return 100;
  if (value < okMin) {
    const range = okMin - worstMin;
    if (range <= 0) return 0;
    return Math.max(0, ((value - worstMin) / range) * 100);
  }
  const range = worstMax - okMax;
  if (range <= 0) return 0;
  return Math.max(0, ((worstMax - value) / range) * 100);
}

function calcHealthIndex(t) {
  if (!t) return { index: 100, factors: [], alertPenalty: 0 };

  const factors = [
    {
      key: 'temp_engine',
      label: 'Температура двигателя',
      unit: '°C',
      value: t.temp_engine,
      score: normalize(t.temp_engine, 60, 88, 30, 110),
      weight: 0.28,
    },
    {
      key: 'pressure_brake',
      label: 'Давление тормозов',
      unit: 'бар',
      value: t.pressure_brake,
      score: normalize(t.pressure_brake, 4.5, 5.5, 2.0, 8.0),
      weight: 0.22,
    },
    {
      key: 'fuel_level',
      label: 'Уровень топлива',
      unit: '%',
      value: t.fuel_level,
      score: normalize(t.fuel_level, 20, 100, 0, 100),
      weight: 0.20,
    },
    {
      key: 'voltage',
      label: 'Напряжение',
      unit: 'В',
      value: t.voltage,
      score: normalize(t.voltage, 570, 640, 480, 720),
      weight: 0.16,
    },
    {
      key: 'temp_oil',
      label: 'Температура масла',
      unit: '°C',
      value: t.temp_oil,
      score: normalize(t.temp_oil, 55, 85, 20, 120),
      weight: 0.14,
    },
  ];

  const weighted = factors.reduce((sum, f) => sum + f.score * f.weight, 0);

  const criticals = (t.alerts || []).filter(a => a.severity === 'critical').length;
  const warnings  = (t.alerts || []).filter(a => a.severity === 'warning').length;
  const alertPenalty = Math.min(35, criticals * 15 + warnings * 5);

  const index = Math.max(0, Math.round(weighted - alertPenalty));

  const sorted = [...factors].sort((a, b) => (a.score - b.score));

  return { index, factors: sorted, alertPenalty };
}

function healthCategory(index) {
  if (index >= 75) return { label: 'Норма',    key: 'normal',   color: 'var(--color-normal)'  };
  if (index >= 45) return { label: 'Внимание', key: 'warning',  color: 'var(--color-warning)' };
  return               { label: 'Критично', key: 'critical', color: 'var(--color-critical)' };
}

// ─── History Config ────────────────────────────────────────────────
const HISTORY_MAX = 900; // 15 min at 1 Hz

export const useTelemetryStore = defineStore('telemetry', () => {
  // ─ State ─────────────────────────────────────────────────────────
  const current         = ref(null);
  const history         = ref([]);          // ring buffer of snapshots
  const connectionStatus = ref('connecting'); // 'connected'|'mock'|'disconnected'
  const isReplayMode    = ref(false);
  const replayIndex     = ref(0);

  // ─ Getters ───────────────────────────────────────────────────────
  const health = computed(() => calcHealthIndex(current.value));
  const category = computed(() => healthCategory(health.value.index));

  const speedHistory = computed(() =>
    history.value.map(s => [s.timestamp, s.speed])
  );
  const tempEngineHistory = computed(() =>
    history.value.map(s => [s.timestamp, s.temp_engine])
  );
  const fuelHistory = computed(() =>
    history.value.map(s => [s.timestamp, s.fuel_level])
  );
  const voltageHistory = computed(() =>
    history.value.map(s => [s.timestamp, s.voltage])
  );
  const healthHistory = computed(() =>
    history.value.map(s => [s.timestamp, calcHealthIndex(s).index])
  );

  // ─ Actions ───────────────────────────────────────────────────────
  function updateTelemetry(data) {
    current.value = data;
    history.value.push({ ...data });
    if (history.value.length > HISTORY_MAX) {
      history.value.splice(0, history.value.length - HISTORY_MAX);
    }
  }

  function setConnectionStatus(status) {
    connectionStatus.value = status;
  }

  // Replay: returns a slice of history for scrubbing
  function getReplaySlice(minutes = 15) {
    const count = Math.min(minutes * 60, history.value.length);
    return history.value.slice(-count);
  }

  function exportCsv() {
    if (!history.value.length) return;
    const headers = [
      'timestamp','speed','fuel_level','fuel_consumption',
      'pressure_brake','pressure_main','temp_engine','temp_oil',
      'voltage','current','health_index',
    ];
    const rows = history.value.map(s => {
      const hi = calcHealthIndex(s).index;
      return [
        new Date(s.timestamp).toISOString(),
        s.speed, s.fuel_level, s.fuel_consumption,
        s.pressure_brake, s.pressure_main, s.temp_engine, s.temp_oil,
        s.voltage, s.current, hi,
      ].join(',');
    });
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `telemetry_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return {
    current, history, connectionStatus, isReplayMode, replayIndex,
    health, category,
    speedHistory, tempEngineHistory, fuelHistory, voltageHistory, healthHistory,
    updateTelemetry, setConnectionStatus, getReplaySlice, exportCsv,
  };
});
