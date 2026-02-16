from __future__ import annotations

from typing import Any, Dict

from backend.models.request import InfertilityRequest
from backend.services.model_service import get_artifacts
from backend.services.preprocessing_service import BINARY_FIELDS, prepare_v2_inputs


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
    models_used: list[str],
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
