import { useAuth } from '../../auth/AuthContext'
import { FacultyPage } from './common'

export default function FacultyProfile() {
  const { user } = useAuth()
  return <FacultyPage title="Profile" description="Your signed-in faculty account and access context."><section className="profile-grid"><div className="profile-identity"><span className="avatar profile-avatar">{user?.username?.slice(0, 2).toUpperCase()}</span><div><span className="eyebrow">Faculty account</span><h2>{user?.username}</h2><p>Access is limited to the assignments and attendance sessions owned by this account.</p></div></div><div className="table-panel profile-details"><div><span className="eyebrow">Account details</span><h2>Access profile</h2></div><dl><div><dt>Username</dt><dd>{user?.username || '—'}</dd></div><div><dt>Role</dt><dd>{user?.role || '—'}</dd></div><div><dt>User ID</dt><dd>{user?.id || '—'}</dd></div></dl></div></section></FacultyPage>
}
