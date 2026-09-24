import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import attendanceApi from '../../api/attendanceApi'
import { Feedback } from '../../components/admin/Feedback'
import { Empty, FacultyPage, Loading, Status, errorMessage, formatDate } from './common'

export default function AttendanceHistory() {
  const [sessions, setSessions] = useState(null); const [assignments, setAssignments] = useState([]); const [error, setError] = useState('')
  useEffect(() => { Promise.all([attendanceApi.sessions(), attendanceApi.assignments()]).then(([loadedSessions, loadedAssignments]) => { setSessions(loadedSessions); setAssignments(loadedAssignments) }).catch((requestError) => setError(errorMessage(requestError))) }, [])
  return <FacultyPage title="Attendance history" description="Review every attendance session created for your assigned classes."><Feedback>{error}</Feedback><section className="table-panel"><div className="table-panel-heading"><div><span className="eyebrow">Session archive</span><h2>Attendance sessions</h2></div><span className="table-status">{sessions?.length || 0} sessions</span></div>{sessions === null ? <Loading /> : sessions.length === 0 ? <Empty title="No history yet">Submitted sessions will appear here.</Empty> : <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Date</th><th>Subject</th><th>Section</th><th>Topic</th><th>Status</th><th /></tr></thead><tbody>{sessions.map((session) => { const assignment = assignments.find((item) => item.id === session.faculty_assignment_id); return <tr key={session.id}><td>{formatDate(session.attendance_date)}</td><td>{assignment?.subject_name || '—'}</td><td>{assignment?.section_name || '—'}</td><td>{session.topic || '—'}</td><td><Status value={session.status} /></td><td className="table-actions"><Link className="text-button" to={`/faculty/attendance/sessions/${session.id}`}>Open</Link></td></tr> })}</tbody></table></div>}</section></FacultyPage>
}
