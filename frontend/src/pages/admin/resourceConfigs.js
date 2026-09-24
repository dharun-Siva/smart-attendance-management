import departmentApi from '../../api/departmentApi'
import classApi from '../../api/classApi'
import sectionApi from '../../api/sectionApi'
import subjectApi from '../../api/subjectApi'
import facultyApi from '../../api/facultyApi'
import studentApi from '../../api/studentApi'

export const departmentConfig = {
  title: 'Departments', singular: 'Department', description: 'Organize academic ownership across the college.', api: departmentApi, allowToggle: true,
  fields: [
    { name: 'name', label: 'Department name', required: true },
    { name: 'code', label: 'Short code', required: true, placeholder: 'e.g. CSE' },
    { name: 'is_active', label: 'Active', type: 'checkbox', required: false, helpText: 'Department is active' },
  ],
  columns: [{ key: 'name', label: 'Name' }, { key: 'code', label: 'Code' }, { key: 'is_active', label: 'Status', render: (row) => row.is_active ? 'Active' : 'Inactive' }],
}

export const classConfig = {
  title: 'Classes', singular: 'Class', description: 'Maintain the programs and class groups that shape enrollment.', api: classApi, allowToggle: true,
  fields: [
    { name: 'department_id', label: 'Department', type: 'select', source: departmentApi, optionLabel: 'name' },
    { name: 'name', label: 'Class name' }, { name: 'code', label: 'Class code' },
    { name: 'is_active', label: 'Active', type: 'checkbox', required: false, helpText: 'Class is active' },
  ],
  columns: [{ key: 'name', label: 'Class' }, { key: 'code', label: 'Code' }, { key: 'department_id', label: 'Department ID' }, { key: 'is_active', label: 'Status', render: (row) => row.is_active ? 'Active' : 'Inactive' }],
}

export const sectionConfig = {
  title: 'Sections', singular: 'Section', description: 'Break classes into the sections faculty and students actually use.', api: sectionApi, allowToggle: true,
  fields: [
    { name: 'class_id', label: 'Class', type: 'select', source: classApi, optionLabel: 'name' }, { name: 'name', label: 'Section name' },
    { name: 'is_active', label: 'Active', type: 'checkbox', required: false, helpText: 'Section is active' },
  ],
  columns: [{ key: 'name', label: 'Section' }, { key: 'class_id', label: 'Class ID' }, { key: 'is_active', label: 'Status', render: (row) => row.is_active ? 'Active' : 'Inactive' }],
}

export const subjectConfig = {
  title: 'Subjects', singular: 'Subject', description: 'Keep the subject catalogue ready for assignment and attendance.', api: subjectApi, allowToggle: true,
  fields: [
    { name: 'department_id', label: 'Department', type: 'select', source: departmentApi, optionLabel: 'name' }, { name: 'name', label: 'Subject name' }, { name: 'code', label: 'Subject code' },
    { name: 'is_active', label: 'Active', type: 'checkbox', required: false, helpText: 'Subject is active' },
  ],
  columns: [{ key: 'name', label: 'Subject' }, { key: 'code', label: 'Code' }, { key: 'department_id', label: 'Department ID' }, { key: 'is_active', label: 'Status', render: (row) => row.is_active ? 'Active' : 'Inactive' }],
}

const accountFields = [
  { name: 'username', label: 'Username' }, { name: 'email', label: 'Email', type: 'email' }, { name: 'password', label: 'Password', type: 'password', required: false, placeholder: 'Set only when creating or changing' },
  { name: 'first_name', label: 'First name' }, { name: 'last_name', label: 'Last name' }, { name: 'department_id', label: 'Department', type: 'select', source: departmentApi, optionLabel: 'name' },
  { name: 'is_active', label: 'Active', type: 'checkbox', required: false, helpText: 'Account is active' },
]

export const facultyConfig = {
  title: 'Faculty', singular: 'Faculty member', description: 'Manage teaching accounts and their department homes.', api: facultyApi, allowToggle: true,
  fields: [...accountFields, { name: 'employee_number', label: 'Employee number' }],
  columns: [{ key: 'first_name', label: 'Name', render: (row) => `${row.first_name} ${row.last_name}` }, { key: 'employee_number', label: 'Employee no.' }, { key: 'username', label: 'Username' }, { key: 'department_id', label: 'Department ID' }, { key: 'is_active', label: 'Status', render: (row) => row.is_active ? 'Active' : 'Inactive' }],
}

export const studentConfig = {
  title: 'Students', singular: 'Student', description: 'Maintain student identities without exposing account passwords.', api: studentApi, allowToggle: true,
  fields: [...accountFields, { name: 'student_number', label: 'Student number' }],
  columns: [{ key: 'first_name', label: 'Name', render: (row) => `${row.first_name} ${row.last_name}` }, { key: 'student_number', label: 'Student no.' }, { key: 'username', label: 'Username' }, { key: 'department_id', label: 'Department ID' }, { key: 'is_active', label: 'Status', render: (row) => row.is_active ? 'Active' : 'Inactive' }],
}

