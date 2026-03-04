# EveBloom - ML-Based Multi-Stage Reproductive Health Risk Prediction System

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

EveBloom is an end-to-end **machine learning system** for reproductive health risk screening across infertility, pregnancy, and postpartum stages. It is designed as a complete ML product workflow: data preparation, model training, artifact versioning, API inference services, and user-facing risk dashboards.

## Why This Is an ML System

EveBloom is not only an application wrapper around static rules. It uses trained models and ML artifacts to generate probabilistic risk outputs and factor-level explanations.

- **Data-driven inference:** predictions are generated from trained models in `ml/`, not hardcoded thresholds alone.
- **Stage-specific modeling:** each clinical stage has a dedicated model strategy and output schema.
- **Probability-based outputs:** the system returns risk probabilities and levels to support triage-style screening.
- **Feature-level interpretability:** top risk factor signals are returned for explainability in the UI.
- **Model lifecycle support:** training scripts, evaluation reports, and metadata are part of the repo.

## ML Architecture by Stage

### Stage 1: Infertility Risk (Fusion Inference)

- Endpoint: `POST /predict/infertility`
- Strategy: dual-branch fusion (`symptom_only`, `history_only`, `fused`)
- Output:
  - predicted class (`no_infertility_risk`, `primary_infertility_risk`, `secondary_infertility_risk`)
  - class probabilities
  - risk level (`Low`, `Moderate`, `High`)
  - top contributing factors

### Stage 2: Pregnancy Risk (Binary Classifier)

- Endpoint: `POST /predict/pregnancy`
- Output:
  - class (`low_pregnancy_risk`, `high_pregnancy_risk`)
  - high/low probabilities
  - risk level + referral/emergency guidance
  - top risk factors

### Stage 3: Postpartum Risk (Binary Classifier)

- Endpoint: `POST /predict/postpartum`
- Output:
  - class (`low_postpartum_risk`, `high_postpartum_risk`)
  - high/low probabilities
  - risk level + referral/emergency guidance
  - top risk factors

## End-to-End System Components

```text
multi-stage-reproductive-health-risk-prediction/
├── backend/                  # FastAPI inference + auth + follow-up APIs
├── frontend/                 # User-facing interface and dashboards
├── ml/                       # Persisted trained model artifacts for runtime inference
├── notebooks/                # Training/evaluation pipelines
├── data/                     # Raw + processed datasets
├── evaluation/               # Metrics, plots, stage reports
├── docs/                     # API docs, diagrams, payload examples
├── docker-compose.yml        # Containerized deployment
└── requirements.txt
```

## Product + ML Workflow

1. **Train and evaluate models** with scripts in `notebooks/`.
2. **Persist artifacts** in `ml/` (models, metadata, schemas).
3. **Serve inference** via FastAPI endpoints in `backend/main.py`.
4. **Capture follow-up assessments** for pregnancy/postpartum longitudinal views.
5. **Render explainable results** in the React dashboards.

## Quick Start (Local)

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 14+

### 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd frontend
npm install
cd ..
```

### 2. Configure backend env

```bash
cp backend/.env.example backend/.env
```

Use either:

- `DATABASE_URL` (recommended), or
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_SSLMODE`

### 3. Create the database

Create the PostgreSQL database before running migrations:

```bash
psql -U postgres -c "CREATE DATABASE reproductive_health;"
```

Or interactively via `psql`:

```sql
CREATE DATABASE reproductive_health;
```

### 4. Apply migrations

```bash
alembic -c backend/alembic.ini upgrade head
```

### 5. Run backend

```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Run frontend

```bash
cd frontend
npm run dev
```

URLs:

- Frontend: `http://localhost:5173`
- API Docs: `http://localhost:8000/docs`

## Docker Deployment

Run full stack:

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

Stop:

```bash
docker compose down
```

## Current API Surface

### Core

- `GET /`
- `GET /health`

### Authentication

- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/logout`

### Model Metadata

- `GET /model/info`
- `GET /model/info/pregnancy`
- `GET /model/info/postpartum`

### Prediction APIs

- `POST /predict/infertility`
- `POST /predict/pregnancy`
- `POST /predict/postpartum`

### Follow-Up APIs

- Pregnancy:
  - `POST /pregnancy/follow-up/assess`
  - `GET /pregnancy/follow-up/history`
  - `GET /pregnancy/follow-up/compare/latest`
  - `GET /pregnancy/follow-up/timeline/summary`
- Postpartum:
  - `POST /postpartum/follow-up/assess`
  - `GET /postpartum/follow-up/history`
  - `GET /postpartum/follow-up/timeline/summary`

## Model Development and Evaluation

Run full pipelines:

```bash
python notebooks/run_infertility_v1_pipeline.py
python notebooks/run_pregnancy_v1_pipeline.py
python notebooks/run_postpartum_v1_pipeline.py
```

Key outputs:

- Runtime artifacts in `ml/`
- Performance reports in `evaluation/*`

## Model Performance Summary

| Stage            | Model            | Test Accuracy | Test ROC-AUC | Weighted F1 | Report                                                                         |
| ---------------- | ---------------- | ------------: | -----------: | ----------: | ------------------------------------------------------------------------------ |
| Infertility (v1) | GradientBoosting |        0.9266 |       0.9662 |      0.9203 | [INFERTILITY_V1_REPORT.md](evaluation/infertility_v1/INFERTILITY_V1_REPORT.md) |
| Pregnancy (v1)   | (see report)     |        0.9625 |       0.9997 |           — | [PREGNANCY_V1_REPORT.md](evaluation/pregnancy_v1/PREGNANCY_V1_REPORT.md)       |
| Postpartum (v1)  | RandomForest     |        0.7007 |       0.8561 |      0.7050 | [POSTPARTUM_V1_REPORT.md](evaluation/postpartum_v1/POSTPARTUM_V1_REPORT.md)    |

> Note: Postpartum uses a recall-priority threshold (0.33) to maximise screening sensitivity for at-risk cases.

## Testing

```bash
# Create the test database (first time only)
psql -U postgres -c "CREATE DATABASE reproductive_health_test;"

export DATABASE_URL="postgresql+psycopg2://postgres:<password>@localhost:5432/reproductive_health_test"
alembic -c backend/alembic.ini upgrade head
pytest
```

## Troubleshooting

**`alembic upgrade head` fails immediately**
The database does not exist. Run `psql -U postgres -c "CREATE DATABASE reproductive_health;"` first.

**`503 Service Unavailable` on prediction endpoints**
Model artifacts in `ml/` are missing or were not generated. Run the pipeline scripts in `notebooks/` to produce them, then restart the backend.

**Frontend shows network errors / CORS blocks requests**
Set `VITE_API_URL` in your frontend environment to match the backend address (`http://localhost:8000`). Check that `CORS_ORIGINS` in `backend/.env` includes the frontend URL.

**`422 Unprocessable Entity` on follow-up compare endpoint**
The user has fewer than 2 stored assessments. Submit at least 2 follow-up assessments before calling `/pregnancy/follow-up/compare/latest`.

**`psql` command not found on macOS**
Install PostgreSQL via Homebrew: `brew install postgresql@14`.

**Backend import errors when running locally**
Run the backend from the repository root (not from inside `backend/`): `python -m uvicorn backend.main:app --reload`.

## Additional Docs

- Backend details: [backend/README.md](backend/README.md)
- Frontend details: [frontend/README.md](frontend/README.md)
- ML training details: [notebooks/README.md](notebooks/README.md)
- API reference: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- Example payloads: [docs/example_test_payloads.md](docs/example_test_payloads.md)
- Model performance: [evaluation/](evaluation/)

## Disclaimer

EveBloom provides screening-oriented ML risk estimates for decision support and educational use. It is not a diagnostic device and does not replace professional medical judgment or emergency care.
