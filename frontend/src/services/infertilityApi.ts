export type InfertilityRequestPayload = {
  age: number
  ever_cohabited: 0 | 1
  children_ever_born: number
  bmi?: number
  months_since_last_sex?: number
  irregular_menstrual_cycles?: 0 | 1
  chronic_pelvic_pain?: 0 | 1
  history_pelvic_infections?: 0 | 1
  hormonal_symptoms?: 0 | 1
  early_menopause_symptoms?: 0 | 1
  autoimmune_history?: 0 | 1
  reproductive_surgery_history?: 0 | 1
}

export type InfertilityPredictionResponse = {
  predicted_class: 'no_infertility_risk' | 'primary_infertility_risk' | 'secondary_infertility_risk'
  probability_infertile: number
  probability_primary: number
  probability_secondary: number
  risk_level: string
  decision_threshold: number
  assessment_mode: 'symptom_only' | 'history_only' | 'fused'
  models_used: string[]
  top_risk_factors: Record<string, number>
  model_version: string
}

const API_BASE = (import.meta.env.VITE_API_URL || '').trim() || 'http://localhost:8000'

async function parseApiError(response: Response, fallbackMessage: string): Promise<never> {
  let message = fallbackMessage
  try {
    const body = (await response.json()) as { detail?: string }
    if (typeof body?.detail === 'string' && body.detail.trim()) {
      message = body.detail
    }
  } catch {
    // Ignore response parsing errors and use fallback.
  }
  throw new Error(message)
}

export async function predictInfertility(
  payload: InfertilityRequestPayload,
): Promise<InfertilityPredictionResponse> {
  const response = await fetch(`${API_BASE}/predict/infertility`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    await parseApiError(response, 'Unable to generate infertility risk assessment.')
  }

  return (await response.json()) as InfertilityPredictionResponse
}
