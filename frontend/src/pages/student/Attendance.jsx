import { useEffect, useState } from 'react'
import attendanceApi from '../../api/attendanceApi'
import { Feedback } from '../../components/admin/Feedback'
import { StudentEmpty, StudentLoading, StudentPage, studentErrorMessage } from './common'

export default function StudentAttendance() {
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { attendanceApi.studentSummary().then(setSummary).catch((requestError) => setError(studentErrorMessage(requestError))) }, [])
  return <StudentPage title="My attendance" description="See your attendance progress across each subject."><Feedback>{error}</Feedback>{summary === null ? <StudentLoading /> : summary.subjects.length === 0 ? <StudentEmpty title="No subject attendance yet">Your subject summaries will appear after submitted sessions are recorded.</StudentEmpty> : <section className="subject-card-grid">{summary.subjects.map((subject) => <article className="subject-card" key={subject.subject_code}><div className="subject-card-heading"><div><span className="eyebrow">{subject.subject_code}</span><h2>{subject.subject_name}</h2></div><span className={`status-badge ${subject.is_low_attendance ? 'status-absent' : 'status-present'}`}>{subject.is_low_attendance ? 'LOW' : 'GOOD'}</span></div><strong className="subject-percentage">{subject.attendance_percentage}%</strong><div className="subject-card-stats"><span><b>{subject.present_sessions}</b> Present</span><span><b>{subject.absent_sessions}</b> Absent</span><span><b>{subject.late_sessions}</b> Late</span><span><b>{subject.excused_sessions}</b> Excused</span></div></article>)}</section>}</StudentPage>
}
