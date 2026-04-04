/**
 * Mock telemetry generator — simulates a locomotive's sensor stream.
 * Uses random-walk + EMA smoothing for realistic variation.
 * Generates occasional alerts with auto-clear.
 */

// EMA smoothing helper
function ema(prev, next, alpha = 0.3) {
  return prev + alpha * (next - prev);
}

// Clamp helper
function clamp(v, min, max) {
  return Math.min(max, Math.max(min, v));
}

// Random walk step
function walk(v, sigma, min, max) {
  return clamp(v + (Math.random() - 0.5) * 2 * sigma, min, max);
}

// Route: simplified Kazakhstan rail corridor (Almaty → Shymkent direction)
const ROUTE_WAYPOINTS = [
  { lat: 43.238949, lng: 76.889709, km: 0,   name: 'Алматы' },
  { lat: 43.18,     lng: 76.52,     km: 45,  name: '' },
  { lat: 43.06,     lng: 76.10,     km: 92,  name: '' },
  { lat: 42.90,     lng: 75.68,     km: 141, name: '' },
  { lat: 42.72,     lng: 75.20,     km: 192, name: 'Чу' },
  { lat: 42.50,     lng: 74.80,     km: 240, name: '' },
  { lat: 42.30,     lng: 74.25,     km: 295, name: 'Луговая' },
  { lat: 42.18,     lng: 73.60,     km: 350, name: 'Тараз' },
];
const ROUTE_MAX_KM = ROUTE_WAYPOINTS[ROUTE_WAYPOINTS.length - 1].km;

function interpolatePosition(km) {
  for (let i = 0; i < ROUTE_WAYPOINTS.length - 1; i++) {
    const a = ROUTE_WAYPOINTS[i];
    const b = ROUTE_WAYPOINTS[i + 1];
    if (km >= a.km && km <= b.km) {
      const t = (km - a.km) / (b.km - a.km);
      return {
        lat: a.lat + t * (b.lat - a.lat),
        lng: a.lng + t * (b.lng - a.lng),
        km: Math.round(km),
      };
    }
  }
  return { ...ROUTE_WAYPOINTS[ROUTE_WAYPOINTS.length - 1] };
}

// ─── Alert definitions ─────────────────────────────────────────────
const ALERT_TYPES = [
  {
    id: 'HIGH_ENGINE_TEMP',
    severity: 'critical',
    title: 'Перегрев двигателя',
    message: 'Температура двигателя превышает допустимый порог (>92°C).',
    recommendation: 'Снизить нагрузку, проверить систему охлаждения.',
    trigger: s => s.temp_engine > 92,
  },
  {
    id: 'LOW_FUEL',
    severity: 'warning',
    title: 'Низкий уровень топлива',
    message: 'Уровень топлива ниже 15%.',
    recommendation: 'Запланировать дозаправку на ближайшей станции.',
    trigger: s => s.fuel_level < 15,
  },
  {
    id: 'LOW_BRAKE_PRESSURE',
    severity: 'critical',
    title: 'Давление тормозов вне нормы',
    message: 'Давление тормозной магистрали вне допустимого диапазона (4.5–5.5 бар).',
    recommendation: 'Немедленно проверить тормозную систему.',
    trigger: s => s.pressure_brake < 4.3 || s.pressure_brake > 5.7,
  },
  {
    id: 'VOLTAGE_HIGH',
    severity: 'warning',
    title: 'Повышенное напряжение',
    message: 'Напряжение бортовой сети выше нормы (>645В).',
    recommendation: 'Проверить генератор и регулятор напряжения.',
    trigger: s => s.voltage > 645,
  },
  {
    id: 'OIL_TEMP_HIGH',
    severity: 'warning',
    title: 'Высокая температура масла',
    message: 'Температура моторного масла превышает 88°C.',
    recommendation: 'Проверить масляный радиатор.',
    trigger: s => s.temp_oil > 88,
  },
  {
    id: 'HIGH_SPEED',
    severity: 'warning',
    title: 'Превышение скорости',
    message: 'Скорость превышает ограничение участка (120 км/ч).',
    recommendation: 'Снизить скорость согласно регламенту.',
    trigger: s => s.speed > 120,
  },
];

// ─── Generator class ───────────────────────────────────────────────
export class MockTelemetryGenerator {
  constructor() {
    this._state = {
      speed:             65,
      fuel_level:        72,
      fuel_consumption:  62,
      pressure_brake:    5.0,
      pressure_main:     8.5,
      temp_engine:       78,
      temp_oil:          70,
      voltage:           608,
      current:           940,
      position_km:       45,
    };
    // Slow targets for smooth variation
    this._targets = { ...this._state };
    this._tick = 0;
    this._activeAlerts = new Map();
  }

  _updateTargets() {
    // Re-pick targets every ~30 ticks
    if (this._tick % 30 === 0) {
      this._targets.speed            = clamp(walk(this._targets.speed, 15, 0, 130), 0, 130);
      this._targets.temp_engine      = clamp(walk(this._targets.temp_engine, 4, 55, 100), 55, 100);
      this._targets.temp_oil         = clamp(walk(this._targets.temp_oil, 3, 50, 95), 50, 95);
      this._targets.voltage          = clamp(walk(this._targets.voltage, 15, 550, 660), 550, 660);
      this._targets.pressure_brake   = clamp(walk(this._targets.pressure_brake, 0.4, 3.8, 6.2), 3.8, 6.2);
      this._targets.pressure_main    = clamp(walk(this._targets.pressure_main, 0.3, 7.5, 9.5), 7.5, 9.5);
    }
  }

  _computeAlerts(state) {
    const now = Date.now();
    for (const def of ALERT_TYPES) {
      if (def.trigger(state)) {
        if (!this._activeAlerts.has(def.id)) {
          this._activeAlerts.set(def.id, { ...def, timestamp: now, id: def.id });
        }
      } else {
        this._activeAlerts.delete(def.id);
      }
    }
    return Array.from(this._activeAlerts.values()).map(a => ({
      id:             a.id,
      severity:       a.severity,
      title:          a.title,
      message:        a.message,
      recommendation: a.recommendation,
      timestamp:      a.timestamp,
    }));
  }

  next() {
    this._tick++;
    this._updateTargets();

    const s = this._state;
    const t = this._targets;

    // Smooth walk toward targets
    s.speed           = ema(s.speed, t.speed, 0.08);
    s.temp_engine     = ema(s.temp_engine, t.temp_engine, 0.05);
    s.temp_oil        = ema(s.temp_oil, t.temp_oil, 0.04);
    s.voltage         = ema(s.voltage, t.voltage, 0.06);
    s.pressure_brake  = ema(s.pressure_brake, t.pressure_brake, 0.07);
    s.pressure_main   = ema(s.pressure_main, t.pressure_main, 0.05);
    s.fuel_consumption = clamp(s.speed * 0.6 + 20 + (Math.random() - 0.5) * 4, 18, 95);
    s.current         = clamp(s.speed * 9 + 200 + (Math.random() - 0.5) * 60, 200, 1400);

    // Fuel decreases slowly based on consumption
    s.fuel_level = Math.max(0, s.fuel_level - s.fuel_consumption / 3600000 * 1000);

    // Position advances based on speed (km/h → km/tick@1Hz)
    s.position_km = (s.position_km + s.speed / 3600) % ROUTE_MAX_KM;

    const position = interpolatePosition(s.position_km);
    const alerts   = this._computeAlerts(s);

    return {
      timestamp:        Date.now(),
      speed:            Math.round(s.speed * 10) / 10,
      fuel_level:       Math.round(s.fuel_level * 10) / 10,
      fuel_consumption: Math.round(s.fuel_consumption * 10) / 10,
      pressure_brake:   Math.round(s.pressure_brake * 100) / 100,
      pressure_main:    Math.round(s.pressure_main * 100) / 100,
      temp_engine:      Math.round(s.temp_engine * 10) / 10,
      temp_oil:         Math.round(s.temp_oil * 10) / 10,
      voltage:          Math.round(s.voltage),
      current:          Math.round(s.current),
      position,
      alerts,
    };
  }
}

export { ROUTE_WAYPOINTS, ROUTE_MAX_KM };
