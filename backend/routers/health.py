"""
REST endpoints for Health Index.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import get_db
from models.telemetry import TelemetryReading
from schemas.telemetry import HealthIndexResponse
from services.health_index import calculate_health_index, get_config
from services.telemetry_buffer import get_buffer

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/current", response_model=HealthIndexResponse)
async def get_current_health():
    """Get the current Health Index from the latest telemetry frame."""
    buffer = get_buffer()
    frames = await buffer.get_latest(1)
    if not frames:
        # Return a default "no data" response
        return HealthIndexResponse(
            index=0.0,
            category="E",
            label="No Data",
            top_factors=[],
        )
    return frames[0].health


@router.get("/history")
async def get_health_history(
    minutes: int = Query(30, ge=1, le=1440),
    locomotive_id: str = Query("LOC-001"),
    db: AsyncSession = Depends(get_db),
):
    """Get Health Index trend over time."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=minutes)

    q = (
        select(
            TelemetryReading.timestamp,
            TelemetryReading.health_index,
            TelemetryReading.health_category,
        )
        .where(
            TelemetryReading.locomotive_id == locomotive_id,
            TelemetryReading.timestamp >= start,
            TelemetryReading.timestamp <= end,
        )
        .order_by(TelemetryReading.timestamp)
    )
    result = await db.execute(q)
    rows = result.all()

    return {
        "items": [
            {
                "timestamp": row.timestamp.isoformat() if row.timestamp else None,
                "health_index": row.health_index,
                "health_category": row.health_category,
            }
            for row in rows
        ],
        "start": start.isoformat(),
        "end": end.isoformat(),
        "count": len(rows),
    }


@router.get("/factors")
async def get_health_factors():
    """Get detailed factor breakdown for the current Health Index."""
    buffer = get_buffer()
    frames = await buffer.get_latest(1)
    if not frames:
        return {"factors": [], "message": "No telemetry data available"}

    frame = frames[0]
    data_dict = frame.data.model_dump()
    # Remove position from dict for health calc
    data_dict.pop("position", None)

    health = calculate_health_index(data_dict)

    config = get_config()
    params_config = config.get("parameters", {})

    detailed_factors = []
    for factor in health.top_factors:
        param_cfg = params_config.get(factor.parameter, {})
        detailed_factors.append({
            "parameter": factor.parameter,
            "label": param_cfg.get("label", factor.parameter),
            "unit": param_cfg.get("unit", ""),
            "current_value": data_dict.get(factor.parameter),
            "score": factor.score,
            "weight": factor.weight,
            "impact": factor.impact,
            "status": factor.status,
            "normal_range": param_cfg.get("normal_range"),
            "warning_range": param_cfg.get("warning_range"),
            "critical_range": param_cfg.get("critical_range"),
        })

    return {
        "index": health.index,
        "category": health.category,
        "label": health.label,
        "factors": detailed_factors,
    }


@router.get("/formula")
async def get_formula():
    """Return explanation of the Health Index formula."""
    return {
        "description": (
            "Health Index is calculated as a weighted average of per-parameter scores, "
            "with penalties for active alerts."
        ),
        "formula": {
            "step_1": "For each parameter, calculate score 0-100 based on threshold ranges",
            "step_2": "Multiply each score by its weight",
            "step_3": "Sum weighted scores and divide by total weight (Raw Index)",
            "step_4": "Subtract penalties for active alerts (warning: -5, critical: -15)",
            "step_5": "Clamp result to [0, 100]",
        },
        "categories": {
            "A": "85-100 (Normal)",
            "B": "70-84 (Attention)",
            "C": "50-69 (Warning)",
            "D": "25-49 (Critical)",
            "E": "0-24 (Emergency)",
        },
        "scoring": {
            "normal_range": "Score = 100",
            "warning_range": "Score = 100 → 50 (linear interpolation)",
            "critical_range": "Score = 50 → 0 (linear interpolation)",
            "beyond_critical": "Score = 0",
        },
    }
