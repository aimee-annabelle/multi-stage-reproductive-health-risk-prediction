# Project Structure

This file reflects the current repository layout and primary responsibilities.

```text
multi-stage-reproductive-health-risk-prediction/
├── backend/
│   ├── alembic/
│   │   └── versions/
│   ├── api/
│   │   └── routes/                     # legacy/experimental route modules
│   ├── db/
│   │   ├── base.py
│   │   ├── models.py                   # users, sessions, pregnancy_assessments
│   │   └── session.py                  # PostgreSQL engine/session
│   ├── middleware/
│   ├── models/
│   │   ├── request.py                  # Pydantic request schemas
│   │   └── response.py                 # Pydantic response schemas
│   ├── services/
│   │   ├── model_service.py            # artifact loading/model info
│   │   ├── prediction_service.py       # infertility + pregnancy inference
│   │   ├── pregnancy_tracking_service.py
│   │   └── preprocessing_service.py
│   ├── tests/
│   │   ├── integration/
│   │   ├── unit/
│   │   └── conftest.py
│   ├── .env.example
│   ├── alembic.ini
│   ├── main.py                         # active FastAPI app and routes
│   └── README.md
├── data/
│   ├── processed/
│   │   ├── Female infertility.csv
│   │   ├── dhs_cleaned.csv
│   │   ├── infertility_features_v1.csv
│   │   └── pregnancy-risk-dataset.csv
│   └── dhs_data_cleaning.py
├── docs/
│   ├── API_DOCUMENTATION.md
│   └── diagrams/
├── evaluation/
│   ├── infertility_v1/
│   └── pregnancy_v1/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── stores/
│   │   └── styles/
│   └── README.md
├── ml/
│   ├── infertility_v2_*.pkl            # Stage 1 production artifacts
│   ├── pregnancy_v1_*.pkl              # Stage 2 production artifacts
│   └── infertility_* legacy artifacts
├── notebooks/
│   ├── 01_...06_...                    # infertility v1 analysis/training flow
│   ├── 07_infertility_fusion_training.py
│   ├── 08_pregnancy_risk_training.py
│   ├── 09_pregnancy_model_evaluation.py
│   ├── run_infertility_v1_pipeline.py
│   ├── run_pregnancy_v1_pipeline.py
│   └── README.md
├── requirements.txt
├── LICENSE
└── README.md
```

## Runtime Notes

- The active API routes are registered in `backend/main.py`.
- PostgreSQL is required for authentication and follow-up storage.
- Integration tests are PostgreSQL-only.
