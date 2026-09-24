import { useEffect, useState } from 'react'
import attendanceApi from '../../api/attendanceApi'
import { Feedback } from '../../components/admin/Feedback'
import { AttendanceStatus, StudentEmpty, StudentLoading, StudentPage, formatStudentDate, studentErrorMessage } from './common'

export default function StudentHistory() {
  const [history, setHistory] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { attendanceApi.studentHistory().then(setHistory).catch((requestError) => setError(studentErrorMessage(requestError))) }, [])
  return <StudentPage title="Attendance history" description="Review your submitted attendance record by date and subject."><Feedback>{error}</Feedback><section className="table-panel"><div className="table-panel-heading"><div><span className="eyebrow">Personal record</span><h2>Attendance history</h2></div><span className="table-status">{history?.length || 0} records</span></div>{history === null ? <StudentLoading /> : history.length === 0 ? <StudentEmpty title="No attendance history">Submitted attendance records will appear here.</StudentEmpty> : <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Date</th><th>Subject</th><th>Topic</th><th>Status</th><th>Remarks</th></tr></thead><tbody>{history.map((record) => <tr key={`${record.attendance_session_id}-${record.subject_id}`}><td>{formatStudentDate(record.attendance_date)}</td><td>{record.subject_name}</td><td>{record.topic || '—'}</td><td><AttendanceStatus value={record.status} /></td><td>{record.remarks || '—'}</td></tr>)}</tbody></table></div>}</section></StudentPage>
}
