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


class PostpartumRequest(BaseModel):
    """Request payload for postpartum risk prediction endpoint."""

    model_config = ConfigDict(extra="forbid")

    age_group: str | None = Field(
        default=None,
        description="Age group used by training data (for example: Below 25, Above 25)",
    )
    baby_age_months: float | None = Field(
        default=None, ge=0.0, le=24.0, description="Infant age in months"
    )
    kgs_gained_during_pregnancy: float | None = Field(
        default=None, ge=0.0, le=50.0, description="Weight gained during pregnancy (kg)"
    )
    marital_status: str | None = None
    household_income: str | None = None
    level_of_education: str | None = None
    residency: str | None = None
    comorbidities: str | None = None

    smoke_cigarettes: int | str | bool | None = Field(default=None)
    smoke_shisha: int | str | bool | None = Field(default=None)
    premature_labour: int | str | bool | None = Field(default=None)
    healthy_baby: int | str | bool | None = Field(default=None)
    baby_admitted_nicu: int | str | bool | None = Field(default=None)
    baby_feeding_difficulties: int | str | bool | None = Field(default=None)
    pregnancy_problem: int | str | bool | None = Field(default=None)
    postnatal_problems: int | str | bool | None = Field(default=None)
    natal_problems: int | str | bool | None = Field(default=None)
    problems_with_husband: int | str | bool | None = Field(default=None)
    financial_problems: int | str | bool | None = Field(default=None)
    family_problems: int | str | bool | None = Field(default=None)
    had_covid_19: int | str | bool | None = Field(default=None)
    had_covid_19_vaccine: int | str | bool | None = Field(default=None)
    access_to_healthcare_services: int | str | bool | None = Field(default=None)
    aware_of_ppd_symptoms: int | str | bool | None = Field(default=None)
    experienced_cultural_stigma_ppd: int | str | bool | None = Field(default=None)
    received_support_or_treatment_ppd: int | str | bool | None = Field(default=None)

    epds_laugh_and_funny_side: str | None = None
    epds_looked_forward_enjoyment: str | None = None
    epds_blamed_myself: str | None = None
    epds_anxious_or_worried: str | None = None
    epds_scared_or_panicky: str | None = None
    epds_things_getting_on_top: str | None = None
    epds_unhappy_difficulty_sleeping: str | None = None
    epds_sad_or_miserable: str | None = None
    epds_unhappy_crying: str | None = None
    epds_thought_of_harming_self: str | None = None

    @model_validator(mode="after")
    def validate_minimum_signal(self) -> "PostpartumRequest":
        payload = self.model_dump()
        has_signal = any(value is not None for value in payload.values())
        if not has_signal:
            raise ValueError("Provide at least one postpartum symptom, habit, or context field.")
        return self
