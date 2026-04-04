"""
Health Index calculation engine.

Transparent, explainable formula:
  For each parameter p with weight w:
    score = 100           if value in normal_range
    score = 100→50 linear if value in warning_range
    score = 50→0 linear   if value in critical_range
    score = 0             if beyond critical

  Raw Index = Σ(score × weight) / Σ(weight)
  Final Index = max(0, Raw Index − alert_penalties)
  Category = A–E based on configurable thresholds
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from schemas.telemetry import HealthFactor, HealthIndexResponse

logger = logging.getLogger(__name__)

_config_cache: dict[str, Any] | None = None
_config_path: str = "health_config.yaml"


def load_config(path: str | None = None) -> dict[str, Any]:
    """Load (and cache) the YAML health config."""
    global _config_cache, _config_path
    if path:
        _config_path = path
    if _config_cache is None:
        p = Path(_config_path)
        if not p.exists():
            raise FileNotFoundError(f"Health config not found: {p.resolve()}")
        with open(p) as f:
            _config_cache = yaml.safe_load(f)
        logger.info("Loaded health config from %s", p.resolve())
    return _config_cache


def reload_config() -> dict[str, Any]:
    """Force-reload config from disk."""
    global _config_cache
    _config_cache = None
    return load_config()


def get_config() -> dict[str, Any]:
    return load_config()


def _score_parameter(
    value: float,
    normal_range: list[float],
    warning_range: list[float],
    critical_range: list[float],
    inverted: bool = False,
) -> tuple[float, str]:
    """
    Calculate per-parameter score 0–100 and status.

    Some parameters are "inverted" — lower value is worse
    (e.g. fuel_level, oil_pressure, brake_pressure, voltage).
    """
    n_lo, n_hi = normal_range
    w_lo, w_hi = warning_range
    c_lo, c_hi = critical_range

    # Determine if this parameter has inverted semantics
    # (warning range is numerically below normal range)
    if w_hi <= n_lo:
        inverted = True

    if inverted:
        # e.g. fuel_level: normal=[30,100], warning=[15,30], critical=[0,15]
        if value >= n_lo:
            return 100.0, "normal"
        if value >= w_lo:
            # Linear 100 → 50 as value drops from n_lo to w_lo
            ratio = (n_lo - value) / max(n_lo - w_lo, 1e-9)
            return 100.0 - 50.0 * ratio, "warning"
        if value >= c_lo:
            ratio = (w_lo - value) / max(w_lo - c_lo, 1e-9)
            return 50.0 - 50.0 * ratio, "critical"
        return 0.0, "critical"
    else:
        # Normal (high-is-bad) parameters: speed, temps, consumption, current
        if n_lo <= value <= n_hi:
            return 100.0, "normal"
        if n_hi < value <= w_hi:
            ratio = (value - n_hi) / max(w_hi - n_hi, 1e-9)
            return 100.0 - 50.0 * ratio, "warning"
        if w_hi < value <= c_hi:
            ratio = (value - w_hi) / max(c_hi - w_hi, 1e-9)
            return 50.0 - 50.0 * ratio, "critical"
        if value > c_hi:
            return 0.0, "critical"
        # Below normal range (under-value for non-inverted — still fine)
        if value < n_lo:
            # For temperature-like params, below normal can also be an issue
            # But for simplicity, treat as normal
            return 100.0, "normal"
        return 100.0, "normal"


def _get_category(index: float, config: dict) -> tuple[str, str]:
    """Map index value to category letter and label."""
    categories = config.get("categories", {})
    for letter in ["A", "B", "C", "D", "E"]:
        cat = categories.get(letter, {})
        if cat.get("min", 0) <= index <= cat.get("max", 100):
            return letter, cat.get("label", letter)
    return "E", "Emergency"


def calculate_health_index(
    telemetry: dict[str, float],
    active_alerts: list[dict] | None = None,
    config: dict[str, Any] | None = None,
) -> HealthIndexResponse:
    """
    Calculate the Health Index from a telemetry dict.

    Args:
        telemetry: dict of parameter_name → current_value
        active_alerts: list of alert dicts with 'severity' key
        config: optional override config (uses cached otherwise)

    Returns:
        HealthIndexResponse with index, category, label, and top factors
    """
    if config is None:
        config = get_config()

    params_config = config.get("parameters", {})
    penalty_config = config.get("alert_penalty", {})

    factors: list[HealthFactor] = []
    total_weighted_score = 0.0
    total_weight = 0.0

    for param_name, param_cfg in params_config.items():
        value = telemetry.get(param_name)
        if value is None:
            continue

        weight = param_cfg.get("weight", 0.0)
        score, status = _score_parameter(
            value=value,
            normal_range=param_cfg["normal_range"],
            warning_range=param_cfg["warning_range"],
            critical_range=param_cfg["critical_range"],
        )

        contribution = score * weight
        total_weighted_score += contribution
        total_weight += weight

        # Impact = how much this parameter drags down the index
        impact = -((100.0 - score) * weight / max(total_weight, 1e-9))

        factors.append(
            HealthFactor(
                parameter=param_name,
                score=round(score, 1),
                weight=weight,
                impact=round(impact, 2),
                status=status,
            )
        )

    # Raw index
    raw_index = total_weighted_score / max(total_weight, 1e-9)

    # Alert penalties
    alert_penalty = 0.0
    if active_alerts:
        for alert in active_alerts:
            severity = alert.get("severity", "info")
            if severity == "warning":
                alert_penalty += penalty_config.get("warning", 5)
            elif severity == "critical":
                alert_penalty += penalty_config.get("critical", 15)

    final_index = max(0.0, min(100.0, raw_index - alert_penalty))

    # Sort factors by impact (most negative first) → top-5
    factors.sort(key=lambda f: f.impact)
    top_factors = factors[:5]

    # Recalculate impact against final total_weight for accuracy
    for f in top_factors:
        f.impact = round(-((100.0 - f.score) * f.weight / max(total_weight, 1e-9)), 2)

    category, label = _get_category(final_index, config)

    return HealthIndexResponse(
        index=round(final_index, 1),
        category=category,
        label=label,
        top_factors=top_factors,
    )
