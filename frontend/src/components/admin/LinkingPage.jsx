import { useEffect, useState } from 'react'
import DataTable from './DataTable'
import FormPanel from './FormPanel'
import { Feedback, LoadingState } from './Feedback'
import { getApiErrorMessage } from '../../utils/apiError'
import AppLayout from '../layout/AppLayout'

export default function LinkingPage({ config }) {
  const [rows, setRows] = useState([])
  const [options, setOptions] = useState({})
  const [form, setForm] = useState(null)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState(null)

  async function load() {
    setLoading(true)
    try {
      const [records, ...sources] = await Promise.all([config.api.list(), ...config.fields.map((field) => field.source.list())])
      const nextOptions = {}
      config.fields.forEach((field, index) => { nextOptions[field.name] = sources[index] })
      setRows(records)
      setOptions(nextOptions)
    } catch (error) { setNotice({ type: 'error', message: getApiErrorMessage(error) }) } finally { setLoading(false) }
  }

  useEffect(() => { load() }, [config])

  function openForm() {
    setNotice(null)
    setForm({ values: config.fields.reduce((result, field) => ({ ...result, [field.name]: '' }), {}), error: '' })
  }

  function onChange(event) {
    setForm((current) => ({ ...current, values: { ...current.values, [event.target.name]: event.target.value } }))
  }

  async function onSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setForm((current) => ({ ...current, error: '' }))
    try {
      const payload = Object.fromEntries(Object.entries(form.values).map(([key, value]) => [key, Number(value)]))
      await config.api.create(payload)
      setForm(null)
      setNotice({ type: 'success', message: `${config.singular} created successfully.` })
      await load()
    } catch (error) { setForm((current) => ({ ...current, error: getApiErrorMessage(error) })) } finally { setBusy(false) }
  }

  async function deactivate(row) {
    if (!window.confirm(`Deactivate this ${config.singular.toLowerCase()}?`)) return
    try {
      await config.api.deactivate(row.id)
      setNotice({ type: 'success', message: `${config.singular} deactivated.` })
      await load()
    } catch (error) { setNotice({ type: 'error', message: getApiErrorMessage(error) }) }
  }

  const fields = config.fields.map((field) => ({ ...field, options: options[field.name] || [] }))
  const lookup = (field, value, label = 'name') => (options[field]?.find((item) => item.id === value)?.[label] || value)

  return <AppLayout><div className="admin-page">
    <div className="admin-page-heading"><div><span className="eyebrow">Administration</span><h1>{config.title}</h1><p>{config.description}</p></div><button className="primary-small-button" onClick={openForm}>+ Add {config.singular}</button></div>
    <Feedback type={notice?.type} onDismiss={() => setNotice(null)}>{notice?.message}</Feedback>
    {form && <FormPanel title={`New ${config.singular}`} fields={fields} values={form.values} onChange={onChange} onSubmit={onSubmit} onCancel={() => setForm(null)} submitLabel={`Create ${config.singular}`} busy={busy} error={form.error} />}
    <section className="table-panel"><div className="table-panel-heading"><div><span className="eyebrow">Directory</span><h2>{rows.length} {config.title.toLowerCase()}</h2></div></div>{loading ? <LoadingState /> : <DataTable columns={config.columns.map((column) => column.lookup ? { ...column, render: (row) => lookup(column.lookup, row[column.key], column.lookupLabel) } : column)} rows={rows} onToggle={config.api.deactivate ? deactivate : null} busy={busy} />}</section>
  </div></AppLayout>
}
