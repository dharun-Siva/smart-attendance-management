import { Navigate, Route, Routes } from 'react-router-dom'
import ProtectedRoute from '../auth/ProtectedRoute'
import Login from '../pages/Login'
import AdminDashboard from '../pages/admin/Dashboard'
import FacultyDashboard from '../pages/faculty/Dashboard'
import StudentDashboard from '../pages/student/Dashboard'
import StudentAttendance from '../pages/student/Attendance'
import StudentHistory from '../pages/student/History'
import StudentProfile from '../pages/student/Profile'
import Departments from '../pages/admin/Departments'
import Classes from '../pages/admin/Classes'
import Sections from '../pages/admin/Sections'
import Subjects from '../pages/admin/Subjects'
import Faculty from '../pages/admin/Faculty'
import Students from '../pages/admin/Students'
import Enrollments from '../pages/admin/Enrollments'
import Assignments from '../pages/admin/Assignments'
import AdminCorrections from '../pages/admin/Corrections'
import AdminReports from '../pages/admin/Reports'
import FacultyAssignments from '../pages/faculty/Assignments'
import TakeAttendance from '../pages/faculty/TakeAttendance'
import AttendanceHistory from '../pages/faculty/AttendanceHistory'
import SessionAttendance from '../pages/faculty/SessionAttendance'
import FacultyCorrections from '../pages/faculty/Corrections'
import FacultyProfile from '../pages/faculty/Profile'

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
        <Route path="/admin/departments" element={<Departments />} />
        <Route path="/admin/classes" element={<Classes />} />
        <Route path="/admin/sections" element={<Sections />} />
        <Route path="/admin/subjects" element={<Subjects />} />
        <Route path="/admin/faculty" element={<Faculty />} />
        <Route path="/admin/students" element={<Students />} />
        <Route path="/admin/enrollments" element={<Enrollments />} />
        <Route path="/admin/assignments" element={<Assignments />} />
        <Route path="/admin/corrections" element={<AdminCorrections />} />
        <Route path="/admin/reports" element={<AdminReports />} />
      </Route>
      <Route element={<ProtectedRoute allowedRoles={['FACULTY']} />}>
        <Route path="/faculty/dashboard" element={<FacultyDashboard />} />
        <Route path="/faculty/assignments" element={<FacultyAssignments />} />
        <Route path="/faculty/attendance/new" element={<TakeAttendance />} />
        <Route path="/faculty/attendance/history" element={<AttendanceHistory />} />
        <Route path="/faculty/attendance/sessions/:sessionId" element={<SessionAttendance />} />
        <Route path="/faculty/corrections" element={<FacultyCorrections />} />
        <Route path="/faculty/profile" element={<FacultyProfile />} />
      </Route>
      <Route element={<ProtectedRoute allowedRoles={['STUDENT']} />}>
        <Route path="/student/dashboard" element={<StudentDashboard />} />
        <Route path="/student/attendance" element={<StudentAttendance />} />
        <Route path="/student/history" element={<StudentHistory />} />
        <Route path="/student/profile" element={<StudentProfile />} />
      </Route>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
