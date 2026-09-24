import departmentApi from './departmentApi'
import facultyApi from './facultyApi'
import studentApi from './studentApi'
import reportApi from './reportApi'

export async function getAdminSummary() {
  const [departments, faculty, students, lowAttendance] = await Promise.all([
    departmentApi.list(),
    facultyApi.list(),
    studentApi.list(),
    reportApi.lowAttendance(),
  ])
  return { departments, faculty, students, lowAttendance }
}
