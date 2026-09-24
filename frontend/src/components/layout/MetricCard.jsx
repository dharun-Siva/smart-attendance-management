export default function MetricCard({ label, value, note, accent = 'green' }) {
  return (
    <article className={`metric-card metric-${accent}`}>
      <span className="metric-label">{label}</span>
      <strong>{value}</strong>
      <span className="metric-note">{note}</span>
    </article>
  )
}
