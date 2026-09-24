import apiClient from './client'

const reportApi = {
  lowAttendance: async (params = {}) => (await apiClient.get('/reports/low-attendance', { params })).data,
}

export default reportApi
