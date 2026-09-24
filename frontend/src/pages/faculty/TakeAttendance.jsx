import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import attendanceApi from '../../api/attendanceApi'
import { Feedback } from '../../components/admin/Feedback'
import { FacultyPage, Loading, errorMessage } from './common'

export default function TakeAttendance() {
  const navigate = useNavigate()
  const [assignments, setAssignments] = useState(null)
  const [form, setForm] = useState({ faculty_assignment_id: '', attendance_date: new Date().toISOString().slice(0, 10), topic: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  useEffect(() => { attendanceApi.assignments().then(setAssignments).catch((requestError) => setError(errorMessage(requestError))) }, [])
  async function submit(event) { event.preventDefault(); setError(''); setBusy(true); try { const session = await attendanceApi.createSession({ ...form, faculty_assignment_id: Number(form.faculty_assignment_id), topic: form.topic || null }); navigate(`/faculty/attendance/sessions/${session.id}`) } catch (requestError) { setError(errorMessage(requestError, 'The attendance session could not be created.')) } finally { setBusy(false) } }
  return <FacultyPage title="Take attendance" description="Start a session for one of your active assignments, then record every enrolled student.">
    <Feedback>{error}</Feedback><section className="form-panel"><div className="form-panel-heading"><div><span className="eyebrow">New session</span><h2>Session details</h2></div></div>{assignments === null ? <Loading /> : assignments.length === 0 ? <div className="admin-empty"><strong>No active assignments</strong><span>Ask an administrator to assign a subject and section first.</span></div> : <form className="admin-form" onSubmit={submit}><div className="form-grid"><label>Assignment<select value={form.faculty_assignment_id} onChange={(event) => setForm({ ...form, faculty_assignment_id: event.target.value })} required><option value="">Select an assignment</option>{assignments.map((assignment) => <option key={assignment.id} value={assignment.id}>{assignment.subject_name} · {assignment.section_name}</option>)}</select></label><label>Attendance date<input type="date" value={form.attendance_date} onChange={(event) => setForm({ ...form, attendance_date: event.target.value })} required /></label><label>Topic <span className="field-optional">optional</span><input value={form.topic} onChange={(event) => setForm({ ...form, topic: event.target.value })} maxLength="255" placeholder="What are you teaching today?" /></label></div><div className="form-actions"><button className="primary-small-button" disabled={busy}>{busy ? 'Creating...' : 'Create session'} <span aria-hidden="true">→</span></button></div></form>}</section>
  </FacultyPage>
}
