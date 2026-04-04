"""
REST endpoints for telemetry history and replay.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import get_db
from models.telemetry import TelemetryReading
from schemas.telemetry import (
    TelemetryHistoryItem,
    TelemetryHistoryResponse,
    TelemetryFrame,
)
from services.telemetry_buffer import get_buffer

router = APIRouter(prefix="/api/telemetry", tags=["telemetry"])


@router.get("/latest", response_model=dict)
async def get_latest():
    """Get the most recent telemetry frame from the buffer."""
    buffer = get_buffer()
    frames = await buffer.get_latest(1)
    if not frames:
        raise HTTPException(status_code=404, detail="No telemetry data available yet")
    return frames[0].model_dump(mode="json")


@router.get("/history", response_model=TelemetryHistoryResponse)
async def get_history(
    start: datetime | None = Query(None, description="Start time (ISO 8601)"),
    end: datetime | None = Query(None, description="End time (ISO 8601)"),
    minutes: int = Query(15, ge=1, le=1440, description="If start/end not provided, last N minutes"),
    limit: int = Query(500, ge=1, le=5000, description="Max records to return"),
    offset: int = Query(0, ge=0),
    locomotive_id: str = Query("LOC-001"),
    db: AsyncSession = Depends(get_db),
):
    """Query historical telemetry from the database."""
    if end is None:
        end = datetime.now(timezone.utc)
    if start is None:
        start = end - timedelta(minutes=minutes)

    # Count total
    count_q = (
        select(func.count())
        .select_from(TelemetryReading)
        .where(
            TelemetryReading.locomotive_id == locomotive_id,
            TelemetryReading.timestamp >= start,
            TelemetryReading.timestamp <= end,
        )
    )
    total = (await db.execute(count_q)).scalar() or 0

    # Fetch data
    q = (
        select(TelemetryReading)
        .where(
            TelemetryReading.locomotive_id == locomotive_id,
            TelemetryReading.timestamp >= start,
            TelemetryReading.timestamp <= end,
        )
        .order_by(TelemetryReading.timestamp)
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(q)
    readings = result.scalars().all()

    items = [
        TelemetryHistoryItem(
            timestamp=r.timestamp,
            speed=r.speed,
            fuel_level=r.fuel_level,
            pressure=r.pressure,
            temperature=r.temperature,
            health_index=r.health_index,
            health_category=r.health_category,
            latitude=r.latitude,
            longitude=r.longitude,
            km_marker=r.km_marker,
        )
        for r in readings
    ]

    return TelemetryHistoryResponse(
        items=items,
        total=total,
        start=start,
        end=end,
    )


@router.get("/buffer", response_model=list[dict])
async def get_buffer_contents(
    n: int = Query(100, ge=1, le=1000, description="Number of recent frames"),
):
    """Get recent frames directly from the in-memory buffer."""
    buffer = get_buffer()
    frames = await buffer.get_latest(n)
    return [f.model_dump(mode="json") for f in frames]


@router.get("/stats")
async def get_stats():
    """Get buffer and connection statistics."""
    from routers.ws import get_connection_count
    buffer = get_buffer()
    return {
        "buffer_size": buffer.size,
        "total_frames_processed": buffer.frame_count,
        "active_ws_connections": get_connection_count(),
    }
