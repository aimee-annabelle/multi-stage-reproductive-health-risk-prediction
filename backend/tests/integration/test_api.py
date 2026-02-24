from __future__ import annotations


def test_predict_infertility_success(client) -> None:
    payload = {
        "age": 30,
        "ever_cohabited": 1,
        "children_ever_born": 0,
        "irregular_menstrual_cycles": 1,
        "chronic_pelvic_pain": 1,
        "history_pelvic_infections": 1,
        "hormonal_symptoms": 1,
        "early_menopause_symptoms": 0,
        "autoimmune_history": 0,
        "reproductive_surgery_history": 0,
        "bmi": 27.1,
        "smoked_last_12mo": 0,
        "alcohol_last_12mo": 0,
        "age_at_first_marriage": 22,
        "months_since_first_cohabitation": 96,
        "months_since_last_sex": 2,
    }

    response = client.post("/predict/infertility", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["predicted_class"] in {
        "no_infertility_risk",
        "primary_infertility_risk",
        "secondary_infertility_risk",
    }
    assert abs(
        (body["probability_primary"] + body["probability_secondary"])
        - body["probability_infertile"]
    ) < 1e-6


def test_predict_infertility_partial_payload_success(client) -> None:
    payload = {
        "age": 41,
        "ever_cohabited": 1,
        "children_ever_born": 3,
    }

    response = client.post("/predict/infertility", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["models_used"] == ["history"]


def test_predict_infertility_missing_required_field(client) -> None:
    payload = {
        "age": 33,
        "irregular_menstrual_cycles": 1,
    }

    response = client.post("/predict/infertility", json=payload)
    assert response.status_code == 422


def test_predict_infertility_out_of_range_validation(client) -> None:
    payload = {
        "age": 25,
        "ever_cohabited": 1,
        "children_ever_born": 1,
        "smoked_last_12mo": 3,
    }

    response = client.post("/predict/infertility", json=payload)
    assert response.status_code == 422


def test_model_info_success(client) -> None:
    response = client.get("/model/info")
    assert response.status_code == 200

    body = response.json()
    assert "model_version" in body
    assert "branch_metrics" in body


def test_predict_never_cohabited_symptom_only(client) -> None:
    payload = {
        "age": 28,
        "ever_cohabited": 0,
        "children_ever_born": 0,
        "irregular_menstrual_cycles": 1,
        "chronic_pelvic_pain": 1,
    }

    response = client.post("/predict/infertility", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["models_used"] == ["symptom"]
    assert body["assessment_mode"] == "symptom_only"


def test_predict_never_cohabited_no_symptoms_returns_422(client) -> None:
    payload = {
        "age": 28,
        "ever_cohabited": 0,
        "children_ever_born": 0,
    }

    response = client.post("/predict/infertility", json=payload)
    assert response.status_code == 422


def test_predict_pregnancy_success(client) -> None:
    payload = {
        "age": 31,
        "systolic_bp": 140,
        "diastolic": 90,
        "bs": 10.2,
        "body_temp": 99.0,
        "bmi": 27.8,
        "previous_complications": 1,
        "preexisting_diabetes": 1,
        "gestational_diabetes": 0,
        "mental_health": 1,
        "heart_rate": 86,
    }

    response = client.post("/predict/pregnancy", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["predicted_class"] in {"low_pregnancy_risk", "high_pregnancy_risk"}
    assert 0.0 <= body["probability_high_risk"] <= 1.0
    assert 0.0 <= body["probability_low_risk"] <= 1.0
    assert abs((body["probability_high_risk"] + body["probability_low_risk"]) - 1.0) < 1e-6
    assert body["risk_level"] in {"Low Risk", "High Risk"}
    assert 0.0 <= body["emergency_threshold"] <= 1.0
    assert body["emergency_threshold"] >= body["decision_threshold"]
    assert isinstance(body["advise_hospital_visit"], bool)
    assert isinstance(body["advise_emergency_care"], bool)
    assert isinstance(body["hospital_advice"], str) and len(body["hospital_advice"]) > 0
    assert isinstance(body["emergency_advice"], str) and len(body["emergency_advice"]) > 0
    assert body["advise_hospital_visit"] == (
        body["probability_high_risk"] >= body["decision_threshold"]
    )
    assert body["advise_emergency_care"] == (
        body["probability_high_risk"] >= body["emergency_threshold"]
    )


def test_predict_pregnancy_minimal_payload_uses_imputation(client) -> None:
    payload = {
        "age": 26,
        "systolic_bp": 120,
        "diastolic": 80,
    }

    response = client.post("/predict/pregnancy", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert len(body["imputed_fields"]) > 0
    assert "bs" in body["imputed_fields"]


def test_predict_pregnancy_missing_required_field(client) -> None:
    payload = {
        "age": 29,
        "systolic_bp": 120,
    }

    response = client.post("/predict/pregnancy", json=payload)
    assert response.status_code == 422


def test_predict_pregnancy_invalid_binary_value(client) -> None:
    payload = {
        "age": 29,
        "systolic_bp": 120,
        "diastolic": 80,
        "previous_complications": 3,
    }

    response = client.post("/predict/pregnancy", json=payload)
    assert response.status_code == 422


def test_model_info_pregnancy_success(client) -> None:
    response = client.get("/model/info/pregnancy")
    assert response.status_code == 200

    body = response.json()
    assert "model_version" in body
    assert "evaluation_metrics" in body
    assert "threshold" in body
    assert "emergency_threshold" in body
