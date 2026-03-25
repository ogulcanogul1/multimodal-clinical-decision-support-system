import api from './api'

export const getPatients = () => api.get('/api/patients')
export const searchByNationalId = (nationalId) =>
  api.get(`/api/patients/search?nationalId=${nationalId}`)
export const getPatientById = (id) => api.get(`/api/patients/id/${id}`)
export const createPatient = (data) => api.post('/api/patients', data)
export const updatePatient = (id, data) => api.put(`/api/patients/${id}`, data)

export const getDiseases = () => api.get('/api/diseases')
export const getAllergies = () => api.get('/api/allergies')
export const getMedications = () => api.get('/api/medications')
