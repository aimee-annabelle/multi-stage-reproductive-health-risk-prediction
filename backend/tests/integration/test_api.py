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
