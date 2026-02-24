from __future__ import annotations

from typing import Any, Dict, List

from backend.models.request import InfertilityRequest, PostpartumRequest, PregnancyRequest
from backend.services.model_service import (
    get_artifacts,
    get_postpartum_artifacts,
    get_pregnancy_artifacts,
)
from backend.services.preprocessing_service import (
    BINARY_FIELDS,
    PREGNANCY_BINARY_FIELDS,
    prepare_postpartum_inputs,
    prepare_pregnancy_inputs,
    prepare_v2_inputs,
)


def _risk_level(probability: float, threshold: float) -> str:
    high_cutoff = 0.75
    moderate_cutoff = max(threshold, 0.45)

    if probability >= high_cutoff:
        return "High Risk"
    if probability >= moderate_cutoff:
        return "Moderate Risk"
    return "Low Risk"


def _collect_top_factors(
    payload: Dict[str, Any],
    feature_importance: Dict[str, Dict[str, float]],
    models_used: List[str],
    fusion_weights: Dict[str, float],
    top_n: int = 5,
) -> Dict[str, float]:
    both_used = len(models_used) == 2

    scores: Dict[str, float] = {}
    for model_name in models_used:
        branch_importance = feature_importance.get(model_name, {})
        branch_weight = fusion_weights.get(model_name, 1.0) if both_used else 1.0

        for feature_name, importance in branch_importance.items():
            value = payload.get(feature_name)
            if value is None:
                continue

            if feature_name in BINARY_FIELDS and int(value) != 1:
                continue

            score = branch_weight * float(importance)
            if score <= 0:
                continue

            scores[feature_name] = scores.get(feature_name, 0.0) + score

    if not scores:
        fallback_scores: Dict[str, float] = {}
        for model_name in models_used:
            branch_importance = feature_importance.get(model_name, {})
            branch_weight = fusion_weights.get(model_name, 1.0) if both_used else 1.0
            for feature_name, importance in branch_importance.items():
                fallback_scores[feature_name] = fallback_scores.get(feature_name, 0.0) + (
                    branch_weight * float(importance)
                )
        scores = fallback_scores

    top_items = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_n]
    return {name: round(value, 6) for name, value in top_items}


def _collect_pregnancy_top_factors(
    payload: Dict[str, Any],
    feature_importance: Dict[str, float],
    top_n: int = 5,
) -> Dict[str, float]:
    scores: Dict[str, float] = {}

    for feature_name, importance in feature_importance.items():
        value = payload.get(feature_name)
        if value is None:
            continue

        if feature_name in PREGNANCY_BINARY_FIELDS and int(value) != 1:
            continue

        score = float(importance)
        if score <= 0:
            continue

        scores[feature_name] = score

    if not scores:
        scores = {
            feature_name: float(importance)
            for feature_name, importance in feature_importance.items()
            if float(importance) > 0
        }

    top_items = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_n]
    return {name: round(value, 6) for name, value in top_items}


def _resolve_emergency_threshold(
    decision_threshold: float,
    metadata: Dict[str, Any],
) -> float:
    stored = metadata.get("emergency_threshold")
    if stored is not None:
        return float(stored)

    # Keep emergency triage stricter than referral threshold.
    return float(min(0.99, max(0.90, decision_threshold + 0.10)))


def _resolve_postpartum_emergency_threshold(
    decision_threshold: float,
    metadata: Dict[str, Any],
) -> float:
    stored = metadata.get("emergency_threshold")
    if stored is not None:
        return float(stored)

    return float(min(0.99, max(0.90, decision_threshold + 0.10)))


def _pregnancy_referral_advice(
    probability_high_risk: float,
    decision_threshold: float,
    emergency_threshold: float,
) -> tuple[bool, bool, str, str]:
    if probability_high_risk >= emergency_threshold:
        return (
            True,
            True,
            "Your risk score is at or above the referral threshold. Please visit a hospital or contact a qualified clinician as soon as possible.",
            "Your risk score is at or above the emergency threshold. Seek emergency medical care immediately.",
        )

    if probability_high_risk >= decision_threshold:
        return (
            True,
            False,
            "Your risk score is at or above the referral threshold. Please visit a hospital or contact a qualified clinician as soon as possible.",
            "Your risk score is below the emergency threshold right now, but urgent same-day clinical review is recommended.",
        )

    return (
        False,
        False,
        "Your risk score is below the referral threshold. Continue routine antenatal follow-up and seek care immediately if warning symptoms appear.",
        "Emergency care is not indicated by score threshold at this time. If severe warning symptoms appear, seek emergency care immediately.",
    )


def _postpartum_referral_advice(
    probability_high_risk: float,
    decision_threshold: float,
    emergency_threshold: float,
) -> tuple[bool, bool, str, str]:
    if probability_high_risk >= emergency_threshold:
        return (
            True,
            True,
            "Your postpartum risk score is above the referral threshold. Seek urgent review by a qualified clinician.",
            "Your postpartum risk score is above the emergency threshold. Seek emergency care immediately.",
        )
    if probability_high_risk >= decision_threshold:
        return (
            True,
            False,
            "Your postpartum risk score is above the referral threshold. Please visit a hospital or mental health professional as soon as possible.",
            "Your postpartum risk score is below the emergency threshold right now, but same-day clinical review is recommended.",
        )
    return (
        False,
        False,
        "Your postpartum risk score is below the referral threshold. Continue routine follow-up and monitor warning symptoms.",
        "Emergency care is not indicated by score threshold at this time. Seek emergency care immediately if severe warning symptoms appear.",
    )


def predict_infertility_v2(request: InfertilityRequest) -> Dict[str, Any]:
    artifacts = get_artifacts()
    metadata = artifacts["metadata"]
    feature_schema = artifacts["feature_schema"]

    prepared = prepare_v2_inputs(request, feature_schema)

    thresholds = metadata["thresholds"]
    fusion_weights = metadata["fusion_weights"]
    branch_probs: Dict[str, float] = {}

    if prepared.symptom_df is not None:
        branch_probs["symptom"] = float(
            artifacts["symptom_model"].predict_proba(prepared.symptom_df)[0][1]
        )

    if prepared.history_df is not None:
        branch_probs["history"] = float(
            artifacts["history_model"].predict_proba(prepared.history_df)[0][1]
        )

    if "symptom" in branch_probs and "history" in branch_probs:
        probability_infertile = (
            fusion_weights["symptom"] * branch_probs["symptom"]
            + fusion_weights["history"] * branch_probs["history"]
        )
        decision_threshold = float(thresholds["fused"])
        assessment_mode = "fused"
    elif "symptom" in branch_probs:
        probability_infertile = branch_probs["symptom"]
        decision_threshold = float(thresholds["symptom"])
        assessment_mode = "symptom_only"
    else:
        probability_infertile = branch_probs["history"]
        decision_threshold = float(thresholds["history"])
        assessment_mode = "history_only"

    children_ever_born = prepared.payload["children_ever_born"]

    if children_ever_born == 0:
        probability_primary = probability_infertile
        probability_secondary = 0.0
    else:
        probability_primary = 0.0
        probability_secondary = probability_infertile

    is_infertile = probability_infertile >= decision_threshold

    if not is_infertile:
        predicted_class = "no_infertility_risk"
    elif children_ever_born == 0:
        predicted_class = "primary_infertility_risk"
    else:
        predicted_class = "secondary_infertility_risk"

    top_risk_factors = _collect_top_factors(
        payload=prepared.payload,
        feature_importance=metadata.get("feature_importance", {}),
        models_used=prepared.models_used,
        fusion_weights=fusion_weights,
    )

    return {
        "predicted_class": predicted_class,
        "probability_infertile": round(probability_infertile, 6),
        "probability_primary": round(probability_primary, 6),
        "probability_secondary": round(probability_secondary, 6),
        "risk_level": _risk_level(probability_infertile, decision_threshold),
        "decision_threshold": round(decision_threshold, 6),
        "assessment_mode": assessment_mode,
        "models_used": prepared.models_used,
        "top_risk_factors": top_risk_factors,
        "model_version": metadata.get("model_version", "2.0.0"),
    }


def predict_infertility(request: InfertilityRequest) -> Dict[str, Any]:
    return predict_infertility_v2(request)


def predict_pregnancy(request: PregnancyRequest) -> Dict[str, Any]:
    artifacts = get_pregnancy_artifacts()
    metadata = artifacts["metadata"]
    feature_schema = artifacts["feature_schema"]

    prepared = prepare_pregnancy_inputs(request, feature_schema)

    probability_high_risk = float(
        artifacts["model"].predict_proba(prepared.pregnancy_df)[0][1]
    )
    decision_threshold = float(metadata.get("threshold", 0.5))
    emergency_threshold = _resolve_emergency_threshold(
        decision_threshold=decision_threshold,
        metadata=metadata,
    )
    probability_low_risk = 1.0 - probability_high_risk

    is_high_risk = probability_high_risk >= decision_threshold
    predicted_class = "high_pregnancy_risk" if is_high_risk else "low_pregnancy_risk"
    risk_level = "High Risk" if is_high_risk else "Low Risk"
    (
        advise_hospital_visit,
        advise_emergency_care,
        hospital_advice,
        emergency_advice,
    ) = _pregnancy_referral_advice(
        probability_high_risk=probability_high_risk,
        decision_threshold=decision_threshold,
        emergency_threshold=emergency_threshold,
    )

    top_risk_factors = _collect_pregnancy_top_factors(
        payload=prepared.payload,
        feature_importance=metadata.get("feature_importance", {}),
    )

    return {
        "predicted_class": predicted_class,
        "probability_high_risk": round(probability_high_risk, 6),
        "probability_low_risk": round(probability_low_risk, 6),
        "risk_level": risk_level,
        "decision_threshold": round(decision_threshold, 6),
        "emergency_threshold": round(emergency_threshold, 6),
        "advise_hospital_visit": advise_hospital_visit,
        "advise_emergency_care": advise_emergency_care,
        "hospital_advice": hospital_advice,
        "emergency_advice": emergency_advice,
        "top_risk_factors": top_risk_factors,
        "imputed_fields": prepared.imputed_fields,
        "model_version": metadata.get("model_version", "1.0.0"),
    }


def predict_postpartum(request: PostpartumRequest) -> Dict[str, Any]:
    artifacts = get_postpartum_artifacts()
    metadata = artifacts["metadata"]
    feature_schema = artifacts["feature_schema"]

    prepared = prepare_postpartum_inputs(request, feature_schema)

    probability_high_risk = float(
        artifacts["model"].predict_proba(prepared.postpartum_df)[0][1]
    )
    decision_threshold = float(
        metadata.get("decision_threshold", metadata.get("threshold", 0.5))
    )
    emergency_threshold = _resolve_postpartum_emergency_threshold(
        decision_threshold=decision_threshold,
        metadata=metadata,
    )
    probability_low_risk = 1.0 - probability_high_risk

    is_high_risk = probability_high_risk >= decision_threshold
    predicted_class = "high_postpartum_risk" if is_high_risk else "low_postpartum_risk"
    (
        advise_hospital_visit,
        advise_emergency_care,
        hospital_advice,
        emergency_advice,
    ) = _postpartum_referral_advice(
        probability_high_risk=probability_high_risk,
        decision_threshold=decision_threshold,
        emergency_threshold=emergency_threshold,
    )

    top_risk_factors = _collect_pregnancy_top_factors(
        payload=prepared.payload,
        feature_importance=metadata.get("feature_importance", {}),
        top_n=5,
    )

    return {
        "predicted_class": predicted_class,
        "probability_high_risk": round(probability_high_risk, 6),
        "probability_low_risk": round(probability_low_risk, 6),
        "risk_level": "High Risk" if is_high_risk else "Low Risk",
        "decision_threshold": round(decision_threshold, 6),
        "emergency_threshold": round(emergency_threshold, 6),
        "advise_hospital_visit": advise_hospital_visit,
        "advise_emergency_care": advise_emergency_care,
        "hospital_advice": hospital_advice,
        "emergency_advice": emergency_advice,
        "top_risk_factors": top_risk_factors,
        "imputed_fields": prepared.imputed_fields,
        "model_version": metadata.get("model_version", "1.1.0"),
    }
