from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from backend.models.request import InfertilityRequest, PostpartumRequest, PregnancyRequest


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


@dataclass
class PreparedPostpartumInputs:
    payload: Dict[str, Any]
    postpartum_df: pd.DataFrame
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

POSTPARTUM_BINARY_FIELDS = {
    "smoke_cigarettes",
    "smoke_shisha",
    "premature_labour",
    "healthy_baby",
    "baby_admitted_nicu",
    "baby_feeding_difficulties",
    "pregnancy_problem",
    "postnatal_problems",
    "natal_problems",
    "problems_with_husband",
    "financial_problems",
    "family_problems",
    "had_covid_19",
    "had_covid_19_vaccine",
    "access_to_healthcare_services",
    "aware_of_ppd_symptoms",
    "experienced_cultural_stigma_ppd",
    "received_support_or_treatment_ppd",
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


def _normalize_yes_no(value: Any) -> Any:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan

    if isinstance(value, bool):
        return "Yes" if value else "No"

    if isinstance(value, (int, float)):
        return "Yes" if int(value) == 1 else "No"

    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "yes", "y", "true"}:
            return "Yes"
        if lowered in {"0", "no", "n", "false"}:
            return "No"
        return value.strip()

    return value


def _normalize_postpartum_payload(request: PostpartumRequest) -> Dict[str, Any]:
    payload = request.model_dump()
    for field in POSTPARTUM_BINARY_FIELDS:
        payload[field] = _normalize_yes_no(payload.get(field))
    return payload


def prepare_postpartum_inputs(
    request: PostpartumRequest,
    feature_schema: Dict[str, List[str]],
) -> PreparedPostpartumInputs:
    payload = _normalize_postpartum_payload(request)

    feature_map: Dict[str, str] = {
        "age_group": "Age (y)",
        "baby_age_months": "Baby age in months",
        "marital_status": "Marital status",
        "household_income": "What is the household income",
        "level_of_education": "Level of education",
        "residency": "Residency",
        "comorbidities": "comorbidities",
        "smoke_cigarettes": "Smoke cigarattes",
        "smoke_shisha": "Smoke Shish",
        "kgs_gained_during_pregnancy": "Kgs gained during pregnancy",
        "premature_labour": "Premature labour",
        "healthy_baby": "Healty baby",
        "baby_admitted_nicu": "Baby admitted in the NICU",
        "baby_feeding_difficulties": "Baby had feeding difficluties",
        "pregnancy_problem": "Pregnancy problem?",
        "postnatal_problems": "Postnatal problems?",
        "natal_problems": "Natal problems?",
        "problems_with_husband": "problems with husband?",
        "financial_problems": "financial problems?",
        "family_problems": "family problems?",
        "had_covid_19": "got COVID-19?",
        "had_covid_19_vaccine": "got COVID-19 vaccine?",
        "access_to_healthcare_services": "Do you have access to healthcare services",
        "aware_of_ppd_symptoms": "Are you aware of the symptoms and risk factors associated with postpartum depression",
        "experienced_cultural_stigma_ppd": "Have you experienced any cultural stigma or judgment surrounding postpartum depression within your community",
        "received_support_or_treatment_ppd": "Have you received any support or treatment for postpartum depression",
        "epds_laugh_and_funny_side": "I have been able to laugh and see the funny side of things",
        "epds_looked_forward_enjoyment": "I have looked forward with enjoyment to things",
        "epds_blamed_myself": "I have blamed myself unnecessarily when things went wrong",
        "epds_anxious_or_worried": "I have been anxious or worried for no good reason",
        "epds_scared_or_panicky": "I have felt scared or panicky for no very good reason",
        "epds_things_getting_on_top": "Things have been getting on top of me",
        "epds_unhappy_difficulty_sleeping": "I have been so unhappy that I have had difficulty sleeping",
        "epds_sad_or_miserable": "I have felt sad or miserable",
        "epds_unhappy_crying": "I have been so unhappy that I have been crying",
        "epds_thought_of_harming_self": "Thought of harming myself has occurred to me",
    }

    all_features = feature_schema["all_features"]
    row: Dict[str, Any] = {feature: np.nan for feature in all_features}

    imputed_fields: List[str] = []
    for api_name, model_name in feature_map.items():
        if model_name not in row:
            continue
        value = payload.get(api_name)
        if value is None:
            imputed_fields.append(api_name)
            continue
        row[model_name] = value

    postpartum_df = pd.DataFrame([row], columns=all_features)

    return PreparedPostpartumInputs(
        payload=payload,
        postpartum_df=postpartum_df,
        imputed_fields=sorted(set(imputed_fields)),
    )
