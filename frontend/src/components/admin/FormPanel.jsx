export default function FormPanel({ title, fields, values, onChange, onSubmit, onCancel, submitLabel, busy, error }) {
  return (
    <section className="form-panel">
      <div className="form-panel-heading"><div><span className="eyebrow">Record editor</span><h2>{title}</h2></div><button className="close-button" onClick={onCancel} aria-label="Close form">×</button></div>
      <form onSubmit={onSubmit} className="admin-form">
        <div className="form-grid">
          {fields.map((field) => (
            <label className={field.wide ? 'field-wide' : ''} key={field.name}>
              {field.label}
              {field.type === 'select' ? (
                <select name={field.name} value={values[field.name] ?? ''} onChange={onChange} required={field.required !== false}>
                  <option value="">Select {field.label.toLowerCase()}</option>
                  {field.options.map((option) => <option key={option[field.optionValue || 'id']} value={option[field.optionValue || 'id']}>{option[field.optionLabel || 'name']}</option>)}
                </select>
              ) : field.type === 'checkbox' ? (
                <span className="checkbox-row"><input type="checkbox" name={field.name} checked={Boolean(values[field.name])} onChange={onChange} /> {field.helpText || field.label}</span>
              ) : (
                <input type={field.type || 'text'} name={field.name} value={values[field.name] ?? ''} onChange={onChange} required={field.required !== false} placeholder={field.placeholder || ''} autoComplete={field.type === 'password' ? 'new-password' : 'off'} />
              )}
            </label>
          ))}
        </div>
        {error && <div className="inline-form-error">{error}</div>}
        <div className="form-actions"><button type="button" className="secondary-button" onClick={onCancel}>Cancel</button><button type="submit" className="primary-small-button" disabled={busy}>{busy ? 'Saving...' : submitLabel}</button></div>
      </form>
    </section>
  )
}
