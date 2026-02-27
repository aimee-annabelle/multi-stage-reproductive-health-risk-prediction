import { ApiError, getAuthToken, requestJson } from './apiClient'
import type { PostpartumRequestPayload } from './predictionApi'

export type PostpartumFollowUpAssessPayload = PostpartumRequestPayload

export type PostpartumAssessmentRecordResponse = {
  assessment_id: number
  created_at: string
  input_payload: Record<string, unknown>
  age_group: string | null
  baby_age_months: number | null
  kgs_gained_during_pregnancy: number | null
  postnatal_problems: number | null
  baby_feeding_difficulties: number | null
  financial_problems: number | null
  predicted_class: 'low_postpartum_risk' | 'high_postpartum_risk'
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
  input_completion_pct: number
}

export type PostpartumAssessmentHistoryResponse = {
  total_records: number
  assessments: PostpartumAssessmentRecordResponse[]
}

export type PostpartumTimelinePointResponse = {
  assessment_id: number
  created_at: string
  probability_high_risk: number
  probability_low_risk: number
  risk_level: 'Low Risk' | 'High Risk'
  advise_hospital_visit: boolean
  advise_emergency_care: boolean
  baby_age_months: number | null
  postnatal_problems: number | null
  baby_feeding_difficulties: number | null
  financial_problems: number | null
  input_completion_pct: number
}

export type PostpartumTimelineSummaryResponse = {
  total_records: number
  time_span_days: number | null
  high_risk_count: number
  hospital_referral_count: number
  emergency_referral_count: number
  high_risk_percentage: number
  hospital_referral_percentage: number
  emergency_referral_percentage: number
  average_input_completion: number
  latest_input_completion: number | null
  earliest_probability_high_risk: number | null
  latest_probability_high_risk: number | null
  probability_high_risk_change: number | null
  trend: 'increased' | 'decreased' | 'stable' | null
  points: PostpartumTimelinePointResponse[]
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

export async function assessPostpartumFollowUp(
  payload: PostpartumFollowUpAssessPayload,
): Promise<PostpartumAssessmentRecordResponse> {
  return requestJson<PostpartumAssessmentRecordResponse>(
    '/postpartum/follow-up/assess',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(),
      },
      body: JSON.stringify(payload),
    },
    'Unable to save postpartum assessment.',
  )
}

export async function getPostpartumFollowUpHistory(
  limit = 20,
): Promise<PostpartumAssessmentHistoryResponse> {
  return requestJson<PostpartumAssessmentHistoryResponse>(
    `/postpartum/follow-up/history?limit=${limit}`,
    {
      method: 'GET',
      headers: authHeaders(),
    },
    'Unable to load postpartum follow-up history.',
  )
}

export async function getPostpartumTimelineSummary(
  limit = 50,
): Promise<PostpartumTimelineSummaryResponse> {
  return requestJson<PostpartumTimelineSummaryResponse>(
    `/postpartum/follow-up/timeline/summary?limit=${limit}`,
    {
      method: 'GET',
      headers: authHeaders(),
    },
    'Unable to load postpartum timeline summary.',
  )
}
