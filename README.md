# Multi-Stage Reproductive Health Risk Prediction System

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/aimee-annabelle/multi-stage-reproductive-health-risk-prediction)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

This project implements a multi-stage backend for reproductive health risk support:

- Stage 1: Infertility risk prediction (dual-branch fusion)
- Stage 2: Pregnancy risk prediction (single-model binary classifier)
- Stage 3: Postpartum risk prediction (single-model binary classifier)
- Authenticated pregnancy follow-up tracking over time

The API is built with FastAPI and SQLAlchemy, and uses persisted model artifacts from the `ml/` directory.

## What Is Implemented

### Stage 1: Infertility Prediction

- Endpoint: `POST /predict/infertility`
- Model strategy: dual-branch fusion (`symptom`, `history`, or `fused` mode)
- Output classes:
  - `no_infertility_risk`
  - `primary_infertility_risk`
  - `secondary_infertility_risk`
- Metadata endpoint: `GET /model/info`

### Stage 2: Pregnancy Prediction

- Endpoint: `POST /predict/pregnancy`
- Binary output classes:
  - `low_pregnancy_risk`
  - `high_pregnancy_risk`
- Supports partial payloads with model-side imputation
- Returns:
  - decision threshold
  - emergency threshold
  - top risk factors
  - referral/emergency advice flags and messages
- Metadata endpoint: `GET /model/info/pregnancy`

### Stage 3: Postpartum Prediction

- Endpoint: `POST /predict/postpartum`
- Binary output classes:
  - `low_postpartum_risk`
  - `high_postpartum_risk`
- Supports partial payloads with model-side imputation
- Returns:
  - decision threshold
  - emergency threshold
  - top risk factors
  - referral/emergency advice flags and messages
- Metadata endpoint: `GET /model/info/postpartum`

### Authentication and Follow-Up Tracking

- Auth endpoints:
  - `POST /auth/signup`
  - `POST /auth/login`
  - `GET /auth/me`
  - `POST /auth/logout`
- User-linked pregnancy follow-up endpoints:
  - `POST /pregnancy/follow-up/assess`
  - `GET /pregnancy/follow-up/history`
  - `GET /pregnancy/follow-up/compare/latest`
  - `GET /pregnancy/follow-up/timeline/summary`

All follow-up endpoints require `Authorization: Bearer <access_token>`.

## Repository Structure

```text
multi-stage-reproductive-health-risk-prediction/
├── backend/
├── data/
│   └── processed/
├── docs/
├── evaluation/
│   ├── infertility_v1/
│   ├── pregnancy_v1/
│   └── postpartum_v1/
├── frontend/
├── ml/
├── notebooks/
├── requirements.txt
└── README.md
```

For a more detailed tree, see `PROJECT_STRUCTURE.md`.

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL
- Node.js 20+ (for frontend)

### 1. Install Python dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure backend environment

```bash
cp backend/.env.example backend/.env
```

Use either:
- `DATABASE_URL` (recommended), or
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_SSLMODE`

### 3. Run migrations

```bash
alembic -c backend/alembic.ini upgrade head
```

### 4. Start backend

```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Docs will be available at `http://localhost:8000/docs`.

### 5. Start frontend (optional)

```bash
cd frontend
npm install
npm run dev
```

Frontend dev URL: `http://localhost:5173`

## Model Training and Evaluation

### Train infertility fusion artifacts

```bash
python notebooks/07_infertility_fusion_training.py
```

### Train pregnancy v1 artifacts

```bash
python notebooks/08_pregnancy_risk_training.py
```

### Train postpartum v1 artifacts

```bash
python notebooks/run_postpartum_v1_pipeline.py
```

### Generate evaluation reports

```bash
python notebooks/run_infertility_v1_pipeline.py
python notebooks/run_pregnancy_v1_pipeline.py
python notebooks/run_postpartum_v1_pipeline.py
```

## API Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/` | API map |
| GET | `/health` | Health check |
| POST | `/auth/signup` | Register user |
| POST | `/auth/login` | Login user |
| GET | `/auth/me` | Get current user |
| POST | `/auth/logout` | Logout |
| GET | `/model/info` | Infertility model metadata |
| GET | `/model/info/pregnancy` | Pregnancy model metadata |
| GET | `/model/info/postpartum` | Postpartum model metadata |
| POST | `/predict/infertility` | Infertility risk prediction |
| POST | `/predict/pregnancy` | Pregnancy risk prediction |
| POST | `/predict/postpartum` | Postpartum risk prediction |
| POST | `/pregnancy/follow-up/assess` | Predict + store pregnancy assessment |
| GET | `/pregnancy/follow-up/history` | List stored pregnancy assessments |
| GET | `/pregnancy/follow-up/compare/latest` | Compare latest two assessments |
| GET | `/pregnancy/follow-up/timeline/summary` | Timeline summary for trend monitoring |

## Testing

Integration tests are PostgreSQL-only.

```bash
export DATABASE_URL="postgresql+psycopg2://postgres:<password>@localhost:5432/reproductive_health_test"
alembic -c backend/alembic.ini upgrade head
pytest
```

## Artifacts and Reports

### ML artifacts (`ml/`)

- `infertility_v2_symptom_model.pkl`
- `infertility_v2_history_model.pkl`
- `infertility_v2_metadata.pkl`
- `infertility_v2_feature_schema.pkl`
- `pregnancy_v1_model.pkl`
- `pregnancy_v1_metadata.pkl`
- `pregnancy_v1_feature_schema.pkl`
- `postpartum_v1_model.pkl`
- `postpartum_v1_metadata.pkl`
- `postpartum_v1_feature_schema.pkl`

### Evaluation reports

- `evaluation/infertility_v1/INFERTILITY_V1_REPORT.md`
- `evaluation/pregnancy_v1/PREGNANCY_V1_REPORT.md`
- `evaluation/postpartum_v1/POSTPARTUM_V1_REPORT.md`

## Datasets Used

- `data/processed/Female infertility.csv`
- `data/processed/dhs_cleaned.csv`
- `data/processed/pregnancy-risk-dataset.csv`
- `data/processed/postpartum_omv_cleaned.csv`

## Disclaimer

This system is for educational and screening-support purposes and does not replace professional medical diagnosis or emergency care.
