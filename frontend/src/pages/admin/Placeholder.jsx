import AppLayout from '../../components/layout/AppLayout'

export default function AdminPlaceholder({ title, description }) {
  return <AppLayout><div className="admin-page"><div className="admin-page-heading"><div><span className="eyebrow">Administration</span><h1>{title}</h1><p>{description}</p></div></div><section className="table-panel"><div className="admin-empty large-empty"><strong>This workspace is queued for the next phase.</strong><span>The navigation is ready, but this workflow is intentionally not part of the current admin frontend scope.</span></div></section></div></AppLayout>
}
