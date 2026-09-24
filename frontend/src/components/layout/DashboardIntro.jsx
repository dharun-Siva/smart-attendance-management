export default function DashboardIntro({ eyebrow, title, description, action }) {
  return (
    <section className="dashboard-intro">
      <div>
        <span className="eyebrow">{eyebrow}</span>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action && <span className="intro-date">{action}</span>}
    </section>
  )
}
