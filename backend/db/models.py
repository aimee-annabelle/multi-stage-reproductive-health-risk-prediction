from datetime import datetime, timezone
from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    salt: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    sessions: Mapped[list["AuthSession"]] = relationship(
        "AuthSession", back_populates="user", cascade="all, delete-orphan"
    )
    pregnancy_assessments: Mapped[list["PregnancyAssessment"]] = relationship(
        "PregnancyAssessment", back_populates="user", cascade="all, delete-orphan"
    )
    postpartum_assessments: Mapped[list["PostpartumAssessment"]] = relationship(
        "PostpartumAssessment", back_populates="user", cascade="all, delete-orphan"
    )


class AuthSession(Base):
    __tablename__ = "sessions"

    token: Mapped[str] = mapped_column(String(255), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped[User] = relationship("User", back_populates="sessions")


class PregnancyAssessment(Base):
    __tablename__ = "pregnancy_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    gestational_age_weeks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    visit_label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    age: Mapped[int] = mapped_column(Integer, nullable=False)
    systolic_bp: Mapped[float] = mapped_column(Float, nullable=False)
    diastolic: Mapped[float] = mapped_column(Float, nullable=False)
    bs: Mapped[float | None] = mapped_column(Float, nullable=True)
    body_temp: Mapped[float | None] = mapped_column(Float, nullable=True)
    bmi: Mapped[float | None] = mapped_column(Float, nullable=True)
    previous_complications: Mapped[int | None] = mapped_column(Integer, nullable=True)
    preexisting_diabetes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gestational_diabetes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mental_health: Mapped[int | None] = mapped_column(Integer, nullable=True)
    heart_rate: Mapped[float | None] = mapped_column(Float, nullable=True)

    predicted_class: Mapped[str] = mapped_column(String(64), nullable=False)
    probability_high_risk: Mapped[float] = mapped_column(Float, nullable=False)
    probability_low_risk: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False)
    decision_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    emergency_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    advise_hospital_visit: Mapped[bool] = mapped_column(Boolean, nullable=False)
    advise_emergency_care: Mapped[bool] = mapped_column(Boolean, nullable=False)
    hospital_advice: Mapped[str] = mapped_column(Text, nullable=False)
    emergency_advice: Mapped[str] = mapped_column(Text, nullable=False)
    top_risk_factors: Mapped[dict] = mapped_column(JSON, nullable=False)
    imputed_fields: Mapped[list] = mapped_column(JSON, nullable=False)
    model_version: Mapped[str] = mapped_column(String(32), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    user: Mapped[User] = relationship("User", back_populates="pregnancy_assessments")


class PostpartumAssessment(Base):
    __tablename__ = "postpartum_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    input_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    age_group: Mapped[str | None] = mapped_column(String(40), nullable=True)
    baby_age_months: Mapped[float | None] = mapped_column(Float, nullable=True)
    kgs_gained_during_pregnancy: Mapped[float | None] = mapped_column(Float, nullable=True)
    postnatal_problems: Mapped[int | None] = mapped_column(Integer, nullable=True)
    baby_feeding_difficulties: Mapped[int | None] = mapped_column(Integer, nullable=True)
    financial_problems: Mapped[int | None] = mapped_column(Integer, nullable=True)

    predicted_class: Mapped[str] = mapped_column(String(64), nullable=False)
    probability_high_risk: Mapped[float] = mapped_column(Float, nullable=False)
    probability_low_risk: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False)
    decision_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    emergency_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    advise_hospital_visit: Mapped[bool] = mapped_column(Boolean, nullable=False)
    advise_emergency_care: Mapped[bool] = mapped_column(Boolean, nullable=False)
    hospital_advice: Mapped[str] = mapped_column(Text, nullable=False)
    emergency_advice: Mapped[str] = mapped_column(Text, nullable=False)
    top_risk_factors: Mapped[dict] = mapped_column(JSON, nullable=False)
    imputed_fields: Mapped[list] = mapped_column(JSON, nullable=False)
    model_version: Mapped[str] = mapped_column(String(32), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    user: Mapped[User] = relationship("User", back_populates="postpartum_assessments")
