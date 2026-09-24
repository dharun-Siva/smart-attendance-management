import AppLayout from '../../components/layout/AppLayout'
import DashboardIntro from '../../components/layout/DashboardIntro'
import MetricCard from '../../components/layout/MetricCard'
import { useEffect, useState } from 'react'
import { getAdminSummary } from '../../api/adminApi'
import { Feedback, LoadingState } from '../../components/admin/Feedback'
import { getApiErrorMessage } from '../../utils/apiError'

export default function AdminDashboard() {
  const [summary, setSummary] = useState({ departments: [], faculty: [], students: [], lowAttendance: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getAdminSummary()
      .then(setSummary)
      .catch((requestError) => setError(getApiErrorMessage(requestError)))
      .finally(() => setLoading(false))
  }, [])

  return (
    <AppLayout>
      <DashboardIntro
        eyebrow="Administrator overview"
        title="A clear view of campus attendance."
        description="Your management workspace is ready for departments, people, assignments, and policy decisions."
        action="Foundation phase"
      />
      {error && <Feedback type="error">{error}</Feedback>}
      {loading ? <LoadingState /> : <section className="metric-grid admin-metrics">
        <MetricCard label="Total students" value={summary.students.length} note="Active student directory" />
        <MetricCard label="Total faculty" value={summary.faculty.length} note="Teaching accounts" accent="blue" />
        <MetricCard label="Departments" value={summary.departments.length} note="Academic ownership" accent="amber" />
        <MetricCard label="Low attendance" value={summary.lowAttendance.length} note="Below 75% threshold" accent="rose" />
      </section>}
      <section className="workspace-panel">
        <div className="panel-heading"><div><span className="eyebrow">Next in your workspace</span><h2>Management tools are on their way</h2></div><span className="panel-index">01 / 04</span></div>
        <div className="empty-state"><span className="empty-number">A</span><div><strong>Build the academic picture first</strong><p>Use the sidebar to manage departments, classes, sections, subjects, people, and their relationships.</p></div></div>
      </section>
    </AppLayout>
  )
}
