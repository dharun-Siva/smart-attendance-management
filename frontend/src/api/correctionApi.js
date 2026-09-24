import apiClient from './client'

const correctionApi = {
  list: async () => (await apiClient.get('/corrections')).data,
  create: async (recordId, payload) => (await apiClient.post(`/attendance/records/${recordId}/corrections`, payload)).data,
}

export default correctionApi
