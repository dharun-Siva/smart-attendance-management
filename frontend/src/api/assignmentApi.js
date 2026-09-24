import apiClient from './client'

const assignmentApi = {
  list: async () => (await apiClient.get('/assignments')).data,
  create: async (payload) => (await apiClient.post('/assignments', payload)).data,
  update: async (id, payload) => (await apiClient.patch(`/assignments/${id}`, payload)).data,
  deactivate: async (id) => (await apiClient.post(`/assignments/${id}/deactivate`)).data,
}

export default assignmentApi
