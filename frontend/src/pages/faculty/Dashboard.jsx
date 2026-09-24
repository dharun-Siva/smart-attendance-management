import { useEffect, useState } from 'react'
import attendanceApi from '../../api/attendanceApi'
import { Empty, FacultyPage, QuickAction, Status, errorMessage, formatDate } from './common'
import { Feedback } from '../../components/admin/Feedback'
import MetricCard from '../../components/layout/MetricCard'

export default function FacultyDashboard() {
  const [data, setData] = useState({ assignments: null, sessions: null })
  const [error, setError] = useState('')
  useEffect(() => { Promise.all([attendanceApi.assignments(), attendanceApi.sessions()]).then(([assignments, sessions]) => setData({ assignments, sessions })).catch((requestError) => setError(errorMessage(requestError))) }, [])
  const name = JSON.parse(localStorage.getItem('attendance_current_user') || '{}').username || 'Faculty member'
  return <FacultyPage eyebrow="Faculty overview" title={`Good day, ${name}.`} description="Keep your attendance work moving from one focused teaching view." action={<QuickAction to="/faculty/attendance/new">Take attendance</QuickAction>}>
    <Feedback>{error}</Feedback>
    <section className="metric-grid"><MetricCard label="Active assignments" value={data.assignments?.length ?? '—'} note="Your current teaching load" /><MetricCard label="Attendance sessions" value={data.sessions?.length ?? '—'} note="Sessions in your workspace" accent="blue" /><MetricCard label="Open sessions" value={data.sessions?.filter((session) => session.status === 'OPEN').length ?? '—'} note="Ready to complete" accent="amber" /></section>
    <section className="table-panel"><div className="table-panel-heading"><div><span className="eyebrow">Recent activity</span><h2>Recent attendance sessions</h2></div><a className="text-button" href="/faculty/attendance/history">View history</a></div>{data.sessions === null ? <div className="admin-loading">Loading recent sessions...</div> : data.sessions.length === 0 ? <Empty title="No attendance sessions yet">Create your first session when you are ready to take attendance.</Empty> : <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Date</th><th>Subject</th><th>Section</th><th>Topic</th><th>Status</th></tr></thead><tbody>{data.sessions.slice(0, 5).map((session) => { const assignment = data.assignments?.find((item) => item.id === session.faculty_assignment_id); return <tr key={session.id}><td><a className="text-button" href={`/faculty/attendance/sessions/${session.id}`}>{formatDate(session.attendance_date)}</a></td><td>{assignment?.subject_name || '—'}</td><td>{assignment?.section_name || '—'}</td><td>{session.topic || '—'}</td><td><Status value={session.status} /></td></tr> })}</tbody></table></div>}</section>
  </FacultyPage>
}
