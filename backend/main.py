from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import numpy as np
import os
from typing import List, Dict

app = FastAPI(
    title="Reproductive Health Risk Prediction API",
    description="API for predicting infertility risk based on symptoms and health indicators",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml")

model = None
scaler = None
feature_names = None
metadata = None

@app.on_event("startup")
async def load_models():
    global model, scaler, feature_names, metadata
    try:
        model = joblib.load(os.path.join(MODEL_DIR, "infertility_model.pkl"))
        scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
        feature_names = joblib.load(os.path.join(MODEL_DIR, "feature_names.pkl"))
        metadata = joblib.load(os.path.join(MODEL_DIR, "model_metadata.pkl"))
        print("Models loaded successfully!")
    except Exception as e:
        print(f"Error loading models: {e}")
        raise

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
                "Male_Factor": 0
            }
        }

class PredictionResponse(BaseModel):
    prediction: str
    risk_level: str
    probability: float
    confidence: str
    message: str
    feature_importance: Dict[str, float]

@app.get("/")
async def root():
    return {
        "message": "Reproductive Health Risk Prediction API",
        "endpoints": {
            "predict": "/predict/infertility",
            "health": "/health",
            "model_info": "/model/info",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "scaler_loaded": scaler is not None
    }

@app.get("/model/info")
async def model_info():
    if metadata is None:
        raise HTTPException(status_code=500, detail="Model metadata not loaded")

    return {
        "model_name": metadata["model_name"],
        "trained_date": metadata["trained_date"],
        "features": metadata["features"],
        "performance_metrics": metadata["performance_metrics"],
        "training_info": metadata["training_info"]
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
            patient.Male_Factor
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
        if hasattr(model, 'feature_importances_'):
            for i, name in enumerate(feature_names):
                feature_importance[name] = float(model.feature_importances_[i])
        elif hasattr(model, 'coef_'):
            for i, name in enumerate(feature_names):
                feature_importance[name] = float(abs(model.coef_[0][i]))

        feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5])

        return PredictionResponse(
            prediction="At Risk" if prediction == 1 else "No Risk",
            risk_level=risk_level,
            probability=round(risk_prob, 4),
            confidence=confidence,
            message=message,
            feature_importance=feature_importance
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
