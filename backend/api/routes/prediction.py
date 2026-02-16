from fastapi import APIRouter, HTTPException

from backend.models.request import InfertilityRequest
from backend.models.response import InfertilityResponse
from backend.services.model_service import get_model_info
from backend.services.prediction_service import predict_infertility


router = APIRouter(tags=["Infertility"])


@router.post("/predict/infertility", response_model=InfertilityResponse)
async def predict_infertility_route(payload: InfertilityRequest) -> InfertilityResponse:
    try:
        prediction = predict_infertility(payload)
        return InfertilityResponse(**prediction)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction error: {exc}") from exc


@router.get("/model/info")
async def model_info() -> dict:
    try:
        return get_model_info()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Model info error: {exc}") from exc
