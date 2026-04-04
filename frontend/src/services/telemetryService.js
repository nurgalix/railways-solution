/**
 * TelemetryService — manages real WebSocket connection with automatic
 * fallback to mock mode when the backend is unavailable.
 *
 * Usage:
 *   telemetryService.start(store)
 *   telemetryService.stop()
 *   telemetryService.setHighload(true)   // x10 burst for stress demo
 */

import { MockTelemetryGenerator } from './mockTelemetry.js';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/telemetry';
const RECONNECT_BASE_MS  = 2000;
const RECONNECT_MAX_MS   = 30000;
const MOCK_INTERVAL_MS   = 1000;   // 1 Hz normal
const MOCK_HIGHLOAD_FACTOR = 10;   // x10 for highload demo

class TelemetryService {
  constructor() {
    this._ws           = null;
    this._mockTimer    = null;
    this._generator    = new MockTelemetryGenerator();
    this._store        = null;
    this._reconnectMs  = RECONNECT_BASE_MS;
    this._reconnectTmr = null;
    this._stopped      = false;
    this._highload     = false;
    this._useMock      = false;
  }

  // ─── Public API ──────────────────────────────────────────────────

  start(store) {
    this._store   = store;
    this._stopped = false;
    this._tryConnect();
  }

  stop() {
    this._stopped = true;
    clearTimeout(this._reconnectTmr);
    this._stopMock();
    if (this._ws) {
      this._ws.onclose = null;
      this._ws.close();
      this._ws = null;
    }
  }

  setHighload(enabled) {
    this._highload = enabled;
    if (this._useMock) {
      this._stopMock();
      this._startMock();
    }
  }

  // ─── WebSocket ───────────────────────────────────────────────────

  _tryConnect() {
    if (this._stopped) return;

    this._store.setConnectionStatus('connecting');

    try {
      const ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        this._ws          = ws;
        this._useMock     = false;
        this._reconnectMs = RECONNECT_BASE_MS;
        this._stopMock();
        this._store.setConnectionStatus('connected');
      };

      ws.onmessage = (evt) => {
        try {
          const data = JSON.parse(evt.data);
          this._store.updateTelemetry(data);
        } catch { /* ignore parse errors */ }
      };

      ws.onerror = () => { /* handled in onclose */ };

      ws.onclose = () => {
        this._ws = null;
        if (this._stopped) return;
        // Backend not available — fall back to mock
        if (!this._useMock) {
          this._useMock = true;
          this._store.setConnectionStatus('mock');
          this._startMock();
        }
        this._scheduleReconnect();
      };

      // Timeout if connection never opens (e.g. refused immediately before onclose fires)
      setTimeout(() => {
        if (ws.readyState !== WebSocket.OPEN && !this._stopped) {
          ws.close();
        }
      }, 3000);

    } catch {
      // WebSocket constructor itself threw (e.g. invalid URL)
      this._useMock = true;
      this._store.setConnectionStatus('mock');
      this._startMock();
    }
  }

  _scheduleReconnect() {
    if (this._stopped) return;
    clearTimeout(this._reconnectTmr);
    this._reconnectTmr = setTimeout(() => {
      this._reconnectMs = Math.min(this._reconnectMs * 1.5, RECONNECT_MAX_MS);
      this._tryConnect();
    }, this._reconnectMs);
  }

  // ─── Mock mode ───────────────────────────────────────────────────

  _startMock() {
    if (this._mockTimer) return;
    const intervalMs = this._highload
      ? MOCK_INTERVAL_MS / MOCK_HIGHLOAD_FACTOR
      : MOCK_INTERVAL_MS;

    // Emit one tick, then batch rapidly for highload
    const tick = () => {
      if (this._highload) {
        // Emit 10 data points but only one UI update via RAF
        for (let i = 0; i < MOCK_HIGHLOAD_FACTOR; i++) {
          this._store.updateTelemetry(this._generator.next());
        }
      } else {
        this._store.updateTelemetry(this._generator.next());
      }
    };

    tick();
    this._mockTimer = setInterval(tick, intervalMs);
  }

  _stopMock() {
    if (this._mockTimer) {
      clearInterval(this._mockTimer);
      this._mockTimer = null;
    }
  }
}

export const telemetryService = new TelemetryService();
