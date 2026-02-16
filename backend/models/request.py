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
        le=80.0,
        description="Body Mass Index (kg/m^2). If DHS format (BMI*100) is provided, it is normalized.",
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
