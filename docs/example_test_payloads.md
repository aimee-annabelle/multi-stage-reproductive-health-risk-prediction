# Example Test Payloads for API Endpoints

This file provides example JSON payloads you can use to manually test the API across infertility, pregnancy, and postpartum risk prediction.

These are **illustrative** and designed to likely produce contrasting risk levels (low vs higher risk), but the exact predicted class will depend on the trained model parameters and thresholds.

---

## 1. Infertility Risk Prediction (`POST /predict/infertility`)

### 1.1 Likely Low Infertility Risk

```json
{
  "age": 29,
  "ever_cohabited": 1,
  "children_ever_born": 2,
  "irregular_menstrual_cycles": 0,
  "chronic_pelvic_pain": 0,
  "history_pelvic_infections": 0,
  "hormonal_symptoms": 0,
  "early_menopause_symptoms": 0,
  "autoimmune_history": 0,
  "reproductive_surgery_history": 0,
  "bmi": 23.5,
  "smoked_last_12mo": 0,
  "alcohol_last_12mo": 0,
  "age_at_first_marriage": 23,
  "months_since_first_cohabitation": 72,
  "months_since_last_sex": 1
}
```
3
### 1.2 Likely Primary Infertility Risk (symptom-heavy, no prior births)

```json
{
  "age": 34,
  "ever_cohabited": 1,
  "children_ever_born": 0,
  "irregular_menstrual_cycles": 1,
  "chronic_pelvic_pain": 1,
  "history_pelvic_infections": 1,
  "hormonal_symptoms": 1,
  "early_menopause_symptoms": 0,
  "autoimmune_history": 0,
  "reproductive_surgery_history": 1,
  "bmi": 31.2,
  "smoked_last_12mo": 1,
  "alcohol_last_12mo": 1,
  "age_at_first_marriage": 25,
  "months_since_first_cohabitation": 96,
  "months_since_last_sex": 2
}
```

### 1.3 Likely Secondary Infertility Risk (history branch focus)

```json
{
  "age": 38,
  "ever_cohabited": 1,
  "children_ever_born": 3,
  "irregular_menstrual_cycles": 1,
  "chronic_pelvic_pain": 0,
  "history_pelvic_infections": 1,
  "hormonal_symptoms": 0,
  "early_menopause_symptoms": 0,
  "autoimmune_history": 0,
  "reproductive_surgery_history": 0,
  "bmi": 29.0,
  "smoked_last_12mo": 0,
  "alcohol_last_12mo": 1,
  "age_at_first_marriage": 21,
  "months_since_first_cohabitation": 180,
  "months_since_last_sex": 3
}
```

### 1.4 Never-Cohabited, Symptom-Only Assessment

```json
{
  "age": 26,
  "ever_cohabited": 0,
  "children_ever_born": 0,
  "irregular_menstrual_cycles": 1,
  "chronic_pelvic_pain": 1,
  "history_pelvic_infections": 1
}
```

---

## 2. Pregnancy Risk Prediction (`POST /predict/pregnancy`)

### 2.1 Likely Low Pregnancy Risk

```json
{
  "age": 27,
  "systolic_bp": 112.0,
  "diastolic": 72.0,
  "bs": 5.2,
  "body_temp": 98.4,
  "bmi": 24.0,
  "previous_complications": 0,
  "preexisting_diabetes": 0,
  "gestational_diabetes": 0,
  "mental_health": 0,
  "heart_rate": 78.0
}
```

### 2.2 Likely High Pregnancy Risk (near decision threshold)

```json
{
  "age": 34,
  "systolic_bp": 150.0,
  "diastolic": 96.0,
  "bs": 11.5,
  "body_temp": 99.8,
  "bmi": 33.0,
  "previous_complications": 1,
  "preexisting_diabetes": 1,
  "gestational_diabetes": 1,
  "mental_health": 1,
  "heart_rate": 100.0
}
```

### 2.3 Likely Emergency-Level Pregnancy Risk (around/above emergency threshold)

```json
{
  "age": 39,
  "systolic_bp": 170.0,
  "diastolic": 110.0,
  "bs": 15.8,
  "body_temp": 100.8,
  "bmi": 37.5,
  "previous_complications": 1,
  "preexisting_diabetes": 1,
  "gestational_diabetes": 1,
  "mental_health": 1,
  "heart_rate": 118.0
}
```

### 2.4 Minimal Payload (triggers imputation)

```json
{
  "age": 25,
  "systolic_bp": 120.0,
  "diastolic": 80.0
}
```

---

## 3. Postpartum Risk Prediction (`POST /predict/postpartum`)

### 3.1 Likely Low Postpartum Risk

```json
{
  "age_group": "Below 25",
  "baby_age_months": 4.0,
  "kgs_gained_during_pregnancy": 11.0,
  "marital_status": "Married",
  "household_income": "Middle",
  "level_of_education": "University",
  "residency": "Urban",
  "comorbidities": "None",
  "smoke_cigarettes": 0,
  "smoke_shisha": 0,
  "premature_labour": 0,
  "healthy_baby": 1,
  "baby_admitted_nicu": 0,
  "baby_feeding_difficulties": 0,
  "pregnancy_problem": 0,
  "postnatal_problems": 0,
  "natal_problems": 0,
  "problems_with_husband": 0,
  "financial_problems": 0,
  "family_problems": 0,
  "had_covid_19": 0,
  "had_covid_19_vaccine": 1,
  "access_to_healthcare_services": 1,
  "aware_of_ppd_symptoms": 1,
  "experienced_cultural_stigma_ppd": 0,
  "received_support_or_treatment_ppd": 1,
  "epds_laugh_and_funny_side": "As much as I always could",
  "epds_looked_forward_enjoyment": "As much as I ever did",
  "epds_blamed_myself": "No, never",
  "epds_anxious_or_worried": "No, not at all",
  "epds_scared_or_panicky": "No, not at all",
  "epds_things_getting_on_top": "No, most of the time I have coped quite well",
  "epds_unhappy_difficulty_sleeping": "No, not at all",
  "epds_sad_or_miserable": "No, not at all",
  "epds_unhappy_crying": "No, never",
  "epds_thought_of_harming_self": "Never"
}
```

### 3.2 Likely High Postpartum Risk (decision-level)

```json
{
  "age_group": "Above 25",
  "baby_age_months": 2.0,
  "kgs_gained_during_pregnancy": 20.0,
  "marital_status": "Married",
  "household_income": "Low",
  "level_of_education": "Secondary",
  "residency": "Urban",
  "comorbidities": "Hypertension",
  "smoke_cigarettes": 1,
  "smoke_shisha": 1,
  "premature_labour": 1,
  "healthy_baby": 0,
  "baby_admitted_nicu": 1,
  "baby_feeding_difficulties": 1,
  "pregnancy_problem": 1,
  "postnatal_problems": 1,
  "natal_problems": 1,
  "problems_with_husband": 1,
  "financial_problems": 1,
  "family_problems": 1,
  "had_covid_19": 1,
  "had_covid_19_vaccine": 0,
  "access_to_healthcare_services": 0,
  "aware_of_ppd_symptoms": 0,
  "experienced_cultural_stigma_ppd": 1,
  "received_support_or_treatment_ppd": 0,
  "epds_laugh_and_funny_side": "Not at all",
  "epds_looked_forward_enjoyment": "Hardly at all",
  "epds_blamed_myself": "Yes, quite often",
  "epds_anxious_or_worried": "Yes, very often",
  "epds_scared_or_panicky": "Yes, quite a lot",
  "epds_things_getting_on_top": "Yes, most of the time I have not been coping at all",
  "epds_unhappy_difficulty_sleeping": "Yes, most of the time",
  "epds_sad_or_miserable": "Yes, most of the time",
  "epds_unhappy_crying": "Yes, most of the time",
  "epds_thought_of_harming_self": "Sometimes"
}
```

### 3.3 Likely Emergency-Level Postpartum Risk

```json
{
  "baby_age_months": 1.0,
  "smoke_cigarettes": 1,
  "smoke_shisha": 1,
  "postnatal_problems": 1,
  "financial_problems": 1,
  "family_problems": 1,
  "problems_with_husband": 1,
  "access_to_healthcare_services": 0,
  "aware_of_ppd_symptoms": 0,
  "experienced_cultural_stigma_ppd": 1,
  "received_support_or_treatment_ppd": 0,
  "epds_anxious_or_worried": "Yes, very often",
  "epds_scared_or_panicky": "Yes, quite a lot",
  "epds_things_getting_on_top": "Yes, most of the time I have not been coping at all",
  "epds_unhappy_difficulty_sleeping": "Yes, most of the time",
  "epds_sad_or_miserable": "Yes, most of the time",
  "epds_unhappy_crying": "Yes, most of the time",
  "epds_thought_of_harming_self": "Yes, quite often"
}
```

---

You can post these payloads to your running backend using `curl`, Postman, or the built-in Swagger UI at `http://localhost:8000/docs`.
