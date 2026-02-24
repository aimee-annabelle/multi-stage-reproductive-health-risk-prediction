# Backend - Reproductive Health Risk Prediction API

FastAPI backend for infertility, pregnancy, and postpartum risk prediction, plus authenticated maternal follow-up tracking.

## Current Backend Layout

```text
backend/
├── alembic/
│   └── versions/
├── api/
│   └── routes/                 # legacy/experimental route modules
├── db/
│   ├── base.py
│   ├── models.py
│   └── session.py
├── models/
│   ├── request.py
│   └── response.py
├── services/
│   ├── model_service.py
│   ├── prediction_service.py
│   ├── pregnancy_tracking_service.py
│   └── preprocessing_service.py
├── tests/
│   ├── integration/
│   ├── unit/
│   └── conftest.py
├── main.py                     # active route registration and app startup
├── alembic.ini
└── .env.example
```

## Setup

```bash
# from repository root
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp backend/.env.example backend/.env
```

Set database config in `backend/.env`:

- `DATABASE_URL` (recommended), or
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_SSLMODE`

Apply migrations:

```bash
alembic -c backend/alembic.ini upgrade head
```

Run API:

```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Active Endpoints

- `GET /`
- `GET /health`
- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/logout`
- `GET /model/info`
- `GET /model/info/pregnancy`
- `GET /model/info/postpartum`
- `POST /predict/infertility`
- `POST /predict/pregnancy`
- `POST /predict/postpartum`
- `POST /pregnancy/follow-up/assess`
- `GET /pregnancy/follow-up/history`
- `GET /pregnancy/follow-up/compare/latest`
- `GET /pregnancy/follow-up/timeline/summary`

## Database

PostgreSQL is used for:

- `users`
- `sessions`
- `pregnancy_assessments`

Migrations:

```bash
alembic -c backend/alembic.ini upgrade head
alembic -c backend/alembic.ini revision --autogenerate -m "describe change"
alembic -c backend/alembic.ini downgrade -1
```

## Testing

Integration tests are PostgreSQL-only.

```bash
export DATABASE_URL="postgresql+psycopg2://postgres:<password>@localhost:5432/reproductive_health_test"
alembic -c backend/alembic.ini upgrade head
pytest
pytest --cov=backend
```

## API Docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Detailed endpoint docs: `docs/API_DOCUMENTATION.md`
