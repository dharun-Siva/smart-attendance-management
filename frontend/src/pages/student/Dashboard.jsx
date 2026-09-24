import { useEffect, useState } from 'react'
import attendanceApi from '../../api/attendanceApi'
import { Feedback } from '../../components/admin/Feedback'
import MetricCard from '../../components/layout/MetricCard'
import { AttendanceStatus, StudentEmpty, StudentLoading, StudentPage, StudentLink, formatStudentDate, studentErrorMessage } from './common'

export default function StudentDashboard() {
  const [summary, setSummary] = useState(null)
  const [history, setHistory] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { Promise.all([attendanceApi.studentSummary(), attendanceApi.studentHistory()]).then(([loadedSummary, loadedHistory]) => { setSummary(loadedSummary); setHistory(loadedHistory) }).catch((requestError) => setError(studentErrorMessage(requestError))) }, [])
  return <StudentPage eyebrow="Student overview" title={summary ? `Welcome back, ${summary.student_name}.` : 'Your attendance, at a glance.'} description="Keep track of your progress across every recorded class." action={<StudentLink to="/student/history">View history</StudentLink>}>
    <Feedback>{error}</Feedback>
    {summary === null ? <StudentLoading /> : <>
      {summary.attendance_percentage < summary.low_attendance_threshold && <div className="attendance-warning" role="status"><strong>Your attendance is below the required percentage.</strong><span>{summary.subjects.filter((subject) => subject.is_low_attendance).map((subject) => subject.subject_name).join(', ') || 'Review your attendance below.'}</span></div>}
      <section className="metric-grid"><MetricCard label="Overall attendance" value={`${summary.attendance_percentage}%`} note={`Required threshold ${summary.low_attendance_threshold}%`} /><MetricCard label="Subjects" value={summary.subjects.length} note="Subjects with recorded attendance" accent="blue" /><MetricCard label="Sessions attended" value={summary.present_sessions + summary.late_sessions} note={`${summary.absent_sessions} absent · ${summary.late_sessions} late`} accent="amber" /></section>
      <section className="student-summary-grid"><div className="table-panel"><div className="table-panel-heading"><div><span className="eyebrow">Subject progress</span><h2>Subject-wise attendance</h2></div></div>{summary.subjects.length === 0 ? <StudentEmpty title="No attendance recorded yet">Your subject summaries will appear after faculty submits attendance.</StudentEmpty> : <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Subject</th><th>Code</th><th>Total</th><th>Present</th><th>Absent</th><th>Late</th><th>Attendance</th><th>Status</th></tr></thead><tbody>{summary.subjects.map((subject) => <tr key={subject.subject_code}><td>{subject.subject_name}</td><td>{subject.subject_code}</td><td>{subject.total_sessions}</td><td>{subject.present_sessions}</td><td>{subject.absent_sessions}</td><td>{subject.late_sessions}</td><td>{subject.attendance_percentage}%</td><td><span className={`status-badge ${subject.is_low_attendance ? 'status-absent' : 'status-present'}`}>{subject.is_low_attendance ? 'LOW' : 'GOOD'}</span></td></tr>)}</tbody></table></div>}</div></section>
      <section className="table-panel student-recent"><div className="table-panel-heading"><div><span className="eyebrow">Recent record</span><h2>Recent attendance information</h2></div></div>{history === null ? <StudentLoading /> : history.length === 0 ? <StudentEmpty title="No attendance history">Submitted attendance records will appear here.</StudentEmpty> : <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Date</th><th>Subject</th><th>Topic</th><th>Status</th></tr></thead><tbody>{history.slice(0, 5).map((record) => <tr key={`${record.attendance_session_id}-${record.subject_id}`}><td>{formatStudentDate(record.attendance_date)}</td><td>{record.subject_name}</td><td>{record.topic || '—'}</td><td><AttendanceStatus value={record.status} /></td></tr>)}</tbody></table></div>}</section>
    </>}
  </StudentPage>
}
