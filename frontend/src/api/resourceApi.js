import apiClient from './client'

export function createResourceApi(path) {
  return {
    list: async () => (await apiClient.get(path)).data,
    create: async (payload) => (await apiClient.post(path, payload)).data,
    get: async (id) => (await apiClient.get(`${path}/${id}`)).data,
    update: async (id, payload) => (await apiClient.patch(`${path}/${id}`, payload)).data,
  }
}
