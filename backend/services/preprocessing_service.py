from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from backend.models.request import InfertilityRequest, PregnancyRequest


@dataclass
class PreparedV2Inputs:
    payload: Dict[str, Any]
    symptom_df: pd.DataFrame | None
    history_df: pd.DataFrame | None
    models_used: List[str]


@dataclass
class PreparedPregnancyInputs:
    payload: Dict[str, Any]
    pregnancy_df: pd.DataFrame
    imputed_fields: List[str]


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

PREGNANCY_BINARY_FIELDS = {
    "previous_complications",
    "preexisting_diabetes",
    "gestational_diabetes",
    "mental_health",
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


def _normalize_pregnancy_payload(request: PregnancyRequest) -> Dict[str, Any]:
    """
    Normalize and validate pregnancy request payload.

    BMI values less than or equal to zero are not physiologically valid and are
    treated as missing data. They are converted to None here so that downstream
    preprocessing/imputation can handle them in a consistent way.
    """
    payload = request.model_dump()

    # Treat non-positive BMI values as missing so they are handled by imputation.
    if payload.get("bmi") is not None and payload["bmi"] <= 0:
        payload["bmi"] = None

    for field in PREGNANCY_BINARY_FIELDS:
        value = payload.get(field)
        if value is None:
            continue
        if value not in (0, 1):
            raise ValueError(f"Field '{field}' must be 0 or 1 when provided.")

    return payload


def prepare_pregnancy_inputs(
    request: PregnancyRequest,
    feature_schema: Dict[str, List[str]],
) -> PreparedPregnancyInputs:
    payload = _normalize_pregnancy_payload(request)

    all_features = feature_schema["all_features"]
    optional_features = feature_schema["optional_features"]

    pregnancy_row = {feature: payload.get(feature, np.nan) for feature in all_features}
    pregnancy_df = pd.DataFrame([pregnancy_row], columns=all_features)

    imputed_fields = [feature for feature in optional_features if payload.get(feature) is None]

    return PreparedPregnancyInputs(
        payload=payload,
        pregnancy_df=pregnancy_df,
        imputed_fields=imputed_fields,
    )
