import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import '../styles/auth.css'
import authImage from '../assets/authentication-image.jpg'
import { useAuthStore } from '../stores/authStore'

export default function SignUpPage() {
  const navigate = useNavigate()
  const signup = useAuthStore((state) => state.signup)
  const isLoading = useAuthStore((state) => state.isLoading)
  const error = useAuthStore((state) => state.error)
  const clearError = useAuthStore((state) => state.clearError)

  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  useEffect(() => {
    return () => clearError()
  }, [clearError])

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    try {
      await signup(fullName.trim(), email.trim(), password)
      navigate('/dashboard')
    } catch {
      // Error state managed in store
    }
  }

  return (
    <div className="auth-page">
      <section className="auth-left">
        <div className="auth-form-wrap">
          <Link to="/" className="auth-brand">
            <span className="auth-brand-mark" aria-hidden>
              <svg viewBox="0 0 24 24">
                <circle cx="12" cy="6" r="3" fill="currentColor" />
                <circle cx="8" cy="12" r="3" fill="currentColor" />
                <circle cx="16" cy="12" r="3" fill="currentColor" />
                <circle cx="12" cy="18" r="3" fill="currentColor" />
              </svg>
            </span>
            Natalis AI
          </Link>

          <p className="auth-kicker">
            <span className="kicker-icon" aria-hidden>
              <svg viewBox="0 0 24 24">
                <path d="M12 3l7 3v6c0 5-3.4 8.4-7 10-3.6-1.6-7-5-7-10V6l7-3z" fill="none" stroke="currentColor" strokeWidth="2" />
              </svg>
            </span>
            Secure Medical Portal
          </p>
          <h1>Create account</h1>
          <p className="auth-subtext">Join 10,000+ women tracking their health securely.</p>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="form-field">
              <label htmlFor="signup-fullname">Full Name</label>
              <div className="input-wrap">
                <input
                  id="signup-fullname"
                  type="text"
                  placeholder="Dr. Jane Doe"
                  value={fullName}
                  onChange={(event) => setFullName(event.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-field">
              <label htmlFor="signup-email">Email Address</label>
              <div className="input-wrap">
                <input
                  id="signup-email"
                  type="email"
                  placeholder="name@example.com"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-field">
              <label htmlFor="signup-password">Password</label>
              <div className="input-wrap">
                <input
                  id="signup-password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                />
                <svg className="input-icon" viewBox="0 0 24 24" aria-hidden>
                  <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6z" fill="none" stroke="currentColor" strokeWidth="1.8" />
                  <circle cx="12" cy="12" r="2.8" fill="none" stroke="currentColor" strokeWidth="1.8" />
                </svg>
              </div>
            </div>

            <div className="auth-agreement">
              <svg viewBox="0 0 24 24" aria-hidden>
                <path d="M12 3l7 3v6c0 5-3.4 8.4-7 10-3.6-1.6-7-5-7-10V6l7-3z" fill="none" stroke="currentColor" strokeWidth="1.8" />
              </svg>
              <p>
                I agree to the <strong>Terms of Service</strong> and acknowledge that my data will be encrypted according to <strong>HIPAA Standards</strong>
              </p>
            </div>

            {error ? <p className="auth-error">{error}</p> : null}

            <button type="submit" className="auth-submit" disabled={isLoading}>
              {isLoading ? 'Creating account...' : 'Create Secure Account'}
            </button>
          </form>

          <p className="divider">Or sign up with</p>

          <div className="socials">
            <button type="button">
              <span className="social-icon" aria-hidden>
                <svg viewBox="0 0 24 24">
                  <path fill="#EA4335" d="M12 10.2v3.9h5.5c-.3 1.9-2.2 3.5-5.5 3.5a5.8 5.8 0 110-11.6c1.7 0 3.1.6 4.2 1.7l2.7-2.6A9.3 9.3 0 0012 2.8a9.4 9.4 0 100 18.8c5.4 0 9-3.8 9-9 0-.6 0-1-.1-1.4H12z"/>
                </svg>
              </span>
              Google
            </button>
            <button type="button">
              <span className="social-icon" aria-hidden>
                <svg viewBox="0 0 24 24">
                  <path fill="#334155" d="M16.6 12.6c0-2.2 1.8-3.2 1.9-3.2-1-1.5-2.6-1.7-3.2-1.7-1.4-.1-2.7.8-3.4.8-.7 0-1.8-.8-3-.8-1.6 0-3 .9-3.8 2.3-1.6 2.7-.4 6.8 1.2 9.1.8 1.1 1.7 2.4 2.9 2.4 1.1 0 1.6-.7 3-.7 1.4 0 1.8.7 3 .7 1.3 0 2.1-1.1 2.9-2.2.9-1.3 1.2-2.6 1.2-2.7 0 0-2.7-1-2.7-4zM14.4 6.4c.7-.8 1.1-1.8 1-2.9-1 .1-2.1.7-2.8 1.5-.6.7-1.2 1.8-1 2.8 1 .1 2.1-.5 2.8-1.4z"/>
                </svg>
              </span>
              Apple
            </button>
          </div>

          <p className="auth-foot-line">
            Already have an account? <Link className="auth-link" to="/sign-in">Log in securely</Link>
          </p>

          <div className="auth-meta">
            <span>Privacy Policy</span>
            <span>Terms of Service</span>
            <span>🔒 256-bit SSL Encrypted</span>
          </div>
        </div>
      </section>

      <section className="auth-right">
        <div className="auth-art">
          <img src={authImage} alt="Medical abstract visual" />

          <div className="auth-status-card">
            <div className="auth-status-head">
              <div>
                <h3>Patient Health Status</h3>
                <p>Live monitoring active</p>
              </div>
              <span>●</span>
            </div>
            <p className="auth-balance">Hormonal Balance <strong>Optimal Range</strong></p>
            <div className="auth-bars" aria-hidden>
              <span /><span /><span /><span /><span /><span /><span />
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
