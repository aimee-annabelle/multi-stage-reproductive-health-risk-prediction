import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertCircle, ClipboardList } from 'lucide-react'
import DashboardLayout from '../../components/dashboard/DashboardLayout'
import { useAuthStore } from '../../stores/authStore'
import { ApiError } from '../../services/apiClient'
import { getPregnancyModelInfo, type PregnancyModelInfo } from '../../services/predictionApi'
import {
  assessPregnancyFollowUp,
  compareLatestPregnancyFollowUps,
  getPregnancyFollowUpHistory,
  getPregnancyTimelineSummary,
  type PregnancyFollowUpAssessPayload,
  type PregnancyAssessmentComparisonResponse,
  type PregnancyAssessmentHistoryResponse,
  type PregnancyAssessmentRecordResponse,
  type PregnancyTimelineSummaryResponse,
} from '../../services/pregnancyFollowUpApi'
import { SNAPSHOT_KEYS, writeStageSnapshot } from '../../utils/dashboardSnapshot'

type PregnancyFormValues = {
  age: string
  systolic_bp: string
  diastolic: string
  bs: string
  body_temp: string
  bmi: string
  heart_rate: string
  previous_complications: '' | '0' | '1'
  preexisting_diabetes: '' | '0' | '1'
  gestational_diabetes: '' | '0' | '1'
  mental_health: '' | '0' | '1'
  gestational_age_weeks: string
  visit_label: string
  notes: string
}

const initialForm: PregnancyFormValues = {
  age: '28',
  systolic_bp: '120',
  diastolic: '80',
  bs: '',
  body_temp: '',
  bmi: '',
  heart_rate: '',
  previous_complications: '',
  preexisting_diabetes: '',
  gestational_diabetes: '',
  mental_health: '',
  gestational_age_weeks: '',
  visit_label: '',
  notes: '',
}

const weekdayFallback = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

function toOptionalBinary(value: '' | '0' | '1'): 0 | 1 | undefined {
  if (value === '') {
    return undefined
  }
  return value === '1' ? 1 : 0
}

function formatShortWeekday(value: string, fallbackIndex: number): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return weekdayFallback[fallbackIndex % weekdayFallback.length]
  }

  return new Intl.DateTimeFormat(undefined, { weekday: 'short' }).format(date)
}

function toTrimester(week: number): string {
  if (week >= 28) {
    return 'Third Trimester'
  }
  if (week >= 13) {
    return 'Second Trimester'
  }
  return 'First Trimester'
}

function toTitleLabel(value: string): string {
  return value
    .replaceAll('_', ' ')
    .split(' ')
    .filter(Boolean)
    .map((chunk) => chunk.charAt(0).toUpperCase() + chunk.slice(1))
    .join(' ')
}

function toBinaryString(value: number | null): '' | '0' | '1' {
  if (value === 0) {
    return '0'
  }
  if (value === 1) {
    return '1'
  }
  return ''
}

function recordToFormValues(record: PregnancyAssessmentRecordResponse): PregnancyFormValues {
  return {
    age: String(record.age),
    systolic_bp: String(record.systolic_bp),
    diastolic: String(record.diastolic),
    bs: record.bs == null ? '' : String(record.bs),
    body_temp: record.body_temp == null ? '' : String(record.body_temp),
    bmi: record.bmi == null ? '' : String(record.bmi),
    heart_rate: record.heart_rate == null ? '' : String(record.heart_rate),
    previous_complications: toBinaryString(record.previous_complications),
    preexisting_diabetes: toBinaryString(record.preexisting_diabetes),
    gestational_diabetes: toBinaryString(record.gestational_diabetes),
    mental_health: toBinaryString(record.mental_health),
    gestational_age_weeks: record.gestational_age_weeks == null ? '' : String(record.gestational_age_weeks),
    visit_label: record.visit_label || '',
    notes: record.notes || '',
  }
}

export default function PregnancyDashboardPage() {
  const navigate = useNavigate()
  const logout = useAuthStore((state) => state.logout)

  const [formValues, setFormValues] = useState<PregnancyFormValues>(initialForm)
  const [firstTimeStep, setFirstTimeStep] = useState<1 | 2>(1)
  const [modelInfo, setModelInfo] = useState<PregnancyModelInfo | null>(null)
  const [latestRecord, setLatestRecord] = useState<PregnancyAssessmentRecordResponse | null>(null)
  const [history, setHistory] = useState<PregnancyAssessmentHistoryResponse | null>(null)
  const [comparison, setComparison] = useState<PregnancyAssessmentComparisonResponse | null>(null)
  const [comparisonNotice, setComparisonNotice] = useState<string | null>(null)
  const [timeline, setTimeline] = useState<PregnancyTimelineSummaryResponse | null>(null)

  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isLoadingWidgets, setIsLoadingWidgets] = useState(false)
  const [isBootstrapping, setIsBootstrapping] = useState(true)

  const handleAuthFailure = useCallback(async () => {
    await logout()
    navigate('/sign-in')
  }, [logout, navigate])

  const loadWidgets = useCallback(async () => {
    setIsLoadingWidgets(true)

    try {
      const [historyResponse, timelineResponse] = await Promise.all([
        getPregnancyFollowUpHistory(20),
        getPregnancyTimelineSummary(50),
      ])

      setHistory(historyResponse)
      setTimeline(timelineResponse)

      if (historyResponse.assessments.length > 0) {
        setLatestRecord(historyResponse.assessments[0])
      } else {
        setLatestRecord(null)
      }

      try {
        const comparisonResponse = await compareLatestPregnancyFollowUps()
        setComparison(comparisonResponse)
        setComparisonNotice(null)
      } catch (comparisonError) {
        if (comparisonError instanceof ApiError && comparisonError.status === 422) {
          setComparison(null)
          setComparisonNotice('Comparison becomes available after at least two stored follow-up records.')
        } else {
          throw comparisonError
        }
      }
    } catch (widgetError) {
      if (widgetError instanceof ApiError && widgetError.status === 401) {
        await handleAuthFailure()
        return
      }
      setError(widgetError instanceof Error ? widgetError.message : 'Unable to load follow-up widgets.')
    } finally {
      setIsLoadingWidgets(false)
    }
  }, [handleAuthFailure])

  useEffect(() => {
    let active = true

    const bootstrap = async () => {
      try {
        const info = await getPregnancyModelInfo()
        if (active) {
          setModelInfo(info)
        }
      } catch {
        if (active) {
          setModelInfo(null)
        }
      }

      if (active) {
        await loadWidgets()
      }

      if (active) {
        setIsBootstrapping(false)
      }
    }

    void bootstrap()

    return () => {
      active = false
    }
  }, [loadWidgets])

  useEffect(() => {
    if (!latestRecord) {
      return
    }
    setFormValues(recordToFormValues(latestRecord))
  }, [latestRecord])

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)

    const age = Number(formValues.age)
    const systolic = Number(formValues.systolic_bp)
    const diastolic = Number(formValues.diastolic)
    const gestationalAgeWeeks = Number(formValues.gestational_age_weeks)
    const hasRecords = (timeline?.total_records ?? 0) > 0 || Boolean(latestRecord)

    if (!Number.isFinite(age) || !Number.isFinite(systolic) || !Number.isFinite(diastolic)) {
      setError('Age, systolic BP, and diastolic BP are required numeric values.')
      return
    }

    if (!hasRecords && !Number.isFinite(gestationalAgeWeeks)) {
      setError('Gestational age (weeks) is required for the baseline assessment.')
      return
    }

    const visitLabel = formValues.visit_label.trim()

    const payload: PregnancyFollowUpAssessPayload = {
      age,
      systolic_bp: systolic,
      diastolic,
      ...(Number.isFinite(Number(formValues.bs)) ? { bs: Number(formValues.bs) } : {}),
      ...(Number.isFinite(Number(formValues.body_temp)) ? { body_temp: Number(formValues.body_temp) } : {}),
      ...(Number.isFinite(Number(formValues.bmi)) ? { bmi: Number(formValues.bmi) } : {}),
      ...(Number.isFinite(Number(formValues.heart_rate)) ? { heart_rate: Number(formValues.heart_rate) } : {}),
      ...(toOptionalBinary(formValues.previous_complications) !== undefined
        ? { previous_complications: toOptionalBinary(formValues.previous_complications) }
        : {}),
      ...(toOptionalBinary(formValues.preexisting_diabetes) !== undefined
        ? { preexisting_diabetes: toOptionalBinary(formValues.preexisting_diabetes) }
        : {}),
      ...(toOptionalBinary(formValues.gestational_diabetes) !== undefined
        ? { gestational_diabetes: toOptionalBinary(formValues.gestational_diabetes) }
        : {}),
      ...(toOptionalBinary(formValues.mental_health) !== undefined
        ? { mental_health: toOptionalBinary(formValues.mental_health) }
        : {}),
      ...(Number.isFinite(Number(formValues.gestational_age_weeks))
        ? { gestational_age_weeks: Number(formValues.gestational_age_weeks) }
        : {}),
      ...(visitLabel ? { visit_label: visitLabel } : !hasRecords ? { visit_label: 'Baseline Assessment' } : {}),
      ...(formValues.notes.trim() ? { notes: formValues.notes.trim() } : {}),
    }

    setIsSubmitting(true)
    try {
      const record = await assessPregnancyFollowUp(payload)
      setLatestRecord(record)
      setFormValues(recordToFormValues(record))
      setFirstTimeStep(1)

      writeStageSnapshot(SNAPSHOT_KEYS.pregnancy, {
        riskLevel: record.risk_level,
        score: record.probability_high_risk * 100,
        summary: `${record.predicted_class.replaceAll('_', ' ')} at ${Math.round(record.probability_high_risk * 100)}% high-risk probability`,
        modelVersion: record.model_version,
        capturedAt: new Date().toISOString(),
      })

      await loadWidgets()
    } catch (submissionError) {
      if (submissionError instanceof ApiError && submissionError.status === 401) {
        await handleAuthFailure()
        return
      }
      setError(submissionError instanceof Error ? submissionError.message : 'Unable to submit pregnancy assessment.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const hasRecords = (timeline?.total_records ?? 0) > 0 || Boolean(latestRecord)
  const currentWeek = hasRecords ? (latestRecord?.gestational_age_weeks ?? null) : null
  const trimester = currentWeek !== null ? toTrimester(currentWeek) : null
  const weekRangeStart = currentWeek !== null ? Math.max(1, currentWeek - 4) : null
  const weekTabs = weekRangeStart === null ? [] : Array.from({ length: 8 }, (_, index) => weekRangeStart + index)

  const latestProbability = hasRecords
    ? (latestRecord?.probability_high_risk ?? timeline?.latest_probability_high_risk ?? comparison?.latest_probability_high_risk ?? null)
    : null
  const latestRiskPercent = latestProbability === null ? null : Math.round(latestProbability * 100)
  const riskThresholdPercent = modelInfo ? Math.round(modelInfo.threshold * 100) : 50
  const riskTone = latestRiskPercent === null ? null : latestRiskPercent >= riskThresholdPercent ? 'high' : 'low'
  const displayedScore = latestRiskPercent
  const ringStyle = {
    background:
      displayedScore === null
        ? 'var(--color-primary-light)'
        : `conic-gradient(from -88deg, var(--color-primary) ${displayedScore}%, var(--color-primary-light) ${displayedScore}% 100%)`,
  }

  const chartData = useMemo(() => {
    const points = timeline?.points.slice(-7) ?? []
    return points.map((point, index) => {
      const riskHeight = Math.max(14, Math.round(point.probability_high_risk * 120))
      const systolicNormalized = Math.max(0, Math.min(100, ((point.systolic_bp - 90) / 70) * 100))
      const systolicHeight = Math.max(12, Math.round((systolicNormalized / 100) * 90))
      return {
        key: String(point.assessment_id),
        label: formatShortWeekday(point.created_at, index),
        riskHeight,
        systolicHeight,
      }
    })
  }, [timeline])

  const topCurrentFactors = useMemo(() => {
    if (!latestRecord) {
      return []
    }
    return Object.entries(latestRecord.top_risk_factors)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 4)
      .map(([name, value]) => ({
        name: toTitleLabel(name),
        value,
      }))
  }, [latestRecord])

  const flagCards = [
    {
      title: 'Gestational Diabetes',
      value:
        latestRecord?.gestational_diabetes === 1
          ? 'Positive Signal'
          : latestRecord?.gestational_diabetes === 0
            ? 'Negative'
            : 'Not Logged',
      tone: latestRecord?.gestational_diabetes === 1 ? 'warn' : 'ok',
    },
    {
      title: 'Blood Pressure',
      value:
        latestRecord && (latestRecord.systolic_bp >= 140 || latestRecord.diastolic >= 90)
          ? 'Elevated'
          : latestRecord
            ? 'Within Range'
            : 'Not Logged',
      tone: latestRecord && (latestRecord.systolic_bp >= 140 || latestRecord.diastolic >= 90) ? 'warn' : 'ok',
    },
    {
      title: 'BMI Status',
      value:
        latestRecord?.bmi == null
          ? 'Not Logged'
          : latestRecord.bmi >= 30
            ? 'Above Range'
            : latestRecord.bmi < 18.5
              ? 'Below Range'
              : 'Healthy Range',
      tone:
        latestRecord?.bmi == null
          ? 'neutral'
          : latestRecord.bmi >= 30 || latestRecord.bmi < 18.5
            ? 'warn'
            : 'ok',
    },
    {
      title: 'Emergency Signal',
      value: latestRecord?.advise_emergency_care ? 'Attention Needed' : latestRecord ? 'No Signal' : 'Not Logged',
      tone: latestRecord?.advise_emergency_care ? 'warn' : 'ok',
    },
  ] as const

  const continueFirstTimeFlow = () => {
    const age = Number(formValues.age)
    const systolic = Number(formValues.systolic_bp)
    const diastolic = Number(formValues.diastolic)
    const gestationalAgeWeeks = Number(formValues.gestational_age_weeks)
    if (
      !Number.isFinite(age) ||
      !Number.isFinite(systolic) ||
      !Number.isFinite(diastolic) ||
      !Number.isFinite(gestationalAgeWeeks)
    ) {
      setError('Age, systolic BP, diastolic BP, and gestational age are required numeric values.')
      return
    }
    setError(null)
    setFirstTimeStep(2)
  }

  const resetPregnancyForm = () => {
    setFormValues(initialForm)
    setError(null)
    setFirstTimeStep(1)
  }

  if (isBootstrapping) {
    return (
      <DashboardLayout title="Pregnancy Risk Prediction" subtitle="Loading your pregnancy history...">
        <section className="stage-form-shell">
          <p className="preg-monitor-placeholder-note">Loading...</p>
        </section>
      </DashboardLayout>
    )
  }

  if (!hasRecords) {
    return (
      <DashboardLayout
        title="Pregnancy Risk Prediction"
        subtitle="Complete your first pregnancy assessment to create baseline monitoring data."
      >
        <section className="stage-form-shell">
          <div className="inf-step-meta-row">
            <p className="inf-step-name">
              {firstTimeStep === 1 ? 'Stage 1: Baseline Vitals' : 'Stage 2: Clinical & Follow-up Details'}
            </p>
            <p className="inf-step-count">Step {firstTimeStep} of 2</p>
          </div>
          <div className="inf-progress-track">
            <span className="inf-progress-fill" style={{ width: firstTimeStep === 1 ? '50%' : '100%' }} />
          </div>

          <form
            className="inf-card"
            onSubmit={(event) => {
              if (firstTimeStep === 1) {
                event.preventDefault()
                return
              }
              void handleSubmit(event)
            }}
          >
            <div className="inf-card-header">
              <h2 className="inf-card-title">Pregnancy Risk Prediction Input</h2>
              <p className="inf-card-subtitle">
                {firstTimeStep === 1
                  ? 'Enter core vitals to start your first pregnancy risk assessment.'
                  : 'Add optional indicators and metadata before saving your baseline assessment.'}
              </p>
            </div>

            {firstTimeStep === 1 ? (
              <div className="inf-section-stack">
                <section className="inf-section">
                  <h3 className="inf-section-title">Required Vitals</h3>
                  <div className="inf-grid-2">
                    {[
                      ['age', 'Age (years)', '28'],
                      ['systolic_bp', 'Systolic BP (mmHg)', '120'],
                      ['diastolic', 'Diastolic BP (mmHg)', '80'],
                      ['gestational_age_weeks', 'Gestational Age (weeks)', '28'],
                    ].map(([key, label, placeholder]) => (
                      <label key={key} className="inf-field">
                        <span className="inf-label">{label}</span>
                        <input
                          type="number"
                          value={formValues[key as keyof PregnancyFormValues]}
                          onChange={(event) => setFormValues((previous) => ({ ...previous, [key]: event.target.value }))}
                          placeholder={placeholder}
                          className="inf-input"
                        />
                      </label>
                    ))}
                  </div>
                  <p className="inf-meta-line">Required: Age, systolic BP, diastolic BP, and gestational age.</p>
                </section>
              </div>
            ) : (
              <div className="inf-section-stack">
                <section className="inf-section">
                  <h3 className="inf-section-title">Optional Clinical Inputs</h3>
                  <div className="inf-grid-2">
                    {[
                      ['bs', 'Blood Sugar (bs)', '6.1'],
                      ['body_temp', 'Body Temp (F)', '98.6'],
                      ['bmi', 'BMI', '24.2'],
                      ['heart_rate', 'Heart Rate', '78'],
                    ].map(([key, label, placeholder]) => (
                      <label key={key} className="inf-field">
                        <span className="inf-label">{label}</span>
                        <input
                          type="number"
                          value={formValues[key as keyof PregnancyFormValues]}
                          onChange={(event) => setFormValues((previous) => ({ ...previous, [key]: event.target.value }))}
                          placeholder={placeholder}
                          className="inf-input"
                        />
                      </label>
                    ))}
                  </div>
                </section>

                <section className="inf-section">
                  <h3 className="inf-section-title">Clinical Indicators</h3>
                  <div className="inf-toggle-list">
                    {[
                      ['previous_complications', 'Previous complications'],
                      ['preexisting_diabetes', 'Preexisting diabetes'],
                      ['gestational_diabetes', 'Gestational diabetes'],
                      ['mental_health', 'Mental health concerns'],
                    ].map(([key, label]) => {
                      const selected = formValues[key as keyof PregnancyFormValues] as '' | '0' | '1'
                      return (
                        <div className="inf-toggle-row" key={key}>
                          <p className="inf-toggle-title">{label}</p>
                          <div className="inf-option-group">
                            <button
                              type="button"
                              className={`inf-chip ${selected === '0' ? 'active' : ''}`}
                              onClick={() => setFormValues((previous) => ({ ...previous, [key]: '0' }))}
                            >
                              No
                            </button>
                            <button
                              type="button"
                              className={`inf-chip ${selected === '1' ? 'active' : ''}`}
                              onClick={() => setFormValues((previous) => ({ ...previous, [key]: '1' }))}
                            >
                              Yes
                            </button>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </section>

                <section className="inf-section">
                  <h3 className="inf-section-title">Follow-up Metadata</h3>
                  <div className="inf-grid-2">
                    <label className="inf-field">
                      <span className="inf-label">Visit Label</span>
                      <input
                        value={formValues.visit_label}
                        onChange={(event) => setFormValues((previous) => ({ ...previous, visit_label: event.target.value }))}
                        placeholder="e.g., ANC Visit 1 or Baseline"
                        className="inf-input"
                      />
                    </label>
                    <label className="inf-field">
                      <span className="inf-label">Notes</span>
                      <input
                        value={formValues.notes}
                        onChange={(event) => setFormValues((previous) => ({ ...previous, notes: event.target.value }))}
                        placeholder="Optional notes"
                        className="inf-input"
                      />
                    </label>
                  </div>
                  <p className="inf-meta-line">
                    Visit label is just a name for this check-in (example: Baseline, ANC Visit 1, Week 28 check).
                  </p>
                </section>
              </div>
            )}

            {error ? <p className="inf-error-box">{error}</p> : null}

            <div className="inf-action-row">
              <button type="button" onClick={resetPregnancyForm} className="inf-btn inf-btn-ghost">
                Clear Form
              </button>
              <div className="inf-action-group">
                {firstTimeStep === 2 ? (
                  <button type="button" onClick={() => setFirstTimeStep(1)} className="inf-btn inf-btn-ghost">
                    Back
                  </button>
                ) : null}
                {firstTimeStep === 1 ? (
                  <button type="button" onClick={continueFirstTimeFlow} className="inf-btn inf-btn-primary">
                    Continue
                  </button>
                ) : (
                  <button type="submit" disabled={isSubmitting} className="inf-btn inf-btn-primary">
                    {isSubmitting ? 'Submitting...' : 'Create First Assessment'}
                  </button>
                )}
              </div>
            </div>
          </form>
        </section>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout title="Pregnancy Risk Monitor">
      <section className="preg-monitor-page">
        <div className="preg-monitor-top-row">
          <div>
            <h2 className="preg-monitor-week-title">Week {currentWeek ?? '--'}</h2>
            <p className="preg-monitor-week-meta">
              {`Record ${timeline?.total_records ?? 0} • ${trimester || 'Trimester unavailable'}`}
            </p>
          </div>
          <div className="preg-monitor-appointment">
            <p className="preg-monitor-appointment-label">Next Appointment</p>
            <p className="preg-monitor-appointment-value">
              {latestRecord?.visit_label || 'Not available from backend yet'}
            </p>
          </div>
        </div>

        {weekTabs.length > 0 ? (
          <div className="preg-monitor-week-tabs">
            {weekTabs.map((week) => (
              <span
                key={week}
                className={`preg-monitor-week-chip${week === currentWeek ? ' is-active' : week > (currentWeek ?? 0) ? ' is-future' : ''}`}
              >
                Wk {week}
              </span>
            ))}
          </div>
        ) : (
          <p className="preg-monitor-placeholder-note">No weekly records available yet.</p>
        )}

        <div className="preg-monitor-grid">
          <div className="preg-monitor-main">
            <article className="preg-monitor-status-card">
              <div className="preg-monitor-score-frame">
                <div className="preg-monitor-score-ring" style={ringStyle}>
                  <div className="preg-monitor-score-core">
                    <p className="preg-monitor-score-value">{displayedScore === null ? '--' : displayedScore}</p>
                    <p className="preg-monitor-score-label">SCORE</p>
                  </div>
                </div>
              </div>

              <div className="preg-monitor-status-content">
                <div className="preg-monitor-status-head">
                  <h3 className="preg-monitor-status-title">
                    {riskTone === null ? 'No records yet' : riskTone === 'high' ? 'Needs closer monitoring' : 'Stable health status'}
                  </h3>
                  <span
                    className={`preg-monitor-risk-pill ${
                      riskTone === null ? 'risk-none' : riskTone === 'high' ? 'risk-high' : 'risk-low'
                    }`}
                  >
                    {riskTone === null ? 'No Data' : riskTone === 'high' ? 'High Risk' : 'Low Risk'}
                  </span>
                </div>
                <p className="preg-monitor-status-text">
                  {latestRecord
                    ? latestRecord.hospital_advice
                    : 'No records yet. Log daily vitals to populate this dashboard with personalized guidance.'}
                </p>

                <div className="preg-monitor-risk-row">
                  <div className="preg-monitor-risk-labels">
                    <span>Key Factors Influencing Current Score</span>
                    <strong>{latestRiskPercent === null ? '--' : `${latestRiskPercent}%`}</strong>
                  </div>
                  {topCurrentFactors.length > 0 ? (
                    <ul className="preg-monitor-factor-list">
                      {topCurrentFactors.map((factor) => (
                        <li key={factor.name} className="preg-monitor-factor-item">
                          <span>{factor.name}</span>
                          <strong>{factor.value.toFixed(3)}</strong>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="preg-monitor-risk-note">No factor breakdown available yet.</p>
                  )}
                  {latestRiskPercent === null ? null : (
                    <p className="preg-monitor-risk-note">
                      Threshold {riskThresholdPercent}% • Trend {comparison?.trend || timeline?.trend || 'not enough records'}
                    </p>
                  )}
                </div>
              </div>
            </article>

            <article className="preg-monitor-history-card">
              <div className="preg-monitor-card-head">
                <h3>Symptom & Vitals History</h3>
                <div className="preg-monitor-pill-row">
                  <span className="preg-monitor-pill active">7 Days</span>
                  <span className="preg-monitor-pill">30 Days</span>
                </div>
              </div>

              {chartData.length > 0 ? (
                <div className="preg-monitor-chart">
                  {chartData.map((item) => (
                    <div key={item.key} className="preg-monitor-chart-col">
                      <div className="preg-monitor-chart-bars">
                        <span className="preg-monitor-bar risk" style={{ height: `${item.riskHeight}px` }} />
                        <span className="preg-monitor-bar systolic" style={{ height: `${item.systolicHeight}px` }} />
                      </div>
                      <span className="preg-monitor-chart-label">{item.label}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="preg-monitor-chart preg-monitor-chart-empty">No history records yet.</div>
              )}

              <div className="preg-monitor-legend">
                <span>
                  <i className="dot risk" />
                  High-risk probability
                </span>
                <span>
                  <i className="dot systolic" />
                  Systolic trend
                </span>
              </div>
              {chartData.length === 0 ? (
                <p className="preg-monitor-placeholder-note">Chart will appear after first saved follow-up.</p>
              ) : null}
            </article>

            <article className="preg-monitor-flags-card">
              <h3>Current Trimester Risk Flags</h3>
              <div className="preg-monitor-flag-grid">
                {flagCards.map((card) => (
                  <div key={card.title} className={`preg-monitor-flag-item tone-${card.tone}`}>
                    <p className="preg-monitor-flag-title">{card.title}</p>
                    <p className="preg-monitor-flag-value">{card.value}</p>
                  </div>
                ))}
              </div>
            </article>

          </div>

          <aside className="preg-monitor-side">
            <form
              onSubmit={(event) => {
                void handleSubmit(event)
              }}
              className="preg-checkin-card"
            >
              <h3 className="preg-checkin-title">
                <ClipboardList size={19} strokeWidth={2.1} aria-hidden />
                Daily Check-in
              </h3>
              <p className="preg-checkin-subtitle">Log current vitals for follow-up risk assessment.</p>

              <label className="preg-checkin-field">
                <span>Age (years)</span>
                <input
                  type="number"
                  value={formValues.age}
                  onChange={(event) => setFormValues((previous) => ({ ...previous, age: event.target.value }))}
                  placeholder="e.g., 28"
                  className="preg-checkin-input"
                />
              </label>

              <label className="preg-checkin-field">
                <span>Blood Pressure (mmHg)</span>
                <div className="preg-checkin-bp-row">
                  <input
                    type="number"
                    value={formValues.systolic_bp}
                    onChange={(event) => setFormValues((previous) => ({ ...previous, systolic_bp: event.target.value }))}
                    placeholder="Sys"
                    className="preg-checkin-input"
                  />
                  <span>/</span>
                  <input
                    type="number"
                    value={formValues.diastolic}
                    onChange={(event) => setFormValues((previous) => ({ ...previous, diastolic: event.target.value }))}
                    placeholder="Dia"
                    className="preg-checkin-input"
                  />
                </div>
              </label>

              <label className="preg-checkin-field">
                <span>BMI (optional)</span>
                <input
                  type="number"
                  value={formValues.bmi}
                  onChange={(event) => setFormValues((previous) => ({ ...previous, bmi: event.target.value }))}
                  placeholder="e.g., 24.5"
                  className="preg-checkin-input"
                />
              </label>

              <div className="preg-checkin-checkboxes">
                <p>Clinical Indicators</p>
                {[
                  ['previous_complications', 'Previous complications'],
                  ['preexisting_diabetes', 'Preexisting diabetes'],
                  ['gestational_diabetes', 'Gestational diabetes'],
                  ['mental_health', 'Mental health concerns'],
                ].map(([key, label]) => (
                  <label key={key} className="preg-checkin-checkbox-row">
                    <input
                      type="checkbox"
                      checked={formValues[key as keyof PregnancyFormValues] === '1'}
                      onChange={(event) =>
                        setFormValues((previous) => ({
                          ...previous,
                          [key]: event.target.checked ? '1' : '',
                        }))
                      }
                    />
                    <span>{label}</span>
                  </label>
                ))}
              </div>

              <details className="preg-checkin-advanced">
                <summary>Advanced Inputs</summary>
                <div className="preg-checkin-advanced-grid">
                  {[
                    ['bs', 'Blood Sugar', '6.1'],
                    ['body_temp', 'Body Temp (F)', '98.6'],
                    ['heart_rate', 'Heart Rate', '78'],
                    ['gestational_age_weeks', 'Gestational Week', '28'],
                  ].map(([key, label, placeholder]) => (
                    <label key={key} className="preg-checkin-field">
                      <span>{label}</span>
                      <input
                        type="number"
                        value={formValues[key as keyof PregnancyFormValues]}
                        onChange={(event) =>
                          setFormValues((previous) => ({ ...previous, [key]: event.target.value }))
                        }
                        placeholder={placeholder}
                        className="preg-checkin-input"
                      />
                    </label>
                  ))}
                  <label className="preg-checkin-field">
                    <span>Visit Label</span>
                    <input
                      value={formValues.visit_label}
                      onChange={(event) => setFormValues((previous) => ({ ...previous, visit_label: event.target.value }))}
                      placeholder="ANC Visit"
                      className="preg-checkin-input"
                    />
                  </label>
                  <label className="preg-checkin-field">
                    <span>Notes</span>
                    <textarea
                      value={formValues.notes}
                      onChange={(event) => setFormValues((previous) => ({ ...previous, notes: event.target.value }))}
                      placeholder="Optional observations"
                      rows={3}
                      className="preg-checkin-textarea"
                    />
                  </label>
                </div>
              </details>

              {error ? <p className="preg-checkin-error">{error}</p> : null}

              <div className="preg-checkin-actions">
                <button type="submit" disabled={isSubmitting} className="preg-checkin-submit">
                  {isSubmitting ? 'Saving...' : 'Log Daily Vitals'}
                </button>
                <button
                  type="button"
                  className="preg-checkin-reset"
                  onClick={() => {
                    setFormValues(initialForm)
                    setError(null)
                  }}
                >
                  Reset
                </button>
              </div>
            </form>

            <div className={`preg-monitor-alert-card ${latestRecord?.advise_emergency_care ? 'is-critical' : ''}`}>
              <p className="preg-monitor-alert-title">
                <AlertCircle size={17} strokeWidth={2.2} aria-hidden />
                {latestRecord?.advise_emergency_care ? 'Urgent Follow-up Recommended' : 'Monitoring Insight'}
              </p>
              <p className="preg-monitor-alert-text">
                {latestRecord?.advise_emergency_care
                  ? latestRecord.emergency_advice
                  : latestRecord?.hospital_advice || 'Submit a check-in to receive latest monitoring guidance.'}
              </p>
            </div>

            <div className="preg-monitor-side-stats">
              <p>
                Records tracked: <strong>{history?.total_records ?? 0}</strong>
              </p>
              <p>
                Trend: <strong>{comparison?.trend || timeline?.trend || 'No trend yet'}</strong>
              </p>
              <p>
                Emergency referrals: <strong>{timeline?.emergency_referral_count ?? 0}</strong>
              </p>
              {comparisonNotice ? <p className="preg-monitor-side-note">{comparisonNotice}</p> : null}
              {isLoadingWidgets ? <p className="preg-monitor-side-note">Refreshing timeline widgets...</p> : null}
            </div>
          </aside>
        </div>
      </section>
    </DashboardLayout>
  )
}
