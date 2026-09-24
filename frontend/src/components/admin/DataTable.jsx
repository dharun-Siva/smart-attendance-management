export default function DataTable({ columns, rows, onEdit, onToggle, busy }) {
  if (!rows.length) {
    return <div className="admin-empty"><strong>No records yet</strong><span>Create the first record to see it here.</span></div>
  }

  return (
    <div className="data-table-wrap">
      <table className="data-table">
        <thead><tr>{columns.map((column) => <th key={column.key}>{column.label}</th>)}<th><span className="sr-only">Actions</span></th></tr></thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              {columns.map((column) => <td key={column.key}>{column.render ? column.render(row) : row[column.key] ?? '—'}</td>)}
              <td className="table-actions">
                {onEdit && <button className="text-button" onClick={() => onEdit(row)} disabled={busy}>Edit</button>}
                {onToggle && <button className="text-button muted-action" onClick={() => onToggle(row)} disabled={busy}>{row.is_active ? 'Deactivate' : 'Activate'}</button>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
