import { Link, useNavigate } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'
import DashboardLayout from '../../components/dashboard/DashboardLayout'
import { useAuthStore } from '../../stores/authStore'
import { ApiError } from '../../services/apiClient'
import {
  getInfertilityModelInfo,
  getPostpartumModelInfo,
  getPregnancyModelInfo,
  type InfertilityModelInfo,
  type PostpartumModelInfo,
  type PregnancyModelInfo,
} from '../../services/predictionApi'
import { getPregnancyTimelineSummary, type PregnancyTimelineSummaryResponse } from '../../services/pregnancyFollowUpApi'
import { readStageSnapshot, SNAPSHOT_KEYS, type StageSnapshot } from '../../utils/dashboardSnapshot'
import infertilityImage from '../../assets/lab-woman.jpg'
import pregnancyImage from '../../assets/pregnant-woman.jpg'
import postpartumImage from '../../assets/woman-baby.jpg'

type StageMeta = {
  key: 'infertility' | 'pregnancy' | 'postpartum'
  label: string
  route: string
  image: string
  description: string
  buttonLabel: string
}

const stages: StageMeta[] = [
  {
    key: 'infertility',
    label: 'Infertility Risk',
    route: '/dashboard/infertility',
    image: infertilityImage,
    description: 'Track ovulation and analyze hormonal health risks.',
    buttonLabel: 'Start Assessment',
  },
  {
    key: 'pregnancy',
    label: 'Pregnancy Health',
    route: '/dashboard/pregnancy',
    image: pregnancyImage,
    description: 'Risk prediction for pre-eclampsia and gestational health.',
    buttonLabel: 'Check Status',
  },
  {
    key: 'postpartum',
    label: 'Postpartum Recovery',
    route: '/dashboard/postpartum',
    image: postpartumImage,
    description: 'Mental health screening and physical recovery tracking.',
    buttonLabel: 'Log Symptoms',
  },
]

type SnapshotState = {
  infertility: StageSnapshot | null
  pregnancy: StageSnapshot | null
  postpartum: StageSnapshot | null
}

function formatPercentage(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return '--'
  }
  return `${Math.round(value * 100)}%`
}

function formatDateTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(date)
}

function stageIcon(stage: StageMeta['key']) {
  if (stage === 'infertility') {
    return (
      <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden>
        <path d="M12 3v18M3 12h18M5.6 5.6l12.8 12.8M18.4 5.6 5.6 18.4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    )
  }

  if (stage === 'pregnancy') {
    return (
      <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden>
        <path d="M12 20s-7-4.4-9-8.8A5.3 5.3 0 0 1 12 6a5.3 5.3 0 0 1 9 5.2C19 15.6 12 20 12 20Z" fill="none" stroke="currentColor" strokeWidth="1.8" />
      </svg>
    )
  }

  return (
    <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden>
      <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <circle cx="9" cy="10" r="1" fill="currentColor" />
      <circle cx="15" cy="10" r="1" fill="currentColor" />
      <path d="M8.5 14c1 1.2 2.2 1.8 3.5 1.8 1.3 0 2.5-.6 3.5-1.8" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  )
}

export default function DashboardOverviewPage() {
  const navigate = useNavigate()
  const logout = useAuthStore((state) => state.logout)
  const user = useAuthStore((state) => state.user)

  const [infertilityInfo, setInfertilityInfo] = useState<InfertilityModelInfo | null>(null)
  const [pregnancyInfo, setPregnancyInfo] = useState<PregnancyModelInfo | null>(null)
  const [postpartumInfo, setPostpartumInfo] = useState<PostpartumModelInfo | null>(null)
  const [timelineSummary, setTimelineSummary] = useState<PregnancyTimelineSummaryResponse | null>(null)

  const [modelInfoError, setModelInfoError] = useState<string | null>(null)
  const [timelineError, setTimelineError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const [snapshots, setSnapshots] = useState<SnapshotState>({
    infertility: readStageSnapshot(SNAPSHOT_KEYS.infertility),
    pregnancy: readStageSnapshot(SNAPSHOT_KEYS.pregnancy),
    postpartum: readStageSnapshot(SNAPSHOT_KEYS.postpartum),
  })

  const firstName = user?.fullName?.split(' ')[0] || 'Sarah'

  const stageSummaries = useMemo(() => {
    return {
      infertility: {
        modelVersion: infertilityInfo?.model_version || 'Unavailable',
        threshold:
          infertilityInfo?.thresholds?.fused ??
          infertilityInfo?.thresholds?.history ??
          infertilityInfo?.thresholds?.symptom ??
          null,
      },
      pregnancy: {
        modelVersion: pregnancyInfo?.model_version || 'Unavailable',
        threshold: pregnancyInfo?.threshold ?? null,
      },
      postpartum: {
        modelVersion: postpartumInfo?.model_version || 'Unavailable',
        threshold: postpartumInfo?.decision_threshold ?? null,
      },
    }
  }, [infertilityInfo, pregnancyInfo, postpartumInfo])

  const latestPoint = timelineSummary?.points.at(-1)
  const pregnancyWeek = latestPoint?.gestational_age_weeks
  const statusText = pregnancyWeek
    ? `Week ${pregnancyWeek} Pregnancy`
    : (timelineSummary?.total_records ?? 0) > 0
      ? 'Active pregnancy follow-up'
      : 'No active follow-up'
  const weeklyLogPercent = Math.min(100, (timelineSummary?.total_records ?? 0) * 20)

  useEffect(() => {
    let active = true

    const load = async () => {
      setIsLoading(true)
      setModelInfoError(null)
      setTimelineError(null)

      try {
        const [infertility, pregnancy, postpartum] = await Promise.all([
          getInfertilityModelInfo(),
          getPregnancyModelInfo(),
          getPostpartumModelInfo(),
        ])

        if (!active) return

        setInfertilityInfo(infertility)
        setPregnancyInfo(pregnancy)
        setPostpartumInfo(postpartum)
      } catch (error) {
        if (!active) return
        setModelInfoError(error instanceof Error ? error.message : 'Unable to load model information.')
      }

      try {
        const summary = await getPregnancyTimelineSummary(50)
        if (!active) return
        setTimelineSummary(summary)
      } catch (error) {
        if (!active) return

        if (error instanceof ApiError && error.status === 401) {
          await logout()
          navigate('/sign-in')
          return
        }

        setTimelineError(error instanceof Error ? error.message : 'Unable to load timeline summary.')
      }

      if (active) {
        setSnapshots({
          infertility: readStageSnapshot(SNAPSHOT_KEYS.infertility),
          pregnancy: readStageSnapshot(SNAPSHOT_KEYS.pregnancy),
          postpartum: readStageSnapshot(SNAPSHOT_KEYS.postpartum),
        })
        setIsLoading(false)
      }
    }

    void load()

    return () => {
      active = false
    }
  }, [logout, navigate])

  const rightTopMetrics = (
    <article className="overview-header-metrics overview-rail-metrics">
      <div className="overview-header-metrics-grid">
        <div className="overview-header-stat">
          <span className="overview-header-icon heart">
            <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden>
              <path d="M12 20s-7-4.4-9-8.8A5.3 5.3 0 0 1 12 6a5.3 5.3 0 0 1 9 5.2C19 15.6 12 20 12 20Z" fill="currentColor" />
            </svg>
          </span>
          <div>
            <p className="overview-header-label">Heart Rate</p>
            <p className="overview-header-value">
              {latestPoint?.heart_rate ? Math.round(latestPoint.heart_rate) : '--'}<span>bpm</span>
            </p>
          </div>
        </div>

        <div className="overview-header-stat">
          <span className="overview-header-icon water">
            <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden>
              <path d="M12 3c-2.5 4-6 7-6 11a6 6 0 0 0 12 0c0-4-3.5-7-6-11Z" fill="currentColor" />
            </svg>
          </span>
          <div>
            <p className="overview-header-label">High-Risk</p>
            <p className="overview-header-value">{formatPercentage(timelineSummary?.latest_probability_high_risk)}</p>
          </div>
        </div>
      </div>
    </article>
  )

  const rightRail = (
    <div className="overview-rail">
      {rightTopMetrics}
      <section className="overview-rail-card">
        <div className="overview-rail-title-row">
          <h2 className="overview-rail-title">Notifications</h2>
          <span className="overview-rail-badge">{timelineSummary?.total_records ? `${timelineSummary.total_records} New` : '0 New'}</span>
        </div>

        {timelineError ? (
          <p className="overview-notification-body">{timelineError}</p>
        ) : (
          <ul className="overview-notification-list">
            <li className="overview-notification-item">
              <p className="overview-notification-head">
                <span className="overview-dot primary" />
                Latest High-Risk Probability
              </p>
              <p className="overview-notification-body">{formatPercentage(timelineSummary?.latest_probability_high_risk)}</p>
            </li>
            <li className="overview-notification-item">
              <p className="overview-notification-head">
                <span className="overview-dot warning" />
                Trend Status
              </p>
              <p className="overview-notification-body">{timelineSummary?.trend || 'No trend yet'}</p>
            </li>
            <li className="overview-notification-item">
              <p className="overview-notification-head">
                <span className="overview-dot info" />
                Records Tracked
              </p>
              <p className="overview-notification-body">{timelineSummary?.total_records ?? 0} stored follow-up entries</p>
            </li>
          </ul>
        )}
      </section>

      <section className="overview-followup-card">
        <h2 className="overview-rail-title">Follow-up Snapshot</h2>

        <div className="overview-followup-inner">
          {latestPoint ? (
            <>
              <p className="overview-followup-kicker">Latest Entry</p>
              <p className="overview-followup-level">{latestPoint.risk_level}</p>
              <p className="overview-followup-time">{formatDateTime(latestPoint.created_at)}</p>
            </>
          ) : (
            <>
              <p className="overview-followup-empty">No stored follow-up yet.</p>
              <p className="overview-followup-empty-sub">Complete a pregnancy assessment to populate this panel.</p>
            </>
          )}
        </div>

        <Link to="/dashboard/pregnancy" className="overview-followup-btn">
          Open Pregnancy Page
        </Link>
      </section>
    </div>
  )

  return (
    <DashboardLayout
      title={`Good Morning, ${firstName}`}
      statusLine={
        <>
          <span className="dashboard-status-dot" />
          <span>Status:</span>
          <strong>{statusText}</strong>
        </>
      }
      rightRail={rightRail}
    >
      {(modelInfoError || timelineError) && !isLoading ? (
        <div className="dashboard-warning-bar">{modelInfoError || timelineError}</div>
      ) : null}

      <section className="overview-stage-list">
        {stages.map((stage) => {
          const snapshot = snapshots[stage.key]
          const summary = stageSummaries[stage.key]

          return (
            <Link key={stage.key} to={stage.route} className="overview-stage-card overview-stage-card-link">
              <div className="overview-stage-grid">
                <img src={stage.image} alt={stage.label} className="overview-stage-image" />

                <div className="overview-stage-content">
                  <div>
                    <div className="overview-stage-top">
                      <div>
                        <h2 className="overview-stage-title">{stage.label}</h2>
                        <p className="overview-stage-desc">{stage.description}</p>
                      </div>

                      <div className="overview-stage-chip-wrap">
                        {stage.key === 'pregnancy' && (timelineSummary?.total_records ?? 0) > 0 ? (
                          <span className="overview-stage-active-chip">Active Stage</span>
                        ) : null}
                        <span className="overview-stage-icon">{stageIcon(stage.key)}</span>
                      </div>
                    </div>

                    <div className="overview-stage-divider" />
                  </div>

                  <div className="overview-stage-bottom">
                    <div>
                      {stage.key === 'pregnancy' ? (
                        <div className="overview-weekly-log">
                          <p>Weekly Log</p>
                          <div className="overview-weekly-track">
                            <div className="overview-weekly-fill" style={{ width: `${weeklyLogPercent}%` }} />
                          </div>
                        </div>
                      ) : stage.key === 'infertility' ? (
                        <p className="overview-stage-subtext">
                          Last check: {snapshot ? formatDateTime(snapshot.capturedAt) : 'No assessment yet'}
                        </p>
                      ) : (
                        <p className="overview-stage-subtext">{snapshot ? 'Recovery trend updated' : 'Prepare ahead'}</p>
                      )}

                      <p className="overview-stage-model">Model: {summary.modelVersion}</p>
                    </div>

                    <span className="overview-stage-btn">
                      {stage.buttonLabel}
                    </span>
                  </div>
                </div>
              </div>
            </Link>
          )
        })}
      </section>

      {isLoading ? <p className="dashboard-loading-note">Loading dashboard data...</p> : null}
    </DashboardLayout>
  )
}
