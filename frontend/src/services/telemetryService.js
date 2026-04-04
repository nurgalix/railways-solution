/**
 * TelemetryService — WebSocket client for the backend telemetry stream.
 *
 * Backend WS: ws://host/api/ws/telemetry
 *
 * Frame shapes:
 *   type = "telemetry"  → full TelemetryFrame, forwarded to store
 *   type = "heartbeat"  → connectivity ping, not forwarded
 *
 * Reconnect: exponential backoff 2 s → 30 s.
 * Highload:  POST /api/simulator/highload?enabled=true|false
 */

const WS_URL     = import.meta.env.VITE_WS_URL  || 'ws://localhost:8000/api/ws/telemetry';
const API_BASE   = import.meta.env.VITE_API_URL  || 'http://localhost:8000/api';

const RECONNECT_BASE_MS = 2_000;
const RECONNECT_MAX_MS  = 30_000;

class TelemetryService {
  constructor() {
    this._ws           = null;
    this._store        = null;
    this._stopped      = false;
    this._reconnectMs  = RECONNECT_BASE_MS;
    this._reconnectTmr = null;
    this._lastTs       = null; // ISO timestamp of last received frame (for replay)
  }

  // ─── Public API ──────────────────────────────────────────────

  start(store) {
    this._store   = store;
    this._stopped = false;
    this._connect();
  }

  stop() {
    this._stopped = true;
    clearTimeout(this._reconnectTmr);
    if (this._ws) {
      this._ws.onclose = null;
      this._ws.close();
      this._ws = null;
    }
    this._store?.setConnectionStatus('disconnected');
  }

  /** Toggle backend simulator highload mode (×10 events/sec). */
  async setHighload(enabled) {
    try {
      await fetch(`${API_BASE}/simulator/highload?enabled=${enabled}`, { method: 'POST' });
    } catch {
      console.warn('[TelemetryService] Could not toggle highload — backend unreachable');
    }
  }

  // ─── WebSocket ───────────────────────────────────────────────

  _connect() {
    if (this._stopped) return;

    this._store.setConnectionStatus('connecting');

    // Append last_timestamp for missed-frame replay on reconnect
    const url = this._lastTs
      ? `${WS_URL}?last_timestamp=${encodeURIComponent(this._lastTs)}`
      : WS_URL;

    let ws;
    try {
      ws = new WebSocket(url);
    } catch (err) {
      console.error('[TelemetryService] WebSocket constructor failed:', err);
      this._scheduleReconnect();
      return;
    }

    ws.onopen = () => {
      this._ws          = ws;
      this._reconnectMs = RECONNECT_BASE_MS;
      this._store.setConnectionStatus('connected');
    };

    ws.onmessage = (evt) => {
      let frame;
      try {
        frame = JSON.parse(evt.data);
      } catch {
        return;
      }

      if (frame.type === 'heartbeat') {
        // Keep connection status in sync; heartbeat carries live connection count
        this._store.setConnectionStatus('connected');
        return;
      }

      if (frame.type === 'telemetry') {
        this._lastTs = frame.timestamp;
        this._store.updateTelemetry(frame);
      }
    };

    ws.onerror = () => { /* handled in onclose */ };

    ws.onclose = (evt) => {
      this._ws = null;
      if (this._stopped) return;
      console.warn(`[TelemetryService] WS closed (code=${evt.code}). Reconnecting in ${this._reconnectMs}ms…`);
      this._store.setConnectionStatus('disconnected');
      this._scheduleReconnect();
    };
  }

  _scheduleReconnect() {
    if (this._stopped) return;
    clearTimeout(this._reconnectTmr);
    this._reconnectTmr = setTimeout(() => {
      this._reconnectMs = Math.min(this._reconnectMs * 1.5, RECONNECT_MAX_MS);
      this._connect();
    }, this._reconnectMs);
  }
}

export const telemetryService = new TelemetryService();
