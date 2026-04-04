"""
REST endpoints for alerts.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import get_db
from middleware.auth import get_current_user
from models.telemetry import AlertEvent
from models.user import User
from schemas.telemetry import AlertData

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertData])
async def get_alerts(
    severity: str | None = Query(None, description="Filter by severity: info/warning/critical"),
    minutes: int = Query(60, ge=1, le=1440),
    limit: int = Query(100, ge=1, le=500),
    locomotive_id: str = Query("LOC-001"),
    db: AsyncSession = Depends(get_db),
):
    """Get alert history."""
    start = datetime.now(timezone.utc) - timedelta(minutes=minutes)

    q = (
        select(AlertEvent)
        .where(
            AlertEvent.locomotive_id == locomotive_id,
            AlertEvent.timestamp >= start,
        )
        .order_by(desc(AlertEvent.timestamp))
        .limit(limit)
    )

    if severity:
        q = q.where(AlertEvent.severity == severity)

    result = await db.execute(q)
    events = result.scalars().all()

    return [
        AlertData(
            id=e.id,
            severity=e.severity,
            code=e.code,
            message=e.message,
            parameter=e.parameter,
            value=e.value,
            threshold=e.threshold,
            recommendation=e.recommendation,
            acknowledged=e.acknowledged,
            timestamp=e.timestamp,
        )
        for e in events
    ]


@router.get("/active", response_model=list[AlertData])
async def get_active_alerts(
    locomotive_id: str = Query("LOC-001"),
    db: AsyncSession = Depends(get_db),
):
    """Get unacknowledged alerts."""
    q = (
        select(AlertEvent)
        .where(
            AlertEvent.locomotive_id == locomotive_id,
            AlertEvent.acknowledged == False,
        )
        .order_by(desc(AlertEvent.timestamp))
        .limit(50)
    )
    result = await db.execute(q)
    events = result.scalars().all()

    return [
        AlertData(
            id=e.id,
            severity=e.severity,
            code=e.code,
            message=e.message,
            parameter=e.parameter,
            value=e.value,
            threshold=e.threshold,
            recommendation=e.recommendation,
            acknowledged=e.acknowledged,
            timestamp=e.timestamp,
        )
        for e in events
    ]


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Acknowledge an alert (requires authentication)."""
    result = await db.execute(
        select(AlertEvent).where(AlertEvent.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.acknowledged = True
    await db.commit()
    return {"status": "acknowledged", "alert_id": alert_id}


@router.get("/summary")
async def get_alert_summary(
    minutes: int = Query(60, ge=1, le=1440),
    locomotive_id: str = Query("LOC-001"),
    db: AsyncSession = Depends(get_db),
):
    """Get alert count summary by severity."""
    start = datetime.now(timezone.utc) - timedelta(minutes=minutes)

    q = (
        select(AlertEvent.severity, func.count())
        .where(
            AlertEvent.locomotive_id == locomotive_id,
            AlertEvent.timestamp >= start,
        )
        .group_by(AlertEvent.severity)
    )
    result = await db.execute(q)
    rows = result.all()

    summary = {"info": 0, "warning": 0, "critical": 0}
    for severity, count in rows:
        summary[severity] = count

    # Active (unacknowledged) count
    active_q = (
        select(func.count())
        .select_from(AlertEvent)
        .where(
            AlertEvent.locomotive_id == locomotive_id,
            AlertEvent.acknowledged == False,
        )
    )
    active_count = (await db.execute(active_q)).scalar() or 0

    return {**summary, "total": sum(summary.values()), "active": active_count}
