import type { CSSProperties } from 'react'
import { Link } from 'react-router-dom'
import '../styles/landing.css'
import heroImage from '../assets/home-page-women.jpg'
import labImage from '../assets/lab-woman.jpg'
import pregnancyImage from '../assets/pregnant-woman.jpg'
import postpartumImage from '../assets/woman-baby.jpg'
import appLogo from '../assets/logo.svg'
import securityBackground from '../assets/security-background.png'

type JourneyCard = {
  title: string
  description: string
  image: string
  icon: 'spark' | 'heart' | 'smile'
  tone?: 'warm' | 'mono'
}

type Step = {
  number: string
  title: string
  description: string
}

type SecurityCard = {
  title: string
  description: string
  icon: 'lock' | 'database' | 'shield'
}

const journeyCards: JourneyCard[] = [
  {
    title: 'Infertility Insights',
    description:
      'Enter cycle and symptom information to receive an infertility risk estimate and a short explanation of the result.',
    image: labImage,
    icon: 'spark',
    tone: 'warm',
  },
  {
    title: 'Pregnancy Monitoring',
    description:
      'Log pregnancy follow-up vitals and indicators to view risk scores, trend summaries, and recent key factors.',
    image: pregnancyImage,
    icon: 'heart',
  },
  {
    title: 'Postpartum Recovery',
    description:
      'Complete postpartum check-ins to review recovery-related risk signals, guidance, and top contributing factors.',
    image: postpartumImage,
    icon: 'smile',
    tone: 'mono',
  },
]

const steps: Step[] = [
  {
    number: '01',
    title: 'Enter Your Information',
    description:
      'Fill in the form for infertility, pregnancy, or postpartum using the inputs requested on each dashboard.',
  },
  {
    number: '02',
    title: 'Run the Assessment',
    description:
      'The system processes the information you enter and generates a stage-specific risk result.',
  },
  {
    number: '03',
    title: 'Review the Dashboard',
    description:
      'See the result, simple guidance, stored history, and highlighted factors that shaped the latest output.',
  },
]

const securityCards: SecurityCard[] = [
  {
    title: 'Protected Access',
    description: 'Accounts are accessed through authenticated sign-in and protected application routes.',
    icon: 'lock',
  },
  {
    title: 'Stored Records',
    description: 'Saved assessments can be used to show recent history, follow-up trends, and dashboard summaries.',
    icon: 'database',
  },
  {
    title: 'Privacy Information',
    description:
      'Privacy policy and terms pages explain how the platform is intended to be used and how records are handled.',
    icon: 'shield',
  },
]

const Icon = ({ name }: { name: string }) => {
  if (name === 'spark') {
    return (
      <svg viewBox="0 0 24 24" aria-hidden>
        <path d="M12 2l1.7 4.8L18.5 8l-4.8 1.2L12 14l-1.7-4.8L5.5 8l4.8-1.2L12 2z" />
        <circle cx="6" cy="18" r="2.4" />
        <circle cx="18" cy="16" r="1.6" />
      </svg>
    )
  }

  if (name === 'heart') {
    return (
      <svg viewBox="0 0 24 24" aria-hidden>
        <path d="M12 21s-7-4.6-9.3-9C.9 8.8 2.5 5.4 6.3 5.1c2-.1 3.4.8 4.7 2.4 1.3-1.6 2.8-2.5 4.7-2.4C19.5 5.4 21.1 8.8 19.3 12 19 12.6 16.3 17 12 21z" />
      </svg>
    )
  }

  if (name === 'smile') {
    return (
      <svg viewBox="0 0 24 24" aria-hidden>
        <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="2" />
        <circle cx="9" cy="10" r="1.1" />
        <circle cx="15" cy="10" r="1.1" />
        <path d="M8 14.2c1.2 1.5 2.5 2.2 4 2.2s2.8-.7 4-2.2" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
    )
  }

  if (name === 'lock') {
    return (
      <svg viewBox="0 0 24 24" aria-hidden>
        <path d="M7 10V8a5 5 0 0110 0v2" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <rect x="5" y="10" width="14" height="10" rx="2" fill="none" stroke="currentColor" strokeWidth="2" />
      </svg>
    )
  }

  if (name === 'database') {
    return (
      <svg viewBox="0 0 24 24" aria-hidden>
        <ellipse cx="12" cy="6" rx="7" ry="3" fill="none" stroke="currentColor" strokeWidth="2" />
        <path d="M5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6" fill="none" stroke="currentColor" strokeWidth="2" />
        <path d="M5 12v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6" fill="none" stroke="currentColor" strokeWidth="2" />
      </svg>
    )
  }

  return (
    <svg viewBox="0 0 24 24" aria-hidden>
      <path d="M12 3l6 2v5c0 5-3.3 8.8-6 10.7C9.3 18.8 6 15 6 10V5l6-2z" fill="none" stroke="currentColor" strokeWidth="2" />
    </svg>
  )
}

export default function LandingPage() {
  const securitySectionStyle = {
    '--security-bg-image': `url(${securityBackground})`,
  } as CSSProperties

  return (
    <div className="landing-page">
      <header className="top-nav">
        <div className="brand">
          <span className="brand-mark" aria-hidden>
            <img src={appLogo} alt="" className="brand-logo" />
          </span>
          <span>EveBloom</span>
        </div>

        <nav className="desktop-nav" aria-label="Primary">
          <a href="#services">Services</a>
          <a href="#how-it-works">How it Works</a>
          <a href="#security">Security</a>
        </nav>

        <Link className="cta-pill" to="/sign-up">
          Get Started
        </Link>
      </header>

      <main>
        <section className="hero" id="services">
          <div className="hero-copy">
            <p className="hero-badge">
              <span aria-hidden>✧</span> Reproductive Health Risk Tracking
            </p>

            <h1>
              Track Risk Signals Across
              <br />
              <span>Every Stage</span> of
              <br />
              Reproductive Care.
            </h1>

            <p className="hero-text">
              EveBloom helps you record infertility, pregnancy, and postpartum information,
              generate stage-specific risk results, and review guidance and trends in one place.
            </p>

            <div className="hero-actions">
              <Link className="button button-primary" to="/sign-up">
                Start Your Assessment <span aria-hidden>→</span>
              </Link>
            </div>
          </div>

          <div className="hero-image-wrap">
            <img src={heroImage} alt="Three women smiling together" />
            <div className="status-pill">
              <span className="status-icon" aria-hidden>
                <svg viewBox="0 0 24 24">
                  <path
                    d="M3 12h3l2-5 3 10 2-6h8"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </span>
              <span>
                <small>HEALTH STATUS</small>
                <strong>Recent Risk Summary</strong>
              </span>
            </div>
          </div>
        </section>

        <section className="journey section-surface">
          <div className="section-head center">
            <h2>Comprehensive Care for Every Journey</h2>
            <p>
              The platform is organized into three dashboards so each stage can collect the
              right inputs and present the right type of result.
            </p>
          </div>

          <div className="journey-grid">
            {journeyCards.map((card) => (
              <article key={card.title} className="journey-card">
                <div className={`journey-media ${card.tone ? `tone-${card.tone}` : ''}`}>
                  <img src={card.image} alt={card.title} />
                </div>
                <div className="journey-card-body">
                  <div className="mini-icon" aria-hidden>
                    <Icon name={card.icon} />
                  </div>

                  <h3>{card.title}</h3>
                  <p>{card.description}</p>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="engine" id="how-it-works">
          <div className="engine-left">
            <h2>How Our Prediction Engine Works</h2>
            <p>
              Each stage uses its own input flow and stored records to generate a focused
              result and supporting dashboard view.
            </p>

            <div className="steps-list">
              {steps.map((step) => (
                <article key={step.number} className="step-item">
                  <div className="step-number">{step.number}</div>
                  <div>
                    <h3>{step.title}</h3>
                    <p>{step.description}</p>
                  </div>
                </article>
              ))}
            </div>
          </div>

          <div className="engine-card-wrap">
            <div className="engine-card">
              <div className="engine-header">
                <span className="brain-dot" aria-hidden>
                  <svg viewBox="0 0 24 24">
                    <path
                      d="M9 4a3 3 0 000 6m6-6a3 3 0 010 6M9 10v2m6-2v2M8 14a2 2 0 004 0m0 0a2 2 0 004 0m-4 0v4"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                </span>
                <div>
                  <h3>Prediction Workflow</h3>
                  <p>Inputs, result, and dashboard summary</p>
                </div>
              </div>

              <div className="bars" aria-hidden>
                <span className="bar b1" />
                <span className="bar b2" />
                <span className="bar b3" />
              </div>

              <div className="accuracy-row">
                <p>Latest Output</p>
                <strong>Risk Summary</strong>
              </div>
            </div>
          </div>
        </section>

        <section className="security" id="security" style={securitySectionStyle}>
          <div className="security-overlay" aria-hidden />
          <div className="security-content">
            <span className="security-icon" aria-hidden>
              <Icon name="shield" />
            </span>
            <h2>Data and Access</h2>
            <p>
              EveBloom stores assessments to support dashboards, follow-up tracking, and legal
              information pages for users before and after sign-in.
            </p>

            <div className="security-grid">
              {securityCards.map((item) => (
                <article key={item.title} className="security-card">
                  <span className="security-card-icon" aria-hidden>
                    <Icon name={item.icon} />
                  </span>
                  <h3>{item.title}</h3>
                  <p>{item.description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="final-cta">
          <h2>Ready to Take Control of Your Health Journey?</h2>
          <p>
            Create an account to start using the infertility, pregnancy, and postpartum tools
            from one dashboard.
          </p>
          <Link to="/sign-up" className="button button-primary">
            Create an Account
          </Link>
        </section>
      </main>

      <footer className="site-footer">© 2026 EveBloom. All rights reserved.</footer>
    </div>
  )
}
