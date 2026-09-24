import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

function destinationFor(role) {
  return `/${role.toLowerCase()}/dashboard`
}

export default function Login() {
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState({ username_or_email: '', password: '' })
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (isAuthenticated) {
    return <Navigate to={destinationFor(JSON.parse(localStorage.getItem('attendance_current_user')).role)} replace />
  }

  function updateField(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      const user = await login(form)
      const requestedPath = location.state?.from?.pathname
      navigate(requestedPath || destinationFor(user.role), { replace: true })
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'We could not sign you in. Check your credentials.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="login-page">
      <section className="login-aside">
        <div className="brand-lockup login-brand">
          <div className="brand-mark">CR</div>
          <div>
            <strong>Campus Rollcall</strong>
            <span>Attendance command center</span>
          </div>
        </div>
        <div className="login-quote">
          <span className="eyebrow">College operations</span>
          <h1>Make every class count.</h1>
          <p>A calm, accountable home for the people and rhythms behind student attendance.</p>
        </div>
        <div className="login-aside-footer">Smart attendance management system <span>2026</span></div>
      </section>
      <section className="login-panel">
        <div className="login-card">
          <span className="eyebrow">Secure access</span>
          <h2>Welcome back</h2>
          <p className="login-helper">Sign in to continue to your attendance workspace.</p>
          <form onSubmit={handleSubmit}>
            <label>
              Username or email
              <input
                name="username_or_email"
                value={form.username_or_email}
                onChange={updateField}
                autoComplete="username"
                placeholder="you@college.edu"
                required
              />
            </label>
            <label>
              Password
              <input
                name="password"
                type="password"
                value={form.password}
                onChange={updateField}
                autoComplete="current-password"
                placeholder="Enter your password"
                required
              />
            </label>
            {error && <div className="form-error" role="alert">{error}</div>}
            <button className="primary-button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Signing in...' : 'Sign in'}
              <span aria-hidden="true">→</span>
            </button>
          </form>
          <p className="login-footnote">Use your college account credentials.</p>
        </div>
      </section>
    </main>
  )
}
