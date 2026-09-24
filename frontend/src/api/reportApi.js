import apiClient from './client'

const reportApi = {
  lowAttendance: async (params = {}) => (await apiClient.get('/reports/low-attendance', { params })).data,
  sectionAttendance: async (id, params = {}) => (await apiClient.get(`/reports/sections/${id}/attendance`, { params })).data,
  subjectAttendance: async (id, params = {}) => (await apiClient.get(`/reports/subjects/${id}/attendance`, { params })).data,
  studentAttendance: async (id, params = {}) => (await apiClient.get(`/reports/students/${id}/attendance`, { params })).data,
}

export default reportApi
