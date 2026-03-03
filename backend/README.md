# Backend - EveBloom ML Inference and Tracking API

This backend is the operational ML serving layer for EveBloom. It exposes model inference endpoints, authentication/session management, and follow-up storage endpoints used by longitudinal dashboards.

## Backend Role in the ML System

The backend is where trained artifacts become usable clinical-screening services.

- Loads persisted model artifacts from `ml/` during startup
- Validates and preprocesses incoming payloads
- Runs stage-specific prediction logic
- Returns risk probabilities, classes, and explanatory factors
- Stores follow-up assessments for trend analysis over time

## Tech Stack
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- scikit-learn artifact loading/inference

## Code Structure

```text
backend/
├── alembic/
│   └── versions/
├── db/
│   ├── models.py
│   └── session.py
├── models/
│   ├── request.py
│   └── response.py
├── services/
│   ├── model_service.py             # artifact loading + metadata
│   ├── prediction_service.py        # core inference functions
│   ├── pregnancy_tracking_service.py
│   └── postpartum_tracking_service.py
├── tests/
│   ├── integration/
│   └── unit/
├── main.py                          # route registration + startup lifecycle
└── .env.example
```

## Local Run

From repository root:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp backend/.env.example backend/.env
alembic -c backend/alembic.ini upgrade head
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

API docs:
- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

## Environment Configuration

Use `DATABASE_URL` for deployed/runtime environments.

Fallback database variables:
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_SSLMODE`

Other important settings:
- `CORS_ORIGINS`
- `HOST`
- `PORT`

## Endpoint Groups

### Authentication
- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/logout`

### Inference APIs
- `POST /predict/infertility`
- `POST /predict/pregnancy`
- `POST /predict/postpartum`

### Model Metadata
- `GET /model/info`
- `GET /model/info/pregnancy`
- `GET /model/info/postpartum`

### Follow-Up Tracking
- Pregnancy:
  - `POST /pregnancy/follow-up/assess`
  - `GET /pregnancy/follow-up/history`
  - `GET /pregnancy/follow-up/compare/latest`
  - `GET /pregnancy/follow-up/timeline/summary`
- Postpartum:
  - `POST /postpartum/follow-up/assess`
  - `GET /postpartum/follow-up/history`
  - `GET /postpartum/follow-up/timeline/summary`

## Migrations

```bash
alembic -c backend/alembic.ini upgrade head
alembic -c backend/alembic.ini revision --autogenerate -m "describe change"
alembic -c backend/alembic.ini downgrade -1
```

## Testing

Integration tests require PostgreSQL.

```bash
export DATABASE_URL="postgresql+psycopg2://postgres:<password>@localhost:5432/reproductive_health_test"
alembic -c backend/alembic.ini upgrade head
pytest
pytest --cov=backend
```

## Docker

- Backend image definition: `backend/Dockerfile`
- Full stack runtime: root `docker-compose.yml`

```bash
docker compose up --build
```
