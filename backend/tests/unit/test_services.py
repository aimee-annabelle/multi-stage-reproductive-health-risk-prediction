from __future__ import annotations

from backend.models.request import InfertilityRequest
from backend.services.model_service import get_model_info, load_artifacts
from backend.services.prediction_service import predict_infertility


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
