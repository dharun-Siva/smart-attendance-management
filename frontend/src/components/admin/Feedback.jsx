export function Feedback({ type = 'error', children, onDismiss }) {
  if (!children) return null
  return <div className={`feedback feedback-${type}`} role={type === 'error' ? 'alert' : 'status'}>{children}{onDismiss && <button onClick={onDismiss} aria-label="Dismiss message">×</button>}</div>
}

export function LoadingState() {
  return <div className="admin-loading"><span className="loading-dot" /> Loading records...</div>
}
