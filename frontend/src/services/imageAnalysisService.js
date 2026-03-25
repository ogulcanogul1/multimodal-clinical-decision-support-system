import api from './api'

export const uploadImage = (formData) =>
  api.post('/api/image-analysis', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
export const getImageAnalyses = (consultationId) =>
  api.get(`/api/image-analysis/consultation/${consultationId}`)
export const giveImageFeedback = (id, isApproved) =>
  api.patch(`/api/image-analysis/${id}/feedback?isApproved=${isApproved}`)
