from typing import Dict, List, Literal

from pydantic import BaseModel, ConfigDict, Field


class InfertilityResponse(BaseModel):
    """Response payload for unified infertility fusion endpoint."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    predicted_class: Literal[
        "no_infertility_risk",
        "primary_infertility_risk",
        "secondary_infertility_risk",
    ] = Field(..., description="Final infertility risk class")
    probability_infertile: float = Field(..., ge=0.0, le=1.0)
    probability_primary: float = Field(..., ge=0.0, le=1.0)
    probability_secondary: float = Field(..., ge=0.0, le=1.0)
    risk_level: str = Field(..., description="Low Risk, Moderate Risk, or High Risk")
    decision_threshold: float = Field(..., ge=0.0, le=1.0)
    assessment_mode: Literal["symptom_only", "history_only", "fused"] = Field(
        ..., description="Prediction path selected from available inputs"
    )
    models_used: List[str] = Field(..., description="Model branches used for this prediction")
    top_risk_factors: Dict[str, float] = Field(
        ..., description="Top contributing input factors"
    )
    model_version: str = Field(..., description="Model artifact version")
