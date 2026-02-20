# API Documentation

## Infertility Risk Prediction API

This document provides comprehensive documentation for the FastAPI-based infertility risk prediction system.

## Base URL

**Local Development**: `http://localhost:8000`
**Production**: `[To be deployed]`

## Authentication

The API now supports token-based authentication for user accounts:

- `POST /auth/signup` to create a new account
- `POST /auth/login` to authenticate and receive a bearer token
- `GET /auth/me` to fetch the current authenticated user
- `POST /auth/logout` to invalidate the current bearer token

Use the token in requests:

`Authorization: Bearer <access_token>`

## API Endpoints

### 1. Root Endpoint

**GET** `/`

Returns API information and available endpoints.

**Response (200 OK)**:

```json
{
  "message": "Reproductive Health Risk Prediction API",
  "endpoints": {
    "predict": "/predict/infertility",
    "health": "/health",
    "model_info": "/model/info",
    "signup": "/auth/signup",
    "login": "/auth/login",
    "me": "/auth/me",
    "logout": "/auth/logout",
    "docs": "/docs"
  }
}
```

### 2. Health Check

**GET** `/health`

Check if the API and models are loaded properly.

**Response (200 OK)**:

```json
{
  "status": "healthy",
  "model_loaded": true,
  "scaler_loaded": true
}
```


### 3. Model Information

**GET** `/model/info`

Get detailed information about the trained model, including performance metrics.

**Response (200 OK)**:

```json
{
  "model_name": "Random Forest Classifier",
  "trained_date": "2026-02-05",
  "features": [
    "Age",
    "Irregular_Menstrual_Cycles",
    "Hormonal_Imbalances",
    "Pelvic_Infections",
    "Endometriosis",
    "Uterine_Fibroids",
    "Blocked_Fallopian_Tubes",
    "Obesity",
    "Smoking_or_Alcohol",
    "Age_Related_Factors",
    "Male_Factor"
  ],
  "performance_metrics": {
    "accuracy": 0.9245,
    "precision": 0.8876,
    "recall": 0.9432,
    "f1_score": 0.9145,
    "roc_auc": 0.9567
  },
  "training_info": {
    "training_samples": 493,
    "test_samples": 212,
    "smote_applied": true,
    "feature_scaling": "StandardScaler"
  }
}
```

### 4. Predict Infertility Risk (Main Endpoint)

**POST** `/predict/infertility`

Predict infertility risk based on patient symptoms and health indicators.

**Request Body**:

```json
{
  "Age": 32,
  "Irregular_Menstrual_Cycles": 1,
  "Hormonal_Imbalances": 1,
  "Pelvic_Infections": 0,
  "Endometriosis": 0,
  "Uterine_Fibroids": 0,
  "Blocked_Fallopian_Tubes": 0,
  "Obesity": 0,
  "Smoking_or_Alcohol": 0,
  "Age_Related_Factors": 0,
  "Male_Factor": 0
}
```

**Field Descriptions**:
| Field | Type | Range | Description |
|-------|------|-------|-------------|
| Age | integer | 18-100 | Patient's age in years |
| Irregular_Menstrual_Cycles | integer | 0-1 | 0 = No, 1 = Yes |
| Hormonal_Imbalances | integer | 0-1 | 0 = No, 1 = Yes |
| Pelvic_Infections | integer | 0-1 | 0 = No, 1 = Yes |
| Endometriosis | integer | 0-1 | 0 = No, 1 = Yes |
| Uterine_Fibroids | integer | 0-1 | 0 = No, 1 = Yes |
| Blocked_Fallopian_Tubes | integer | 0-1 | 0 = No, 1 = Yes |
| Obesity | integer | 0-1 | 0 = No, 1 = Yes |
| Smoking_or_Alcohol | integer | 0-1 | 0 = No, 1 = Yes |
| Age_Related_Factors | integer | 0-1 | 0 = No, 1 = Yes |
| Male_Factor | integer | 0-1 | 0 = No, 1 = Yes |

**Response (200 OK)**:

```json
{
  "prediction": "At Risk",
  "risk_level": "High Risk",
  "probability": 0.8542,
  "confidence": "High Confidence",
  "message": "Patient shows multiple risk factors for infertility. Medical consultation strongly recommended.",
  "feature_importance": {
    "Irregular_Menstrual_Cycles": 0.2341,
    "Hormonal_Imbalances": 0.1987,
    "Age": 0.1654,
    "Endometriosis": 0.1432,
    "Blocked_Fallopian_Tubes": 0.1234
  }
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| prediction | string | "At Risk" or "No Risk" |
| risk_level | string | "High Risk", "Moderate Risk", or "Low Risk" |
| probability | float | Probability of being at risk (0.0-1.0) |
| confidence | string | Model confidence level |
| message | string | Interpretation and recommendation |
| feature_importance | object | Top 5 features contributing to prediction |

**Risk Level Classification**:

- **High Risk** (probability ≥ 0.7): Multiple risk factors, immediate medical consultation recommended
- **Moderate Risk** (0.5 ≤ probability < 0.7): Some risk factors, consider consulting healthcare provider
- **Low Risk** (probability < 0.5): Minimal risk factors based on provided symptoms

**Error Responses**:

**400 Bad Request** - Invalid input data:

```json
{
  "detail": [
    {
      "loc": ["body", "Age"],
      "msg": "ensure this value is greater than or equal to 18",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

**500 Internal Server Error** - Server or model error:

```json
{
  "detail": "Prediction error: [error message]"
}
```


## Usage Examples

### Using cURL

```bash
curl -X POST "http://localhost:8000/predict/infertility" \
  -H "Content-Type: application/json" \
  -d '{
    "Age": 32,
    "Irregular_Menstrual_Cycles": 1,
    "Hormonal_Imbalances": 1,
    "Pelvic_Infections": 0,
    "Endometriosis": 0,
    "Uterine_Fibroids": 0,
    "Blocked_Fallopian_Tubes": 0,
    "Obesity": 0,
    "Smoking_or_Alcohol": 0,
    "Age_Related_Factors": 0,
    "Male_Factor": 0
  }'
```

### Using Python requests

```python
import requests

url = "http://localhost:8000/predict/infertility"
payload = {
    "Age": 32,
    "Irregular_Menstrual_Cycles": 1,
    "Hormonal_Imbalances": 1,
    "Pelvic_Infections": 0,
    "Endometriosis": 0,
    "Uterine_Fibroids": 0,
    "Blocked_Fallopian_Tubes": 0,
    "Obesity": 0,
    "Smoking_or_Alcohol": 0,
    "Age_Related_Factors": 0,
    "Male_Factor": 0
}

response = requests.post(url, json=payload)
print(response.json())
```

### Using JavaScript fetch

```javascript
const url = "http://localhost:8000/predict/infertility";
const data = {
  Age: 32,
  Irregular_Menstrual_Cycles: 1,
  Hormonal_Imbalances: 1,
  Pelvic_Infections: 0,
  Endometriosis: 0,
  Uterine_Fibroids: 0,
  Blocked_Fallopian_Tubes: 0,
  Obesity: 0,
  Smoking_or_Alcohol: 0,
  Age_Related_Factors: 0,
  Male_Factor: 0,
};

fetch(url, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(data),
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

## Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:

- View all endpoints and their specifications
- Test endpoints directly from the browser
- See request/response schemas
- Download OpenAPI specification

## CORS Configuration

The API currently allows all origins (`allow_origins=["*"]`). For production, restrict to specific domains:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Rate Limiting

For production deployment, consider implementing rate limiting:

```python
# Example using slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/predict/infertility")
@limiter.limit("10/minute")
async def predict_infertility(request: Request, patient: PatientSymptoms):
    # ... endpoint logic
```

## Best Practices

1. **Input Validation**: All inputs are validated using Pydantic models
2. **Error Handling**: Comprehensive error messages for debugging
3. **Model Loading**: Models loaded once at startup for efficiency
4. **Feature Importance**: Provides interpretability for healthcare decisions
5. **Risk Stratification**: Three-tier risk classification for actionable insights

## Security Considerations

For production deployment:

1. **Enable HTTPS**: Use SSL/TLS certificates
2. **Authentication**: Implement API keys or OAuth2
3. **Rate Limiting**: Prevent abuse and ensure availability
4. **Input Sanitization**: Already handled by Pydantic
5. **Logging**: Log all predictions for audit trails
6. **Environment Variables**: Store sensitive configurations securely
7. **CORS**: Restrict to specific trusted domains

## Model Versioning

Current model version: **v1.0.0**

Model metadata includes:

- Training date
- Performance metrics
- Feature list
- Preprocessing steps

For model updates:

1. Train new model with updated notebook
2. Save to `ml/` directory with version tag
3. Update model loading in `backend/main.py`
4. Document changes in release notes

## Support

For issues or questions:

- GitHub Issues: https://github.com/aimee-annabelle/multi-stage-reproductive-health-risk-prediction/issues
- Documentation: This file and README.md
- Interactive Docs: http://localhost:8000/docs
