import apiClient from './client'

const enrollmentApi = {
  list: async () => (await apiClient.get('/enrollments')).data,
  create: async (payload) => (await apiClient.post('/enrollments', payload)).data,
  update: async (id, payload) => (await apiClient.patch(`/enrollments/${id}`, payload)).data,
}

export default enrollmentApi
