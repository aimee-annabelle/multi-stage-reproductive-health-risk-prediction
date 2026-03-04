import { requestJson } from './apiClient'

export type InfertilityRequestPayload = {
  age: number
  ever_cohabited: 0 | 1
  children_ever_born: number
  irregular_menstrual_cycles?: 0 | 1
  chronic_pelvic_pain?: 0 | 1
  history_pelvic_infections?: 0 | 1
  hormonal_symptoms?: 0 | 1
  early_menopause_symptoms?: 0 | 1
  autoimmune_history?: 0 | 1
  reproductive_surgery_history?: 0 | 1
  bmi?: number
  smoked_last_12mo?: 0 | 1
  alcohol_last_12mo?: 0 | 1
  age_at_first_marriage?: number
  months_since_first_cohabitation?: number
  months_since_last_sex?: number
}

export type PregnancyRequestPayload = {
  age: number
  systolic_bp: number
  diastolic: number
  bs?: number
  body_temp?: number
  bmi?: number
  previous_complications?: 0 | 1
  preexisting_diabetes?: 0 | 1
  gestational_diabetes?: 0 | 1
  mental_health?: 0 | 1
  heart_rate?: number
}

export type PostpartumRequestPayload = {
  age_group?: string
  baby_age_months?: number
  kgs_gained_during_pregnancy?: number
  marital_status?: string
  household_income?: string
  level_of_education?: string
  residency?: string
  comorbidities?: string
  smoke_cigarettes?: string | number | boolean
  smoke_shisha?: string | number | boolean
  premature_labour?: string | number | boolean
  healthy_baby?: string | number | boolean
  baby_admitted_nicu?: string | number | boolean
  baby_feeding_difficulties?: string | number | boolean
  pregnancy_problem?: string | number | boolean
  postnatal_problems?: string | number | boolean
  natal_problems?: string | number | boolean
  problems_with_husband?: string | number | boolean
  financial_problems?: string | number | boolean
  family_problems?: string | number | boolean
  had_covid_19?: string | number | boolean
  had_covid_19_vaccine?: string | number | boolean
  access_to_healthcare_services?: string | number | boolean
  aware_of_ppd_symptoms?: string | number | boolean
  experienced_cultural_stigma_ppd?: string | number | boolean
  received_support_or_treatment_ppd?: string | number | boolean
  epds_laugh_and_funny_side?: string
  epds_looked_forward_enjoyment?: string
  epds_blamed_myself?: string
  epds_anxious_or_worried?: string
  epds_scared_or_panicky?: string
  epds_things_getting_on_top?: string
  epds_unhappy_difficulty_sleeping?: string
  epds_sad_or_miserable?: string
  epds_unhappy_crying?: string
  epds_thought_of_harming_self?: string
}

export type InfertilityPredictionResponse = {
  predicted_class: 'no_infertility_risk' | 'primary_infertility_risk' | 'secondary_infertility_risk'
  probability_infertile: number
  probability_primary: number
  probability_secondary: number
  risk_level: 'Low Risk' | 'Moderate Risk' | 'High Risk'
  decision_threshold: number
  assessment_mode: 'symptom_only' | 'history_only' | 'fused'
  models_used: string[]
  top_risk_factors: Record<string, number>
  model_version: string
}

export type PregnancyPredictionResponse = {
  predicted_class: 'low_pregnancy_risk' | 'high_pregnancy_risk'
  probability_high_risk: number
  probability_low_risk: number
  risk_level: 'Low Risk' | 'High Risk'
  decision_threshold: number
  emergency_threshold: number
  advise_hospital_visit: boolean
  advise_emergency_care: boolean
  hospital_advice: string
  emergency_advice: string
  top_risk_factors: Record<string, number>
  imputed_fields: string[]
  model_version: string
}

export type PostpartumPredictionResponse = {
  predicted_class: 'low_postpartum_risk' | 'high_postpartum_risk'
  probability_high_risk: number
  probability_low_risk: number
  risk_level: 'Low Risk' | 'High Risk'
  severity_level: 'Low Risk' | 'Medium Risk' | 'High Risk'
  model_classification: 'binary_2_class'
  classification_note: string
  decision_threshold: number
  emergency_threshold: number
  advise_hospital_visit: boolean
  advise_emergency_care: boolean
  hospital_advice: string
  emergency_advice: string
  top_risk_factors: Record<string, number>
  imputed_fields: string[]
  model_version: string
}

export type InfertilityModelInfo = {
  model_version: string
  thresholds?: Record<string, number>
  training_date_utc?: string
}

export type PregnancyModelInfo = {
  model_version: string
  threshold: number
  emergency_threshold: number
  training_date_utc?: string
}

export type PostpartumModelInfo = {
  model_version: string
  threshold?: number
  decision_threshold: number
  emergency_threshold: number
  model_classification?: 'binary_2_class'
  classification_note?: string
  training_date_utc?: string
}

export async function predictInfertility(
  payload: InfertilityRequestPayload,
): Promise<InfertilityPredictionResponse> {
  return requestJson<InfertilityPredictionResponse>(
    '/predict/infertility',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    },
    'Unable to generate infertility assessment.',
  )
}

export async function predictPregnancy(
  payload: PregnancyRequestPayload,
): Promise<PregnancyPredictionResponse> {
  return requestJson<PregnancyPredictionResponse>(
    '/predict/pregnancy',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    },
    'Unable to generate pregnancy assessment.',
  )
}

export async function predictPostpartum(
  payload: PostpartumRequestPayload,
): Promise<PostpartumPredictionResponse> {
  return requestJson<PostpartumPredictionResponse>(
    '/predict/postpartum',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    },
    'Unable to generate postpartum assessment.',
  )
}

export async function getInfertilityModelInfo(): Promise<InfertilityModelInfo> {
  return requestJson<InfertilityModelInfo>(
    '/model/info',
    { method: 'GET' },
    'Unable to load infertility model info.',
  )
}

export async function getPregnancyModelInfo(): Promise<PregnancyModelInfo> {
  return requestJson<PregnancyModelInfo>(
    '/model/info/pregnancy',
    { method: 'GET' },
    'Unable to load pregnancy model info.',
  )
}

export async function getPostpartumModelInfo(): Promise<PostpartumModelInfo> {
  return requestJson<PostpartumModelInfo>(
    '/model/info/postpartum',
    { method: 'GET' },
    'Unable to load postpartum model info.',
  )
}
