import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8080',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (import.meta.env.DEV) {
      console.error('[API Error]', {
        url: error.config?.url,
        status: error.response?.status,
        errorCode: error.response?.data?.errorCode,
        message: error.response?.data?.message,
      })
    }
    if (error.response?.status === 401) {
      localStorage.removeItem('jwt_token')
      localStorage.removeItem('doctor_info')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
