import api from './api'

export const getMessages = (consultationId) =>
  api.get(`/api/chat/consultation/${consultationId}`)
export const sendMessage = (consultationId, data) =>
  api.post(`/api/chat/consultation/${consultationId}/send`, data)
