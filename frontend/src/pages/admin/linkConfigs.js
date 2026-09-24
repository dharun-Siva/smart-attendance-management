import facultyApi from '../../api/facultyApi'
import studentApi from '../../api/studentApi'
import sectionApi from '../../api/sectionApi'
import subjectApi from '../../api/subjectApi'
import enrollmentApi from '../../api/enrollmentApi'
import assignmentApi from '../../api/assignmentApi'

export const enrollmentConfig = {
  title: 'Enrollments', singular: 'Enrollment', description: 'Place each student in the section they currently attend.', api: enrollmentApi,
  fields: [{ name: 'student_id', label: 'Student', type: 'select', source: studentApi, optionLabel: 'student_number' }, { name: 'section_id', label: 'Section', type: 'select', source: sectionApi, optionLabel: 'name' }],
  columns: [{ key: 'student_id', label: 'Student', lookup: 'student_id', lookupLabel: 'student_number' }, { key: 'section_id', label: 'Section', lookup: 'section_id' }, { key: 'is_active', label: 'Status', render: (row) => row.is_active ? 'Active' : 'Inactive' }],
}

export const assignmentConfig = {
  title: 'Faculty assignments', singular: 'Assignment', description: 'Connect faculty, subjects, and sections into teachable units.', api: assignmentApi,
  fields: [{ name: 'faculty_id', label: 'Faculty', type: 'select', source: facultyApi, optionLabel: 'username' }, { name: 'subject_id', label: 'Subject', type: 'select', source: subjectApi, optionLabel: 'name' }, { name: 'section_id', label: 'Section', type: 'select', source: sectionApi, optionLabel: 'name' }],
  columns: [{ key: 'faculty_id', label: 'Faculty', lookup: 'faculty_id', lookupLabel: 'username' }, { key: 'subject_id', label: 'Subject', lookup: 'subject_id' }, { key: 'section_id', label: 'Section', lookup: 'section_id' }, { key: 'is_active', label: 'Status', render: (row) => row.is_active ? 'Active' : 'Inactive' }],
}
