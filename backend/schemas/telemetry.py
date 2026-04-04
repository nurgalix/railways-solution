"""
Pydantic schemas for telemetry data transfer.
"""

from datetime import datetime
from pydantic import BaseModel, Field


# ── Position ──────────────────────────────────────────────────


class PositionData(BaseModel):
    lat: float = 0.0
    lng: float = 0.0
    km_marker: float = 0.0


# ── Single telemetry frame ───────────────────────────────────


class TelemetryData(BaseModel):
    speed: float = Field(0.0, ge=0, description="km/h")
    fuel_level: float = Field(100.0, ge=0, le=100, description="% remaining")
    pressure: float = Field(4.0, ge=0, description="bar")
    temperature: float = Field(80.0, description="C")
    position: PositionData = Field(default_factory=PositionData)


# ── Health Index ──────────────────────────────────────────────


class HealthFactor(BaseModel):
    parameter: str
    score: float = Field(..., ge=0, le=100, description="Parameter health score 0-100")
    weight: float
    impact: float = Field(..., description="Negative impact on overall index")
    status: str  # normal / warning / critical


class HealthIndexResponse(BaseModel):
    index: float = Field(..., ge=0, le=100)
    category: str = Field(..., pattern=r"^[A-E]$")
    label: str  # Normal, Attention, Warning, Critical, Emergency
    top_factors: list[HealthFactor] = []


# ── Alert ─────────────────────────────────────────────────────


class AlertData(BaseModel):
    id: int | None = None
    severity: str  # info / warning / critical
    code: str
    message: str
    parameter: str | None = None
    value: float | None = None
    threshold: float | None = None
    recommendation: str | None = None
    acknowledged: bool = False
    timestamp: datetime | None = None


# ── Full WebSocket frame ─────────────────────────────────────


class TelemetryFrame(BaseModel):
    """Complete frame sent over WebSocket."""
    type: str = "telemetry"
    timestamp: datetime
    locomotive_id: str
    data: TelemetryData
    health: HealthIndexResponse
    alerts: list[AlertData] = []


# ── History / Replay ──────────────────────────────────────────


class TelemetryHistoryItem(BaseModel):
    timestamp: datetime
    speed: float
    fuel_level: float
    pressure: float
    temperature: float
    health_index: float | None = None
    health_category: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    km_marker: float | None = None


class TelemetryHistoryResponse(BaseModel):
    items: list[TelemetryHistoryItem]
    total: int
    start: datetime
    end: datetime


class ReplayRequest(BaseModel):
    start: datetime
    end: datetime
    speed_multiplier: float = Field(1.0, ge=0.1, le=10.0)
