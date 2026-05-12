from typing import Any, Optional

from pydantic import BaseModel, Field


class AIQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=8000)
    dataset_id: Optional[int] = None


class AIQueryResponse(BaseModel):
    answer: str
    model: str


class AutoEDARequest(BaseModel):
    dataset_id: int


class AutoEDAResponse(BaseModel):
    summary: str
    column_stats: list[dict[str, Any]] = []
    correlations: list[dict[str, Any]] = []
    warnings: list[str] = []


class SuggestChartRequest(BaseModel):
    dataset_id: int
    question: Optional[str] = None


class SuggestChartResponse(BaseModel):
    suggestions: list[dict[str, Any]] = []


class DetectAnomalyRequest(BaseModel):
    dataset_id: int
    column: str = Field(..., min_length=1)


class DetectAnomalyResponse(BaseModel):
    column: str
    anomalies: list[dict[str, Any]] = []
    summary: str = ""


class ForecastRequest(BaseModel):
    dataset_id: int
    date_column: str = Field(..., min_length=1)
    value_column: str = Field(..., min_length=1)
    periods: int = Field(default=10, ge=1, le=100)


class ForecastResponse(BaseModel):
    forecast: list[dict[str, Any]] = []
    model: str = ""
