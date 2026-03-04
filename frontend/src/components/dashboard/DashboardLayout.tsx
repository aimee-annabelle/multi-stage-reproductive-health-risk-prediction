import { type ReactNode, useState } from 'react'
import DashboardSidebar from './DashboardSidebar'

type DashboardLayoutProps = {
  title: string
  subtitle?: string
  statusLine?: ReactNode
  headerRight?: ReactNode
  rightRail?: ReactNode
  children: ReactNode
}

export default function DashboardLayout({
  title,
  subtitle,
  statusLine,
  headerRight,
  rightRail,
  children,
}: DashboardLayoutProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const hasRightRail = Boolean(rightRail)

  return (
    <div className="dashboard-root">
      <div className={`dashboard-shell-grid${hasRightRail ? '' : ' dashboard-shell-grid-no-rail'}`}>
        <div className="dashboard-sidebar-pane">
          <DashboardSidebar />
        </div>

        <div className="dashboard-main-pane">
          <header className="dashboard-header">
            <div className="dashboard-header-row">
              <div className="dashboard-title-wrap">
                <h1 className="dashboard-title">{title}</h1>

                {statusLine ? (
                  <div className="dashboard-status-line">{statusLine}</div>
                ) : subtitle ? (
                  <p className="dashboard-subtitle">{subtitle}</p>
                ) : null}
              </div>

              <div className="dashboard-header-right-desktop">{headerRight}</div>

              <button
                type="button"
                className="dashboard-mobile-menu-btn"
                onClick={() => setMobileMenuOpen(true)}
                aria-label="Open navigation"
              >
                <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden>
                  <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                </svg>
              </button>
            </div>

            {headerRight ? <div className="dashboard-header-right-mobile">{headerRight}</div> : null}
          </header>

          <main className="dashboard-main-content">
            <div className="dashboard-fade-in">{children}</div>
          </main>

          {rightRail ? (
            <div className="dashboard-mobile-rail">
              <div className="dashboard-fade-in">{rightRail}</div>
            </div>
          ) : null}
        </div>

        {hasRightRail ? <aside className="dashboard-rail-pane">{rightRail}</aside> : null}
      </div>

      {mobileMenuOpen ? (
        <div className="dashboard-overlay">
          <button
            type="button"
            className="dashboard-overlay-backdrop"
            onClick={() => setMobileMenuOpen(false)}
            aria-label="Close navigation"
          />
          <div className="dashboard-mobile-sidebar">
            <div className="dashboard-mobile-sidebar-top">
              <p>Navigation</p>
              <button
                type="button"
                className="dashboard-mobile-close"
                onClick={() => setMobileMenuOpen(false)}
                aria-label="Close navigation"
              >
                <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden>
                  <path d="m6 6 12 12M18 6 6 18" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                </svg>
              </button>
            </div>
            <div className="dashboard-mobile-sidebar-body">
              <DashboardSidebar onNavigate={() => setMobileMenuOpen(false)} />
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}
