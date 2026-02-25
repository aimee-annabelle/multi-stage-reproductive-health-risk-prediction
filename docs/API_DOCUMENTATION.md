# API Documentation

## Reproductive Health Risk Prediction API

Base URL (local): `http://localhost:8000`

The API currently provides:

- Stage 1 infertility risk prediction
- Stage 2 pregnancy risk prediction
- Stage 3 postpartum risk prediction
- Authentication
- User-linked pregnancy follow-up tracking and trend comparison

## Authentication

Auth token type: Bearer

Header format:

`Authorization: Bearer <access_token>`

### Endpoints

- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/logout`

## System Endpoints

- `GET /` - API map
- `GET /health` - service status
- `GET /model/info` - infertility model metadata
- `GET /model/info/pregnancy` - pregnancy model metadata
- `GET /model/info/postpartum` - postpartum model metadata

## Prediction Endpoints

### 1) `POST /predict/infertility`

#### Required fields

- `age` (15-60)
- `ever_cohabited` (0 or 1)
- `children_ever_born` (0-20)

#### Optional symptom fields (0 or 1)

- `irregular_menstrual_cycles`
- `chronic_pelvic_pain`
- `history_pelvic_infections`
- `hormonal_symptoms`
- `early_menopause_symptoms`
- `autoimmune_history`
- `reproductive_surgery_history`

#### Optional history fields

- `bmi` (10-8000; supports legacy BMI*100 encoding)
- `smoked_last_12mo` (0 or 1)
- `alcohol_last_12mo` (0 or 1)
- `age_at_first_marriage` (0-60, and must be `>= 8` when `ever_cohabited=1`)
- `months_since_first_cohabitation` (0-720)
- `months_since_last_sex` (0-2000)

#### Response keys

- `predicted_class`
- `probability_infertile`
- `probability_primary`
- `probability_secondary`
- `risk_level`
- `decision_threshold`
- `assessment_mode` (`symptom_only` | `history_only` | `fused`)
- `models_used`
- `top_risk_factors`
- `model_version`

### 2) `POST /predict/pregnancy`

#### Required fields

- `age` (10-65)
- `systolic_bp` (70-200)
- `diastolic` (40-140)

#### Optional fields

- `bs` (3-19)
- `body_temp` (95-105)
- `bmi` (0-60; values `<= 0` are treated as missing)
- `previous_complications` (0 or 1)
- `preexisting_diabetes` (0 or 1)
- `gestational_diabetes` (0 or 1)
- `mental_health` (0 or 1)
- `heart_rate` (40-140)

#### Response keys

- `predicted_class` (`low_pregnancy_risk` | `high_pregnancy_risk`)
- `probability_high_risk`
- `probability_low_risk`
- `risk_level` (`Low Risk` | `High Risk`)
- `decision_threshold`
- `emergency_threshold`
- `advise_hospital_visit`
- `advise_emergency_care`
- `hospital_advice`
- `emergency_advice`
- `top_risk_factors`
- `imputed_fields`
- `model_version`

### 3) `POST /predict/postpartum`

#### Optional fields

- `age_group`
- `baby_age_months` (0-24)
- `kgs_gained_during_pregnancy` (0-50)
- `marital_status`
- `household_income`
- `level_of_education`
- `residency`
- `comorbidities`
- `smoke_cigarettes` (supports `0/1`, `true/false`, `yes/no`)
- `smoke_shisha` (supports `0/1`, `true/false`, `yes/no`)
- `premature_labour` (supports `0/1`, `true/false`, `yes/no`)
- `healthy_baby` (supports `0/1`, `true/false`, `yes/no`)
- `baby_admitted_nicu` (supports `0/1`, `true/false`, `yes/no`)
- `baby_feeding_difficulties` (supports `0/1`, `true/false`, `yes/no`)
- `pregnancy_problem` (supports `0/1`, `true/false`, `yes/no`)
- `postnatal_problems` (supports `0/1`, `true/false`, `yes/no`)
- `natal_problems` (supports `0/1`, `true/false`, `yes/no`)
- `problems_with_husband` (supports `0/1`, `true/false`, `yes/no`)
- `financial_problems` (supports `0/1`, `true/false`, `yes/no`)
- `family_problems` (supports `0/1`, `true/false`, `yes/no`)
- `had_covid_19` (supports `0/1`, `true/false`, `yes/no`)
- `had_covid_19_vaccine` (supports `0/1`, `true/false`, `yes/no`)
- `access_to_healthcare_services` (supports `0/1`, `true/false`, `yes/no`)
- `aware_of_ppd_symptoms` (supports `0/1`, `true/false`, `yes/no`)
- `experienced_cultural_stigma_ppd` (supports `0/1`, `true/false`, `yes/no`)
- `received_support_or_treatment_ppd` (supports `0/1`, `true/false`, `yes/no`)
- `epds_laugh_and_funny_side`
- `epds_looked_forward_enjoyment`
- `epds_blamed_myself`
- `epds_anxious_or_worried`
- `epds_scared_or_panicky`
- `epds_things_getting_on_top`
- `epds_unhappy_difficulty_sleeping`
- `epds_sad_or_miserable`
- `epds_unhappy_crying`
- `epds_thought_of_harming_self`

At least one field must be provided.

#### Response keys

- `predicted_class` (`low_postpartum_risk` | `high_postpartum_risk`)
- `probability_high_risk`
- `probability_low_risk`
- `risk_level` (`Low Risk` | `High Risk`)
- `decision_threshold`
- `emergency_threshold`
- `advise_hospital_visit`
- `advise_emergency_care`
- `hospital_advice`
- `emergency_advice`
- `top_risk_factors`
- `imputed_fields`
- `model_version`

## Follow-Up Endpoints (Authenticated)

### 1) `POST /pregnancy/follow-up/assess`

Runs pregnancy prediction and stores the full assessment for the authenticated user.

Accepts all pregnancy request fields plus optional follow-up metadata:

- `gestational_age_weeks` (1-45)
- `visit_label` (1-120 chars)
- `notes` (max 1000 chars)

Returns a stored assessment record with:

- metadata (`assessment_id`, `created_at`, visit fields)
- raw input values
- prediction/probabilities
- thresholds and advice flags/messages
- `top_risk_factors`, `imputed_fields`, `model_version`

### 2) `GET /pregnancy/follow-up/history?limit=20`

Returns stored assessments (newest first).

Query params:

- `limit` (1-200, default 20)

Response keys:

- `total_records`
- `assessments` (array of stored assessment records)

### 3) `GET /pregnancy/follow-up/compare/latest`

Compares the latest assessment with the previous one.

Response keys:

- `latest_assessment_id`
- `previous_assessment_id`
- `latest_created_at`
- `previous_created_at`
- `latest_probability_high_risk`
- `previous_probability_high_risk`
- `probability_high_risk_delta`
- `trend` (`increased` | `decreased` | `stable`)
- `metric_deltas`

If fewer than 2 records exist, returns `422`.

### 4) `GET /pregnancy/follow-up/timeline/summary?limit=50`

Returns chronological trend data for charting and follow-up monitoring.

Query params:

- `limit` (1-500, default 50)

Response keys:

- `total_records`
- `time_span_days`
- `high_risk_count`
- `hospital_referral_count`
- `emergency_referral_count`
- `earliest_probability_high_risk`
- `latest_probability_high_risk`
- `probability_high_risk_change`
- `trend` (`increased` | `decreased` | `stable` | `null`)
- `points` (oldest to newest)

## Example Requests

### Signup

```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test.user@example.com",
    "password": "StrongPass123"
  }'
```

### Pregnancy prediction

```bash
curl -X POST "http://localhost:8000/predict/pregnancy" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 31,
    "systolic_bp": 140,
    "diastolic": 90,
    "bs": 10.2,
    "body_temp": 99.0,
    "bmi": 27.8,
    "previous_complications": 1,
    "preexisting_diabetes": 1,
    "gestational_diabetes": 0,
    "mental_health": 1,
    "heart_rate": 86
  }'
```

### Postpartum prediction

```bash
curl -X POST "http://localhost:8000/predict/postpartum" \
  -H "Content-Type: application/json" \
  -d '{
    "baby_age_months": 3,
    "smoke_cigarettes": 0,
    "postnatal_problems": 1,
    "epds_anxious_or_worried": "Yes, very often",
    "epds_sad_or_miserable": "Yes, quite often",
    "epds_thought_of_harming_self": "Sometimes"
  }'
```

### Follow-up assess (authenticated)

```bash
curl -X POST "http://localhost:8000/pregnancy/follow-up/assess" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "gestational_age_weeks": 28,
    "visit_label": "ANC Visit 2",
    "notes": "Follow-up visit",
    "age": 28,
    "systolic_bp": 140,
    "diastolic": 90,
    "bs": 8.8,
    "body_temp": 99.1,
    "bmi": 25.1,
    "previous_complications": 1,
    "preexisting_diabetes": 0,
    "gestational_diabetes": 0,
    "mental_health": 1,
    "heart_rate": 82
  }'
```

## Error Semantics

- `401`: missing/invalid/expired auth token
- `409`: duplicate email on signup
- `422`: validation failure or insufficient comparison history
- `503`: required model artifacts missing
- `500`: unexpected server error

## Database Notes

PostgreSQL stores authentication and follow-up data.

Migration command:

```bash
alembic -c backend/alembic.ini upgrade head
```
