import { useEffect, useState } from 'react'
import attendanceApi from '../../api/attendanceApi'
import { Feedback } from '../../components/admin/Feedback'
import { Empty, FacultyPage, Loading, Status, errorMessage } from './common'

export default function FacultyAssignments() {
  const [assignments, setAssignments] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { attendanceApi.assignments().then(setAssignments).catch((requestError) => setError(errorMessage(requestError))) }, [])
  return <FacultyPage title="My assignments" description="The subjects and sections currently assigned to your faculty account.">
    <Feedback>{error}</Feedback>
    <section className="table-panel">
      <div className="table-panel-heading"><div><span className="eyebrow">Teaching load</span><h2>Active faculty assignments</h2></div><span className="table-status">{assignments?.length || 0} assignments</span></div>
      {assignments === null ? <Loading /> : assignments.length === 0 ? <Empty title="No assignments found">Your administrator has not assigned a class to you yet.</Empty> : <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Subject</th><th>Section</th><th>Class</th><th>Department</th><th>Status</th></tr></thead><tbody>{assignments.map((assignment) => <tr key={assignment.id}><td>{assignment.subject_name}</td><td>{assignment.section_name}</td><td>{assignment.class_name}</td><td>{assignment.department_name}</td><td><Status value={assignment.is_active ? 'ACTIVE' : 'INACTIVE'} /></td></tr>)}</tbody></table></div>}
    </section>
  </FacultyPage>
}
