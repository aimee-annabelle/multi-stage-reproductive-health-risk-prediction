# EveBloom - Integrated Multi-Stage Reproductive Health Risk Screening Platform

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

EveBloom is an end-to-end **machine learning system** for reproductive health risk screening across infertility, pregnancy, and postpartum stages. It combines stage-specific models, API inference services, user authentication, follow-up tracking, and dashboard-based result presentation in one web platform.

The project should be described carefully in documentation: the current implementation is an **integrated multi-stage screening platform**, not a jointly trained longitudinal model. The stages are connected operationally through a shared application workflow and persistent user history, while each prediction model is trained separately on its own dataset and artifacts.

## Start Here

Use this guide depending on what you want to do first:

- **Run the full application locally:** go to [Quick Start (Local)](#quick-start-local) or [Docker Deployment](#docker-deployment)
- **Understand the repository layout quickly:** see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **Inspect the active backend entry point:** start with `backend/main.py` for the live FastAPI routes
- **Understand the ML pipelines:** see [notebooks/README.md](notebooks/README.md)
- **Review datasets and provenance:** see [data/README.md](data/README.md)
- **Try the API with real payloads:** see [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) and [docs/example_test_payloads.md](docs/example_test_payloads.md)
- **Review model evaluation evidence:** see [evaluation/](evaluation/) and the stage reports linked below

## Positioning and Current Limits

- **What the platform demonstrates:** stage-specific ML inference, unified web workflows, explainable outputs, and longitudinal storage of pregnancy/postpartum follow-up assessments.
- **How the stages are connected today:** shared frontend, shared backend services, shared user identity, and shared assessment history.
- **What it does not yet demonstrate:** a single longitudinal model trained on patient-linked data across infertility, pregnancy, and postpartum stages.
- **Dataset reality:** infertility uses Kaggle symptom data plus DHS-derived historical features; pregnancy and postpartum use separate public datasets.
- **Interpretation boundary:** this repository is best presented as a technical proof-of-concept screening platform, not a Rwanda-validated clinical decision system.

## Deployed Version

- Frontend (Railway): [EveBloom](https://frontendservice-production-1308.up.railway.app/)
- Backend API (Railway): [Backend](https://backendservice-production-d4c1.up.railway.app)

## Demo Video

- [Link to Demo Video](https://drive.google.com/file/d/16fwb-SvbcPWxLPQNDgZ1fS-YCHnMjZH4/view?usp=sharing)

## Why This Is an ML System

EveBloom is not only an application wrapper around static rules. It uses trained models and ML artifacts to generate probabilistic risk outputs and factor-level explanations.

- **Data-driven inference:** predictions are generated from trained models in `ml/`, not hardcoded thresholds alone.
- **Stage-specific modeling:** each clinical stage has a dedicated model strategy and output schema.
- **Probability-based outputs:** the system returns risk probabilities and levels to support triage-style screening.
- **Feature-level interpretability:** top risk factor signals are returned for explainability in the UI.
- **Model lifecycle support:** training scripts, evaluation reports, and metadata are part of the repo.

## Stage-Specific Inference Architecture

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

For a more detailed map of the repo, use [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md). It explains where the active runtime code lives and calls out folders such as `backend/api/routes/` that are retained for reference rather than used by the current app startup path.

## Product + ML Workflow

1. **Train and evaluate models** with scripts in `notebooks/`.
2. **Persist artifacts** in `ml/` (models, metadata, schemas).
3. **Serve inference** via FastAPI endpoints in `backend/main.py`.
4. **Capture follow-up assessments** for pregnancy/postpartum longitudinal views.
5. **Render explainable results** in the React dashboards.
6. **Review evaluation outputs** in `evaluation/` for confusion matrices, ROC/PR curves, and model comparison artifacts used in report documentation.

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

Public endpoints in this section can be called without authentication unless noted otherwise.

### Core

- `GET /`
- `GET /health`

### Authentication

- Public:
  - `POST /auth/signup`
  - `POST /auth/login`
- Protected (Bearer token required):
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

These endpoints are **protected**. Authenticate with `POST /auth/signup` or `POST /auth/login`, then send the returned bearer token in the `Authorization` header.

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

Run the active runtime pipelines:

```bash
python notebooks/07_infertility_fusion_training.py
python notebooks/run_pregnancy_v1_pipeline.py
python notebooks/run_postpartum_v1_pipeline.py
```

Historical infertility experimentation and baseline/tuning artifacts are also available:

```bash
python notebooks/run_infertility_v1_pipeline.py
```

Key outputs:

- Runtime artifacts in `ml/`
- Performance reports in `evaluation/*`

## Model Performance Summary

| Evaluation Lineage | Model / Runtime Role          | Test Accuracy | Test ROC-AUC | Weighted / Positive F1 | Report                                                                         |
| ------------------ | ----------------------------- | ------------: | -----------: | ---------------------: | ------------------------------------------------------------------------------ |
| Infertility v1     | GradientBoosting baseline/tuning evaluation |        0.9266 |       0.9662 |                 0.9203 | [INFERTILITY_V1_REPORT.md](evaluation/infertility_v1/INFERTILITY_V1_REPORT.md) |
| Pregnancy v1       | Threshold-tuned deployment model            |        0.9625 |       0.9997 |                 0.9515 | [PREGNANCY_V1_REPORT.md](evaluation/pregnancy_v1/PREGNANCY_V1_REPORT.md)       |
| Postpartum v1      | RandomForest screening model               |        0.7007 |       0.8561 |                 0.7050 | [POSTPARTUM_V1_REPORT.md](evaluation/postpartum_v1/POSTPARTUM_V1_REPORT.md)    |

Notes:

- The deployed infertility endpoint loads `ml/infertility_v2_*` dual-branch fusion artifacts. The checked-in `evaluation/infertility_v1/` directory documents the earlier baseline/tuning workflow that informed the infertility modeling line of work, so the infertility metrics below should be read as documented lineage evidence rather than the exact runtime endpoint scorecard.
- Pregnancy uses a decision threshold of `0.755` and emergency threshold of `0.90`.
- Postpartum uses a recall-priority decision threshold of `0.33` to maximise screening sensitivity for at-risk cases.
- These results are useful for technical evaluation, but they are **not** a substitute for external clinical validation.

### How to Interpret These Results

- **Infertility v1:** the high ROC-AUC (`0.9662`) and weighted F1 (`0.9203`) suggest strong class separation and balanced predictive performance on the symptom-based evaluation dataset. This is encouraging as a modeling baseline, but it comes from the earlier v1 experimentation line with `11` features and a `528 / 177` train-test split, not the deployed v2 fusion endpoint.
- **Pregnancy v1:** the near-perfect ROC-AUC (`0.9997`) shows the model separates high-risk and low-risk cases very strongly on the held-out test set, while the positive-class F1 (`0.9515`) reflects strong screening performance after threshold tuning. The threshold was deliberately set to support high-risk recall, so this result should be interpreted as strong internal test performance on the available `1169` cleaned rows rather than proof of real-world clinical generalization.
- **Postpartum v1:** the lower accuracy (`0.7007`) should be read together with the much higher at-risk recall (`0.9074`) and ROC-AUC (`0.8561`). This model is intentionally tuned as a screening-oriented classifier with a low decision threshold, which means it catches most at-risk cases but accepts more false positives; that tradeoff is reasonable for triage support, especially on a smaller `545`-row dataset.

## Testing

```bash
# Create the test database (first time only)
psql -U postgres -c "CREATE DATABASE reproductive_health_test;"

export DATABASE_URL="postgresql+psycopg2://postgres:<password>@localhost:5432/reproductive_health_test"
alembic -c backend/alembic.ini upgrade head
pytest
```

The automated tests in this repo validate:

- endpoint behavior and response schemas,
- authentication and token lifecycle behavior,
- persistence for pregnancy/postpartum follow-up records,
- prediction-service logic such as threshold handling and imputation.

The automated tests in this repo do **not** validate:

- clinical effectiveness,
- external generalization across populations,
- deployment-scale performance or load handling.


## Known Limitations

- The platform integrates three stage-specific models, but they are not jointly trained on patient-linked longitudinal data.
- Dataset provenance differs across stages, so performance should not be interpreted as Rwanda-specific clinical validity.
- External validation has not yet been completed.
- Load testing and realistic deployment-scale benchmarking are not included in this repository.
- The platform is intended for risk awareness and screening support, not diagnosis.

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

- Repository map: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- Backend details: [backend/README.md](backend/README.md)
- Frontend details: [frontend/README.md](frontend/README.md)
- ML training details: [notebooks/README.md](notebooks/README.md)
- Data details: [data/README.md](data/README.md)
- API reference: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- Example payloads: [docs/example_test_payloads.md](docs/example_test_payloads.md)
- Model performance: [evaluation/](evaluation/)

## Disclaimer

EveBloom provides screening-oriented ML risk estimates for decision support and educational use. It is not a diagnostic device and does not replace professional medical judgment or emergency care.
