# API Documentation

## Infertility Risk Prediction API

Unified FastAPI documentation for infertility risk prediction using a cohabitation-aware dual-branch model.

## Base URL

- Local: `http://localhost:8000`
- Production: `[To be deployed]`

## Database

Authentication is persisted in PostgreSQL (not SQLite/NoSQL).

- Use `DATABASE_URL` for deployed environments.
- Or set local connection values: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_SSLMODE`.
- Apply schema migrations with Alembic: `alembic -c backend/alembic.ini upgrade head`.

## Authentication

The API now supports token-based authentication for user accounts:

- `POST /auth/signup` to create a new account
- `POST /auth/login` to authenticate and receive a bearer token
- `GET /auth/me` to fetch the current authenticated user
- `POST /auth/logout` to invalidate the current bearer token

Use the token in requests:

`Authorization: Bearer <access_token>`

## API Endpoints

### 1. Root

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

Returns service health and model load status.

**Response (200)**

```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### 3. Model Information

**GET** `/model/info`

Returns fusion model metadata.

**Response (200)**

```json
{
  "model_version": "2.0.0",
  "pipeline_type": "dual_branch_fusion",
  "target_name": "infertile",
  "training_date_utc": "2026-02-16T10:00:00+00:00",
  "recall_target": 0.9,
  "thresholds": {
    "symptom": 0.505,
    "history": 0.75,
    "fused": 0.6354
  },
  "fusion_weights": {
    "symptom": 0.4679,
    "history": 0.5321
  },
  "branch_metrics": {
    "symptom": {
      "accuracy": 0.8531,
      "precision": 0.9103,
      "recall": 0.9103,
      "f1": 0.9103,
      "roc_auc": 0.8675
    },
    "history": {
      "accuracy": 0.9294,
      "precision": 0.9669,
      "recall": 0.9044,
      "f1": 0.9346,
      "roc_auc": 0.9862
    }
  }
}
```

### 4. Predict Infertility Risk

**POST** `/predict/infertility`

Unified endpoint that routes inference based on cohabitation context:

- `ever_cohabited = 0`: symptom-only branch
- `ever_cohabited = 1`: history-only or fused prediction depending on provided symptom fields

Maternal dataset is excluded from this infertility endpoint.

## Request Schema

### Required fields

- `age` (integer)
- `ever_cohabited` (integer, `0` or `1`)
- `children_ever_born` (integer)

### Optional symptom fields

- `irregular_menstrual_cycles`
- `chronic_pelvic_pain`
- `history_pelvic_infections`
- `hormonal_symptoms`
- `early_menopause_symptoms`
- `autoimmune_history`
- `reproductive_surgery_history`

Important rule for never-cohabited users:

- If `ever_cohabited = 0`, you must provide at least one symptom field above.
- If none are provided, the API returns `422` because no model branch can be evaluated.

### Optional history fields

- `bmi`
- `smoked_last_12mo`
- `alcohol_last_12mo`
- `age_at_first_marriage`
- `months_since_first_cohabitation`
- `months_since_last_sex`

If history fields are omitted, model-side imputation is applied.

## Request Example

```json
{
  "age": 28,
  "ever_cohabited": 0,
  "children_ever_born": 0,
  "irregular_menstrual_cycles": 1,
  "chronic_pelvic_pain": 1
}
```

## Response Example

```json
{
  "predicted_class": "primary_infertility_risk",
  "probability_infertile": 0.812341,
  "probability_primary": 0.812341,
  "probability_secondary": 0.0,
  "risk_level": "High Risk",
  "decision_threshold": 0.505,
  "assessment_mode": "symptom_only",
  "models_used": ["symptom"],
  "top_risk_factors": {
    "irregular_menstrual_cycles": 0.113201,
    "chronic_pelvic_pain": 0.091177,
    "age": 0.082011
  },
  "model_version": "2.0.0"
}
```

## Class Rules

- `no_infertility_risk`: `probability_infertile < decision_threshold`
- `primary_infertility_risk`: infertile-positive and `children_ever_born == 0`
- `secondary_infertility_risk`: infertile-positive and `children_ever_born > 0`

## Error Responses

- `422`: validation error or incompatible input context
- `503`: model artifacts unavailable
- `500`: inference/internal error

### Example 422 Case (Never-Cohabited With No Symptoms)

Request:

```json
{
  "age": 28,
  "ever_cohabited": 0,
  "children_ever_born": 0
}
```

Response:

```json
{
  "detail": "No model branch can be evaluated with the provided input. For never-cohabited users, provide at least one symptom field."
}
```

## Usage (cURL)

```bash
curl -X POST "http://localhost:8000/predict/infertility" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 28,
    "ever_cohabited": 0,
    "children_ever_born": 0,
    "irregular_menstrual_cycles": 1,
    "chronic_pelvic_pain": 1
  }'
```
