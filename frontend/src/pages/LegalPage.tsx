import { Link } from 'react-router-dom'
import '../styles/auth.css'
import appLogo from '../assets/logo.svg'

type LegalPageProps = {
  focus: 'privacy' | 'terms'
}

export default function LegalPage({ focus }: LegalPageProps) {
  const isPrivacy = focus === 'privacy'

  return (
    <div className="legal-page">
      <div className="legal-shell">
        <div className="legal-topbar">
          <Link to="/" className="auth-brand">
            <span className="auth-brand-mark" aria-hidden>
              <img src={appLogo} alt="" className="auth-brand-logo" />
            </span>
            EveBloom
          </Link>

          <div className="legal-topbar-actions">
            <Link to="/privacy-policy" className={`legal-tab${isPrivacy ? ' is-active' : ''}`}>
              Privacy Policy
            </Link>
            <Link to="/terms-of-service" className={`legal-tab${!isPrivacy ? ' is-active' : ''}`}>
              Terms & EULA
            </Link>
            <Link to="/sign-in" className="legal-back-link">
              Back to Sign In
            </Link>
          </div>
        </div>

        <section className="legal-hero">
          <p className="legal-kicker">Legal Information</p>
          <h1>{isPrivacy ? 'Privacy Policy' : 'End-User Licence Agreement'}</h1>
          <p className="legal-subtext">
            {isPrivacy
              ? 'This page explains what information is collected, how it is used, and how it is protected while using EveBloom.'
              : 'This page explains the rules for using EveBloom, the intended use of the app, and important responsibilities for both users and the service provider.'}
          </p>
          <p className="legal-effective-date">Effective date: March 29, 2026</p>
        </section>

        <div className="legal-grid">
          <aside className="legal-summary-card">
            <h2>Quick Summary</h2>
            <ul className="legal-summary-list">
              {isPrivacy ? (
                <>
                  <li>Account details and health entries are used to run dashboards and predictions.</li>
                  <li>Information is stored to support follow-up tracking and record history.</li>
                  <li>Reasonable safeguards are used to protect stored data.</li>
                  <li>Users can contact the service owner to request help with their records.</li>
                </>
              ) : (
                <>
                  <li>EveBloom is for personal health tracking and informational support.</li>
                  <li>The app does not replace a clinician, diagnosis, or emergency care.</li>
                  <li>Users should provide accurate information when entering records.</li>
                  <li>Use of the app means accepting the terms described on this page.</li>
                </>
              )}
            </ul>
          </aside>

          <main className="legal-content-card">
            {isPrivacy ? (
              <>
                <section className="legal-section">
                  <h2>1. Information Collected</h2>
                  <p>
                    EveBloom may collect account details such as name, email address, and password credentials, as well as
                    health information entered into the platform. This can include fertility inputs, pregnancy follow-up
                    records, postpartum screening answers, and notes added during check-ins.
                  </p>
                </section>

                <section className="legal-section">
                  <h2>2. How Information Is Used</h2>
                  <p>
                    Information is used to authenticate access, generate dashboards, support prediction workflows, store
                    progress over time, and improve continuity across follow-up records. Information may also be used to
                    show summaries, trends, reminders, and health guidance inside the product.
                  </p>
                </section>

                <section className="legal-section">
                  <h2>3. Data Protection</h2>
                  <p>
                    Reasonable technical and organizational measures are used to help protect personal information from
                    unauthorized access, loss, misuse, or disclosure. No digital system can guarantee absolute security,
                    but care is taken to reduce avoidable risk.
                  </p>
                </section>

                <section className="legal-section">
                  <h2>4. Sharing and Access</h2>
                  <p>
                    Information is not intended for public display. Access is limited to authenticated use of the platform
                    and any authorized service operations required to support the application. Information should only be
                    shared when necessary to operate, maintain, or legally support the service.
                  </p>
                </section>

                <section className="legal-section">
                  <h2>5. Record Retention</h2>
                  <p>
                    Stored records may remain available to support health history views, trend analysis, and follow-up
                    continuity unless they are removed according to future product controls or administrative support
                    processes.
                  </p>
                </section>

                <section className="legal-section">
                  <h2>6. Contact and Requests</h2>
                  <p>
                    Questions about stored information, corrections, or privacy concerns should be directed to the service
                    owner or project administrator through the contact channel made available with the platform.
                  </p>
                </section>
              </>
            ) : (
              <>
                <section className="legal-section">
                  <h2>1. Acceptance of Terms</h2>
                  <p>
                    By creating an account or using EveBloom, the user agrees to these terms. If the user does not agree,
                    the service should not be used.
                  </p>
                </section>

                <section className="legal-section">
                  <h2>2. Intended Use</h2>
                  <p>
                    EveBloom is intended to support personal health tracking, screening, and educational insight. It is not
                    a substitute for professional medical advice, diagnosis, treatment, or emergency response.
                  </p>
                </section>

                <section className="legal-section">
                  <h2>3. User Responsibilities</h2>
                  <p>
                    Users are responsible for providing accurate information to the best of their knowledge, keeping account
                    credentials secure, and using the service in a lawful and respectful manner.
                  </p>
                </section>

                <section className="legal-section">
                  <h2>4. Health Guidance Disclaimer</h2>
                  <p>
                    Any prediction, recommendation, or dashboard output shown in EveBloom is informational. Important
                    symptoms, urgent concerns, or emergencies should always be taken to a qualified clinician or emergency
                    service without delay.
                  </p>
                </section>

                <section className="legal-section">
                  <h2>5. Service Availability</h2>
                  <p>
                    The service may change over time, including updates to features, prediction models, design, and record
                    handling. Temporary interruptions, maintenance, or revisions may occur.
                  </p>
                </section>

                <section className="legal-section">
                  <h2>6. Limitation of Use</h2>
                  <p>
                    Users must not misuse the platform, attempt unauthorized access, interfere with normal operation, or use
                    the service for harmful, deceptive, or unlawful activity.
                  </p>
                </section>
              </>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}
