import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Lock, Shield } from 'lucide-react'
import '../styles/auth.css'
import authImage from '../assets/authentication-image.jpg'
import appLogo from '../assets/logo.svg'
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
  const [isPasswordVisible, setIsPasswordVisible] = useState(false)

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
              <img src={appLogo} alt="" className="auth-brand-logo" />
            </span>
            EveBloom
          </Link>

          <p className="auth-kicker">
            <span className="kicker-icon" aria-hidden>
              <Shield size={12} strokeWidth={2} />
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
                  type={isPasswordVisible ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                  minLength={8}
                />
                <button
                  type="button"
                  className="input-icon-btn"
                  aria-label={isPasswordVisible ? 'Hide password' : 'Show password'}
                  onClick={() => setIsPasswordVisible((previous) => !previous)}
                >
                  {isPasswordVisible ? (
                    <EyeOff className="input-icon" size={18} strokeWidth={1.8} aria-hidden />
                  ) : (
                    <Eye className="input-icon" size={18} strokeWidth={1.8} aria-hidden />
                  )}
                </button>
              </div>
            </div>

            <div className="auth-agreement">
              <Shield size={18} strokeWidth={1.8} aria-hidden />
              <p>
                I agree to the <Link className="auth-link" to="/terms-of-service">Terms of Service</Link> and acknowledge
                that my data will be handled as described in the{' '}
                <Link className="auth-link" to="/privacy-policy">Privacy Policy</Link>.
              </p>
            </div>

            {error ? <p className="auth-error">{error}</p> : null}

            <button type="submit" className="auth-submit" disabled={isLoading}>
              {isLoading ? 'Creating account...' : 'Create Secure Account'}
            </button>
          </form>

          <p className="auth-foot-line">
            Already have an account? <Link className="auth-link" to="/sign-in">Log in securely</Link>
          </p>

          <div className="auth-meta">
            <Link className="auth-meta-link" to="/privacy-policy">Privacy Policy</Link>
            <Link className="auth-meta-link" to="/terms-of-service">Terms of Service</Link>
            <span className="auth-meta-lock">
              <Lock size={12} strokeWidth={2} aria-hidden />
              256-bit SSL Encrypted
            </span>
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
