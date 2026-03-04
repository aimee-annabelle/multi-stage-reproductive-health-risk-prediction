import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, Lock, Shield } from 'lucide-react'
import '../styles/auth.css'
import authImage from '../assets/authentication-image.jpg'
import appLogo from '../assets/logo.svg'
import { useAuthStore } from '../stores/authStore'

export default function SignInPage() {
  const navigate = useNavigate()
  const login = useAuthStore((state) => state.login)
  const isLoading = useAuthStore((state) => state.isLoading)
  const error = useAuthStore((state) => state.error)
  const clearError = useAuthStore((state) => state.clearError)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  useEffect(() => {
    return () => clearError()
  }, [clearError])

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    try {
      await login(email.trim(), password)
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
          <h1>Welcome back</h1>
          <p className="auth-subtext">Please enter your secure credentials to access your patient portal.</p>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="form-field">
              <label htmlFor="signin-email">Email Address</label>
              <div className="input-wrap">
                <input
                  id="signin-email"
                  type="email"
                  placeholder="name@example.com"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-field">
              <label htmlFor="signin-password">Password</label>
              <div className="input-wrap">
                <input
                  id="signin-password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                />
                <Eye className="input-icon" size={18} strokeWidth={1.8} aria-hidden />
              </div>
            </div>

            <div className="auth-row">
              <span>Remember me</span>
              <button type="button" className="auth-link" disabled>Forgot password?</button>
            </div>

            {error ? <p className="auth-error">{error}</p> : null}

            <button type="submit" className="auth-submit" disabled={isLoading}>
              <span className="auth-submit-icon" aria-hidden>
                <Lock size={16} strokeWidth={2} />
              </span>
              {isLoading ? 'Signing in...' : 'Secure Login'}
            </button>
          </form>

          <p className="auth-foot-line">
            Don&apos;t have an account? <Link className="auth-link" to="/sign-up">Sign up securely</Link>
          </p>

          <div className="auth-meta">
            <span>Privacy Policy</span>
            <span>Terms of Service</span>
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
