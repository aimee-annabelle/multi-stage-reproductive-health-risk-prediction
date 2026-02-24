from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session
import hashlib
import hmac
import logging
import os
import re
import secrets

from backend.models.request import (
    InfertilityRequest,
    PostpartumRequest,
    PregnancyFollowUpRequest,
    PregnancyRequest,
)
from backend.models.response import (
    InfertilityResponse,
    PostpartumResponse,
    PregnancyAssessmentComparisonResponse,
    PregnancyAssessmentHistoryResponse,
    PregnancyAssessmentRecordResponse,
    PregnancyTimelinePointResponse,
    PregnancyTimelineSummaryResponse,
    PregnancyResponse,
)
from backend.db.models import AuthSession, PregnancyAssessment, User
from backend.db.session import engine, get_db_session
from backend.services.model_service import (
    get_model_info,
    get_postpartum_model_info,
    get_pregnancy_model_info,
    load_artifacts,
    load_postpartum_artifacts,
    load_pregnancy_artifacts,
)
from backend.services.prediction_service import (
    predict_infertility,
    predict_postpartum,
    predict_pregnancy,
)
from backend.services.pregnancy_tracking_service import (
    build_timeline_summary,
    compare_latest_assessments,
    count_pregnancy_assessments,
    create_pregnancy_assessment,
    list_pregnancy_assessments,
)

logger = logging.getLogger(__name__)


def parse_cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return origins or ["http://localhost:5173", "http://localhost:3000"]


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        load_artifacts()
        logger.info("Infertility fusion artifacts loaded successfully.")
        try:
            load_pregnancy_artifacts()
            logger.info("Pregnancy v1 artifacts loaded successfully.")
        except FileNotFoundError:
            logger.warning("Pregnancy artifacts are not available yet.")
        try:
            load_postpartum_artifacts()
            logger.info("Postpartum v1 artifacts loaded successfully.")
        except FileNotFoundError:
            logger.warning("Postpartum artifacts are not available yet.")
    except Exception:
        logger.exception("Error loading models during startup")
        raise

    yield


app = FastAPI(
    title="Reproductive Health Risk Prediction API",
    description="API for predicting infertility risk based on symptoms and health indicators",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PASSWORD_ITERATIONS = 310_000
TOKEN_TTL_HOURS = 24
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

security = HTTPBearer(auto_error=False)


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


def create_auth_session(db: Session, user_id: int) -> tuple[str, int]:
    token = secrets.token_urlsafe(48)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=TOKEN_TTL_HOURS)
    db.add(AuthSession(token=token, user_id=user_id, expires_at=expires, created_at=now))
    db.commit()
    return token, TOKEN_TTL_HOURS * 3600


def user_to_response(user: User) -> AuthUser:
    created_at = user.created_at.isoformat() if hasattr(user.created_at, "isoformat") else str(user.created_at)
    return AuthUser(id=user.id, full_name=user.full_name, email=user.email, created_at=created_at)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session),
) -> AuthUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid token")

    result = db.execute(
        select(User, AuthSession)
        .join(AuthSession, AuthSession.user_id == User.id)
        .where(AuthSession.token == credentials.credentials)
    ).first()

    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user, auth_session = result
    expires_at = auth_session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        db.delete(auth_session)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

    return user_to_response(user)


def pregnancy_assessment_to_response(
    assessment: PregnancyAssessment,
) -> PregnancyAssessmentRecordResponse:
    created_at = (
        assessment.created_at.isoformat()
        if hasattr(assessment.created_at, "isoformat")
        else str(assessment.created_at)
    )
    return PregnancyAssessmentRecordResponse(
        assessment_id=assessment.id,
        created_at=created_at,
        gestational_age_weeks=assessment.gestational_age_weeks,
        visit_label=assessment.visit_label,
        notes=assessment.notes,
        age=assessment.age,
        systolic_bp=assessment.systolic_bp,
        diastolic=assessment.diastolic,
        bs=assessment.bs,
        body_temp=assessment.body_temp,
        bmi=assessment.bmi,
        previous_complications=assessment.previous_complications,
        preexisting_diabetes=assessment.preexisting_diabetes,
        gestational_diabetes=assessment.gestational_diabetes,
        mental_health=assessment.mental_health,
        heart_rate=assessment.heart_rate,
        predicted_class=assessment.predicted_class,
        probability_high_risk=assessment.probability_high_risk,
        probability_low_risk=assessment.probability_low_risk,
        risk_level=assessment.risk_level,
        decision_threshold=assessment.decision_threshold,
        emergency_threshold=assessment.emergency_threshold,
        advise_hospital_visit=assessment.advise_hospital_visit,
        advise_emergency_care=assessment.advise_emergency_care,
        hospital_advice=assessment.hospital_advice,
        emergency_advice=assessment.emergency_advice,
        top_risk_factors=assessment.top_risk_factors or {},
        imputed_fields=assessment.imputed_fields or [],
        model_version=assessment.model_version,
    )


@app.get("/")
async def root() -> dict:
    return {
        "message": "Reproductive Health Risk Prediction API",
        "endpoints": {
            "predict": "/predict/infertility",
            "predict_infertility": "/predict/infertility",
            "predict_pregnancy": "/predict/pregnancy",
            "predict_postpartum": "/predict/postpartum",
            "pregnancy_followup_assess": "/pregnancy/follow-up/assess",
            "pregnancy_followup_history": "/pregnancy/follow-up/history",
            "pregnancy_followup_compare_latest": "/pregnancy/follow-up/compare/latest",
            "pregnancy_followup_timeline_summary": "/pregnancy/follow-up/timeline/summary",
            "health": "/health",
            "model_info": "/model/info",
            "model_info_infertility": "/model/info",
            "model_info_pregnancy": "/model/info/pregnancy",
            "model_info_postpartum": "/model/info/postpartum",
            "signup": "/auth/signup",
            "login": "/auth/login",
            "me": "/auth/me",
            "logout": "/auth/logout",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check() -> dict:
    artifacts_loaded = True
    try:
        load_artifacts()
    except Exception:
        artifacts_loaded = False

    return {
        "status": "healthy",
        "artifacts_loaded": artifacts_loaded,
    }


@app.post("/auth/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest, db: Session = Depends(get_db_session)):
    email = validate_email(payload.email)

    existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    salt_hex = secrets.token_hex(16)
    password_hash = hash_password(payload.password, salt_hex)

    user = User(
        full_name=payload.full_name.strip(),
        email=email,
        password_hash=password_hash,
        salt=salt_hex,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token, expires_in = create_auth_session(db, user.id)

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        user=user_to_response(user),
    )


@app.post("/auth/login", response_model=AuthResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db_session)):
    email = validate_email(payload.email)

    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.salt, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token, expires_in = create_auth_session(db, user.id)

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        user=user_to_response(user),
    )


@app.get("/auth/me", response_model=AuthUser)
async def me(current_user: AuthUser = Depends(get_current_user)):
    return current_user


@app.post("/auth/logout", status_code=status.HTTP_200_OK)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session),
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid token")

    db.execute(delete(AuthSession).where(AuthSession.token == credentials.credentials))
    db.commit()
    return {"message": "Logged out successfully"}


@app.get("/model/info")
async def model_info():
    try:
        return get_model_info()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Model info error")
        raise HTTPException(status_code=500, detail="Model info error") from exc


@app.get("/model/info/pregnancy")
async def pregnancy_model_info():
    try:
        return get_pregnancy_model_info()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Pregnancy model info error")
        raise HTTPException(status_code=500, detail="Pregnancy model info error") from exc


@app.get("/model/info/postpartum")
async def postpartum_model_info():
    try:
        return get_postpartum_model_info()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Postpartum model info error")
        raise HTTPException(status_code=500, detail="Postpartum model info error") from exc


@app.post("/predict/infertility", response_model=InfertilityResponse)
async def predict_infertility_route(payload: InfertilityRequest):
    try:
        prediction = predict_infertility(payload)
        return InfertilityResponse(**prediction)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Prediction error")
        raise HTTPException(status_code=500, detail="Prediction error") from exc


@app.post("/predict/pregnancy", response_model=PregnancyResponse)
async def predict_pregnancy_route(payload: PregnancyRequest):
    try:
        prediction = predict_pregnancy(payload)
        return PregnancyResponse(**prediction)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Pregnancy prediction error")
        raise HTTPException(status_code=500, detail="Pregnancy prediction error") from exc


@app.post("/predict/postpartum", response_model=PostpartumResponse)
async def predict_postpartum_route(payload: PostpartumRequest):
    try:
        prediction = predict_postpartum(payload)
        return PostpartumResponse(**prediction)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Postpartum prediction error")
        raise HTTPException(status_code=500, detail="Postpartum prediction error") from exc


@app.post(
    "/pregnancy/follow-up/assess",
    response_model=PregnancyAssessmentRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assess_and_store_pregnancy_followup(
    payload: PregnancyFollowUpRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    try:
        prediction = predict_pregnancy(payload)
        assessment = create_pregnancy_assessment(
            db=db,
            user_id=current_user.id,
            payload=payload,
            prediction=prediction,
        )
        return pregnancy_assessment_to_response(assessment)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Pregnancy follow-up storage error")
        raise HTTPException(status_code=500, detail="Pregnancy follow-up storage error") from exc


@app.get(
    "/pregnancy/follow-up/history",
    response_model=PregnancyAssessmentHistoryResponse,
)
async def get_pregnancy_followup_history(
    limit: int = Query(default=20, ge=1, le=200),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    assessments = list_pregnancy_assessments(db=db, user_id=current_user.id, limit=limit)
    total = count_pregnancy_assessments(db=db, user_id=current_user.id)
    return PregnancyAssessmentHistoryResponse(
        total_records=total,
        assessments=[pregnancy_assessment_to_response(item) for item in assessments],
    )


@app.get(
    "/pregnancy/follow-up/compare/latest",
    response_model=PregnancyAssessmentComparisonResponse,
)
async def compare_latest_pregnancy_followups(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    try:
        comparison = compare_latest_assessments(db=db, user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    latest = comparison["latest"]
    previous = comparison["previous"]
    return PregnancyAssessmentComparisonResponse(
        latest_assessment_id=latest.id,
        previous_assessment_id=previous.id,
        latest_created_at=latest.created_at.isoformat(),
        previous_created_at=previous.created_at.isoformat(),
        latest_probability_high_risk=latest.probability_high_risk,
        previous_probability_high_risk=previous.probability_high_risk,
        probability_high_risk_delta=comparison["probability_high_risk_delta"],
        trend=comparison["trend"],
        metric_deltas=comparison["metric_deltas"],
    )


@app.get(
    "/pregnancy/follow-up/timeline/summary",
    response_model=PregnancyTimelineSummaryResponse,
)
async def get_pregnancy_followup_timeline_summary(
    limit: int = Query(default=50, ge=1, le=500),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    summary = build_timeline_summary(db=db, user_id=current_user.id, limit=limit)
    points = [
        PregnancyTimelinePointResponse(
            assessment_id=item.id,
            created_at=item.created_at.isoformat(),
            gestational_age_weeks=item.gestational_age_weeks,
            visit_label=item.visit_label,
            probability_high_risk=item.probability_high_risk,
            probability_low_risk=item.probability_low_risk,
            risk_level=item.risk_level,
            advise_hospital_visit=item.advise_hospital_visit,
            advise_emergency_care=item.advise_emergency_care,
            systolic_bp=item.systolic_bp,
            diastolic=item.diastolic,
            bs=item.bs,
            bmi=item.bmi,
            heart_rate=item.heart_rate,
        )
        for item in summary["points"]
    ]

    return PregnancyTimelineSummaryResponse(
        total_records=summary["total_records"],
        time_span_days=summary["time_span_days"],
        high_risk_count=summary["high_risk_count"],
        hospital_referral_count=summary["hospital_referral_count"],
        emergency_referral_count=summary["emergency_referral_count"],
        earliest_probability_high_risk=summary["earliest_probability_high_risk"],
        latest_probability_high_risk=summary["latest_probability_high_risk"],
        probability_high_risk_change=summary["probability_high_risk_change"],
        trend=summary["trend"],
        points=points,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
