from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from backend.models.request import InfertilityRequest


@dataclass
class PreparedV2Inputs:
    payload: Dict[str, Any]
    symptom_df: pd.DataFrame | None
    history_df: pd.DataFrame | None
    models_used: List[str]


BINARY_FIELDS = {
    "irregular_menstrual_cycles",
    "chronic_pelvic_pain",
    "history_pelvic_infections",
    "hormonal_symptoms",
    "early_menopause_symptoms",
    "autoimmune_history",
    "reproductive_surgery_history",
    "smoked_last_12mo",
    "alcohol_last_12mo",
}


def _normalize_payload(request: InfertilityRequest) -> Dict[str, Any]:
    payload = request.model_dump()

    # Accept legacy DHS BMI encoding (BMI * 100) when provided.
    if payload.get("bmi") is not None and payload["bmi"] > 100:
        payload["bmi"] = payload["bmi"] / 100.0

    for field in BINARY_FIELDS:
        value = payload.get(field)
        if value is None:
            continue
        if value not in (0, 1):
            raise ValueError(f"Field '{field}' must be 0 or 1 when provided.")

    return payload


def prepare_v2_inputs(
    request: InfertilityRequest,
    feature_schema: Dict[str, List[str]],
) -> PreparedV2Inputs:
    payload = _normalize_payload(request)

    symptom_features = feature_schema["symptom_features"]
    history_features = feature_schema["history_features"]

    symptom_optional = set(feature_schema["symptom_optional_features"])
    symptom_available = any(payload.get(feature) is not None for feature in symptom_optional)

    history_available = payload["ever_cohabited"] == 1

    symptom_df = None
    if symptom_available:
        symptom_row = {feature: payload.get(feature, np.nan) for feature in symptom_features}
        symptom_df = pd.DataFrame([symptom_row], columns=symptom_features)

    history_df = None
    if history_available:
        history_row = {feature: payload.get(feature, np.nan) for feature in history_features}
        history_df = pd.DataFrame([history_row], columns=history_features)

    models_used = []
    if symptom_df is not None:
        models_used.append("symptom")
    if history_df is not None:
        models_used.append("history")

    if not models_used:
        raise ValueError(
            "No model branch can be evaluated with the provided input. "
            "For never-cohabited users, provide at least one symptom field."
        )

    return PreparedV2Inputs(
        payload=payload,
        symptom_df=symptom_df,
        history_df=history_df,
        models_used=models_used,
    )
