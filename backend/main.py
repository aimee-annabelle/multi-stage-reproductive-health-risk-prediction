from datetime import datetime, timedelta, timezone
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
import hashlib
import hmac
import joblib
import numpy as np
import os
import re
import secrets
import sqlite3
from typing import Dict

app = FastAPI(
    title="Reproductive Health Risk Prediction API",
    description="API for predicting infertility risk based on symptoms and health indicators",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "ml")
AUTH_DB_PATH = os.path.join(os.path.dirname(__file__), "auth.db")
PASSWORD_ITERATIONS = 310_000
TOKEN_TTL_HOURS = 24
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

model = None
scaler = None
feature_names = None
metadata = None
security = HTTPBearer(auto_error=False)


class PatientSymptoms(BaseModel):
    Age: int = Field(..., ge=18, le=100, description="Patient's age (18-100)")
    Irregular_Menstrual_Cycles: int = Field(..., ge=0, le=1, description="0 = No, 1 = Yes")
    Hormonal_Imbalances: int = Field(..., ge=0, le=1, description="0 = No, 1 = Yes")
    Pelvic_Infections: int = Field(..., ge=0, le=1, description="0 = No, 1 = Yes")
    Endometriosis: int = Field(..., ge=0, le=1, description="0 = No, 1 = Yes")
    Uterine_Fibroids: int = Field(..., ge=0, le=1, description="0 = No, 1 = Yes")
    Blocked_Fallopian_Tubes: int = Field(..., ge=0, le=1, description="0 = No, 1 = Yes")
    Obesity: int = Field(..., ge=0, le=1, description="0 = No, 1 = Yes")
    Smoking_or_Alcohol: int = Field(..., ge=0, le=1, description="0 = No, 1 = Yes")
    Age_Related_Factors: int = Field(..., ge=0, le=1, description="0 = No, 1 = Yes")
    Male_Factor: int = Field(..., ge=0, le=1, description="0 = No, 1 = Yes")

    class Config:
        json_schema_extra = {
            "example": {
                "Age": 32,
                "Irregular_Menstrual_Cycles": 1,
                "Hormonal_Imbalances": 1,
                "Pelvic_Infections": 0,
                "Endometriosis": 0,
                "Uterine_Fibroids": 0,
                "Blocked_Fallopian_Tubes": 0,
                "Obesity": 0,
                "Smoking_or_Alcohol": 0,
                "Age_Related_Factors": 0,
                "Male_Factor": 0,
            }
        }


class PredictionResponse(BaseModel):
    prediction: str
    risk_level: str
    probability: float
    confidence: str
    message: str
    feature_importance: Dict[str, float]


class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: str = Field(..., min_length=5, max_length=254)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=254)
    password: str = Field(..., min_length=8, max_length=128)


class AuthUser(BaseModel):
    id: int
    full_name: str
    email: str
    created_at: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: AuthUser


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(AUTH_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )
    conn.commit()
    return conn


def init_auth_db() -> None:
    conn = get_db()
    conn.close()


def hash_password(password: str, salt_hex: str) -> str:
    salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return dk.hex()


def verify_password(password: str, salt_hex: str, expected_hash: str) -> bool:
    candidate = hash_password(password, salt_hex)
    return hmac.compare_digest(candidate, expected_hash)


def validate_email(email: str) -> str:
    clean_email = email.strip().lower()
    if not EMAIL_REGEX.match(clean_email):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid email format")
    return clean_email


def create_session(conn: sqlite3.Connection, user_id: int) -> tuple[str, int]:
    token = secrets.token_urlsafe(48)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=TOKEN_TTL_HOURS)
    conn.execute(
        "INSERT INTO sessions (token, user_id, expires_at, created_at) VALUES (?, ?, ?, ?)",
        (token, user_id, expires.isoformat(), now.isoformat()),
    )
    conn.commit()
    return token, TOKEN_TTL_HOURS * 3600


def row_to_user(row: sqlite3.Row) -> AuthUser:
    return AuthUser(
        id=row["id"],
        full_name=row["full_name"],
        email=row["email"],
        created_at=row["created_at"],
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AuthUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid token")

    conn = get_db()
    try:
        row = conn.execute(
            """
            SELECT u.id, u.full_name, u.email, u.created_at, s.expires_at
            FROM sessions s
            INNER JOIN users u ON u.id = s.user_id
            WHERE s.token = ?
            """,
            (credentials.credentials,),
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        expires_at = datetime.fromisoformat(row["expires_at"])
        if expires_at < datetime.now(timezone.utc):
            conn.execute("DELETE FROM sessions WHERE token = ?", (credentials.credentials,))
            conn.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

        return row_to_user(row)
    finally:
        conn.close()


@app.on_event("startup")
async def startup() -> None:
    global model, scaler, feature_names, metadata

    init_auth_db()
    try:
        model = joblib.load(os.path.join(MODEL_DIR, "infertility_model.pkl"))
        scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
        feature_names = joblib.load(os.path.join(MODEL_DIR, "feature_names.pkl"))
        metadata = joblib.load(os.path.join(MODEL_DIR, "model_metadata.pkl"))
        print("Models loaded successfully!")
    except Exception as e:
        print(f"Error loading models: {e}")
        raise


@app.get("/")
async def root():
    return {
        "message": "Reproductive Health Risk Prediction API",
        "endpoints": {
            "predict": "/predict/infertility",
            "health": "/health",
            "model_info": "/model/info",
            "signup": "/auth/signup",
            "login": "/auth/login",
            "me": "/auth/me",
            "logout": "/auth/logout",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "scaler_loaded": scaler is not None,
    }


@app.post("/auth/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest):
    email = validate_email(payload.email)
    conn = get_db()
    try:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        salt_hex = secrets.token_hex(16)
        password_hash = hash_password(payload.password, salt_hex)
        created_at = datetime.now(timezone.utc).isoformat()

        cursor = conn.execute(
            """
            INSERT INTO users (full_name, email, password_hash, salt, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (payload.full_name.strip(), email, password_hash, salt_hex, created_at),
        )

        user_id = cursor.lastrowid
        token, expires_in = create_session(conn, user_id)

        user_row = conn.execute(
            "SELECT id, full_name, email, created_at FROM users WHERE id = ?", (user_id,)
        ).fetchone()

        return AuthResponse(
            access_token=token,
            token_type="bearer",
            expires_in=expires_in,
            user=row_to_user(user_row),
        )
    finally:
        conn.close()


@app.post("/auth/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    email = validate_email(payload.email)
    conn = get_db()
    try:
        user_row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user_row is None or not verify_password(payload.password, user_row["salt"], user_row["password_hash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        token, expires_in = create_session(conn, user_row["id"])

        return AuthResponse(
            access_token=token,
            token_type="bearer",
            expires_in=expires_in,
            user=row_to_user(user_row),
        )
    finally:
        conn.close()


@app.get("/auth/me", response_model=AuthUser)
async def me(current_user: AuthUser = Depends(get_current_user)):
    return current_user


@app.post("/auth/logout", status_code=status.HTTP_200_OK)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid token")

    conn = get_db()
    try:
        conn.execute("DELETE FROM sessions WHERE token = ?", (credentials.credentials,))
        conn.commit()
        return {"message": "Logged out successfully"}
    finally:
        conn.close()


@app.get("/model/info")
async def model_info():
    if metadata is None:
        raise HTTPException(status_code=500, detail="Model metadata not loaded")

    return {
        "model_name": metadata["model_name"],
        "trained_date": metadata["trained_date"],
        "features": metadata["features"],
        "performance_metrics": metadata["performance_metrics"],
        "training_info": metadata["training_info"],
    }


@app.post("/predict/infertility", response_model=PredictionResponse)
async def predict_infertility(patient: PatientSymptoms):
    if model is None or scaler is None:
        raise HTTPException(status_code=500, detail="Models not loaded")

    try:
        input_data = [
            patient.Age,
            patient.Irregular_Menstrual_Cycles,
            patient.Hormonal_Imbalances,
            patient.Pelvic_Infections,
            patient.Endometriosis,
            patient.Uterine_Fibroids,
            patient.Blocked_Fallopian_Tubes,
            patient.Obesity,
            patient.Smoking_or_Alcohol,
            patient.Age_Related_Factors,
            patient.Male_Factor,
        ]

        input_array = np.array(input_data).reshape(1, -1)
        input_scaled = scaler.transform(input_array)

        prediction = model.predict(input_scaled)[0]
        probability = model.predict_proba(input_scaled)[0]

        risk_prob = probability[1]

        if risk_prob >= 0.7:
            risk_level = "High Risk"
            confidence = "High Confidence"
            message = "Patient shows multiple risk factors for infertility. Medical consultation strongly recommended."
        elif risk_prob >= 0.5:
            risk_level = "Moderate Risk"
            confidence = "Moderate Confidence"
            message = "Patient shows some risk factors for infertility. Consider consulting a healthcare provider."
        else:
            risk_level = "Low Risk"
            confidence = "Moderate to High Confidence"
            message = "Patient shows minimal risk factors for infertility based on provided symptoms."

        feature_importance = {}
        if hasattr(model, "feature_importances_"):
            for i, name in enumerate(feature_names):
                feature_importance[name] = float(model.feature_importances_[i])
        elif hasattr(model, "coef_"):
            for i, name in enumerate(feature_names):
                feature_importance[name] = float(abs(model.coef_[0][i]))

        feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5])

        return PredictionResponse(
            prediction="At Risk" if prediction == 1 else "No Risk",
            risk_level=risk_level,
            probability=round(risk_prob, 4),
            confidence=confidence,
            message=message,
            feature_importance=feature_importance,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
