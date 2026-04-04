"""
Data retention service: periodically purges telemetry and alert records
older than the configured retention window (default 72 hours).
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from database.engine import async_session_factory
from models.telemetry import TelemetryReading, AlertEvent

logger = logging.getLogger(__name__)

DEFAULT_RETENTION_HOURS = 72
CLEANUP_INTERVAL_SECONDS = 3600  # Run every hour


class DataRetentionService:
    """Background task that purges expired data."""

    def __init__(self, retention_hours: int = DEFAULT_RETENTION_HOURS):
        self.retention_hours = retention_hours
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._cleanup_loop())
        logger.info(
            "Data retention service started (keep last %d hours)",
            self.retention_hours,
        )

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _cleanup_loop(self) -> None:
        while self._running:
            try:
                await self._purge_old_data()
            except Exception:
                logger.exception("Data retention cleanup failed")
            await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)

    async def _purge_old_data(self) -> None:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.retention_hours)

        async with async_session_factory() as session:
            # Purge old telemetry readings
            result_tel = await session.execute(
                delete(TelemetryReading).where(
                    TelemetryReading.timestamp < cutoff
                )
            )
            # Purge old acknowledged alerts
            result_alert = await session.execute(
                delete(AlertEvent).where(
                    AlertEvent.timestamp < cutoff,
                    AlertEvent.acknowledged == True,
                )
            )
            await session.commit()

            tel_count = result_tel.rowcount or 0
            alert_count = result_alert.rowcount or 0

            if tel_count > 0 or alert_count > 0:
                logger.info(
                    "Retention cleanup: removed %d telemetry, %d alerts (older than %s)",
                    tel_count, alert_count, cutoff.isoformat(),
                )


# ── Singleton ─────────────────────────────────────────────────

_retention_service: DataRetentionService | None = None


def get_retention_service() -> DataRetentionService:
    global _retention_service
    if _retention_service is None:
        _retention_service = DataRetentionService()
    return _retention_service
