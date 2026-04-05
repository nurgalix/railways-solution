"""
Alert engine: checks telemetry against thresholds, generates alerts with
recommendations, and debounces repeated alerts.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from services.health_index import get_config

logger = logging.getLogger(__name__)

# Recommendation templates per parameter
_RECOMMENDATIONS: dict[str, dict[str, str]] = {
    "speed": {
        "warning": "Reduce speed to within operational limits",
        "critical": "EMERGENCY: Apply brakes immediately, speed dangerously high",
    },
    "fuel_level": {
        "warning": "Plan refueling stop at next station",
        "critical": "URGENT: Fuel critically low, stop at nearest point",
    },
    "pressure": {
        "warning": "Pressure below normal — monitor closely",
        "critical": "CRITICAL: Pressure dangerously low, risk of failure",
    },
    "temperature": {
        "warning": "Overheating — reduce load, check system",
        "critical": "CRITICAL: Severe overheating, stop engine if safe to do so",
    },
}


class AlertEngine:
    """Stateful alert detection with debouncing."""

    def __init__(self, debounce_seconds: float = 60.0):
        self._debounce_sec = debounce_seconds
        # last fire time per (param, severity)
        self._last_fired: dict[tuple[str, str], datetime] = {}

    def _is_debounced(self, param: str, severity: str, now: datetime) -> bool:
        key = (param, severity)
        last = self._last_fired.get(key)
        if last is None:
            return False
        delta = (now - last).total_seconds()
        return delta < self._debounce_sec

    def _record_fire(self, param: str, severity: str, now: datetime) -> None:
        self._last_fired[(param, severity)] = now

    def check(
        self,
        telemetry: dict[str, float],
        locomotive_id: str = "LOC-001",
        config: dict[str, Any] | None = None,
    ) -> list[dict]:
        """
        Check all parameters against thresholds and return new alert dicts.
        Respects debouncing so the same alert is not re-fired immediately.
        """
        if config is None:
            config = get_config()

        now = datetime.now(timezone.utc)
        params_config = config.get("parameters", {})
        alerts: list[dict] = []

        for param_name, param_cfg in params_config.items():
            value = telemetry.get(param_name)
            if value is None:
                continue

            n_lo, n_hi = param_cfg["normal_range"]
            w_lo, w_hi = param_cfg["warning_range"]
            c_lo, c_hi = param_cfg["critical_range"]

            # Detect inverted parameters
            inverted = w_hi <= n_lo

            severity = None
            threshold_val = None

            if inverted:
                if value < c_lo:
                    severity = "critical"
                    threshold_val = c_lo
                elif value < w_lo:
                    severity = "critical"
                    threshold_val = w_lo
                elif value < n_lo:
                    severity = "warning"
                    threshold_val = n_lo
            else:
                if value > c_hi:
                    severity = "critical"
                    threshold_val = c_hi
                elif value > w_hi:
                    severity = "critical"
                    threshold_val = w_hi
                elif value > n_hi:
                    severity = "warning"
                    threshold_val = n_hi

            if severity and not self._is_debounced(param_name, severity, now):
                self._record_fire(param_name, severity, now)
                code = f"{param_name.upper()}_{severity.upper()}"
                rec = _RECOMMENDATIONS.get(param_name, {}).get(
                    severity, f"Check {param_name}"
                )
                alerts.append({
                    "severity": severity,
                    "code": code,
                    "message": (
                        f"{param_cfg.get('label', param_name)} is "
                        f"{'below' if inverted else 'above'} "
                        f"{severity} threshold: "
                        f"{value:.1f} {param_cfg.get('unit', '')} "
                        f"(limit: {threshold_val:.1f})"
                    ),
                    "parameter": param_name,
                    "value": value,
                    "threshold": threshold_val,
                    "recommendation": rec,
                    "locomotive_id": locomotive_id,
                    "timestamp": now,
                })

        return alerts


# ── Singleton ─────────────────────────────────────────────────

_engine_instance: AlertEngine | None = None


def get_alert_engine() -> AlertEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = AlertEngine()
    return _engine_instance
