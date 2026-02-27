from sqlalchemy import delete

from backend.db.base import Base
from backend.db.models import AuthSession, PostpartumAssessment, PregnancyAssessment, User
from backend.db.session import SessionLocal, engine
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def _cleanup_auth_db() -> None:
    db = SessionLocal()
    try:
        db.execute(delete(PostpartumAssessment))
        db.execute(delete(PregnancyAssessment))
        db.execute(delete(AuthSession))
        db.execute(delete(User))
        db.commit()
    finally:
        db.close()


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)
    _cleanup_auth_db()


def teardown_module() -> None:
    _cleanup_auth_db()


def test_signup_login_me_logout_flow() -> None:
    signup_res = client.post(
        "/auth/signup",
        json={
            "full_name": "Test User",
            "email": "test.user@example.com",
            "password": "StrongPass123",
        },
    )
    assert signup_res.status_code == 201
    signup_data = signup_res.json()

    assert "access_token" in signup_data
    assert signup_data["token_type"] == "bearer"
    assert signup_data["expires_in"] == 86400
    assert signup_data["user"]["email"] == "test.user@example.com"

    token = signup_data["access_token"]

    me_res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "test.user@example.com"

    logout_res = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_res.status_code == 200

    me_after_logout_res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_after_logout_res.status_code == 401

    login_res = client.post(
        "/auth/login",
        json={
            "email": "test.user@example.com",
            "password": "StrongPass123",
        },
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()


def test_signup_duplicate_email_returns_conflict() -> None:
    first_signup = client.post(
        "/auth/signup",
        json={
            "full_name": "Another User",
            "email": "duplicate@example.com",
            "password": "StrongPass123",
        },
    )
    assert first_signup.status_code == 201

    second_signup = client.post(
        "/auth/signup",
        json={
            "full_name": "Another User",
            "email": "duplicate@example.com",
            "password": "StrongPass123",
        },
    )
    assert second_signup.status_code == 409


def test_pregnancy_followup_storage_history_and_comparison() -> None:
    signup_res = client.post(
        "/auth/signup",
        json={
            "full_name": "Pregnancy User",
            "email": "pregnancy.user@example.com",
            "password": "StrongPass123",
        },
    )
    assert signup_res.status_code == 201
    token = signup_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload_1 = {
        "gestational_age_weeks": 22,
        "visit_label": "ANC Visit 1",
        "notes": "Baseline follow-up",
        "age": 28,
        "systolic_bp": 120,
        "diastolic": 80,
        "bs": 6.2,
        "body_temp": 98.6,
        "bmi": 24.3,
        "previous_complications": 0,
        "preexisting_diabetes": 0,
        "gestational_diabetes": 0,
        "mental_health": 0,
        "heart_rate": 74,
    }
    create_1 = client.post("/pregnancy/follow-up/assess", json=payload_1, headers=headers)
    assert create_1.status_code == 201
    body_1 = create_1.json()
    assert body_1["visit_label"] == "ANC Visit 1"
    assert body_1["assessment_id"] > 0

    payload_2 = {
        "gestational_age_weeks": 28,
        "visit_label": "ANC Visit 2",
        "notes": "Follow-up with higher blood pressure",
        "age": 28,
        "systolic_bp": 140,
        "diastolic": 90,
        "bs": 8.8,
        "body_temp": 99.1,
        "bmi": 25.1,
        "previous_complications": 1,
        "preexisting_diabetes": 0,
        "gestational_diabetes": 0,
        "mental_health": 1,
        "heart_rate": 82,
    }
    create_2 = client.post("/pregnancy/follow-up/assess", json=payload_2, headers=headers)
    assert create_2.status_code == 201
    body_2 = create_2.json()
    assert body_2["visit_label"] == "ANC Visit 2"
    assert body_2["assessment_id"] > body_1["assessment_id"]

    history_res = client.get("/pregnancy/follow-up/history?limit=10", headers=headers)
    assert history_res.status_code == 200
    history = history_res.json()
    assert history["total_records"] >= 2
    assert len(history["assessments"]) >= 2
    assert history["assessments"][0]["assessment_id"] == body_2["assessment_id"]

    compare_res = client.get("/pregnancy/follow-up/compare/latest", headers=headers)
    assert compare_res.status_code == 200
    compare = compare_res.json()
    assert compare["latest_assessment_id"] == body_2["assessment_id"]
    assert compare["previous_assessment_id"] == body_1["assessment_id"]
    assert compare["trend"] in {"increased", "decreased", "stable"}
    assert "systolic_bp" in compare["metric_deltas"]

    timeline_res = client.get("/pregnancy/follow-up/timeline/summary?limit=10", headers=headers)
    assert timeline_res.status_code == 200
    timeline = timeline_res.json()
    assert timeline["total_records"] >= 2
    assert timeline["trend"] in {"increased", "decreased", "stable"}
    assert timeline["latest_probability_high_risk"] is not None
    assert timeline["earliest_probability_high_risk"] is not None
    assert len(timeline["points"]) >= 2
    assert timeline["points"][0]["assessment_id"] == body_1["assessment_id"]
    assert timeline["points"][-1]["assessment_id"] == body_2["assessment_id"]


def test_postpartum_followup_storage_history_and_timeline() -> None:
    signup_res = client.post(
        "/auth/signup",
        json={
            "full_name": "Postpartum User",
            "email": "postpartum.user@example.com",
            "password": "StrongPass123",
        },
    )
    assert signup_res.status_code == 201
    token = signup_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload_1 = {
        "baby_age_months": 2,
        "postnatal_problems": "yes",
        "baby_feeding_difficulties": "yes",
        "financial_problems": "no",
        "epds_anxious_or_worried": "Yes, very often",
        "epds_sad_or_miserable": "Yes, quite often",
        "epds_thought_of_harming_self": "Sometimes",
    }
    create_1 = client.post("/postpartum/follow-up/assess", json=payload_1, headers=headers)
    assert create_1.status_code == 201
    body_1 = create_1.json()
    assert body_1["assessment_id"] > 0
    assert body_1["input_payload"]["baby_age_months"] == 2

    payload_2 = {
        "baby_age_months": 4,
        "postnatal_problems": "no",
        "baby_feeding_difficulties": "no",
        "financial_problems": "yes",
        "epds_anxious_or_worried": "Hardly ever",
        "epds_sad_or_miserable": "Not very often",
        "epds_thought_of_harming_self": "Never",
    }
    create_2 = client.post("/postpartum/follow-up/assess", json=payload_2, headers=headers)
    assert create_2.status_code == 201
    body_2 = create_2.json()
    assert body_2["assessment_id"] > body_1["assessment_id"]

    history_res = client.get("/postpartum/follow-up/history?limit=10", headers=headers)
    assert history_res.status_code == 200
    history = history_res.json()
    assert history["total_records"] >= 2
    assert len(history["assessments"]) >= 2
    assert history["assessments"][0]["assessment_id"] == body_2["assessment_id"]
    assert "input_completion_pct" in history["assessments"][0]

    timeline_res = client.get("/postpartum/follow-up/timeline/summary?limit=10", headers=headers)
    assert timeline_res.status_code == 200
    timeline = timeline_res.json()
    assert timeline["total_records"] >= 2
    assert timeline["trend"] in {"increased", "decreased", "stable"}
    assert timeline["latest_probability_high_risk"] is not None
    assert timeline["earliest_probability_high_risk"] is not None
    assert len(timeline["points"]) >= 2
    assert "high_risk_percentage" in timeline
    assert "average_input_completion" in timeline
