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


class PregnancyResponse(BaseModel):
    """Response payload for pregnancy risk prediction endpoint."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    predicted_class: Literal["low_pregnancy_risk", "high_pregnancy_risk"] = Field(
        ..., description="Final pregnancy risk class"
    )
    probability_high_risk: float = Field(..., ge=0.0, le=1.0)
    probability_low_risk: float = Field(..., ge=0.0, le=1.0)
    risk_level: Literal["Low Risk", "High Risk"] = Field(
        ..., description="Pregnancy risk label"
    )
    decision_threshold: float = Field(..., ge=0.0, le=1.0)
    emergency_threshold: float = Field(
        ..., ge=0.0, le=1.0, description="Stricter threshold for emergency-care escalation"
    )
    advise_hospital_visit: bool = Field(
        ..., description="True when predicted high-risk probability meets referral threshold"
    )
    advise_emergency_care: bool = Field(
        ..., description="True when predicted high-risk probability meets emergency threshold"
    )
    hospital_advice: str = Field(
        ..., description="Threshold-based recommendation for whether to seek hospital care"
    )
    emergency_advice: str = Field(
        ..., description="Threshold-based recommendation for emergency-care escalation"
    )
    top_risk_factors: Dict[str, float] = Field(
        ..., description="Top contributing input factors"
    )
    imputed_fields: List[str] = Field(
        ..., description="Optional fields imputed by model preprocessing"
    )
    model_version: str = Field(..., description="Model artifact version")


class PostpartumResponse(BaseModel):
    """Response payload for postpartum risk prediction endpoint."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    predicted_class: Literal["low_postpartum_risk", "high_postpartum_risk"] = Field(
        ..., description="Final postpartum risk class"
    )
    probability_high_risk: float = Field(..., ge=0.0, le=1.0)
    probability_low_risk: float = Field(..., ge=0.0, le=1.0)
    risk_level: Literal["Low Risk", "High Risk"] = Field(
        ..., description="Postpartum risk label"
    )
    severity_level: Literal["Low Risk", "Medium Risk", "High Risk"] = Field(
        ...,
        description="Backend-derived severity tier from probability thresholds",
    )
    model_classification: Literal["binary_2_class"] = Field(
        ...,
        description="Underlying model class structure",
    )
    classification_note: str = Field(
        ...,
        description="Clarifies binary model classes vs backend severity tiers",
    )
    decision_threshold: float = Field(..., ge=0.0, le=1.0)
    emergency_threshold: float = Field(..., ge=0.0, le=1.0)
    advise_hospital_visit: bool
    advise_emergency_care: bool
    hospital_advice: str
    emergency_advice: str
    top_risk_factors: Dict[str, float] = Field(
        ..., description="Top contributing input factors"
    )
    imputed_fields: List[str] = Field(
        ..., description="Fields not provided and imputed by model preprocessing"
    )
    model_version: str = Field(..., description="Model artifact version")


class PostpartumAssessmentRecordResponse(BaseModel):
    """Stored postpartum assessment record tied to an authenticated user."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    assessment_id: int
    created_at: str
    input_payload: Dict[str, object]

    age_group: str | None
    baby_age_months: float | None
    kgs_gained_during_pregnancy: float | None
    postnatal_problems: int | None
    baby_feeding_difficulties: int | None
    financial_problems: int | None

    predicted_class: Literal["low_postpartum_risk", "high_postpartum_risk"]
    probability_high_risk: float = Field(..., ge=0.0, le=1.0)
    probability_low_risk: float = Field(..., ge=0.0, le=1.0)
    risk_level: Literal["Low Risk", "High Risk"]
    severity_level: Literal["Low Risk", "Medium Risk", "High Risk"]
    model_classification: Literal["binary_2_class"]
    classification_note: str
    decision_threshold: float = Field(..., ge=0.0, le=1.0)
    emergency_threshold: float = Field(..., ge=0.0, le=1.0)
    advise_hospital_visit: bool
    advise_emergency_care: bool
    hospital_advice: str
    emergency_advice: str
    top_risk_factors: Dict[str, float]
    imputed_fields: List[str]
    model_version: str
    input_completion_pct: float = Field(..., ge=0.0, le=100.0)


class PostpartumAssessmentHistoryResponse(BaseModel):
    """Paginated postpartum follow-up history for a user."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    total_records: int
    assessments: List[PostpartumAssessmentRecordResponse]


class PostpartumTimelinePointResponse(BaseModel):
    """Single chronological point for postpartum follow-up timeline visualizations."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    assessment_id: int
    created_at: str
    probability_high_risk: float = Field(..., ge=0.0, le=1.0)
    probability_low_risk: float = Field(..., ge=0.0, le=1.0)
    risk_level: Literal["Low Risk", "High Risk"]
    severity_level: Literal["Low Risk", "Medium Risk", "High Risk"]
    model_classification: Literal["binary_2_class"]
    classification_note: str
    advise_hospital_visit: bool
    advise_emergency_care: bool
    baby_age_months: float | None
    postnatal_problems: int | None
    baby_feeding_difficulties: int | None
    financial_problems: int | None
    input_completion_pct: float = Field(..., ge=0.0, le=100.0)


class PostpartumTimelineSummaryResponse(BaseModel):
    """Aggregated timeline summary for postpartum follow-up tracking."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    total_records: int
    time_span_days: float | None
    high_risk_count: int
    hospital_referral_count: int
    emergency_referral_count: int
    high_risk_percentage: float = Field(..., ge=0.0, le=100.0)
    hospital_referral_percentage: float = Field(..., ge=0.0, le=100.0)
    emergency_referral_percentage: float = Field(..., ge=0.0, le=100.0)
    average_input_completion: float = Field(..., ge=0.0, le=100.0)
    latest_input_completion: float | None = Field(default=None, ge=0.0, le=100.0)
    earliest_probability_high_risk: float | None = Field(default=None, ge=0.0, le=1.0)
    latest_probability_high_risk: float | None = Field(default=None, ge=0.0, le=1.0)
    probability_high_risk_change: float | None
    trend: Literal["increased", "decreased", "stable"] | None
    points: List[PostpartumTimelinePointResponse]


class PregnancyAssessmentRecordResponse(BaseModel):
    """Stored pregnancy assessment record tied to an authenticated user."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    assessment_id: int
    created_at: str
    gestational_age_weeks: int | None
    visit_label: str | None
    notes: str | None

    age: int
    systolic_bp: float
    diastolic: float
    bs: float | None
    body_temp: float | None
    bmi: float | None
    previous_complications: int | None
    preexisting_diabetes: int | None
    gestational_diabetes: int | None
    mental_health: int | None
    heart_rate: float | None

    predicted_class: Literal["low_pregnancy_risk", "high_pregnancy_risk"]
    probability_high_risk: float = Field(..., ge=0.0, le=1.0)
    probability_low_risk: float = Field(..., ge=0.0, le=1.0)
    risk_level: Literal["Low Risk", "High Risk"]
    decision_threshold: float = Field(..., ge=0.0, le=1.0)
    emergency_threshold: float = Field(..., ge=0.0, le=1.0)
    advise_hospital_visit: bool
    advise_emergency_care: bool
    hospital_advice: str
    emergency_advice: str
    top_risk_factors: Dict[str, float]
    imputed_fields: List[str]
    model_version: str


class PregnancyAssessmentHistoryResponse(BaseModel):
    """Paginated pregnancy follow-up history for a user."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    total_records: int
    assessments: List[PregnancyAssessmentRecordResponse]


class PregnancyAssessmentComparisonResponse(BaseModel):
    """Comparison between latest and previous pregnancy assessments."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    latest_assessment_id: int
    previous_assessment_id: int
    latest_created_at: str
    previous_created_at: str
    latest_probability_high_risk: float = Field(..., ge=0.0, le=1.0)
    previous_probability_high_risk: float = Field(..., ge=0.0, le=1.0)
    probability_high_risk_delta: float
    trend: Literal["increased", "decreased", "stable"]
    metric_deltas: Dict[str, float]


class PregnancyTimelinePointResponse(BaseModel):
    """Single chronological point for pregnancy follow-up timeline visualizations."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    assessment_id: int
    created_at: str
    gestational_age_weeks: int | None
    visit_label: str | None
    probability_high_risk: float = Field(..., ge=0.0, le=1.0)
    probability_low_risk: float = Field(..., ge=0.0, le=1.0)
    risk_level: Literal["Low Risk", "High Risk"]
    advise_hospital_visit: bool
    advise_emergency_care: bool
    systolic_bp: float
    diastolic: float
    bs: float | None
    bmi: float | None
    heart_rate: float | None


class PregnancyTimelineSummaryResponse(BaseModel):
    """Aggregated timeline summary for pregnancy follow-up tracking."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    total_records: int
    time_span_days: float | None
    high_risk_count: int
    hospital_referral_count: int
    emergency_referral_count: int
    earliest_probability_high_risk: float | None = Field(default=None, ge=0.0, le=1.0)
    latest_probability_high_risk: float | None = Field(default=None, ge=0.0, le=1.0)
    probability_high_risk_change: float | None
    trend: Literal["increased", "decreased", "stable"] | None
    points: List[PregnancyTimelinePointResponse]
