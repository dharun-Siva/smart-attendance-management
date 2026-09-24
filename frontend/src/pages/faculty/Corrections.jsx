import { useEffect, useState } from 'react'
import attendanceApi from '../../api/attendanceApi'
import correctionApi from '../../api/correctionApi'
import { Feedback } from '../../components/admin/Feedback'
import { Empty, FacultyPage, Loading, Status, errorMessage, formatDate } from './common'

export default function FacultyCorrections() {
  const [corrections, setCorrections] = useState(null); const [recordMap, setRecordMap] = useState({}); const [error, setError] = useState('')
  useEffect(() => { Promise.all([correctionApi.list(), attendanceApi.sessions()]).then(async ([loadedCorrections, sessions]) => { const recordLists = await Promise.all(sessions.map((session) => attendanceApi.records(session.id))); const nextMap = {}; recordLists.flat().forEach((record) => { nextMap[record.id] = record }); setRecordMap(nextMap); setCorrections(loadedCorrections) }).catch((requestError) => setError(errorMessage(requestError))) }, [])
  return <FacultyPage title="Correction requests" description="Track the attendance changes you have requested and any administrator review comments."><Feedback>{error}</Feedback><section className="table-panel"><div className="table-panel-heading"><div><span className="eyebrow">Review trail</span><h2>Your correction requests</h2></div><span className="table-status">{corrections?.length || 0} requests</span></div>{corrections === null ? <Loading /> : corrections.length === 0 ? <Empty title="No correction requests">Requests raised from a submitted session will appear here.</Empty> : <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Student</th><th>Previous status</th><th>Requested status</th><th>Reason</th><th>Status</th><th>Created</th><th>Review comment</th></tr></thead><tbody>{corrections.map((item) => <tr key={item.id}><td>{recordMap[item.attendance_record_id]?.student_name || `Record #${item.attendance_record_id}`}</td><td><Status value={item.old_status} /></td><td><Status value={item.new_status} /></td><td>{item.reason}</td><td><Status value={item.status} /></td><td>{formatDate(item.created_at?.slice(0, 10))}</td><td>{item.review_comment || '—'}</td></tr>)}</tbody></table></div>}</section></FacultyPage>
}
