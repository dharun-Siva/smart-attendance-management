import { Link } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'

export function errorMessage(error, fallback = 'The request could not be completed.') {
  const detail = error.response?.data?.detail
  if (Array.isArray(detail)) return detail.map((item) => item.msg).join(' ')
  return detail || (error.request ? 'The server could not be reached. Check your connection.' : fallback)
}


export function FacultyPage({ eyebrow = 'Faculty workspace', title, description, children, action }) {
  return <AppLayout><div className="admin-page">
    <div className="admin-page-heading"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{description}</p></div>{action}</div>
    {children}
  </div></AppLayout>
}

export function Loading() { return <div className="admin-loading"><span className="loading-dot" /> Loading faculty records...</div> }
export function Empty({ title, children }) { return <div className="admin-empty large-empty"><strong>{title}</strong><span>{children}</span></div> }
export function Status({ value }) { return <span className={`status-badge status-${String(value).toLowerCase()}`}>{value}</span> }
export function formatDate(value) { return value ? new Intl.DateTimeFormat('en', { dateStyle: 'medium' }).format(new Date(`${value}T00:00:00`)) : '—' }
export function QuickAction({ to, children }) { return <Link className="primary-small-button" to={to}>{children} <span aria-hidden="true">→</span></Link> }
