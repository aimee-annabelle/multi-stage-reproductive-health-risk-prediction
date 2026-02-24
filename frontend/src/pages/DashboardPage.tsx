import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { useDashboardStore, type HealthStage } from '../stores/dashboardStore'
import '../styles/dashboard.css'

const stageMeta: Record<HealthStage, { label: string; icon: string }> = {
  infertility: { label: 'Infertility', icon: '✣' },
  pregnancy: { label: 'Pregnancy', icon: '♡' },
  postpartum: { label: 'Postpartum', icon: '☺' },
}

const stageOrder: HealthStage[] = ['infertility', 'pregnancy', 'postpartum']

type StageField = {
  field: string
  label: string
  placeholder?: string
  inputType?: 'binary' | 'text'
}

const stageFormFields: Record<HealthStage, StageField[]> = {
  infertility: [
    { field: 'age', label: 'Age', placeholder: '28', inputType: 'text' },
    { field: 'childrenEverBorn', label: 'Children Ever Born', placeholder: '0', inputType: 'text' },
    { field: 'bmi', label: 'BMI', placeholder: '24.5', inputType: 'text' },
    { field: 'ageAtFirstMarriage', label: 'Age At First Marriage/Cohabitation', placeholder: '22', inputType: 'text' },
    { field: 'monthsSinceFirstCohabitation', label: 'Months Since First Cohabitation', placeholder: '96', inputType: 'text' },
    { field: 'monthsSinceLastSex', label: 'Months Since Last Sex', placeholder: '2', inputType: 'text' },
    { field: 'everCohabited', label: 'Ever Cohabited', placeholder: '1', inputType: 'binary' },
    { field: 'irregularMenstrualCycles', label: 'Irregular Menstrual Cycles', placeholder: '0', inputType: 'binary' },
    { field: 'chronicPelvicPain', label: 'Chronic Pelvic Pain', placeholder: '0', inputType: 'binary' },
    { field: 'historyPelvicInfections', label: 'History of Pelvic Infections', placeholder: '0', inputType: 'binary' },
    { field: 'hormonalSymptoms', label: 'Hormonal Symptoms', placeholder: '0', inputType: 'binary' },
    { field: 'earlyMenopauseSymptoms', label: 'Early Menopause Symptoms', placeholder: '0', inputType: 'binary' },
    { field: 'autoimmuneHistory', label: 'Autoimmune History', placeholder: '0', inputType: 'binary' },
    { field: 'reproductiveSurgeryHistory', label: 'Reproductive Surgery History', placeholder: '0', inputType: 'binary' },
    { field: 'smokedLast12mo', label: 'Smoked Last 12 Months', placeholder: '0', inputType: 'binary' },
    { field: 'alcoholLast12mo', label: 'Alcohol Last 12 Months', placeholder: '0', inputType: 'binary' },
  ],
  pregnancy: [
    { field: 'currentWeek', label: 'Current Week', placeholder: 'Week 1-40' },
    { field: 'systolicBP', label: 'Systolic BP', placeholder: '120' },
    { field: 'diastolicBP', label: 'Diastolic BP', placeholder: '80' },
    { field: 'symptoms', label: 'Symptoms', placeholder: 'e.g. dizziness, headache' },
  ],
  postpartum: [
    { field: 'weeksPostpartum', label: 'Weeks Postpartum', placeholder: '6' },
    { field: 'sleepHours', label: 'Sleep Hours (avg/night)', placeholder: '7' },
    { field: 'moodScore', label: 'Mood Score (1-10)', placeholder: '8' },
    { field: 'symptoms', label: 'Symptoms', placeholder: 'e.g. mood swings, fatigue' },
  ],
}

const historicalInfertilityFields = new Set([
  'bmi',
  'smokedLast12mo',
  'alcoholLast12mo',
  'ageAtFirstMarriage',
  'monthsSinceFirstCohabitation',
  'monthsSinceLastSex',
])

export default function DashboardPage() {
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)
  const selectedStage = useDashboardStore((state) => state.selectedStage)
  const formValues = useDashboardStore((state) => state.formValues)
  const result = useDashboardStore((state) => state.result)
  const setStage = useDashboardStore((state) => state.setStage)
  const setField = useDashboardStore((state) => state.setField)
  const assessRisk = useDashboardStore((state) => state.assessRisk)
  const resetAssessment = useDashboardStore((state) => state.resetAssessment)
  const isAssessing = useDashboardStore((state) => state.isAssessing)
  const assessmentError = useDashboardStore((state) => state.assessmentError)

  const firstName = user?.fullName?.split(' ')[0] || 'Sarah'

  const wellnessPoints = [82, 85, 84, 88, 90, 89, 92]

  const chartPath = useMemo(() => {
    const max = 100
    const min = 0
    const width = 520
    const height = 170

    return wellnessPoints
      .map((value, index) => {
        const x = (index / (wellnessPoints.length - 1)) * width
        const y = height - ((value - min) / (max - min)) * height
        return `${index === 0 ? 'M' : 'L'} ${x} ${y}`
      })
      .join(' ')
  }, [wellnessPoints])

  const handleLogout = async () => {
    await logout()
    navigate('/sign-in')
  }

  const activeFormValues = formValues[selectedStage]
  const activeFields = stageFormFields[selectedStage]
  const stageIndex = stageOrder.indexOf(selectedStage)
  const standardInfertilityFields = selectedStage === 'infertility'
    ? activeFields.filter((item) => item.inputType !== 'binary')
    : []
  const binaryInfertilityFields = selectedStage === 'infertility'
    ? activeFields.filter((item) => item.inputType === 'binary')
    : []
  const hideHistoricalInputs =
    selectedStage === 'infertility' && activeFormValues.everCohabited === '0'
  const visibleStandardInfertilityFields = hideHistoricalInputs
    ? standardInfertilityFields.filter((item) => !historicalInfertilityFields.has(item.field))
    : standardInfertilityFields
  const visibleBinaryInfertilityFields = hideHistoricalInputs
    ? binaryInfertilityFields.filter((item) => !historicalInfertilityFields.has(item.field))
    : binaryInfertilityFields

  return (
    <div className="dashboard-page">
      <header className="dashboard-top-nav">
        <div className="dashboard-shell dashboard-shell-nav">
          <div className="dashboard-brand">
            <span className="dashboard-brand-mark" aria-hidden>✧</span>
            <span>Natalis AI</span>
          </div>

          <nav className="dashboard-links" aria-label="Primary">
            <a className="active" href="#">Dashboard</a>
            <a href="#">My Health</a>
            <a href="#">Reports</a>
            <a href="#">Community</a>
          </nav>

          <div className="dashboard-actions">
            <button type="button" className="icon-btn" aria-label="Notifications">🔔</button>
            <button type="button" className="avatar-btn" onClick={handleLogout} title="Logout">
              {firstName[0]}
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main dashboard-shell">
        <section className="dashboard-hero">
          <div>
            <h1>Good Morning, {firstName}</h1>
            <p>Here is your daily reproductive health overview.</p>
          </div>
          <div className="dashboard-hero-actions">
            <button type="button" className="ghost-btn">📅 Feb 2026</button>
            <button type="button" className="primary-btn">Generate Report</button>
          </div>
        </section>

        <section className="metric-grid">
          <article className="metric-card"><p>Cycle Day</p><h3>Day 14</h3><small>Ovulation Window</small></article>
          <article className="metric-card"><p>Avg. Temp</p><h3>98.4°F</h3><small>+0.3°F from yesterday</small></article>
          <article className="metric-card"><p>Sleep Quality</p><h3>7h 45m</h3><small>Optimal Rest</small></article>
          <article className="metric-card"><p>Hormone Lvl</p><h3>Normal</h3><small>Estrogen Spiking</small></article>
        </section>

        <section className="assessment-shell">
          <div className="assessment-head">
            <h2>Health Risk Assessment</h2>
            <p>Select your current stage and update your metrics for real-time risk prediction.</p>
          </div>

          <div className="stage-tabs">
            {(Object.keys(stageMeta) as HealthStage[]).map((stage) => {
              const isActive = selectedStage === stage
              return (
                <button
                  key={stage}
                  type="button"
                  className={isActive ? 'stage-tab active' : 'stage-tab'}
                  onClick={() => setStage(stage)}
                >
                  <span>{stageMeta[stage].icon}</span>
                  {stageMeta[stage].label}
                </button>
              )
            })}
          </div>

          <div className="assessment-grid">
            <form
              className="assessment-form"
              onSubmit={(event) => {
                event.preventDefault()
                void assessRisk()
              }}
            >
              <div className="assessment-form-top">
                <h3>{stageMeta[selectedStage].label} Assessment</h3>
                <div className="form-nav">
                  <button
                    type="button"
                    className="ghost-btn"
                    disabled={stageIndex === 0}
                    onClick={() => setStage(stageOrder[Math.max(0, stageIndex - 1)])}
                  >
                    Previous
                  </button>
                  <button
                    type="button"
                    className="ghost-btn"
                    disabled={stageIndex === stageOrder.length - 1}
                    onClick={() => setStage(stageOrder[Math.min(stageOrder.length - 1, stageIndex + 1)])}
                  >
                    Next
                  </button>
                </div>
              </div>

              {selectedStage === 'infertility' ? (
                <div className="assessment-sections">
                  <section className="assessment-group">
                    <p className="assessment-group-title">Clinical Inputs</p>
                    {hideHistoricalInputs ? (
                      <p className="assessment-group-note">
                        Historical cohabitation inputs are hidden because Ever Cohabited is set to No.
                      </p>
                    ) : null}
                    <div className="dynamic-field-grid">
                      {visibleStandardInfertilityFields.map((item) => (
                        <label key={item.field}>
                          <span>{item.label}</span>
                          <input
                            value={activeFormValues[item.field] || ''}
                            placeholder={item.placeholder}
                            onChange={(event) => setField(item.field, event.target.value)}
                          />
                        </label>
                      ))}
                    </div>
                  </section>

                  <section className="assessment-group">
                    <p className="assessment-group-title">Yes/No Indicators</p>
                    <div className="binary-field-grid">
                      {visibleBinaryInfertilityFields.map((item) => (
                        <label key={item.field} className="binary-field">
                          <span>{item.label}</span>
                          <div className="yes-no-switch" role="group" aria-label={item.label}>
                            <label className="radio-option">
                              <input
                                type="radio"
                                name={item.field}
                                checked={activeFormValues[item.field] === '1'}
                                onChange={() => setField(item.field, '1')}
                              />
                              <span>Yes</span>
                            </label>
                            <label className="radio-option">
                              <input
                                type="radio"
                                name={item.field}
                                checked={activeFormValues[item.field] === '0'}
                                onChange={() => setField(item.field, '0')}
                              />
                              <span>No</span>
                            </label>
                          </div>
                        </label>
                      ))}
                    </div>
                  </section>
                </div>
              ) : (
                <div className="dynamic-field-grid">
                  {activeFields.map((item) => (
                    <label
                      key={item.field}
                      className={item.field === 'symptoms' ? 'full-width' : undefined}
                    >
                      <span>{item.label}</span>
                      <input
                        value={activeFormValues[item.field] || ''}
                        placeholder={item.placeholder}
                        onChange={(event) => setField(item.field, event.target.value)}
                      />
                    </label>
                  ))}
                </div>
              )}

              {assessmentError ? <p className="assessment-error">{assessmentError}</p> : null}

              <div className="form-actions">
                <button type="submit" className="primary-btn block" disabled={isAssessing}>
                  {isAssessing ? 'Assessing...' : 'Assess Risk'}
                </button>
                <button type="button" className="ghost-btn block" onClick={resetAssessment}>Reset</button>
              </div>
            </form>

            <article className="assessment-result">
              {!result ? (
                <div className="empty-result">
                  <span>ⓘ</span>
                  <h4>No Assessment Yet</h4>
                  <p>Fill out the form on the left to generate a real-time health risk prediction.</p>
                </div>
              ) : (
                <div className="result-body">
                  <h4>{result.riskLabel}</h4>
                  <p className="result-score">Risk Score: {result.score}/100</p>
                  <p>{result.summary}</p>
                  <ul>
                    {result.recommendations.map((rec) => (
                      <li key={rec}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </article>
          </div>
        </section>

        <section className="lower-grid">
          <article className="trend-card">
            <h3>Wellness Trends</h3>
            <p>Wellness score over the last 7 days</p>
            <svg viewBox="0 0 520 170" preserveAspectRatio="none" className="trend-chart" aria-hidden>
              <defs>
                <linearGradient id="fillPink" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="#f15bad" stopOpacity="0.28" />
                  <stop offset="100%" stopColor="#f15bad" stopOpacity="0.02" />
                </linearGradient>
              </defs>
              <path d={`${chartPath} L 520 170 L 0 170 Z`} fill="url(#fillPink)" />
              <path d={chartPath} fill="none" stroke="#ed4298" strokeWidth="3" />
            </svg>
          </article>

          <article className="insights-card">
            <h3>Daily Insights</h3>
            <div className="insight insight-pink">
              <h4>Peak Fertility</h4>
              <p>Based on your temperature and cycle data, you are entering your peak fertility window for the next 48 hours.</p>
            </div>
            <div className="insight insight-blue">
              <h4>Sleep Pattern</h4>
              <p>Your sleep consistency has improved by 15% this week. Keep maintaining this schedule.</p>
            </div>
          </article>
        </section>
      </main>

      <footer className="dashboard-footer">
        <div className="dashboard-shell dashboard-shell-footer">
          <div className="dashboard-brand"><span className="dashboard-brand-mark" aria-hidden>✧</span><span>Natalis AI</span></div>
          <p>© 2026 Natalis AI Inc. HIPAA Compliant & GDPR Secure.</p>
          <div className="footer-links"><span>Privacy</span><span>Terms</span><span>Support</span></div>
        </div>
      </footer>
    </div>
  )
}
