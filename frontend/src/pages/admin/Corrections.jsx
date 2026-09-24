import { useEffect, useState } from 'react'
import AppLayout from '../../components/layout/AppLayout'
import { Feedback, LoadingState } from '../../components/admin/Feedback'
import { getApiErrorMessage } from '../../utils/apiError'
import correctionApi from '../../api/correctionApi'
import attendanceApi from '../../api/attendanceApi'
import departmentApi from '../../api/departmentApi'
import classApi from '../../api/classApi'
import sectionApi from '../../api/sectionApi'
import subjectApi from '../../api/subjectApi'
import facultyApi from '../../api/facultyApi'

function formatDate(value) {
  return value ? new Intl.DateTimeFormat('en', { dateStyle: 'medium' }).format(new Date(value)) : '—'
}

function StatusBadge({ value }) {
  return <span className={`status-badge status-${String(value).toLowerCase()}`}>{value}</span>
}

export default function AdminCorrections() {
  const [corrections, setCorrections] = useState([])
  const [context, setContext] = useState(null)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState(null)
  const [rejecting, setRejecting] = useState(null)
  const [reviewComment, setReviewComment] = useState('')

  async function load() {
    setLoading(true)
    try {
      const [loadedCorrections, sessions, assignments, departments, classes, sections, subjects, faculty] = await Promise.all([
        correctionApi.list(), attendanceApi.sessions(), attendanceApi.assignments(), departmentApi.list(), classApi.list(), sectionApi.list(), subjectApi.list(), facultyApi.list(),
      ])
      const recordLists = await Promise.all(sessions.map((session) => attendanceApi.records(session.id)))
      const records = recordLists.flat()
      setCorrections(loadedCorrections)
      setContext({
        records: Object.fromEntries(records.map((record) => [record.id, record])),
        sessions: Object.fromEntries(sessions.map((session) => [session.id, session])),
        assignments: Object.fromEntries(assignments.map((assignment) => [assignment.id, assignment])),
        departments, classes, sections, subjects,
        faculty: Object.fromEntries(faculty.map((member) => [member.user_id, member])),
      })
    } catch (error) {
      setNotice({ type: 'error', message: getApiErrorMessage(error) })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  function detailsFor(correction) {
    const record = context?.records[correction.attendance_record_id]
    const session = record ? context.sessions[record.attendance_session_id] : null
    const assignment = session ? context.assignments[session.faculty_assignment_id] : null
    const subject = assignment ? context.subjects.find((item) => item.id === assignment.subject_id) : null
    const section = assignment ? context.sections.find((item) => item.id === assignment.section_id) : null
    const classItem = section ? context.classes.find((item) => item.id === section.class_id) : null
    const department = subject ? context.departments.find((item) => item.id === subject.department_id) : null
    return { record, session, assignment, subject, section, classItem, department }
  }

  async function approve(correction) {
    if (!window.confirm('Approve this attendance correction? The student record will be updated.')) return
    setBusy(true); setNotice(null)
    try {
      await correctionApi.approve(correction.id)
      setNotice({ type: 'success', message: 'Correction approved and attendance updated.' })
      await load()
    } catch (error) { setNotice({ type: 'error', message: getApiErrorMessage(error) }) } finally { setBusy(false) }
  }

  async function reject(event) {
    event.preventDefault()
    if (!reviewComment.trim()) return
    if (!window.confirm('Reject this attendance correction?')) return
    setBusy(true); setNotice(null)
    try {
      await correctionApi.reject(rejecting.id, { review_comment: reviewComment.trim() })
      setNotice({ type: 'success', message: 'Correction rejected.' })
      setRejecting(null); setReviewComment(''); await load()
    } catch (error) { setNotice({ type: 'error', message: getApiErrorMessage(error) }) } finally { setBusy(false) }
  }

  return <AppLayout><div className="admin-page">
    <div className="admin-page-heading"><div><span className="eyebrow">Administration</span><h1>Corrections</h1><p>Review faculty requests to amend submitted attendance records.</p></div></div>
    <Feedback type={notice?.type} onDismiss={() => setNotice(null)}>{notice?.message}</Feedback>
    {rejecting && <section className="form-panel"><div className="form-panel-heading"><div><span className="eyebrow">Review response</span><h2>Reject correction request</h2></div><button className="close-button" onClick={() => setRejecting(null)} aria-label="Close rejection form">×</button></div><form className="admin-form" onSubmit={reject}><label className="field-wide">Review comment<textarea value={reviewComment} onChange={(event) => setReviewComment(event.target.value)} rows="3" maxLength="500" required placeholder="Explain why this request is being rejected." /></label><div className="form-actions"><button type="button" className="secondary-button" onClick={() => setRejecting(null)}>Cancel</button><button className="primary-small-button" disabled={busy || !reviewComment.trim()}>{busy ? 'Rejecting...' : 'Reject correction'}</button></div></form></section>}
    <section className="table-panel"><div className="table-panel-heading"><div><span className="eyebrow">Review queue</span><h2>{corrections.length} correction requests</h2></div>{loading && <span className="table-status">Syncing...</span>}</div>{loading ? <LoadingState /> : !corrections.length ? <div className="admin-empty large-empty"><strong>No correction requests</strong><span>Faculty requests will appear here after submitted attendance is reviewed.</span></div> : <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Student</th><th>Student number</th><th>Subject</th><th>Section</th><th>Attendance date</th><th>Old status</th><th>Requested status</th><th>Reason</th><th>Requested by</th><th>Status</th><th>Created</th><th><span className="sr-only">Actions</span></th></tr></thead><tbody>{corrections.map((correction) => { const details = detailsFor(correction); const faculty = context?.faculty[correction.requested_by_id]; return <tr key={correction.id}><td>{details.record?.student_name || `Record #${correction.attendance_record_id}`}</td><td>{details.record?.student_number || '—'}</td><td>{details.subject?.name || '—'}</td><td>{details.section?.name || '—'}</td><td>{formatDate(details.session?.attendance_date)}</td><td><StatusBadge value={correction.old_status} /></td><td><StatusBadge value={correction.new_status} /></td><td>{correction.reason}</td><td>{faculty?.username || `User #${correction.requested_by_id}`}</td><td><StatusBadge value={correction.status} /></td><td>{formatDate(correction.created_at)}</td><td className="table-actions">{correction.status === 'PENDING' && <><button className="text-button" onClick={() => approve(correction)} disabled={busy}>Approve</button><button className="text-button muted-action" onClick={() => { setRejecting(correction); setReviewComment('') }} disabled={busy}>Reject</button></>}</td></tr> })}</tbody></table></div>}</section>
  </div></AppLayout>
}
