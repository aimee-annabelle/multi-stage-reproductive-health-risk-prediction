# Backend - Multi-Stage Reproductive Health Risk Prediction

FastAPI backend for the Multi-Stage Reproductive Health Risk Prediction system.

## Project Structure

```
backend/
├── api/
│   └── routes/
│       ├── health.py      # Health check endpoints
│       ├── prediction.py  # Prediction endpoints
│       └── model.py       # Model management
├── services/
│   ├── prediction_service.py    # Prediction logic
│   ├── preprocessing_service.py # Data preprocessing
│   └── model_service.py         # Model management
├── models/
│   ├── request.py        # Request schemas
│   └── response.py       # Response schemas
├── utils/
│   └── config.py         # Config, logging, error handling
├── middleware/
│   └── error_handler.py  # CORS & error handling
├── tests/
│   ├── unit/
│   │   └── test_services.py
│   ├── integration/
│   │   └── test_api.py
│   └── conftest.py
├── main.py
├── requirements.txt
└── .env.example
```

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies from root
pip install -r ../requirements.txt

# Configure environment
cp .env.example .env

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
pytest                    # Run all tests
pytest --cov=.           # With coverage
```
