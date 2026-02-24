from pydantic import BaseModel, ConfigDict, Field, model_validator


class InfertilityRequest(BaseModel):
    """Request payload for unified infertility fusion endpoint."""

    model_config = ConfigDict(extra="forbid")

    age: int = Field(..., ge=15, le=60, description="Current age in years")
    ever_cohabited: int = Field(
        ...,
        ge=0,
        le=1,
        description="Cohabitation history: 0=Never cohabited, 1=Has cohabited/married",
    )
    children_ever_born: int = Field(
        ..., ge=0, le=20, description="Number of children ever born"
    )

    irregular_menstrual_cycles: int | None = Field(
        default=None, ge=0, le=1, description="0=No, 1=Yes"
    )
    chronic_pelvic_pain: int | None = Field(
        default=None, ge=0, le=1, description="0=No, 1=Yes"
    )
    history_pelvic_infections: int | None = Field(
        default=None, ge=0, le=1, description="0=No, 1=Yes"
    )
    hormonal_symptoms: int | None = Field(
        default=None, ge=0, le=1, description="0=No, 1=Yes"
    )
    early_menopause_symptoms: int | None = Field(
        default=None, ge=0, le=1, description="0=No, 1=Yes"
    )
    autoimmune_history: int | None = Field(
        default=None, ge=0, le=1, description="0=No, 1=Yes"
    )
    reproductive_surgery_history: int | None = Field(
        default=None, ge=0, le=1, description="0=No, 1=Yes"
    )

    bmi: float | None = Field(
        default=None,
        ge=10.0,
        le=8000.0,
        description=(
            "Body Mass Index (kg/m^2). Supports standard BMI (10-80) and legacy DHS "
            "encoding (BMI*100 up to 8000), which is normalized during preprocessing."
        ),
    )
    smoked_last_12mo: int | None = Field(
        default=None, ge=0, le=1, description="0=No, 1=Yes"
    )
    alcohol_last_12mo: int | None = Field(
        default=None, ge=0, le=1, description="0=No, 1=Yes"
    )
    age_at_first_marriage: float | None = Field(
        default=None,
        ge=0,
        le=60,
        description="Age at first marriage/cohabitation",
    )
    months_since_first_cohabitation: float | None = Field(
        default=None,
        ge=0,
        le=720,
        description="Months since first cohabitation",
    )
    months_since_last_sex: float | None = Field(
        default=None,
        ge=0,
        le=2000,
        description="Months since last sexual intercourse",
    )

    @model_validator(mode="after")
    def validate_cohabitation_context(self) -> "InfertilityRequest":
        # For never-cohabited users, allow sentinel values like 0 for cohabitation fields.
        if self.ever_cohabited == 0:
            return self

        # For cohabited users, keep realistic lower bound when provided.
        if self.age_at_first_marriage is not None and self.age_at_first_marriage < 8:
            raise ValueError(
                "age_at_first_marriage must be >= 8 when ever_cohabited is 1."
            )

        return self


class PregnancyRequest(BaseModel):
    """Request payload for pregnancy risk prediction endpoint."""

    model_config = ConfigDict(extra="forbid")

    age: int = Field(..., ge=10, le=65, description="Maternal age in years")
    systolic_bp: float = Field(
        ...,
        ge=70.0,
        le=200.0,
        description="Systolic blood pressure (mmHg)",
    )
    diastolic: float = Field(
        ...,
        ge=40.0,
        le=140.0,
        description="Diastolic blood pressure (mmHg)",
    )

    bs: float | None = Field(
        default=None,
        ge=3.0,
        le=19.0,
        description="Blood sugar level",
    )
    body_temp: float | None = Field(
        default=None,
        ge=95.0,
        le=105.0,
        description="Body temperature in Fahrenheit",
    )
    bmi: float | None = Field(
        default=None,
        ge=0.0,
        le=60.0,
        description="Body Mass Index (kg/m^2). Values <= 0 are treated as missing.",
    )
    previous_complications: int | None = Field(
        default=None,
        ge=0,
        le=1,
        description="History of previous pregnancy complications: 0=No, 1=Yes",
    )
    preexisting_diabetes: int | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Preexisting diabetes before pregnancy: 0=No, 1=Yes",
    )
    gestational_diabetes: int | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Gestational diabetes during current pregnancy: 0=No, 1=Yes",
    )
    mental_health: int | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Mental health risk indicator: 0=No, 1=Yes",
    )
    heart_rate: float | None = Field(
        default=None,
        ge=40.0,
        le=140.0,
        description="Heart rate (beats per minute)",
    )


class PregnancyFollowUpRequest(PregnancyRequest):
    """Pregnancy assessment payload enriched with follow-up metadata."""

    gestational_age_weeks: int | None = Field(
        default=None,
        ge=1,
        le=45,
        description="Current pregnancy week for maternal follow-up tracking",
    )
    visit_label: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        description="Optional user-defined visit label (for example: ANC visit 3)",
    )
    notes: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional follow-up notes for this assessment",
    )
