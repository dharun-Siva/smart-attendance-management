import { useEffect, useMemo, useState } from 'react'
import DataTable from './DataTable'
import FormPanel from './FormPanel'
import { Feedback, LoadingState } from './Feedback'
import { getApiErrorMessage } from '../../utils/apiError'
import AppLayout from '../layout/AppLayout'

function emptyValues(fields) {
  return fields.reduce((result, field) => ({ ...result, [field.name]: field.type === 'checkbox' ? true : '' }), {})
}

function formValues(fields, record) {
  return fields.reduce((result, field) => ({ ...result, [field.name]: record[field.name] ?? (field.type === 'checkbox' ? true : '') }), {})
}

export default function ResourcePage({ config }) {
  const [rows, setRows] = useState([])
  const [options, setOptions] = useState({})
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [editing, setEditing] = useState(null)
  const [notice, setNotice] = useState(null)
  const [formError, setFormError] = useState('')

  const sourceFields = useMemo(() => config.fields.filter((field) => field.source), [config.fields])

  async function load() {
    setIsLoading(true)
    try {
      const [records, ...sourceResults] = await Promise.all([
        config.api.list(),
        ...sourceFields.map((field) => field.source.list()),
      ])
      const nextOptions = {}
      sourceFields.forEach((field, index) => { nextOptions[field.name] = sourceResults[index] })
      setRows(records)
      setOptions(nextOptions)
    } catch (error) {
      setNotice({ type: 'error', message: getApiErrorMessage(error) })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => { load() }, [config])

  function beginCreate() {
    setEditing({ record: null, values: emptyValues(config.fields) })
    setFormError('')
    setNotice(null)
  }

  function beginEdit(record) {
    setEditing({ record, values: formValues(config.fields, record) })
    setFormError('')
    setNotice(null)
  }

  function handleChange(event) {
    const { name, value, type, checked } = event.target
    setEditing((current) => ({ ...current, values: { ...current.values, [name]: type === 'checkbox' ? checked : value } }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setIsSaving(true)
    setFormError('')
    try {
      const payload = { ...editing.values }
      config.fields.forEach((field) => {
        if (field.type === 'select' && payload[field.name] !== '') payload[field.name] = Number(payload[field.name])
        if (field.type === 'password' && !payload[field.name]) delete payload[field.name]
      })
      if (editing.record) await config.api.update(editing.record.id, payload)
      else await config.api.create(payload)
      setEditing(null)
      setNotice({ type: 'success', message: `${config.singular} ${editing.record ? 'updated' : 'created'} successfully.` })
      await load()
    } catch (error) {
      setFormError(getApiErrorMessage(error))
    } finally {
      setIsSaving(false)
    }
  }

  async function toggleActive(record) {
    if (!window.confirm(`${record.is_active ? 'Deactivate' : 'Activate'} this ${config.singular.toLowerCase()}?`)) return
    try {
      await config.api.update(record.id, { is_active: !record.is_active })
      setNotice({ type: 'success', message: `${config.singular} status updated.` })
      await load()
    } catch (error) {
      setNotice({ type: 'error', message: getApiErrorMessage(error) })
    }
  }

  const resolvedFields = config.fields.map((field) => ({ ...field, options: options[field.name] || field.options || [] }))

  return (
    <AppLayout><div className="admin-page">
      <div className="admin-page-heading"><div><span className="eyebrow">Administration</span><h1>{config.title}</h1><p>{config.description}</p></div><button className="primary-small-button" onClick={beginCreate}>+ Add {config.singular}</button></div>
      <Feedback type={notice?.type} onDismiss={() => setNotice(null)}>{notice?.message}</Feedback>
      {editing && <FormPanel title={`${editing.record ? 'Edit' : 'New'} ${config.singular}`} fields={resolvedFields} values={editing.values} onChange={handleChange} onSubmit={handleSubmit} onCancel={() => setEditing(null)} submitLabel={editing.record ? 'Save changes' : `Create ${config.singular}`} busy={isSaving} error={formError} />}
      <section className="table-panel"><div className="table-panel-heading"><div><span className="eyebrow">Directory</span><h2>{rows.length} {config.title.toLowerCase()}</h2></div>{isLoading && <span className="table-status">Syncing...</span>}</div>{isLoading ? <LoadingState /> : <DataTable columns={config.columns} rows={rows} onEdit={beginEdit} onToggle={config.allowToggle ? toggleActive : null} busy={isSaving} />}</section>
    </div></AppLayout>
  )
}
