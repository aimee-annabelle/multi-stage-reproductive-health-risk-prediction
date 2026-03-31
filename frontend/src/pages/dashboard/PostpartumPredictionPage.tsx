import { useCallback, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import DashboardLayout from '../../components/dashboard/DashboardLayout'
import FormFieldInfo from '../../components/dashboard/FormFieldInfo'
import { ApiError } from '../../services/apiClient'
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
  epdsDescriptionsByField,
  epdsLabelsByField,
  epdsOptionsByField,
  initialPostpartumFormValues,
  yesNoOptions,
} from './postpartumFormSets'
type PostpartumSeverity = 'Low Risk' | 'Medium Risk' | 'High Risk'

const postpartumFieldDescriptions: Record<string, string> = {
  age_group: 'Choose the age range that applies at the time of this assessment.',
  baby_age_months: 'Enter baby age in completed months. Example: enter 3 for a 3-month-old baby.',
  kgs_gained_during_pregnancy: 'Enter how many kilograms were gained during pregnancy if known. Example: 11.',
  marital_status: 'Choose the current relationship or marital status that best fits.',
  household_income: 'Choose the income option that best matches the current household situation.',
  level_of_education: 'Choose the highest completed level of education.',
  residency: 'Choose whether current residence is urban or rural.',
  access_to_healthcare_services: 'Choose the option that best describes how healthcare services were accessed or paid for.',
  comorbidities: 'Enter other medical conditions if any. Example: hypertension, asthma, or diabetes.',
}

const postpartumStepOneRequiredProfileFields = ['age_group', 'baby_age_months'] as const

function getResultGuidance(severity: PostpartumSeverity) {
  if (severity === 'High Risk') {
    return {
      title: 'Care is needed soon',
      explanation:
        'Your answers suggest that extra support would be helpful right now. Reaching out early can make recovery easier.',
      steps: [
        'Book care as soon as possible.',
        'Share these results with a health professional or trusted support person.',
        'Repeat the check-in after getting support to see how things are changing.',
      ],
    }
  }

  if (severity === 'Medium Risk') {
    return {
      title: 'A gentle check-in is recommended',
      explanation:
        'Your answers show a few signs that deserve attention. A timely check-in can help you feel supported and safe.',
      steps: [
        'Arrange a check-in soon.',
        'Talk through the highlighted concerns with someone you trust.',
        'Repeat the assessment after a few support steps to track progress.',
      ],
    }
  }

  return {
    title: 'Things look more steady right now',
    explanation:
      'Your answers suggest things are more stable at the moment. Keep checking in with yourself and return if anything changes.',
    steps: [
      'Keep up regular check-ins.',
      'Pay attention to mood, sleep, and support around you.',
      'Come back for another check if warning signs increase.',
    ],
  }
}

function humanizeFactorName(value: string): string {
  return value
    .replaceAll('_', ' ')
    .replace(/\[[^\]]+\]/g, '')
    .replace(/\b\w/g, (char) => char.toUpperCase())
    .replace(/\s+/g, ' ')
    .trim()
}

function getSeverityStrokeColor(tone: 'low' | 'medium' | 'high') {
  if (tone === 'high') {
    return 'var(--color-error)'
  }
  if (tone === 'medium') {
    return 'var(--color-warning)'
  }
  return 'var(--color-success)'
}

export default function PostpartumPredictionPage() {
  const navigate = useNavigate()
  const logout = useAuthStore((state) => state.logout)

  const [formValues, setFormValues] = useState<Record<string, string>>(initialPostpartumFormValues)
  const [activeStep, setActiveStep] = useState<1 | 2>(1)

  const [result, setResult] = useState<PostpartumAssessmentRecordResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleAuthFailure = useCallback(async () => {
    await logout()
    navigate('/sign-in')
  }, [logout, navigate])

  const setValue = (field: string, value: string) => {
    setFormValues((previous) => ({ ...previous, [field]: value }))
  }

  const clearForm = () => {
    setFormValues(initialPostpartumFormValues)
    setError(null)
    setResult(null)
    setActiveStep(1)
  }

  const validateStepOne = () => {
    const babyAgeMonths = Number(formValues.baby_age_months)

    if (!formValues.age_group || !Number.isFinite(babyAgeMonths) || babyAgeMonths < 0) {
      setError('Age group and baby age are required before moving to the next step.')
      return false
    }

    const hasMissingCoreBinary = coreBinaryFields.some((field) => formValues[field.key] === '')
    if (hasMissingCoreBinary) {
      setError('Please answer all key indicator questions before moving to the next step.')
      return false
    }

    const hasMissingCoreEpds = coreEpdsKeys.some((fieldKey) => !formValues[fieldKey])
    if (hasMissingCoreEpds) {
      setError('Please complete all core EPDS questions before moving to the next step.')
      return false
    }

    setError(null)
    return true
  }

  const continueToStepTwo = () => {
    if (!validateStepOne()) {
      return
    }

    setActiveStep(2)
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

  const riskPercent = result ? Math.round(result.probability_high_risk * 100) : 0
  const severityStrokeColor = getSeverityStrokeColor(resultSeverityTone)

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
                  continueToStepTwo()
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
                        <span className="inf-label">
                          <FormFieldInfo
                            label="Age Group"
                            description={postpartumFieldDescriptions.age_group}
                            textClassName="inf-label"
                          />
                        </span>
                        <select
                          value={formValues.age_group}
                          onChange={(event) => setValue('age_group', event.target.value)}
                          className="inf-input"
                          required={postpartumStepOneRequiredProfileFields.includes('age_group')}
                        >
                          <option value="">Not provided</option>
                          <option value="Below 25">Below 25</option>
                          <option value="Above 25">Above 25</option>
                        </select>
                      </label>

                      <label className="inf-field">
                        <span className="inf-label">
                          <FormFieldInfo
                            label="Baby Age (months)"
                            description={postpartumFieldDescriptions.baby_age_months}
                            textClassName="inf-label"
                          />
                        </span>
                        <input
                          type="number"
                          value={formValues.baby_age_months}
                          onChange={(event) => setValue('baby_age_months', event.target.value)}
                          placeholder="e.g., 3"
                          className="inf-input"
                          required={postpartumStepOneRequiredProfileFields.includes('baby_age_months')}
                        />
                      </label>

                      <label className="inf-field">
                        <span className="inf-label">
                          <FormFieldInfo
                            label="Weight Gain During Pregnancy (kg)"
                            description={postpartumFieldDescriptions.kgs_gained_during_pregnancy}
                            textClassName="inf-label"
                          />
                        </span>
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
                              <p className="inf-toggle-title">
                                <FormFieldInfo
                                  label={field.label}
                                  description={field.description}
                                  textClassName="inf-toggle-title"
                                />
                              </p>
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
                        <span className="inf-label">
                          <FormFieldInfo
                            label={epdsLabelsByField[fieldKey]}
                            description={epdsDescriptionsByField[fieldKey]}
                            textClassName="inf-label"
                          />
                        </span>
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
                      <span className="inf-label">
                        <FormFieldInfo
                          label="Marital Status"
                          description={postpartumFieldDescriptions.marital_status}
                          textClassName="inf-label"
                        />
                      </span>
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
                      <span className="inf-label">
                        <FormFieldInfo
                          label="Household Income"
                          description={postpartumFieldDescriptions.household_income}
                          textClassName="inf-label"
                        />
                      </span>
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
                      <span className="inf-label">
                        <FormFieldInfo
                          label="Level of Education"
                          description={postpartumFieldDescriptions.level_of_education}
                          textClassName="inf-label"
                        />
                      </span>
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
                      <span className="inf-label">
                        <FormFieldInfo
                          label="Residency"
                          description={postpartumFieldDescriptions.residency}
                          textClassName="inf-label"
                        />
                      </span>
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
                      <span className="inf-label">
                        <FormFieldInfo
                          label="Healthcare Access"
                          description={postpartumFieldDescriptions.access_to_healthcare_services}
                          textClassName="inf-label"
                        />
                      </span>
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
                      <span className="inf-label">
                        <FormFieldInfo
                          label="Comorbidities"
                          description={postpartumFieldDescriptions.comorbidities}
                          textClassName="inf-label"
                        />
                      </span>
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
                            <p className="inf-toggle-title">
                              <FormFieldInfo
                                label={field.label}
                                description={field.description}
                                textClassName="inf-toggle-title"
                              />
                            </p>
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
                        <span className="inf-label">
                          <FormFieldInfo
                            label={epdsLabelsByField[fieldKey]}
                            description={epdsDescriptionsByField[fieldKey]}
                            textClassName="inf-label"
                          />
                        </span>
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
                <article className={`inf-summary-card inf-summary-card-${resultSeverityTone === 'medium' ? 'moderate-risk' : `${resultSeverityTone}-risk`}`}>
                  <div className="inf-gauge-wrap">
                    <svg viewBox="0 0 120 70" className="inf-gauge" aria-hidden>
                      <path
                        d="M10 60 A50 50 0 0 1 110 60"
                        fill="none"
                        stroke="var(--color-gray-200)"
                        strokeWidth="10"
                        strokeLinecap="round"
                      />
                      <path
                        d="M10 60 A50 50 0 0 1 110 60"
                        fill="none"
                        stroke={severityStrokeColor}
                        strokeWidth="10"
                        strokeLinecap="round"
                        strokeDasharray={`${(riskPercent / 100) * 157} 157`}
                      />
                    </svg>
                    <div className="inf-gauge-value">
                      <p className="inf-gauge-number">{riskPercent}%</p>
                      <p className="inf-gauge-level">{resultSeverity?.toUpperCase()}</p>
                    </div>
                  </div>

                    <div className="pp-result-summary-copy">
                    <p className="inf-highlight-kicker">Your Check-In Result</p>
                    <h3 className="inf-summary-title">{resultGuidance?.title || 'Your Postpartum Check-In'}</h3>
                    <p className="inf-summary-text">
                      Overall check-in: <strong>{resultSeverity}</strong>
                    </p>
                    <p className="inf-summary-text">{resultGuidance?.explanation}</p>

                    <div className="pp-result-detail-list">
                      <article className="pp-result-detail-row">
                        <span>Risk level</span>
                        <strong>{resultSeverity}</strong>
                      </article>
                      <article className="pp-result-detail-row">
                        <span>What this suggests</span>
                        <strong>{resultGuidance?.title}</strong>
                      </article>
                      <article className="pp-result-detail-row">
                        <span>Best next step</span>
                        <strong>{resultGuidance?.steps[0]}</strong>
                      </article>
                    </div>
                  </div>
                </article>

                <article className={`inf-action-card inf-highlight-card inf-highlight-card-${resultSeverityTone}`}>
                  <p className="inf-highlight-kicker">What Stood Out Most</p>
                  <h3 className="inf-section-heading">Key Factors</h3>
                  {topFactors.length > 0 ? (
                    <div className="pp-factor-card-grid">
                      {topFactors.map(([name, value], index) => (
                        <article
                          key={name}
                          className={`inf-factor-card ${index === 0 ? 'inf-factor-card-warning' : 'inf-factor-card-positive'}`}
                        >
                          <p className="inf-factor-label">Top #{index + 1}</p>
                          <p className="pp-factor-card-title">{humanizeFactorName(name)}</p>
                          <p className="inf-factor-value">{value.toFixed(2)}</p>
                          <p className="inf-factor-note">
                            {index === 0 ? 'Most important signal in this check-in.' : 'Also contributed to this result.'}
                          </p>
                        </article>
                      ))}
                    </div>
                  ) : (
                    <p className="inf-summary-text">No factor details were returned.</p>
                  )}
                </article>
              </div>

              <aside className="inf-result-side">
                <article className={`inf-info-card inf-highlight-card inf-highlight-card-${resultSeverityTone} pp-next-steps-card`}>
                  <p className="inf-highlight-kicker">Recommended Next Steps</p>
                  <h4 className="inf-info-title">What to do next</h4>
                  <p className="inf-summary-text">{resultGuidance?.explanation}</p>
                  <ul className="inf-list pp-result-recommend-list">
                    {resultGuidance?.steps.map((step) => (
                      <li key={step}>{step}</li>
                    ))}
                  </ul>
                </article>

                <article className={`inf-info-card inf-highlight-card inf-highlight-card-${resultSeverityTone} pp-clinical-card`}>
                  <p className="inf-highlight-kicker">Helpful Guidance</p>
                  <h4 className="inf-info-title">Support to keep in mind</h4>
                  <div className="pp-clinical-grid">
                    <article className="pp-clinical-item">
                      <span className="pp-clinical-label">Care suggestion</span>
                      <p>{result.hospital_advice}</p>
                    </article>
                    <article className="pp-clinical-item">
                      <span className="pp-clinical-label">Urgent support</span>
                      <p>{result.emergency_advice}</p>
                    </article>
                  </div>
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
