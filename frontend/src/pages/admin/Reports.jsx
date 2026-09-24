import { useEffect, useState } from 'react'
import AppLayout from '../../components/layout/AppLayout'
import { Feedback, LoadingState } from '../../components/admin/Feedback'
import { getApiErrorMessage } from '../../utils/apiError'
import reportApi from '../../api/reportApi'
import departmentApi from '../../api/departmentApi'
import classApi from '../../api/classApi'
import sectionApi from '../../api/sectionApi'
import subjectApi from '../../api/subjectApi'
import studentApi from '../../api/studentApi'

const tabs = [
  ['low', 'Low attendance'],
  ['section', 'Section attendance'],
  ['subject', 'Subject attendance'],
  ['student', 'Student attendance'],
]

function StatusBadge({ low }) {
  return <span className={`status-badge ${low ? 'status-absent' : 'status-present'}`}>{low ? 'LOW' : 'GOOD'}</span>
}

function ReportTable({ rows, mode, catalogs }) {
  if (!rows.length) return <div className="admin-empty large-empty"><strong>No report data</strong><span>There are no submitted attendance records for the selected filters.</span></div>
  const find = (items, id, field = 'name') => catalogs[items]?.find((item) => item.id === id)?.[field] || '—'
  return <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Student</th><th>Student number</th>{mode === 'low' && <><th>Department</th><th>Section</th></>}{mode !== 'low' && <th>Subject</th>}<th>Attended</th><th>Qualifying</th><th>Attendance</th><th>Status</th></tr></thead><tbody>{rows.map((row) => <tr key={`${row.student_id}-${row.subject_id || mode}`}><td>{row.student_name}</td><td>{row.student_number}</td>{mode === 'low' && <><td>{find('departments', row.department_id)}</td><td>{find('sections', row.section_id)}</td></>}{mode !== 'low' && <td>{row.subject_id ? find('subjects', row.subject_id) : 'All subjects'}</td>}<td>{row.attended_sessions}</td><td>{row.qualifying_sessions}</td><td>{row.attendance_percentage}%</td><td><StatusBadge low={row.attendance_percentage < (catalogs.threshold ?? 75)} /></td></tr>)}</tbody></table></div>
}

export default function AdminReports() {
  const [tab, setTab] = useState('low')
  const [catalogs, setCatalogs] = useState({ departments: [], classes: [], sections: [], subjects: [], students: [], threshold: 75 })
  const [selectedId, setSelectedId] = useState('')
  const [threshold, setThreshold] = useState('75')
  const [dates, setDates] = useState({ start_date: '', end_date: '' })
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadingCatalogs, setLoadingCatalogs] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([departmentApi.list(), classApi.list(), sectionApi.list(), subjectApi.list(), studentApi.list()])
      .then(([departments, classes, sections, subjects, students]) => setCatalogs((current) => ({ ...current, departments, classes, sections, subjects, students })))
      .catch((requestError) => setError(getApiErrorMessage(requestError)))
      .finally(() => setLoadingCatalogs(false))
  }, [])

  async function loadReport(nextTab = tab, nextId = selectedId) {
    setLoading(true); setError('')
    const params = Object.fromEntries(Object.entries(dates).filter(([, value]) => value))
    try {
      let result
      if (nextTab === 'low') result = await reportApi.lowAttendance({ ...params, threshold: Number(threshold) })
      else if (!nextId) { setRows([]); setLoading(false); return }
      else if (nextTab === 'section') result = await reportApi.sectionAttendance(nextId, params)
      else if (nextTab === 'subject') result = await reportApi.subjectAttendance(nextId, params)
      else result = await reportApi.studentAttendance(nextId, params)
      setRows(result)
    } catch (requestError) { setError(getApiErrorMessage(requestError)); setRows([]) } finally { setLoading(false) }
  }

  useEffect(() => { loadReport('low', '') }, [])

  function changeTab(nextTab) { setTab(nextTab); setSelectedId(''); setRows([]); if (nextTab === 'low') loadReport(nextTab, '') }
  function selectedLabel() { if (tab === 'section') return 'Section'; if (tab === 'subject') return 'Subject'; return 'Student' }
  const options = tab === 'section' ? catalogs.sections : tab === 'subject' ? catalogs.subjects : catalogs.students

  return <AppLayout><div className="admin-page">
    <div className="admin-page-heading"><div><span className="eyebrow">Administration</span><h1>Reports</h1><p>Explore attendance health using submitted records and backend-calculated percentages.</p></div></div>
    <Feedback>{error}</Feedback>
    <div className="report-tabs" role="tablist">{tabs.map(([value, label]) => <button key={value} className={`report-tab ${tab === value ? 'active' : ''}`} onClick={() => changeTab(value)} role="tab" aria-selected={tab === value}>{label}</button>)}</div>
    <section className="form-panel report-filters"><div className="form-panel-heading"><div><span className="eyebrow">Report filters</span><h2>{tab === 'low' ? 'Threshold and date range' : `${selectedLabel()} report filters`}</h2></div></div><div className="admin-form"><div className="form-grid">{tab === 'low' ? <label>Minimum attendance threshold (%)<input type="number" min="0" max="100" step="0.01" value={threshold} onChange={(event) => setThreshold(event.target.value)} /></label> : <label>{selectedLabel()}<select value={selectedId} onChange={(event) => setSelectedId(event.target.value)} disabled={loadingCatalogs}><option value="">Select {selectedLabel().toLowerCase()}</option>{options.map((item) => <option key={item.id} value={item.id}>{tab === 'section' ? `${item.name} · ${catalogs.classes.find((classItem) => classItem.id === item.class_id)?.name || 'Class'}` : tab === 'student' ? `${item.student_number} · ${item.first_name} ${item.last_name}` : `${item.name} · ${item.code}`}</option>)}</select></label>}<label>Start date <span className="field-optional">optional</span><input type="date" value={dates.start_date} onChange={(event) => setDates({ ...dates, start_date: event.target.value })} /></label><label>End date <span className="field-optional">optional</span><input type="date" value={dates.end_date} onChange={(event) => setDates({ ...dates, end_date: event.target.value })} /></label></div><div className="form-actions"><button className="primary-small-button" onClick={() => loadReport()} disabled={loading || (tab !== 'low' && !selectedId)}>{loading ? 'Loading...' : 'Run report'} <span aria-hidden="true">→</span></button></div></div></section>
    <section className="table-panel"><div className="table-panel-heading"><div><span className="eyebrow">Attendance analysis</span><h2>{tabs.find(([value]) => value === tab)?.[1]}</h2></div>{loading && <span className="table-status">Loading...</span>}</div>{loading ? <LoadingState /> : <ReportTable rows={rows} mode={tab} catalogs={{ ...catalogs, threshold: Number(threshold) }} />}</section>
  </div></AppLayout>
}
