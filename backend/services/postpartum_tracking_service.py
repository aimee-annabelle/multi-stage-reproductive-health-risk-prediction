from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from backend.db.models import PostpartumAssessment
from backend.models.request import PostpartumRequest

_TOTAL_POSTPARTUM_INPUT_FIELDS = len(PostpartumRequest.model_fields)


def _parse_binary_flag(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, (int, float)) and value in {0, 1}:
        return int(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "yes", "true", "y"}:
            return 1
        if normalized in {"0", "no", "false", "n"}:
            return 0
    return None


def _input_completion_pct(payload: Dict[str, Any]) -> float:
    if _TOTAL_POSTPARTUM_INPUT_FIELDS <= 0:
        return 0.0
    return round((len(payload) / _TOTAL_POSTPARTUM_INPUT_FIELDS) * 100.0, 6)


def create_postpartum_assessment(
    db: Session,
    user_id: int,
    payload: PostpartumRequest,
    prediction: Dict[str, Any],
) -> PostpartumAssessment:
    payload_data = payload.model_dump(exclude_none=True)

    assessment = PostpartumAssessment(
        user_id=user_id,
        input_payload=payload_data,
        age_group=payload_data.get("age_group"),
        baby_age_months=payload_data.get("baby_age_months"),
        kgs_gained_during_pregnancy=payload_data.get("kgs_gained_during_pregnancy"),
        postnatal_problems=_parse_binary_flag(payload_data.get("postnatal_problems")),
        baby_feeding_difficulties=_parse_binary_flag(payload_data.get("baby_feeding_difficulties")),
        financial_problems=_parse_binary_flag(payload_data.get("financial_problems")),
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


def list_postpartum_assessments(
    db: Session,
    user_id: int,
    limit: int = 20,
) -> List[PostpartumAssessment]:
    stmt = (
        select(PostpartumAssessment)
        .where(PostpartumAssessment.user_id == user_id)
        .order_by(desc(PostpartumAssessment.created_at), desc(PostpartumAssessment.id))
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def count_postpartum_assessments(db: Session, user_id: int) -> int:
    stmt = (
        select(func.count())
        .select_from(PostpartumAssessment)
        .where(PostpartumAssessment.user_id == user_id)
    )
    return int(db.execute(stmt).scalar_one())


def build_postpartum_timeline_summary(db: Session, user_id: int, limit: int = 50) -> Dict[str, Any]:
    records_desc = list_postpartum_assessments(db=db, user_id=user_id, limit=limit)
    total_records = count_postpartum_assessments(db=db, user_id=user_id)

    if not records_desc:
        return {
            "total_records": total_records,
            "time_span_days": None,
            "high_risk_count": 0,
            "hospital_referral_count": 0,
            "emergency_referral_count": 0,
            "high_risk_percentage": 0.0,
            "hospital_referral_percentage": 0.0,
            "emergency_referral_percentage": 0.0,
            "average_input_completion": 0.0,
            "latest_input_completion": None,
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
    completion_values = [_input_completion_pct(item.input_payload or {}) for item in records]
    average_completion = (
        round(sum(completion_values) / len(completion_values), 6) if completion_values else 0.0
    )
    latest_completion = completion_values[-1] if completion_values else None

    denominator = len(records) if records else 1
    high_risk_percentage = round((high_risk_count / denominator) * 100.0, 6)
    hospital_referral_percentage = round((hospital_referral_count / denominator) * 100.0, 6)
    emergency_referral_percentage = round((emergency_referral_count / denominator) * 100.0, 6)

    return {
        "total_records": total_records,
        "time_span_days": round(float(time_span_days), 6),
        "high_risk_count": high_risk_count,
        "hospital_referral_count": hospital_referral_count,
        "emergency_referral_count": emergency_referral_count,
        "high_risk_percentage": high_risk_percentage,
        "hospital_referral_percentage": hospital_referral_percentage,
        "emergency_referral_percentage": emergency_referral_percentage,
        "average_input_completion": average_completion,
        "latest_input_completion": latest_completion,
        "earliest_probability_high_risk": float(first.probability_high_risk),
        "latest_probability_high_risk": float(last.probability_high_risk),
        "probability_high_risk_change": round(delta, 6),
        "trend": trend,
        "points": records,
    }
