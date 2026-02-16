from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.prediction import router as prediction_router
from backend.services.model_service import artifacts_available, load_artifacts

app = FastAPI(
    title="Reproductive Health Risk Prediction API",
    description=(
        "Unified infertility risk prediction API using symptom-based and "
        "history-based fusion with cohabitation-aware routing."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def load_models() -> None:
    try:
        load_artifacts()
        print("Infertility artifacts loaded successfully!")
    except Exception as exc:
        print(f"Error loading infertility artifacts: {exc}")
        raise


@app.get("/")
async def root() -> dict:
    return {
        "message": "Reproductive Health Risk Prediction API",
        "endpoints": {
            "predict": "/predict/infertility",
            "health": "/health",
            "model_info": "/model/info",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "model_loaded": artifacts_available(),
    }


app.include_router(prediction_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
