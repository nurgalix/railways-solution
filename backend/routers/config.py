"""
REST endpoints for Health Index configuration management.
"""

from fastapi import APIRouter, Depends, HTTPException

from middleware.auth import require_admin
from models.user import User
from schemas.config_schemas import (
    HealthConfigResponse,
    ParameterConfig,
    CategoryRange,
    AlertPenalties,
    ThresholdUpdate,
    WeightUpdate,
)
from services.health_index import get_config, reload_config

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/thresholds", response_model=HealthConfigResponse)
async def get_thresholds():
    """Get current Health Index configuration (thresholds, weights, categories)."""
    config = get_config()
    params = {}
    for name, cfg in config.get("parameters", {}).items():
        params[name] = ParameterConfig(
            weight=cfg["weight"],
            unit=cfg.get("unit", ""),
            label=cfg.get("label", name),
            normal_range=cfg["normal_range"],
            warning_range=cfg["warning_range"],
            critical_range=cfg["critical_range"],
        )

    categories = {}
    for letter, cat in config.get("categories", {}).items():
        categories[letter] = CategoryRange(
            min_value=cat["min"],
            max_value=cat["max"],
            label=cat.get("label", letter),
        )

    penalty = config.get("alert_penalty", {})
    return HealthConfigResponse(
        parameters=params,
        alert_penalty=AlertPenalties(
            warning=penalty.get("warning", 5),
            critical=penalty.get("critical", 15),
        ),
        categories=categories,
    )


@router.put("/thresholds", response_model=dict)
async def update_threshold(
    update: ThresholdUpdate,
    user: User = Depends(require_admin),
):
    """Update thresholds for a specific parameter (admin only)."""
    import yaml
    from config import get_settings

    settings = get_settings()
    config = get_config()
    params = config.get("parameters", {})

    if update.parameter not in params:
        raise HTTPException(
            status_code=404,
            detail=f"Parameter '{update.parameter}' not found in config",
        )

    # Update in-memory config
    if update.normal_range is not None:
        params[update.parameter]["normal_range"] = update.normal_range
    if update.warning_range is not None:
        params[update.parameter]["warning_range"] = update.warning_range
    if update.critical_range is not None:
        params[update.parameter]["critical_range"] = update.critical_range

    # Persist to YAML file
    with open(settings.HEALTH_CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    # Reload config
    reload_config()

    return {"status": "updated", "parameter": update.parameter}


@router.put("/weights", response_model=dict)
async def update_weight(
    update: WeightUpdate,
    user: User = Depends(require_admin),
):
    """Update weight for a specific parameter (admin only)."""
    import yaml
    from config import get_settings

    settings = get_settings()
    config = get_config()
    params = config.get("parameters", {})

    if update.parameter not in params:
        raise HTTPException(
            status_code=404,
            detail=f"Parameter '{update.parameter}' not found in config",
        )

    params[update.parameter]["weight"] = update.weight

    with open(settings.HEALTH_CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    reload_config()

    return {"status": "updated", "parameter": update.parameter, "weight": update.weight}


@router.get("/health-formula")
async def get_health_formula():
    """Return the Health Index formula with current weights."""
    config = get_config()
    params = config.get("parameters", {})

    weights = {
        name: {
            "weight": cfg["weight"],
            "label": cfg.get("label", name),
            "unit": cfg.get("unit", ""),
        }
        for name, cfg in params.items()
    }

    total_weight = sum(cfg["weight"] for cfg in params.values())

    return {
        "total_weight": round(total_weight, 4),
        "parameters": weights,
        "alert_penalties": config.get("alert_penalty", {}),
        "categories": config.get("categories", {}),
        "description": (
            "Health Index = Σ(parameter_score × weight) / Σ(weights) − alert_penalties. "
            "Each parameter score is 0–100 based on threshold ranges."
        ),
    }


@router.post("/reload")
async def reload_configuration(
    user: User = Depends(require_admin),
):
    """Force-reload config from YAML file (admin only)."""
    reload_config()
    return {"status": "reloaded"}
