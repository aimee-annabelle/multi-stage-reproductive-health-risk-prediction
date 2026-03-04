import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import DashboardLayout from '../../components/dashboard/DashboardLayout'
import { ApiError } from '../../services/apiClient'
import { getPostpartumModelInfo, type PostpartumModelInfo } from '../../services/predictionApi'
import {
  assessPostpartumFollowUp,
  type PostpartumAssessmentRecordResponse,
} from '../../services/postpartumFollowUpApi'
import { useAuthStore } from '../../stores/authStore'
import { SNAPSHOT_KEYS, writeStageSnapshot } from '../../utils/dashboardSnapshot'
import {
  advancedBinaryFields,
  advancedEpdsFields,
  buildPostpartumPayload,
  coreBinaryFields,
  coreEpdsKeys,
  epdsLabelsByField,
  epdsOptionsByField,
  initialPostpartumFormValues,
  yesNoOptions,
} from './postpartumFormSets'
type PostpartumSeverity = 'Low Risk' | 'Medium Risk' | 'High Risk'

function getResultGuidance(severity: PostpartumSeverity) {
  if (severity === 'High Risk') {
    return {
      title: 'Higher postpartum risk signal',
      explanation:
        'Your latest assessment indicates elevated risk. The tool recommends prompt follow-up with a qualified clinician or mental health professional.',
      steps: [
        'Book a same-day or near-term clinical consultation.',
        'Share the top risk factors and referral advice shown below.',
        'Repeat assessment after support steps to track change over time.',
      ],
    }
  }

  if (severity === 'Medium Risk') {
    return {
      title: 'Moderate postpartum risk signal',
      explanation:
        'Your score is above the referral threshold but below the emergency threshold. Prompt same-day clinical follow-up is recommended.',
      steps: [
        'Schedule a same-day or next-day clinical consultation.',
        'Share the top risk factors and referral advice shown below.',
        'Repeat assessment after support steps to track direction of change.',
      ],
    }
  }

  return {
    title: 'Lower postpartum risk signal',
    explanation:
      'Your current risk is below the referral threshold. Continue self-monitoring and repeat assessment whenever symptoms or stress levels change.',
    steps: [
      'Maintain regular postpartum check-ins.',
      'Track mood, sleep, and social support weekly.',
      'Return for reassessment if warning symptoms increase.',
    ],
  }
}

export default function PostpartumPredictionPage() {
  const navigate = useNavigate()
  const logout = useAuthStore((state) => state.logout)

  const [formValues, setFormValues] = useState<Record<string, string>>(initialPostpartumFormValues)
  const [activeStep, setActiveStep] = useState<1 | 2>(1)
  const [modelInfo, setModelInfo] = useState<PostpartumModelInfo | null>(null)

  const [result, setResult] = useState<PostpartumAssessmentRecordResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleAuthFailure = useCallback(async () => {
    await logout()
    navigate('/sign-in')
  }, [logout, navigate])

  useEffect(() => {
    let active = true

    const loadModel = async () => {
      try {
        const info = await getPostpartumModelInfo()
        if (active) {
          setModelInfo(info)
        }
      } catch {
        if (active) {
          setModelInfo(null)
        }
      }
    }

    void loadModel()

    return () => {
      active = false
    }
  }, [])

  const setValue = (field: string, value: string) => {
    setFormValues((previous) => ({ ...previous, [field]: value }))
  }

  const clearForm = () => {
    setFormValues(initialPostpartumFormValues)
    setError(null)
    setResult(null)
    setActiveStep(1)
  }

  const handleSubmit = async () => {
    setError(null)

    const payload = buildPostpartumPayload(formValues)
    if (Object.keys(payload).length === 0) {
      setError('Provide at least one postpartum field before prediction.')
      return
    }

    setIsSubmitting(true)
    try {
      const record = await assessPostpartumFollowUp(payload)
      setResult(record)

      writeStageSnapshot(SNAPSHOT_KEYS.postpartum, {
        riskLevel: record.severity_level,
        score: record.probability_high_risk * 100,
        summary: `${record.predicted_class.replaceAll('_', ' ')} at ${Math.round(record.probability_high_risk * 100)}% high-risk probability`,
        modelVersion: record.model_version,
        capturedAt: new Date().toISOString(),
      })
    } catch (submissionError) {
      if (submissionError instanceof ApiError && submissionError.status === 401) {
        await handleAuthFailure()
        return
      }
      setError(submissionError instanceof Error ? submissionError.message : 'Unable to submit postpartum assessment.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const resultSeverity = result?.severity_level ?? null
  const resultSeverityTone =
    resultSeverity === 'High Risk' ? 'high' : resultSeverity === 'Medium Risk' ? 'medium' : 'low'

  const resultGuidance = useMemo(() => {
    if (!result || !resultSeverity) {
      return null
    }
    return getResultGuidance(resultSeverity)
  }, [result, resultSeverity])

  const topFactors = useMemo(() => {
    if (!result) {
      return []
    }

    return Object.entries(result.top_risk_factors)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
  }, [result])

  return (
    <DashboardLayout
      title="Postpartum Risk Prediction"
      subtitle="Complete the assessment form to generate a stored prediction used by the postpartum dashboard charts."
    >
      <section className="stage-form-shell pp-form-page">
        {result ? null : (
          <section className="inf-page">
            <div className="inf-step-meta-row">
              <p className="inf-step-name">
                {activeStep === 1 ? 'Stage 1: Postpartum Core Signals' : 'Stage 2: Contextual & Full EPDS Inputs'}
              </p>
              <p className="inf-step-count">Step {activeStep} of 2</p>
            </div>

            <div className="inf-progress-track">
              <span className="inf-progress-fill" style={{ width: activeStep === 1 ? '50%' : '100%' }} />
            </div>

            <form
              className="inf-card"
              onSubmit={(event) => {
                event.preventDefault()
                if (activeStep === 1) {
                  setError(null)
                  setActiveStep(2)
                  return
                }
                void handleSubmit()
              }}
            >
              <div className="inf-card-header">
                <h2 className="inf-card-title">Postpartum Assessment Input</h2>
                <p className="inf-card-subtitle">
                  Use this form to submit and store postpartum data. Each submission updates the dashboard trend and referral statistics.
                </p>
              </div>

              {activeStep === 1 ? (
                <div className="inf-section-stack">
                  <section className="inf-section">
                    <h3 className="inf-section-title">Core Profile</h3>
                    <div className="inf-grid-2">
                      <label className="inf-field">
                        <span className="inf-label">Age Group</span>
                        <select
                          value={formValues.age_group}
                          onChange={(event) => setValue('age_group', event.target.value)}
                          className="inf-input"
                        >
                          <option value="">Not provided</option>
                          <option value="Below 25">Below 25</option>
                          <option value="Above 25">Above 25</option>
                        </select>
                      </label>

                      <label className="inf-field">
                        <span className="inf-label">Baby Age (months)</span>
                        <input
                          type="number"
                          value={formValues.baby_age_months}
                          onChange={(event) => setValue('baby_age_months', event.target.value)}
                          placeholder="e.g., 3"
                          className="inf-input"
                        />
                      </label>

                      <label className="inf-field">
                        <span className="inf-label">Weight Gain During Pregnancy (kg)</span>
                        <input
                          type="number"
                          value={formValues.kgs_gained_during_pregnancy}
                          onChange={(event) => setValue('kgs_gained_during_pregnancy', event.target.value)}
                          placeholder="e.g., 11"
                          className="inf-input"
                        />
                      </label>
                    </div>
                  </section>

                  <section className="inf-section">
                    <h3 className="inf-section-title">Key Indicators</h3>
                    <div className="inf-toggle-list">
                      {coreBinaryFields.map((field) => {
                        const selected = formValues[field.key]
                        return (
                          <div className="inf-toggle-row" key={field.key}>
                            <div>
                              <p className="inf-toggle-title">{field.label}</p>
                              <p className="inf-toggle-hint">{field.hint}</p>
                            </div>
                            <div className="inf-option-group">
                              {yesNoOptions.map((option) => (
                                <button
                                  key={`${field.key}-${option.value}`}
                                  type="button"
                                  className={`inf-chip ${selected === option.value ? 'active' : ''}`}
                                  onClick={() => setValue(field.key, option.value)}
                                >
                                  {option.label}
                                </button>
                              ))}
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </section>

                <section className="inf-section">
                  <h3 className="inf-section-title">Core EPDS Signals</h3>
                  <div className="inf-grid-2">
                    {coreEpdsKeys.map((fieldKey) => (
                      <label key={fieldKey} className="inf-field">
                        <span className="inf-label">{epdsLabelsByField[fieldKey]}</span>
                        <select
                          value={formValues[fieldKey]}
                          onChange={(event) => setValue(fieldKey, event.target.value)}
                          className="inf-input"
                        >
                          <option value="">Not provided</option>
                          {epdsOptionsByField[fieldKey].map((option) => (
                            <option key={option} value={option}>
                              {option}
                            </option>
                          ))}
                        </select>
                      </label>
                    ))}
                  </div>
                </section>
              </div>
            ) : (
              <div className="inf-section-stack">
                <section className="inf-section">
                  <h3 className="inf-section-title">Socio-demographic and Clinical Context</h3>
                  <div className="inf-grid-2">
                    <label className="inf-field">
                      <span className="inf-label">Marital Status</span>
                      <select
                        value={formValues.marital_status}
                        onChange={(event) => setValue('marital_status', event.target.value)}
                        className="inf-input"
                      >
                        <option value="">Not provided</option>
                        <option value="Single">Single</option>
                        <option value="Married">Married</option>
                        <option value="Divorced">Divorced</option>
                      </select>
                    </label>

                    <label className="inf-field">
                      <span className="inf-label">Household Income</span>
                      <select
                        value={formValues.household_income}
                        onChange={(event) => setValue('household_income', event.target.value)}
                        className="inf-input"
                      >
                        <option value="">Not provided</option>
                        <option value="Insufficient">Insufficient</option>
                        <option value="Sufficient">Sufficient</option>
                        <option value="More than sufficient">More than sufficient</option>
                      </select>
                    </label>

                    <label className="inf-field">
                      <span className="inf-label">Level of Education</span>
                      <select
                        value={formValues.level_of_education}
                        onChange={(event) => setValue('level_of_education', event.target.value)}
                        className="inf-input"
                      >
                        <option value="">Not provided</option>
                        <option value="Primary">Primary</option>
                        <option value="Preparatory or high school">Preparatory or high school</option>
                        <option value="University or above">University or above</option>
                      </select>
                    </label>

                    <label className="inf-field">
                      <span className="inf-label">Residency</span>
                      <select
                        value={formValues.residency}
                        onChange={(event) => setValue('residency', event.target.value)}
                        className="inf-input"
                      >
                        <option value="">Not provided</option>
                        <option value="Urban">Urban</option>
                        <option value="Rural">Rural</option>
                      </select>
                    </label>

                    <label className="inf-field">
                      <span className="inf-label">Healthcare Access</span>
                      <select
                        value={formValues.access_to_healthcare_services}
                        onChange={(event) => setValue('access_to_healthcare_services', event.target.value)}
                        className="inf-input"
                      >
                        <option value="">Not provided</option>
                        <option value="i had insurance">I had insurance coverage</option>
                        <option value="on the country cost">Covered by government services</option>
                        <option value="i charge for my self">I paid for services myself</option>
                        <option value="the maternal and baby services provided for free">
                          Maternal and baby services were provided for free
                        </option>
                        <option value="others">Others</option>
                      </select>
                    </label>

                    <label className="inf-field">
                      <span className="inf-label">Comorbidities</span>
                      <input
                        value={formValues.comorbidities}
                        onChange={(event) => setValue('comorbidities', event.target.value)}
                        placeholder="Optional details"
                        className="inf-input"
                      />
                    </label>
                  </div>
                </section>

                <section className="inf-section">
                  <h3 className="inf-section-title">Additional Binary Indicators</h3>
                  <div className="inf-toggle-list">
                    {advancedBinaryFields.map((field) => {
                      const selected = formValues[field.key]
                      return (
                        <div className="inf-toggle-row" key={field.key}>
                          <div>
                            <p className="inf-toggle-title">{field.label}</p>
                            <p className="inf-toggle-hint">{field.hint}</p>
                          </div>
                          <div className="inf-option-group">
                            {yesNoOptions.map((option) => (
                              <button
                                key={`${field.key}-${option.value}`}
                                type="button"
                                className={`inf-chip ${selected === option.value ? 'active' : ''}`}
                                onClick={() => setValue(field.key, option.value)}
                              >
                                {option.label}
                              </button>
                            ))}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </section>

                <section className="inf-section">
                  <h3 className="inf-section-title">Additional EPDS Inputs</h3>
                  <div className="inf-grid-2">
                    {advancedEpdsFields.map((fieldKey) => (
                      <label key={fieldKey} className="inf-field">
                        <span className="inf-label">{epdsLabelsByField[fieldKey]}</span>
                        <select
                          value={formValues[fieldKey]}
                          onChange={(event) => setValue(fieldKey, event.target.value)}
                          className="inf-input"
                        >
                          <option value="">Not provided</option>
                          {epdsOptionsByField[fieldKey].map((option) => (
                            <option key={option} value={option}>
                              {option}
                            </option>
                          ))}
                        </select>
                      </label>
                    ))}
                  </div>
                </section>
              </div>
            )}

              {error ? <p className="inf-error-box">{error}</p> : null}

            <div className="inf-action-row">
              <button type="button" onClick={clearForm} className="inf-btn inf-btn-ghost">
                Clear Form
              </button>

              <div className="inf-action-group">
                <button
                  type="button"
                  className="inf-btn inf-btn-ghost"
                  onClick={() => navigate('/dashboard/postpartum')}
                >
                  Back to Dashboard
                </button>

                {activeStep === 2 ? (
                  <button
                    type="button"
                    onClick={() => {
                      setActiveStep(1)
                      setError(null)
                    }}
                    className="inf-btn inf-btn-ghost"
                  >
                    Back
                  </button>
                ) : null}

                {activeStep === 1 ? (
                  <button type="submit" className="inf-btn inf-btn-primary">
                    Continue
                  </button>
                ) : (
                  <button type="submit" disabled={isSubmitting} className="inf-btn inf-btn-primary">
                    {isSubmitting ? 'Predicting...' : 'Predict Risk'}
                  </button>
                )}
              </div>
            </div>
            </form>
          </section>
        )}

        {result ? (
          <section className="inf-result-page">
            <div className="inf-result-head">
              <div>
                <p className="inf-result-kicker">ASSESSMENT COMPLETE</p>
                <h2 className="inf-result-title">Postpartum Prediction Result</h2>
                <p className="inf-result-meta">Your result has been saved and now contributes to the postpartum dashboard trend.</p>
              </div>
              <div className="inf-result-head-actions">
                <span
                  className={`inf-risk-pill inf-risk-pill-${
                    resultSeverityTone === 'high'
                      ? 'high-risk'
                      : resultSeverityTone === 'medium'
                        ? 'moderate-risk'
                        : 'low-risk'
                  }`}
                >
                  {resultSeverity}
                </span>
              </div>
            </div>

            <div className="inf-result-grid">
              <div className="inf-result-main">
                <article className="inf-info-card">
                  <h4 className="inf-info-title">Summary</h4>
                  <ul className="inf-list">
                    <li>
                      Predicted class: <strong>{result.predicted_class.replaceAll('_', ' ')}</strong>
                    </li>
                    <li>
                      High-risk probability: <strong>{Math.round(result.probability_high_risk * 100)}%</strong>
                    </li>
                    <li>
                      Decision threshold: <strong>{Math.round(result.decision_threshold * 100)}%</strong>
                    </li>
                    <li>
                      Classification mode: <strong>{result.classification_note}</strong>
                    </li>
                    <li>
                      Input completion: <strong>{Math.round(result.input_completion_pct)}%</strong>
                    </li>
                  </ul>
                </article>

                <article className="inf-info-card">
                  <h4 className="inf-info-title">What this means</h4>
                  <p className="inf-summary-text">{resultGuidance?.title}</p>
                  <p className="inf-summary-text">{resultGuidance?.explanation}</p>
                  <ul className="inf-list">
                    {resultGuidance?.steps.map((step) => (
                      <li key={step}>{step}</li>
                    ))}
                  </ul>
                </article>

                <article className="inf-info-card">
                  <h4 className="inf-info-title">Clinical Advice</h4>
                  <ul className="inf-list">
                    <li>
                      Referral advice: <strong>{result.hospital_advice}</strong>
                    </li>
                    <li>
                      Emergency advice: <strong>{result.emergency_advice}</strong>
                    </li>
                  </ul>
                </article>
              </div>

              <aside className="inf-result-side">
                <article className="inf-action-card">
                  <h3 className="inf-section-heading">Top Factors</h3>
                  {topFactors.length > 0 ? (
                    <ul className="inf-list">
                      {topFactors.map(([name, value]) => (
                        <li key={name}>
                          {name.replaceAll('_', ' ')}: <strong>{value.toFixed(3)}</strong>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="inf-summary-text">No factor details were returned.</p>
                  )}
                </article>

                <article className="inf-action-card">
                  <h3 className="inf-section-heading">Model Metadata</h3>
                  <ul className="inf-list">
                    <li>
                      Response model version: <strong>{result.model_version}</strong>
                    </li>
                    <li>
                      Config model version: <strong>{modelInfo?.model_version || 'N/A'}</strong>
                    </li>
                    <li>
                      Emergency threshold: <strong>{Math.round(result.emergency_threshold * 100)}%</strong>
                    </li>
                  </ul>
                </article>

                <button
                  type="button"
                  className="inf-btn inf-btn-ghost inf-btn-full"
                  onClick={clearForm}
                >
                  Run Another Prediction
                </button>

                <button
                  type="button"
                  className="inf-btn inf-btn-primary inf-btn-full"
                  onClick={() => navigate('/dashboard/postpartum')}
                >
                  View Postpartum Dashboard
                </button>
              </aside>
            </div>
          </section>
        ) : null}
      </section>
    </DashboardLayout>
  )
}
