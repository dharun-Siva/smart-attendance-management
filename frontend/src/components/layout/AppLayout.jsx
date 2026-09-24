import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext'

const roleLabels = {
  ADMIN: 'Administrator',
  FACULTY: 'Faculty member',
  STUDENT: 'Student',
}

export default function AppLayout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [isAccountMenuOpen, setIsAccountMenuOpen] = useState(false)
  const role = user?.role?.toLowerCase()
  const initials = user?.username?.slice(0, 2).toUpperCase() || 'SC'
  const adminNavigation = [
    ['Dashboard', '/admin/dashboard', '01'],
    ['Departments', '/admin/departments', '02'],
    ['Classes', '/admin/classes', '03'],
    ['Sections', '/admin/sections', '04'],
    ['Subjects', '/admin/subjects', '05'],
    ['Faculty', '/admin/faculty', '06'],
    ['Students', '/admin/students', '07'],
    ['Enrollments', '/admin/enrollments', '08'],
    ['Faculty assignments', '/admin/assignments', '09'],
    ['Corrections', '/admin/corrections', '10'],
    ['Reports', '/admin/reports', '11'],
  ]
  const facultyNavigation = [
    ['Dashboard', '/faculty/dashboard', '01'],
    ['My assignments', '/faculty/assignments', '02'],
    ['Take attendance', '/faculty/attendance/new', '03'],
    ['Attendance history', '/faculty/attendance/history', '04'],
    ['Correction requests', '/faculty/corrections', '05'],
    ['Profile', '/faculty/profile', '06'],
  ]
  const studentNavigation = [
    ['Dashboard', '/student/dashboard', '01'],
    ['My attendance', '/student/attendance', '02'],
    ['Attendance history', '/student/history', '03'],
    ['Profile', '/student/profile', '04'],
  ]
  const navigation = role === 'admin' ? adminNavigation : role === 'faculty' ? facultyNavigation : role === 'student' ? studentNavigation : [['Overview', `/${role}/dashboard`, '01']]

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="app-shell" onClick={() => setIsAccountMenuOpen(false)}>
      <aside className="sidebar">
        <div className="brand-lockup">
          <div className="brand-mark">CR</div>
          <div>
            <strong>Campus Rollcall</strong>
            <span>Attendance command center</span>
          </div>
        </div>

        <div className="sidebar-section-label">Workspace</div>
        <nav className="sidebar-nav" aria-label="Primary navigation">
          {navigation.map(([label, path, index]) => <NavLink key={path} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} to={path}><span className="nav-icon">{index}</span>{label}</NavLink>)}
        </nav>

        <div className="sidebar-footer">
          <div className="status-pill"><span /> System foundation online</div>
          <button className="logout-button" onClick={handleLogout}>Sign out</button>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div>
            <span className="topbar-kicker">Academic operations</span>
            <p className="topbar-title">{roleLabels[user?.role] || 'Workspace'}</p>
          </div>
          <div className="account-menu" onClick={(event) => event.stopPropagation()}>
            <button className="user-chip" type="button" aria-expanded={isAccountMenuOpen} aria-haspopup="menu" onClick={() => setIsAccountMenuOpen((current) => !current)} onKeyDown={(event) => { if (event.key === 'Escape') setIsAccountMenuOpen(false) }}>
            <span className="avatar">{initials}</span>
            <span>
              <strong>{user?.username}</strong>
              <small>{user?.role}</small>
            </span>
            </button>
            {isAccountMenuOpen && <div className="account-dropdown" role="menu"><button type="button" role="menuitem" onClick={handleLogout}>Sign out</button></div>}
          </div>
        </header>
        <div className="page-content">{children}</div>
      </main>
    </div>
  )
}
