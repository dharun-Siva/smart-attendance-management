import { useEffect, useState } from 'react'
import attendanceApi from '../../api/attendanceApi'
import { Feedback } from '../../components/admin/Feedback'
import { StudentLoading, StudentPage, studentErrorMessage } from './common'

export default function StudentProfile() {
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { attendanceApi.studentSummary().then(setSummary).catch((requestError) => setError(studentErrorMessage(requestError))) }, [])
  return <StudentPage title="Profile" description="Your personal student account and enrollment context."><Feedback>{error}</Feedback>{summary === null ? <StudentLoading /> : <section className="profile-grid"><div className="profile-identity"><span className="avatar profile-avatar">{summary.student_name.slice(0, 2).toUpperCase()}</span><div><span className="eyebrow">Student account</span><h2>{summary.student_name}</h2><p>{summary.student_number} · {summary.email}</p></div></div><div className="table-panel profile-details"><div><span className="eyebrow">Enrollment details</span><h2>Academic context</h2></div><dl><div><dt>Student number</dt><dd>{summary.student_number}</dd></div><div><dt>Email</dt><dd>{summary.email}</dd></div><div><dt>Department</dt><dd>{summary.department_name}</dd></div><div><dt>Class</dt><dd>{summary.class_name || '—'}</dd></div><div><dt>Section</dt><dd>{summary.section_name || '—'}</dd></div></dl></div></section>}</StudentPage>
}
