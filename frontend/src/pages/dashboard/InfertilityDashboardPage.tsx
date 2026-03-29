import { useMemo, useState } from 'react'
import DashboardLayout from '../../components/dashboard/DashboardLayout'
import FormFieldInfo from '../../components/dashboard/FormFieldInfo'
import {
  predictInfertility,
  type InfertilityRequestPayload,
  type InfertilityPredictionResponse,
} from '../../services/predictionApi'
import { SNAPSHOT_KEYS, writeStageSnapshot } from '../../utils/dashboardSnapshot'

type InfertilityFormValues = {
  age: string
  everCohabited: '' | '0' | '1'
  childrenEverBorn: string
  bmi: string
  ageAtFirstMarriage: string
  monthsSinceFirstCohabitation: string
  monthsSinceLastSex: string
  irregularMenstrualCycles: '' | '0' | '1'
  chronicPelvicPain: '' | '0' | '1'
  historyPelvicInfections: '' | '0' | '1'
  hormonalSymptoms: '' | '0' | '1'
  earlyMenopauseSymptoms: '' | '0' | '1'
  autoimmuneHistory: '' | '0' | '1'
  reproductiveSurgeryHistory: '' | '0' | '1'
  smokedLast12mo: '' | '0' | '1'
  alcoholLast12mo: '' | '0' | '1'
}

type NumericFieldDef = {
  key: keyof InfertilityFormValues
  label: string
  placeholder: string
  description: string
}

type BinaryFieldDef = {
  key: keyof InfertilityFormValues
  label: string
  hint: string
  description: string
}

const requiredFields: NumericFieldDef[] = [
  {
    key: 'age',
    label: 'Age',
    placeholder: 'e.g., 28',
    description: 'Age in years.',
  },
  {
    key: 'childrenEverBorn',
    label: 'Children Ever Born',
    placeholder: 'e.g., 0',
    description: 'Total number of children previously delivered.',
  },
]

const historicalFields: NumericFieldDef[] = [
  {
    key: 'bmi',
    label: 'BMI',
    placeholder: 'e.g., 24.5',
    description: 'Body Mass Index based on height and weight.',
  },
  {
    key: 'ageAtFirstMarriage',
    label: 'Age At First Marriage/Cohabitation',
    placeholder: 'e.g., 22',
    description: 'Age at first marriage or long-term cohabitation.',
  },
  {
    key: 'monthsSinceFirstCohabitation',
    label: 'Months Since First Cohabitation',
    placeholder: 'e.g., 96',
    description: 'Number of months since first cohabitation.',
  },
  {
    key: 'monthsSinceLastSex',
    label: 'Months Since Last Sexual Intercourse',
    placeholder: 'e.g., 2',
    description: 'Number of months since last sexual intercourse.',
  },
]

const binaryFields: BinaryFieldDef[] = [
  {
    key: 'irregularMenstrualCycles',
    label: 'Irregular Menstrual Cycles',
    hint: 'Cycle timing pattern over recent months',
    description: 'Whether menstrual cycles are irregular.',
  },
  {
    key: 'chronicPelvicPain',
    label: 'Chronic Pelvic Pain',
    hint: 'Persistent pain reported for at least 3 months',
    description: 'Pelvic pain lasting at least several months.',
  },
  {
    key: 'historyPelvicInfections',
    label: 'History of Pelvic Infections',
    hint: 'Prior diagnosis or treatment history',
    description: 'Whether there has been a past pelvic infection.',
  },
  {
    key: 'hormonalSymptoms',
    label: 'Hormonal Symptoms',
    hint: 'Acne, hair growth changes, or endocrine symptoms',
    description: 'Symptoms related to hormonal imbalance.',
  },
  {
    key: 'earlyMenopauseSymptoms',
    label: 'Early Menopause Symptoms',
    hint: 'Hot flashes, cycle cessation, or ovarian decline signs',
    description: 'Symptoms suggesting early menopause.',
  },
  {
    key: 'autoimmuneHistory',
    label: 'Autoimmune History',
    hint: 'Known autoimmune condition affecting fertility context',
    description: 'Whether there is a history of autoimmune disease.',
  },
  {
    key: 'reproductiveSurgeryHistory',
    label: 'Reproductive Surgery History',
    hint: 'Prior gynecologic or reproductive procedures',
    description: 'Whether there has been surgery involving reproductive organs.',
  },
  {
    key: 'smokedLast12mo',
    label: 'Smoked in Last 12 Months',
    hint: 'Tobacco exposure in previous year',
    description: 'Whether cigarettes or other tobacco products were used in the past 12 months.',
  },
  {
    key: 'alcoholLast12mo',
    label: 'Alcohol in Last 12 Months',
    hint: 'Regular alcohol intake within previous year',
    description: 'Whether alcohol was consumed during the previous 12 months.',
  },
]

const everCohabitedDescription =
  'Whether there has ever been marriage or long-term cohabitation with a partner.'

const initialForm: InfertilityFormValues = {
  age: '',
  everCohabited: '',
  childrenEverBorn: '',
  bmi: '',
  ageAtFirstMarriage: '',
  monthsSinceFirstCohabitation: '',
  monthsSinceLastSex: '',
  irregularMenstrualCycles: '',
  chronicPelvicPain: '',
  historyPelvicInfections: '',
  hormonalSymptoms: '',
  earlyMenopauseSymptoms: '',
  autoimmuneHistory: '',
  reproductiveSurgeryHistory: '',
  smokedLast12mo: '',
  alcoholLast12mo: '',
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value))
}

function toBinary(value: '0' | '1'): 0 | 1 {
  return value === '1' ? 1 : 0
}

function toOptionalBinary(value: '' | '0' | '1'): 0 | 1 | undefined {
  if (value === '') {
    return undefined
  }
  return value === '1' ? 1 : 0
}

function humanizeFactor(factor: string): string {
  return factor
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function getFactorPresentation(value: number, index: number): { tone: 'warning' | 'positive'; note: string } {
  if (index === 0 && value >= 0.1) {
    return { tone: 'warning', note: 'Slightly Elevated Risk' }
  }

  return { tone: 'positive', note: 'Within Healthy Range' }
}

export default function InfertilityDashboardPage() {
  const [formValues, setFormValues] = useState<InfertilityFormValues>(initialForm)
  const [activeStep, setActiveStep] = useState<1 | 2>(1)
  const [result, setResult] = useState<InfertilityPredictionResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const hideHistoricalInputs = formValues.everCohabited === '0'

  const topRiskFactors = useMemo(() => {
    if (!result) {
      return []
    }
    return Object.entries(result.top_risk_factors).sort((a, b) => b[1] - a[1])
  }, [result])

  const topThreeFactors = topRiskFactors.slice(0, 3)
  const riskPercent = result ? Math.round(result.probability_infertile * 100) : 0
  const riskTone = result ? result.risk_level.toLowerCase().replace(' ', '-') : 'low-risk'
  const riskStrokeColor =
    result?.risk_level === 'High Risk'
      ? 'var(--color-error)'
      : result?.risk_level === 'Moderate Risk'
        ? 'var(--color-warning)'
        : 'var(--color-success)'

  const resultSummary = useMemo(() => {
    if (!result) {
      return null
    }

    if (result.risk_level === 'High Risk') {
      return {
        title: 'Higher infertility risk signal',
        explanation:
          'This prediction suggests a higher infertility risk signal, but it is not a final diagnosis. It is used to estimate probabilities and risk levels so you can take early precautions.',
        nextSteps: [
          'Book a reproductive health consultation soon.',
          'Track cycle consistency and symptom severity daily.',
          'Discuss top factor drivers with your provider.',
        ],
      }
    }

    if (result.risk_level === 'Moderate Risk') {
      return {
        title: 'Moderate infertility risk signal',
        explanation:
          'Your results indicate a moderate risk of infertility. With steady monitoring and early guidance, many risks can be managed well.',
        nextSteps: [
          'Schedule a near-term follow-up with a specialist.',
          'Maintain consistent symptom and cycle records.',
          'Review controllable factors such as sleep, weight, and stress.',
        ],
      }
    }

    return {
      title: 'Lower infertility risk signal',
      explanation:
        'The results indicate that you have a low risk of infertility. Keep taking care of your health, monitor any unusual changes, and check your status occasionally.',
      nextSteps: [
        'Continue routine reproductive health checks.',
        'Maintain healthy diet, movement, and sleep patterns.',
        'Reassess if cycle irregularity or pain increases.',
      ],
    }
  }, [result])

  const clearForm = () => {
    setFormValues(initialForm)
    setActiveStep(1)
    setResult(null)
    setError(null)
  }

  const validateCoreInputs = (): boolean => {
    const age = Number(formValues.age)
    const childrenEverBorn = Number(formValues.childrenEverBorn)

    if (!Number.isFinite(age) || !Number.isFinite(childrenEverBorn) || formValues.everCohabited === '') {
      setError('Age, Children Ever Born, and Ever Cohabited are required.')
      return false
    }

    return true
  }

  const submitAssessment = async () => {
    setError(null)

    if (!validateCoreInputs()) {
      return
    }

    const age = Number(formValues.age)
    const childrenEverBorn = Number(formValues.childrenEverBorn)
    const everCohabited = formValues.everCohabited
    if (everCohabited === '') {
      setError('Ever Cohabited is required.')
      return
    }

    const payload: InfertilityRequestPayload = {
      age: clamp(age, 15, 60),
      ever_cohabited: toBinary(everCohabited),
      children_ever_born: clamp(childrenEverBorn, 0, 20),
      ...(toOptionalBinary(formValues.irregularMenstrualCycles) !== undefined
        ? { irregular_menstrual_cycles: toOptionalBinary(formValues.irregularMenstrualCycles) }
        : {}),
      ...(toOptionalBinary(formValues.chronicPelvicPain) !== undefined
        ? { chronic_pelvic_pain: toOptionalBinary(formValues.chronicPelvicPain) }
        : {}),
      ...(toOptionalBinary(formValues.historyPelvicInfections) !== undefined
        ? { history_pelvic_infections: toOptionalBinary(formValues.historyPelvicInfections) }
        : {}),
      ...(toOptionalBinary(formValues.hormonalSymptoms) !== undefined
        ? { hormonal_symptoms: toOptionalBinary(formValues.hormonalSymptoms) }
        : {}),
      ...(toOptionalBinary(formValues.earlyMenopauseSymptoms) !== undefined
        ? { early_menopause_symptoms: toOptionalBinary(formValues.earlyMenopauseSymptoms) }
        : {}),
      ...(toOptionalBinary(formValues.autoimmuneHistory) !== undefined
        ? { autoimmune_history: toOptionalBinary(formValues.autoimmuneHistory) }
        : {}),
      ...(toOptionalBinary(formValues.reproductiveSurgeryHistory) !== undefined
        ? { reproductive_surgery_history: toOptionalBinary(formValues.reproductiveSurgeryHistory) }
        : {}),
      ...(everCohabited === '1' && Number.isFinite(Number(formValues.bmi))
        ? { bmi: Number(formValues.bmi) }
        : {}),
      ...(everCohabited === '1' && toOptionalBinary(formValues.smokedLast12mo) !== undefined
        ? { smoked_last_12mo: toOptionalBinary(formValues.smokedLast12mo) }
        : {}),
      ...(everCohabited === '1' && toOptionalBinary(formValues.alcoholLast12mo) !== undefined
        ? { alcohol_last_12mo: toOptionalBinary(formValues.alcoholLast12mo) }
        : {}),
      ...(everCohabited === '1' && Number.isFinite(Number(formValues.ageAtFirstMarriage))
        ? { age_at_first_marriage: Number(formValues.ageAtFirstMarriage) }
        : {}),
      ...(everCohabited === '1' && Number.isFinite(Number(formValues.monthsSinceFirstCohabitation))
        ? { months_since_first_cohabitation: Number(formValues.monthsSinceFirstCohabitation) }
        : {}),
      ...(everCohabited === '1' && Number.isFinite(Number(formValues.monthsSinceLastSex))
        ? { months_since_last_sex: Number(formValues.monthsSinceLastSex) }
        : {}),
    }

    setIsSubmitting(true)
    try {
      const prediction = await predictInfertility(payload)

      setResult(prediction)

      writeStageSnapshot(SNAPSHOT_KEYS.infertility, {
        riskLevel: prediction.risk_level,
        score: prediction.probability_infertile * 100,
        summary: `${prediction.predicted_class.replaceAll('_', ' ')} via ${prediction.assessment_mode.replaceAll('_', ' ')}`,
        modelVersion: prediction.model_version,
        capturedAt: new Date().toISOString(),
      })
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : 'Unable to generate infertility assessment.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <DashboardLayout
      title={result ? 'Infertility Risk Assessment' : 'Infertility Risk Assessment Input'}
      subtitle={
        result
          ? 'Assessment complete. Review contributing factors and next actions below.'
          : 'Provide demographics, cohabitation history, and symptom signals for the infertility model.'
      }
    >
      {!result ? (
        <section className="inf-page stage-form-shell">
          <div className="inf-step-meta-row">
            <p className="inf-step-name">
              {activeStep === 1 ? 'Stage 1: Background & Cohabitation History' : 'Stage 2: Biometrics & Symptoms'}
            </p>
            <p className="inf-step-count">Step {activeStep} of 2</p>
          </div>

          <div className="inf-progress-track">
            <div
              className="inf-progress-fill"
              style={{ width: activeStep === 1 ? '50%' : '100%' }}
            />
          </div>

          <form
            onSubmit={(event) => {
              event.preventDefault()
            }}
            className="inf-card"
          >
            <div className="inf-card-header">
              <h2 className="inf-card-title">Risk Prediction Input</h2>
              <p className="inf-card-subtitle">
                Enter required history and clinical observations. The payload maps directly to backend infertility fields.
              </p>
            </div>

            {activeStep === 1 ? (
              <div className="inf-section-stack">
                <section className="inf-section">
                  <h3 className="inf-section-title">Patient Background</h3>
                  <div className="inf-grid-2">
                    {requiredFields.map((field) => (
                      <label key={field.key} className="inf-field">
                        <span className="inf-label">
                          <FormFieldInfo label={field.label} description={field.description} textClassName="inf-label" />
                        </span>
                        <input
                          type="number"
                          required
                          value={formValues[field.key]}
                          onChange={(event) =>
                            setFormValues((previous) => ({ ...previous, [field.key]: event.target.value }))
                          }
                          placeholder={field.placeholder}
                          className="inf-input"
                        />
                      </label>
                    ))}
                  </div>

                  <div className="inf-field inf-field-inline">
                    <span className="inf-label">
                      <FormFieldInfo
                        label="Ever Cohabited"
                        description={everCohabitedDescription}
                        textClassName="inf-label"
                      />
                    </span>
                    <div className="inf-option-group">
                      <button
                        type="button"
                        onClick={() => setFormValues((previous) => ({ ...previous, everCohabited: '1' }))}
                        className={`inf-chip ${formValues.everCohabited === '1' ? 'active' : ''}`}
                      >
                        Yes
                      </button>
                      <button
                        type="button"
                        onClick={() => setFormValues((previous) => ({ ...previous, everCohabited: '0' }))}
                        className={`inf-chip ${formValues.everCohabited === '0' ? 'active' : ''}`}
                      >
                        No
                      </button>
                    </div>
                  </div>
                </section>

                {!hideHistoricalInputs ? (
                  <section className="inf-section">
                    <h3 className="inf-section-title">Historical Cohabitation Fields</h3>
                    <div className="inf-grid-2">
                      {historicalFields.map((field) => (
                        <label key={field.key} className="inf-field">
                          <span className="inf-label">
                            <FormFieldInfo label={field.label} description={field.description} textClassName="inf-label" />
                          </span>
                          <input
                            type="number"
                            value={formValues[field.key]}
                            onChange={(event) =>
                              setFormValues((previous) => ({ ...previous, [field.key]: event.target.value }))
                            }
                            placeholder={field.placeholder}
                            className="inf-input"
                          />
                        </label>
                      ))}
                    </div>
                  </section>
                ) : (
                  <p className="inf-note-box">
                    Historical cohabitation fields are hidden because Ever Cohabited is set to No.
                  </p>
                )}
              </div>
            ) : (
              <div className="inf-section-stack">
                <section className="inf-section">
                  <h3 className="inf-section-title">Symptoms & Observations</h3>
                  <div className="inf-toggle-list">
                    {binaryFields.map((field) => {
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
                            <button
                              type="button"
                              onClick={() => setFormValues((previous) => ({ ...previous, [field.key]: '0' }))}
                              className={`inf-chip ${selected === '0' ? 'active' : ''}`}
                            >
                              No
                            </button>
                            <button
                              type="button"
                              onClick={() => setFormValues((previous) => ({ ...previous, [field.key]: '1' }))}
                              className={`inf-chip ${selected === '1' ? 'active' : ''}`}
                            >
                              Yes
                            </button>
                          </div>
                        </div>
                      )
                    })}
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
                  <button
                    type="button"
                    onClick={() => {
                      setError(null)
                      if (!validateCoreInputs()) {
                        return
                      }
                      setActiveStep(2)
                    }}
                    className="inf-btn inf-btn-primary"
                  >
                    Continue
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={() => {
                      void submitAssessment()
                    }}
                    disabled={isSubmitting}
                    className="inf-btn inf-btn-primary"
                  >
                    {isSubmitting ? 'Calculating...' : 'Calculate Risk Assessment'}
                  </button>
                )}
              </div>
            </div>
          </form>
        </section>
      ) : (
        <section className="inf-result-page">
          <div className="inf-result-head">
            <div>
              <p className="inf-result-kicker">ASSESSMENT COMPLETE</p>
              <h2 className="inf-result-title">Infertility Risk Assessment</h2>
              <p className="inf-result-meta">
                Your assessment is ready. Review what this result means and the next best steps below.
              </p>
            </div>
            <div className="inf-result-head-actions">
              <span className={`inf-risk-pill inf-risk-pill-${riskTone}`}>{result.risk_level}</span>
            </div>
          </div>

          <div className="inf-result-grid">
            <div className="inf-result-main">
              <article className={`inf-summary-card inf-summary-card-${riskTone}`}>
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
                      stroke={riskStrokeColor}
                      strokeWidth="10"
                      strokeLinecap="round"
                      strokeDasharray={`${(riskPercent / 100) * 157} 157`}
                    />
                  </svg>
                  <div className="inf-gauge-value">
                    <p className="inf-gauge-number">{riskPercent}%</p>
                    <p className="inf-gauge-level">{result.risk_level.toUpperCase()}</p>
                  </div>
                </div>

                <div>
                  <h3 className="inf-summary-title">{resultSummary?.title || result.risk_level}</h3>
                  <p className="inf-summary-text">
                    Current result: <strong>{result.risk_level}</strong>
                  </p>
                  <p className="inf-summary-text">{resultSummary?.explanation}</p>
                </div>
              </article>

              <article className={`inf-info-card inf-highlight-card inf-highlight-card-${riskTone}`}>
                <p className="inf-highlight-kicker">System Recommendation</p>
                <h4 className="inf-info-title">What These Prediction Results Mean</h4>
                <p className="inf-summary-text">{resultSummary?.explanation}</p>
                <p className="inf-summary-text">
                  This is a screening estimate to guide follow-up care, not a final diagnosis. Here&apos;s some things you can immediately do:
                </p>
                <ul className="inf-list">
                  {resultSummary?.nextSteps.map((step) => (
                    <li key={step}>{step}</li>
                  ))}
                </ul>
              </article>

              <section>
                <div className={`inf-key-factor-shell inf-highlight-card inf-highlight-card-${riskTone}`}>
                <p className="inf-highlight-kicker">Key Factors</p>
                <h3 className="inf-section-heading">Key Contributing Factors</h3>
                <div className="inf-factor-grid">
                  {topThreeFactors.length > 0 ? (
                    topThreeFactors.map(([factor, value], index) => {
                      const factorView = getFactorPresentation(value, index)
                      return (
                        <article key={factor} className={`inf-factor-card inf-factor-card-${factorView.tone}`}>
                          <p className="inf-factor-label">{humanizeFactor(factor)}</p>
                          <span className={`inf-factor-dot inf-factor-dot-${factorView.tone}`} aria-hidden />
                          <p className="inf-factor-value">{value.toFixed(2)}</p>
                          <p className={`inf-factor-note inf-factor-note-${factorView.tone}`}>{factorView.note}</p>
                        </article>
                      )
                    })
                  ) : (
                    <p className="inf-note-box">No factor attributions were returned for this run.</p>
                  )}
                </div>
                </div>
              </section>

            </div>

            <aside className="inf-result-side">
              <article className={`inf-action-card inf-highlight-card inf-highlight-card-${riskTone}`}>
                <p className="inf-highlight-kicker">Next Best Actions</p>
                <h3 className="inf-section-heading">Quick Guidance</h3>
                <ul className="inf-list">
                  <li>Share this result with your healthcare provider.</li>
                  <li>Keep logging symptoms to track changes over time.</li>
                  <li>Seek care early if symptoms become more frequent or severe.</li>
                </ul>
              </article>

              <button type="button" className="inf-btn inf-btn-ghost inf-btn-full" onClick={clearForm}>
                Start New Assessment
              </button>
            </aside>
          </div>

          <p className="inf-disclaimer">
            Disclaimer: This tool provides a statistical risk assessment based on provided inputs and general clinical research.
            It is not a diagnostic tool and does not replace professional medical advice, diagnosis, or treatment.
          </p>
        </section>
      )}
    </DashboardLayout>
  )
}
