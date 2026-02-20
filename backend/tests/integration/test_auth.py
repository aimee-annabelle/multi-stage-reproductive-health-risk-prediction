import os

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def _cleanup_auth_db() -> None:
    db_path = os.path.join(os.path.dirname(__file__), "..", "..", "auth.db")
    db_path = os.path.abspath(db_path)
    if os.path.exists(db_path):
        os.remove(db_path)


def setup_module() -> None:
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
