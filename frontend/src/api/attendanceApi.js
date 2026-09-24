import apiClient from './client'

const attendanceApi = {
  assignments: async () => (await apiClient.get('/attendance/assignments')).data,
  sessions: async () => (await apiClient.get('/attendance/sessions')).data,
  session: async (id) => (await apiClient.get(`/attendance/sessions/${id}`)).data,
  createSession: async (payload) => (await apiClient.post('/attendance/sessions', payload)).data,
  records: async (id) => (await apiClient.get(`/attendance/sessions/${id}/records`)).data,
  saveRecords: async (id, records) => (await apiClient.put(`/attendance/sessions/${id}/records`, { records })).data,
  submit: async (id) => (await apiClient.post(`/attendance/sessions/${id}/submit`)).data,
  studentSummary: async () => (await apiClient.get('/attendance/students/me/summary')).data,
  studentHistory: async () => (await apiClient.get('/attendance/students/me/history')).data,
}

export default attendanceApi
