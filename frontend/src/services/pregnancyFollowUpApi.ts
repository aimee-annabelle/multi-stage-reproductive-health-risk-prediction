import { ApiError, getAuthToken, requestJson } from './apiClient'
import type { PregnancyRequestPayload } from './predictionApi'

export type PregnancyFollowUpAssessPayload = PregnancyRequestPayload & {
  gestational_age_weeks?: number
  visit_label?: string
  notes?: string
}

export type PregnancyAssessmentRecordResponse = {
  assessment_id: number
  created_at: string
  gestational_age_weeks: number | null
  visit_label: string | null
  notes: string | null
  age: number
  systolic_bp: number
  diastolic: number
  bs: number | null
  body_temp: number | null
  bmi: number | null
  previous_complications: number | null
  preexisting_diabetes: number | null
  gestational_diabetes: number | null
  mental_health: number | null
  heart_rate: number | null
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

export type PregnancyAssessmentHistoryResponse = {
  total_records: number
  assessments: PregnancyAssessmentRecordResponse[]
}

export type PregnancyAssessmentComparisonResponse = {
  latest_assessment_id: number
  previous_assessment_id: number
  latest_created_at: string
  previous_created_at: string
  latest_probability_high_risk: number
  previous_probability_high_risk: number
  probability_high_risk_delta: number
  trend: 'increased' | 'decreased' | 'stable'
  metric_deltas: Record<string, number>
}

export type PregnancyTimelinePointResponse = {
  assessment_id: number
  created_at: string
  gestational_age_weeks: number | null
  visit_label: string | null
  probability_high_risk: number
  probability_low_risk: number
  risk_level: 'Low Risk' | 'High Risk'
  advise_hospital_visit: boolean
  advise_emergency_care: boolean
  systolic_bp: number
  diastolic: number
  bs: number | null
  bmi: number | null
  heart_rate: number | null
}

export type PregnancyTimelineSummaryResponse = {
  total_records: number
  time_span_days: number | null
  high_risk_count: number
  hospital_referral_count: number
  emergency_referral_count: number
  earliest_probability_high_risk: number | null
  latest_probability_high_risk: number | null
  probability_high_risk_change: number | null
  trend: 'increased' | 'decreased' | 'stable' | null
  points: PregnancyTimelinePointResponse[]
}

function authHeaders(): Record<string, string> {
  const token = getAuthToken()
  if (!token) {
    throw new ApiError('Authentication required. Please sign in again.', 401)
  }

  return {
    Authorization: `Bearer ${token}`,
  }
}

export async function assessPregnancyFollowUp(
  payload: PregnancyFollowUpAssessPayload,
): Promise<PregnancyAssessmentRecordResponse> {
  return requestJson<PregnancyAssessmentRecordResponse>(
    '/pregnancy/follow-up/assess',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(),
      },
      body: JSON.stringify(payload),
    },
    'Unable to save pregnancy follow-up assessment.',
  )
}

export async function getPregnancyFollowUpHistory(
  limit = 20,
): Promise<PregnancyAssessmentHistoryResponse> {
  return requestJson<PregnancyAssessmentHistoryResponse>(
    `/pregnancy/follow-up/history?limit=${limit}`,
    {
      method: 'GET',
      headers: authHeaders(),
    },
    'Unable to load pregnancy follow-up history.',
  )
}

export async function compareLatestPregnancyFollowUps(): Promise<PregnancyAssessmentComparisonResponse> {
  return requestJson<PregnancyAssessmentComparisonResponse>(
    '/pregnancy/follow-up/compare/latest',
    {
      method: 'GET',
      headers: authHeaders(),
    },
    'Unable to compare recent pregnancy follow-up records.',
  )
}

export async function getPregnancyTimelineSummary(
  limit = 50,
): Promise<PregnancyTimelineSummaryResponse> {
  return requestJson<PregnancyTimelineSummaryResponse>(
    `/pregnancy/follow-up/timeline/summary?limit=${limit}`,
    {
      method: 'GET',
      headers: authHeaders(),
    },
    'Unable to load pregnancy timeline summary.',
  )
}
