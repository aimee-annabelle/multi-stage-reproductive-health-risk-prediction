from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from backend.db.models import PregnancyAssessment
from backend.models.request import PregnancyFollowUpRequest


_COMPARABLE_METRICS = [
    "gestational_age_weeks",
    "systolic_bp",
    "diastolic",
    "bs",
    "body_temp",
    "bmi",
    "heart_rate",
]


def create_pregnancy_assessment(
    db: Session,
    user_id: int,
    payload: PregnancyFollowUpRequest,
    prediction: Dict,
) -> PregnancyAssessment:
    data = payload.model_dump()
    assessment = PregnancyAssessment(
        user_id=user_id,
        gestational_age_weeks=data.get("gestational_age_weeks"),
        visit_label=data.get("visit_label"),
        notes=data.get("notes"),
        age=data["age"],
        systolic_bp=data["systolic_bp"],
        diastolic=data["diastolic"],
        bs=data.get("bs"),
        body_temp=data.get("body_temp"),
        bmi=data.get("bmi"),
        previous_complications=data.get("previous_complications"),
        preexisting_diabetes=data.get("preexisting_diabetes"),
        gestational_diabetes=data.get("gestational_diabetes"),
        mental_health=data.get("mental_health"),
        heart_rate=data.get("heart_rate"),
        predicted_class=prediction["predicted_class"],
        probability_high_risk=prediction["probability_high_risk"],
        probability_low_risk=prediction["probability_low_risk"],
        risk_level=prediction["risk_level"],
        decision_threshold=prediction["decision_threshold"],
        emergency_threshold=prediction["emergency_threshold"],
        advise_hospital_visit=prediction["advise_hospital_visit"],
        advise_emergency_care=prediction["advise_emergency_care"],
        hospital_advice=prediction["hospital_advice"],
        emergency_advice=prediction["emergency_advice"],
        top_risk_factors=prediction["top_risk_factors"],
        imputed_fields=prediction["imputed_fields"],
        model_version=prediction["model_version"],
        created_at=datetime.now(timezone.utc),
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def list_pregnancy_assessments(
    db: Session,
    user_id: int,
    limit: int = 20,
) -> List[PregnancyAssessment]:
    stmt = (
        select(PregnancyAssessment)
        .where(PregnancyAssessment.user_id == user_id)
        .order_by(desc(PregnancyAssessment.created_at), desc(PregnancyAssessment.id))
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def count_pregnancy_assessments(db: Session, user_id: int) -> int:
    stmt = (
        select(func.count())
        .select_from(PregnancyAssessment)
        .where(PregnancyAssessment.user_id == user_id)
    )
    return int(db.execute(stmt).scalar_one())


def compare_latest_assessments(db: Session, user_id: int) -> Dict:
    records = list_pregnancy_assessments(db=db, user_id=user_id, limit=2)
    if len(records) < 2:
        raise ValueError(
            "At least two stored assessments are required to compute a comparison."
        )

    latest, previous = records[0], records[1]

    probability_delta = float(latest.probability_high_risk - previous.probability_high_risk)
    epsilon = 1e-9
    if probability_delta > epsilon:
        trend = "increased"
    elif probability_delta < -epsilon:
        trend = "decreased"
    else:
        trend = "stable"

    metric_deltas: Dict[str, float] = {}
    for metric in _COMPARABLE_METRICS:
        latest_value = getattr(latest, metric)
        previous_value = getattr(previous, metric)
        if latest_value is None or previous_value is None:
            continue
        metric_deltas[metric] = round(float(latest_value) - float(previous_value), 6)

    return {
        "latest": latest,
        "previous": previous,
        "probability_high_risk_delta": round(probability_delta, 6),
        "trend": trend,
        "metric_deltas": metric_deltas,
    }


def build_timeline_summary(db: Session, user_id: int, limit: int = 50) -> Dict:
    records_desc = list_pregnancy_assessments(db=db, user_id=user_id, limit=limit)
    total_records = count_pregnancy_assessments(db=db, user_id=user_id)

    if not records_desc:
        return {
            "total_records": total_records,
            "time_span_days": None,
            "high_risk_count": 0,
            "hospital_referral_count": 0,
            "emergency_referral_count": 0,
            "earliest_probability_high_risk": None,
            "latest_probability_high_risk": None,
            "probability_high_risk_change": None,
            "trend": None,
            "points": [],
        }

    records = list(reversed(records_desc))
    first = records[0]
    last = records[-1]

    delta = float(last.probability_high_risk - first.probability_high_risk)
    epsilon = 1e-9
    if delta > epsilon:
        trend = "increased"
    elif delta < -epsilon:
        trend = "decreased"
    else:
        trend = "stable"

    time_span_days = (
        (last.created_at - first.created_at).total_seconds() / 86400.0
        if len(records) > 1
        else 0.0
    )

    high_risk_count = sum(1 for item in records if item.risk_level == "High Risk")
    hospital_referral_count = sum(1 for item in records if item.advise_hospital_visit)
    emergency_referral_count = sum(1 for item in records if item.advise_emergency_care)

    return {
        "total_records": total_records,
        "time_span_days": round(float(time_span_days), 6),
        "high_risk_count": high_risk_count,
        "hospital_referral_count": hospital_referral_count,
        "emergency_referral_count": emergency_referral_count,
        "earliest_probability_high_risk": float(first.probability_high_risk),
        "latest_probability_high_risk": float(last.probability_high_risk),
        "probability_high_risk_change": round(delta, 6),
        "trend": trend,
        "points": records,
    }
