import api from './api'

export const uploadDocument = (formData) =>
  api.post('/api/document-analysis', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
export const getDocumentAnalyses = (consultationId) =>
  api.get(`/api/document-analysis/consultation/${consultationId}`)
export const giveDocumentFeedback = (id, isApproved) =>
  api.patch(`/api/document-analysis/${id}/feedback?isApproved=${isApproved}`)
