from __future__ import annotations

from backend.models.request import InfertilityRequest, PregnancyRequest
from backend.services.model_service import (
    get_model_info,
    get_pregnancy_model_info,
    load_artifacts,
    load_pregnancy_artifacts,
)
from backend.services.prediction_service import predict_infertility, predict_pregnancy
from backend.services.preprocessing_service import prepare_pregnancy_inputs


def test_predict_with_full_payload() -> None:
    load_artifacts(force_reload=True)

    payload = InfertilityRequest(
        age=32,
        ever_cohabited=1,
        children_ever_born=0,
        irregular_menstrual_cycles=1,
        chronic_pelvic_pain=1,
        history_pelvic_infections=0,
        hormonal_symptoms=1,
        early_menopause_symptoms=0,
        autoimmune_history=0,
        reproductive_surgery_history=0,
        bmi=24.8,
        smoked_last_12mo=0,
        alcohol_last_12mo=0,
        age_at_first_marriage=23,
        months_since_first_cohabitation=84,
        months_since_last_sex=1,
    )

    result = predict_infertility(payload)

    assert result["predicted_class"] in {
        "no_infertility_risk",
        "primary_infertility_risk",
        "secondary_infertility_risk",
    }
    assert set(result["models_used"]) == {"symptom", "history"}
    assert 0.0 <= result["probability_infertile"] <= 1.0
    assert 0.0 <= result["probability_primary"] <= 1.0
    assert 0.0 <= result["probability_secondary"] <= 1.0

    # primary + secondary should equal overall infertility risk probability.
    assert abs(
        (result["probability_primary"] + result["probability_secondary"])
        - result["probability_infertile"]
    ) < 1e-6


def test_predict_with_partial_payload_uses_history_branch() -> None:
    load_artifacts(force_reload=True)

    payload = InfertilityRequest(
        age=38,
        ever_cohabited=1,
        children_ever_born=2,
    )

    result = predict_infertility(payload)

    assert result["models_used"] == ["history"]
    assert result["predicted_class"] in {
        "no_infertility_risk",
        "secondary_infertility_risk",
    }


def test_predict_never_cohabited_uses_symptom_only_branch() -> None:
    load_artifacts(force_reload=True)

    payload = InfertilityRequest(
        age=27,
        ever_cohabited=0,
        children_ever_born=0,
        irregular_menstrual_cycles=1,
        chronic_pelvic_pain=1,
    )

    result = predict_infertility(payload)

    assert result["models_used"] == ["symptom"]
    assert result["assessment_mode"] == "symptom_only"


def test_get_model_info_has_expected_keys() -> None:
    load_artifacts(force_reload=True)

    info = get_model_info()

    expected_keys = {
        "model_version",
        "pipeline_type",
        "target_name",
        "training_date_utc",
        "recall_target",
        "thresholds",
        "fusion_weights",
        "branch_metrics",
        "features",
        "training_samples",
        "class_distribution",
        "notes",
    }

    assert expected_keys.issubset(info.keys())


def test_predict_pregnancy_with_full_payload() -> None:
    load_pregnancy_artifacts(force_reload=True)

    payload = PregnancyRequest(
        age=32,
        systolic_bp=140,
        diastolic=90,
        bs=10.4,
        body_temp=99.0,
        bmi=28.2,
        previous_complications=1,
        preexisting_diabetes=1,
        gestational_diabetes=0,
        mental_health=1,
        heart_rate=86,
    )

    result = predict_pregnancy(payload)
    info = get_pregnancy_model_info()
    threshold = float(info["threshold"])
    emergency_threshold = float(info["emergency_threshold"])

    assert result["predicted_class"] in {"low_pregnancy_risk", "high_pregnancy_risk"}
    assert 0.0 <= result["probability_high_risk"] <= 1.0
    assert 0.0 <= result["probability_low_risk"] <= 1.0
    assert abs(
        (result["probability_high_risk"] + result["probability_low_risk"]) - 1.0
    ) < 1e-6
    if result["probability_high_risk"] >= threshold:
        assert result["predicted_class"] == "high_pregnancy_risk"
    else:
        assert result["predicted_class"] == "low_pregnancy_risk"
    assert result["advise_hospital_visit"] == (result["probability_high_risk"] >= threshold)
    assert emergency_threshold >= threshold
    assert result["advise_emergency_care"] == (
        result["probability_high_risk"] >= emergency_threshold
    )
    assert isinstance(result["hospital_advice"], str) and len(result["hospital_advice"]) > 0
    assert isinstance(result["emergency_advice"], str) and len(result["emergency_advice"]) > 0


def test_predict_pregnancy_with_minimal_payload_uses_imputation() -> None:
    load_pregnancy_artifacts(force_reload=True)

    payload = PregnancyRequest(
        age=25,
        systolic_bp=120,
        diastolic=80,
    )

    result = predict_pregnancy(payload)

    assert result["predicted_class"] in {"low_pregnancy_risk", "high_pregnancy_risk"}
    assert len(result["imputed_fields"]) > 0
    assert "bs" in result["imputed_fields"]


def test_prepare_pregnancy_inputs_normalizes_bmi_and_optional_missing() -> None:
    artifacts = load_pregnancy_artifacts(force_reload=True)
    feature_schema = artifacts["feature_schema"]

    payload = PregnancyRequest(
        age=30,
        systolic_bp=125,
        diastolic=82,
        bmi=0,
    )

    prepared = prepare_pregnancy_inputs(payload, feature_schema)

    assert prepared.payload["bmi"] is None
    assert "bmi" in prepared.imputed_fields
    assert "bs" in prepared.imputed_fields


def test_get_pregnancy_model_info_has_expected_keys() -> None:
    load_pregnancy_artifacts(force_reload=True)

    info = get_pregnancy_model_info()

    expected_keys = {
        "model_version",
        "pipeline_type",
        "target_name",
        "training_date_utc",
        "recall_target",
        "threshold",
        "emergency_threshold",
        "evaluation_metrics",
        "features",
        "class_distribution",
        "dropped_rows",
        "training_samples",
        "label_mapping",
        "notes",
    }

    assert expected_keys.issubset(info.keys())
