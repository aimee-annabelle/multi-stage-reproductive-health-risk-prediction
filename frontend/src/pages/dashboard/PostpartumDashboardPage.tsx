import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import DashboardLayout from '../../components/dashboard/DashboardLayout'
import { ApiError } from '../../services/apiClient'
import { getPostpartumModelInfo, type PostpartumModelInfo } from '../../services/predictionApi'
import {
  getPostpartumFollowUpHistory,
  getPostpartumTimelineSummary,
  type PostpartumAssessmentHistoryResponse,
  type PostpartumAssessmentRecordResponse,
  type PostpartumTimelineSummaryResponse,
} from '../../services/postpartumFollowUpApi'
import { useAuthStore } from '../../stores/authStore'
import {
  toRecoveryPhase,
  toTitleLabel,
} from './postpartumShared'

export default function PostpartumDashboardPage() {
  const navigate = useNavigate()
  const logout = useAuthStore((state) => state.logout)
  const user = useAuthStore((state) => state.user)

  const [modelInfo, setModelInfo] = useState<PostpartumModelInfo | null>(null)
  const [latestRecord, setLatestRecord] = useState<PostpartumAssessmentRecordResponse | null>(null)
  const [history, setHistory] = useState<PostpartumAssessmentHistoryResponse | null>(null)
  const [timeline, setTimeline] = useState<PostpartumTimelineSummaryResponse | null>(null)

  const [error, setError] = useState<string | null>(null)
  const [isLoadingWidgets, setIsLoadingWidgets] = useState(false)
  const [isBootstrapping, setIsBootstrapping] = useState(true)

  const firstName = useMemo(() => {
    const rawName = user?.fullName?.trim()
    if (!rawName) {
      return 'Sarah'
    }
    return rawName.split(/\s+/)[0]
  }, [user])

  const handleAuthFailure = useCallback(async () => {
    await logout()
    navigate('/sign-in')
  }, [logout, navigate])

  const loadWidgets = useCallback(async () => {
    setIsLoadingWidgets(true)
    try {
      const [historyResponse, timelineResponse] = await Promise.all([
        getPostpartumFollowUpHistory(20),
        getPostpartumTimelineSummary(50),
      ])

      setHistory(historyResponse)
      setTimeline(timelineResponse)

      if (historyResponse.assessments.length > 0) {
        setLatestRecord(historyResponse.assessments[0])
      } else {
        setLatestRecord(null)
      }
    } catch (widgetError) {
      if (widgetError instanceof ApiError && widgetError.status === 401) {
        await handleAuthFailure()
        return
      }
      setError(widgetError instanceof Error ? widgetError.message : 'Unable to load postpartum dashboard widgets.')
    } finally {
      setIsLoadingWidgets(false)
    }
  }, [handleAuthFailure])

  useEffect(() => {
    let active = true

    const bootstrap = async () => {
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

  const hasRecords = (timeline?.total_records ?? 0) > 0 || Boolean(latestRecord)

  const chartWidth = 620
  const chartHeight = 250
  const chartPadding = 26

  const daySlots = useMemo(() => {
    const points = timeline?.points ?? []
    const byDate = new Map<string, (typeof points)[number]>()

    for (const point of points) {
      const date = new Date(point.created_at)
      if (Number.isNaN(date.getTime())) {
        continue
      }
      const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
      byDate.set(key, point)
    }

    const today = new Date()
    const slots: Array<{
      key: string
      dayLabel: string
      dayNumber: string
      value: number | null
      hasLog: boolean
      isToday: boolean
    }> = []

    for (let index = 6; index >= 0; index -= 1) {
      const date = new Date(today)
      date.setHours(0, 0, 0, 0)
      date.setDate(today.getDate() - index)

      const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
      const point = byDate.get(key)
      const isToday = index === 0
      slots.push({
        key,
        dayLabel: new Intl.DateTimeFormat(undefined, { weekday: 'short' }).format(date),
        dayNumber: String(date.getDate()),
        value: point ? Math.round(point.probability_high_risk * 100) : null,
        hasLog: Boolean(point),
        isToday,
      })
    }

    return slots
  }, [timeline])

  const trendLinePath = useMemo(() => {
    if (daySlots.length === 0) {
      return ''
    }

    const usableWidth = chartWidth - chartPadding * 2
    const usableHeight = chartHeight - chartPadding * 2
    let path = ''
    let isSegmentOpen = false

    daySlots.forEach((slot, index) => {
      if (slot.value === null) {
        isSegmentOpen = false
        return
      }

      const x = daySlots.length === 1 ? chartWidth / 2 : chartPadding + (index / (daySlots.length - 1)) * usableWidth
      const y = chartPadding + (1 - slot.value / 100) * usableHeight
      path += `${isSegmentOpen ? ' L' : ' M'} ${x.toFixed(2)} ${y.toFixed(2)}`
      isSegmentOpen = true
    })

    return path.trim()
  }, [daySlots])

  const trendLineDots = useMemo(() => {
    if (daySlots.length === 0) {
      return [] as Array<{ key: string; x: number; y: number; value: number | null }>
    }

    const usableWidth = chartWidth - chartPadding * 2
    const usableHeight = chartHeight - chartPadding * 2
    const missingY = chartHeight - chartPadding

    return daySlots.map((slot, index) => {
      const x = daySlots.length === 1 ? chartWidth / 2 : chartPadding + (index / (daySlots.length - 1)) * usableWidth
      if (slot.value === null) {
        return { key: slot.key, x, y: missingY, value: null }
      }
      const y = chartPadding + (1 - slot.value / 100) * usableHeight
      return { key: slot.key, x, y, value: slot.value }
    })
  }, [daySlots])

  const topFactors = useMemo(() => {
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

  const latestRiskPercent = latestRecord ? Math.round(latestRecord.probability_high_risk * 100) : null
  const thresholdPercent = modelInfo ? Math.round(modelInfo.decision_threshold * 100) : 50
  const latestRiskTone = latestRiskPercent !== null && latestRiskPercent >= thresholdPercent ? 'high' : 'low'

  const trendLabel =
    timeline?.trend === 'increased'
      ? 'Rising'
      : timeline?.trend === 'decreased'
        ? 'Improving'
        : timeline?.trend === 'stable'
          ? 'Stable'
          : 'No trend yet'

  const trendDeltaLabel =
    timeline?.probability_high_risk_change == null
      ? 'Need two or more records'
      : `${timeline.probability_high_risk_change >= 0 ? '+' : ''}${(timeline.probability_high_risk_change * 100).toFixed(1)}% vs earliest tracked record`

  const highRiskShare = timeline ? Math.round(timeline.high_risk_percentage) : 0
  const hospitalShare = timeline ? Math.round(timeline.hospital_referral_percentage) : 0
  const emergencyShare = timeline ? Math.round(timeline.emergency_referral_percentage) : 0
  const averageInputCompletion = timeline ? Math.round(timeline.average_input_completion) : 0
  const latestInputCompletion = latestRecord ? Math.round(latestRecord.input_completion_pct) : 0

  const recoveryWeek = latestRecord?.baby_age_months == null ? null : Math.max(1, Math.round(latestRecord.baby_age_months * 4))
  const recoveryPhase = toRecoveryPhase(recoveryWeek)
  const headerStatus = recoveryWeek === null ? 'Start with your first postpartum prediction.' : `Week ${recoveryWeek}: ${recoveryPhase}`

  const guidanceSummary =
    latestRecord?.risk_level === 'High Risk'
      ? 'Your latest record indicates elevated postpartum risk. Prioritize timely professional support and repeat tracking after interventions.'
      : latestRecord
        ? 'Your latest record is below the risk threshold. Continue routine monitoring and track any symptom changes.'
        : 'No postpartum records yet. Start with your first prediction to unlock trend monitoring and personalized guidance.'

  if (isBootstrapping) {
    return (
      <DashboardLayout title={`Good morning, ${firstName}`} subtitle="Loading your postpartum dashboard...">
        <section className="stage-form-shell">
          <p className="preg-monitor-placeholder-note">Loading...</p>
        </section>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout
      title={`Good morning, ${firstName}`}
      statusLine={
        <>
          <span className="dashboard-status-dot" />
          {headerStatus}
        </>
      }
    >
      <section className="stage-form-shell ppd-page">
        {error ? <div className="dashboard-warning-bar">{error}</div> : null}

        {!hasRecords ? (
          <article className="ppd-empty-card">
            <h2>Postpartum dashboard is ready</h2>
            <p>
              Create your first postpartum prediction to generate trend charts, referral percentages, and clear
              guidance based on your stored history.
            </p>
            <div className="ppd-empty-actions">
              <button
                type="button"
                className="inf-btn inf-btn-primary"
                onClick={() => navigate('/dashboard/postpartum/predict')}
              >
                Start First Prediction
              </button>
              <p>After your first entry, this page will visualize trend and recovery insights automatically.</p>
            </div>
          </article>
        ) : (
          <>
            <div className="ppd-top-actions">
              <button
                type="button"
                className="inf-btn inf-btn-primary"
                onClick={() => navigate('/dashboard/postpartum/predict')}
              >
                Run New Prediction
              </button>
            </div>

            <div className="ppd-main-grid">
              <article className="ppd-card ppd-trend-card">
                <div className="ppd-card-head">
                  <div>
                    <h2>Emotional Well-being</h2>
                    <p>Postpartum risk trend (last 7 days, including unlogged days)</p>
                  </div>
                  <div className="ppd-trend-chip">
                    <strong>{trendLabel}</strong>
                    <span>{trendDeltaLabel}</span>
                  </div>
                </div>

                {daySlots.length > 0 ? (
                  <div className="ppd-line-chart-wrap">
                    <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="ppd-line-chart" preserveAspectRatio="none">
                      <g>
                        {[0, 25, 50, 75, 100].map((line) => {
                          const y = chartPadding + (1 - line / 100) * (chartHeight - chartPadding * 2)
                          return (
                            <g key={line}>
                              <line x1={chartPadding} y1={y} x2={chartWidth - chartPadding} y2={y} className="ppd-grid-line" />
                              {line !== 0 ? (
                                <text x={6} y={y + 4} className="ppd-axis-label">
                                  {line}%
                                </text>
                              ) : null}
                            </g>
                          )
                        })}
                        {daySlots.map((_, index) => {
                          const x =
                            daySlots.length === 1
                              ? chartWidth / 2
                              : chartPadding + (index / (daySlots.length - 1)) * (chartWidth - chartPadding * 2)
                          return (
                            <line
                              key={`v-${index}`}
                              x1={x}
                              y1={chartPadding}
                              x2={x}
                              y2={chartHeight - chartPadding}
                              className="ppd-grid-line ppd-grid-line-vertical"
                            />
                          )
                        })}
                      </g>
                      {trendLinePath ? <path d={trendLinePath} className="ppd-line-path" /> : null}
                      {trendLineDots.map((dot) => (
                        <circle
                          key={dot.key}
                          cx={dot.x}
                          cy={dot.y}
                          r={dot.value === null ? 3 : 4.5}
                          className={dot.value === null ? 'ppd-line-dot ppd-line-dot-missing' : 'ppd-line-dot'}
                        />
                      ))}
                    </svg>
                    <div className="ppd-line-labels" aria-hidden>
                      {daySlots.map((slot) => (
                        <span key={slot.key} className={`ppd-day-label${slot.isToday ? ' is-today' : ''}`}>
                          <strong>{slot.dayLabel}</strong>
                          <em>{slot.dayNumber}</em>
                          <i>{slot.hasLog ? 'Logged' : 'No log'}</i>
                        </span>
                      ))}
                    </div>
                    <div className="ppd-chart-legend" aria-hidden>
                      <span>
                        <i className="dot logged" />
                        Logged day
                      </span>
                      <span>
                        <i className="dot missing" />
                        No log
                      </span>
                    </div>
                  </div>
                ) : (
                  <p className="preg-monitor-placeholder-note">No timeline points available yet.</p>
                )}
              </article>

              <div className="ppd-side-stack">
                <article className="ppd-card ppd-side-card ppd-recovery-card">
                  <h3>Physical Recovery</h3>
                  <p className="ppd-side-value">{latestRiskPercent ?? '--'}%</p>
                  <p className="ppd-side-muted">Current high-risk probability</p>
                  <div className="ppd-meter">
                    <span style={{ width: `${latestRiskPercent ?? 0}%` }} />
                  </div>
                  <div className="ppd-mini-grid">
                    <div>
                      <p>Risk Level</p>
                      <strong className={`ppd-risk-badge ${latestRiskTone === 'high' ? 'high' : 'low'}`}>
                        {latestRecord?.risk_level || 'No Data'}
                      </strong>
                    </div>
                    <div>
                      <p>Input Quality</p>
                      <strong>{latestInputCompletion}%</strong>
                    </div>
                  </div>
                </article>

                <article className="ppd-card ppd-side-card ppd-referral-card">
                  <h3>Referral Snapshot</h3>
                  <div className="ppd-stat-row">
                    <span>High-risk records</span>
                    <strong>{highRiskShare}%</strong>
                  </div>
                  <div className="ppd-stat-row">
                    <span>Hospital referrals</span>
                    <strong>{hospitalShare}%</strong>
                  </div>
                  <div className="ppd-stat-row">
                    <span>Emergency referrals</span>
                    <strong>{emergencyShare}%</strong>
                  </div>
                  <p className="ppd-side-muted">Based on stored postpartum predictions.</p>
                </article>

                <article className="ppd-card ppd-side-card ppd-essentials-card">
                  <h3>Daily Essentials</h3>
                  <div className="ppd-stat-row">
                    <span>Records tracked</span>
                    <strong>{history?.total_records ?? 0}</strong>
                  </div>
                  <div className="ppd-stat-row">
                    <span>Average form completion</span>
                    <strong>{averageInputCompletion}%</strong>
                  </div>
                  <div className="ppd-stat-row">
                    <span>Model threshold</span>
                    <strong>{thresholdPercent}%</strong>
                  </div>
                  {isLoadingWidgets ? <p className="ppd-side-muted">Refreshing dashboard...</p> : null}
                </article>
              </div>
            </div>

            <div className="ppd-quick-grid">
              <article className="ppd-card ppd-quick-card ppd-factors-card">
                <h4>Top Risk Factors</h4>
                {topFactors.length > 0 ? (
                  <ul>
                    {topFactors.map((factor) => (
                      <li key={factor.name}>
                        <span>{factor.name}</span>
                        <strong>{factor.value.toFixed(3)}</strong>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>No factors available yet.</p>
                )}
              </article>

              <article className="ppd-card ppd-quick-card ppd-guidance-card">
                <h4>Latest Guidance</h4>
                <p>{latestRecord?.hospital_advice || 'Run another prediction to update guidance.'}</p>
                <small>{latestRecord?.emergency_advice || ''}</small>
              </article>

              <article className="ppd-card ppd-quick-card ppd-class-card">
                <h4>Prediction Class</h4>
                <p>
                  {latestRecord?.predicted_class
                    ? latestRecord.predicted_class.replaceAll('_', ' ')
                    : 'No class available yet'}
                </p>
                <small>Model version: {latestRecord?.model_version || modelInfo?.model_version || 'Unavailable'}</small>
                <button
                  type="button"
                  className="inf-btn inf-btn-primary ppd-card-cta"
                  onClick={() => navigate('/dashboard/postpartum/predict')}
                >
                  Update Prediction
                </button>
              </article>
            </div>

            <article className="ppd-nav-disclaimer">
              <h4>Navigation Guide</h4>
              <p>{guidanceSummary}</p>
              <p>
                Use <strong>Run New Prediction</strong> to add a new record. The chart shows the last 7 calendar days,
                including unlogged days. The right-side cards summarize referral percentages and model thresholds.
              </p>
            </article>
          </>
        )}
      </section>
    </DashboardLayout>
  )
}
