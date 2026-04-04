"""
Pydantic schemas for Health Index configuration (thresholds & weights).
"""

from pydantic import BaseModel, Field


class ParameterRange(BaseModel):
    normal_range: list[float] = Field(..., min_length=2, max_length=2)
    warning_range: list[float] = Field(..., min_length=2, max_length=2)
    critical_range: list[float] = Field(..., min_length=2, max_length=2)


class ParameterConfig(BaseModel):
    weight: float = Field(..., ge=0, le=1)
    unit: str = ""
    label: str = ""
    normal_range: list[float]
    warning_range: list[float]
    critical_range: list[float]


class AlertPenalties(BaseModel):
    warning: float = 5.0
    critical: float = 15.0


class CategoryRange(BaseModel):
    min_value: float
    max_value: float
    label: str


class HealthConfigResponse(BaseModel):
    parameters: dict[str, ParameterConfig]
    alert_penalty: AlertPenalties
    categories: dict[str, CategoryRange]


class ThresholdUpdate(BaseModel):
    parameter: str
    normal_range: list[float] | None = None
    warning_range: list[float] | None = None
    critical_range: list[float] | None = None


class WeightUpdate(BaseModel):
    parameter: str
    weight: float = Field(..., ge=0, le=1)
