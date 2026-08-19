"""Pydantic response models and shared exception types."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ValidationError(Exception):
    """Raised by validation_service when uploaded data fails the contract."""

    def __init__(self, issues: List[str]):
        self.issues = issues
        super().__init__("; ".join(issues))


class AnalogSelectionItem(BaseModel):
    drug_id: str
    drug_name: Optional[str] = None
    similarity_score: float
    weight: float
    rank: int


class BassParams(BaseModel):
    scenario: str
    p: float = Field(..., description="Bass coefficient of innovation")
    q: float = Field(..., description="Bass coefficient of imitation")
    m: float = Field(..., description="Estimated market potential / ceiling (patients)")


class ScenarioForecast(BaseModel):
    scenario: str
    monthly_forecast: List[float]
    cumulative_forecast: List[float]


class ForecastRunResponse(BaseModel):
    run_id: str
    new_drug_id: str
    forecast_horizon_months: int
    top_k: int
    known_monthly_rx: List[float] = []
    selected_analogs: List[AnalogSelectionItem]
    blended_analog_curve: List[float]
    bass_parameters: List[BassParams]
    scenarios: List[ScenarioForecast]
    scenario_assumptions_used: Dict[str, Dict[str, float]]
    output_files: Dict[str, str]
    warnings: List[str] = []
