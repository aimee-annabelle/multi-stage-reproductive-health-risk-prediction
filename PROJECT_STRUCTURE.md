# Project Structure

## Complete Directory Structure

```
multi-stage-reproductive-health-risk-prediction/
│
├── backend/                          # FastAPI Backend
│   ├── api/
│   │   └── routes/
│   │       ├── health.py            # Health check
│   │       ├── prediction.py        # Predictions
│   │       └── model.py             # Model management
│   ├── services/
│   │   ├── prediction_service.py    # Prediction logic
│   │   ├── preprocessing_service.py # Preprocessing
│   │   └── model_service.py         # Model operations
│   ├── models/
│   │   ├── request.py               # Request schemas
│   │   └── response.py              # Response schemas
│   ├── utils/
│   │   └── config.py                # Config & utilities
│   ├── middleware/
│   │   └── error_handler.py         # CORS & errors
│   ├── tests/
│   │   ├── unit/
│   │   │   └── test_services.py
│   │   ├── integration/
│   │   │   └── test_api.py
│   │   └── conftest.py
│   ├── logs/
│   ├── main.py
│   ├── .env.example
│   └── README.md
│
├── notebooks/                        # ML Pipeline
│   ├── 01_exploratory_data_analysis.py
│   ├── 02_feature_engineering.py
│   ├── 03_data_preprocessing.py
│   ├── 04_model_training.py
│   ├── 05_hyperparameter_tuning.py
│   ├── 06_model_evaluation.py
│   ├── infertility_risk_prediction.ipynb
│   └── README.md
│
├── ml/                              # ML Models
│   ├── infertility_model.pkl
│   ├── scaler.pkl
│   ├── feature_names.pkl
│   └── model_metadata.pkl
│
├── data/                            # Data
│   ├── raw/
│   ├── processed/
│   └── dhs_data_cleaning.py
│
├── frontend/                        # React Frontend
│   └── ...
│
├── deployment/                      # Deployment
├── docs/                            # Documentation
├── evaluation/                      # Evaluation
│
└── README.md
```

## Key Components

### Backend (23 files)
- **3 API routes**: health, prediction, model
- **3 services**: prediction, preprocessing, model
- **2 schemas**: request, response
- **1 utility**: config (includes logging, error handling)
- **1 middleware**: error_handler (includes CORS)
- **3 test files**: services, API, fixtures

### Notebooks (6 files)
- **Data prep (1-3)**: EDA, feature engineering, preprocessing
- **Modeling (4-6)**: training, tuning, evaluation