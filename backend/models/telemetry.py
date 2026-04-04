"""
ORM models for telemetry readings and alert events.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from database.engine import Base


class TelemetryReading(Base):
    """Single telemetry snapshot persisted for historical queries."""
    __tablename__ = "telemetry_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True,
        server_default=func.now(),
    )
    locomotive_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    # ── Motion ────────────────────────────────────────────────
    speed: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # ── Fuel / Energy ─────────────────────────────────────────
    fuel_level: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    fuel_consumption: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # ── Pressures ─────────────────────────────────────────────
    oil_pressure: Mapped[float] = mapped_column(Float, nullable=False, default=4.0)
    brake_pressure: Mapped[float] = mapped_column(Float, nullable=False, default=6.0)

    # ── Temperatures ──────────────────────────────────────────
    coolant_temp: Mapped[float] = mapped_column(Float, nullable=False, default=80.0)
    exhaust_temp: Mapped[float] = mapped_column(Float, nullable=False, default=350.0)
    bearing_temp: Mapped[float] = mapped_column(Float, nullable=False, default=55.0)

    # ── Electrical ────────────────────────────────────────────
    voltage: Mapped[float] = mapped_column(Float, nullable=False, default=3000.0)
    current: Mapped[float] = mapped_column(Float, nullable=False, default=800.0)
    power: Mapped[float] = mapped_column(Float, nullable=False, default=2400.0)

    # ── Position ──────────────────────────────────────────────
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    km_marker: Mapped[float] = mapped_column(Float, nullable=True)

    # ── Health ────────────────────────────────────────────────
    health_index: Mapped[float] = mapped_column(Float, nullable=True)
    health_category: Mapped[str] = mapped_column(String(1), nullable=True)  # A-E

    # ── Raw JSON (full frame) ─────────────────────────────────
    raw_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_telemetry_loco_ts", "locomotive_id", "timestamp"),
    )


class AlertEvent(Base):
    """Individual alert generated when a parameter breaches a threshold."""
    __tablename__ = "alert_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), index=True,
    )
    locomotive_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    severity: Mapped[str] = mapped_column(
        String(16), nullable=False,
    )  # info / warning / critical
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    parameter: Mapped[str] = mapped_column(String(32), nullable=True)
    value: Mapped[float] = mapped_column(Float, nullable=True)
    threshold: Mapped[float] = mapped_column(Float, nullable=True)
    recommendation: Mapped[str] = mapped_column(Text, nullable=True)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("ix_alert_loco_ts", "locomotive_id", "timestamp"),
    )
