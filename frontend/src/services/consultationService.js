import api from './api'

export const createConsultation = (data) => api.post('/api/consultations', data)
export const getConsultation = (id) => api.get(`/api/consultations/${id}`)
export const getConsultationsByPatient = (patientId) =>
  api.get(`/api/consultations/patient/${patientId}`)
export const getActiveConsultationsByDoctor = (doctorId) =>
  api.get(`/api/consultations/active/doctor/${doctorId}`)
export const closeConsultation = (id) =>
  api.patch(`/api/consultations/${id}/close`)
