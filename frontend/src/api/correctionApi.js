import apiClient from './client'

const correctionApi = {
  list: async () => (await apiClient.get('/corrections')).data,
  create: async (recordId, payload) => (await apiClient.post(`/attendance/records/${recordId}/corrections`, payload)).data,
  approve: async (id, payload = {}) => (await apiClient.post(`/corrections/${id}/approve`, payload)).data,
  reject: async (id, payload = {}) => (await apiClient.post(`/corrections/${id}/reject`, payload)).data,
}

export default correctionApi
