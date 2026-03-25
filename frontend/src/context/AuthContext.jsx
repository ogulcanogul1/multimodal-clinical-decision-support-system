import { createContext, useState, useEffect } from 'react'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [doctor, setDoctor] = useState(null)
  const [token, setToken] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const savedToken = localStorage.getItem('jwt_token')
    const savedDoctor = localStorage.getItem('doctor_info')
    if (savedToken && savedDoctor) {
      setToken(savedToken)
      setDoctor(JSON.parse(savedDoctor))
      setIsAuthenticated(true)
    }
    setLoading(false)
  }, [])

  function login(authResponse) {
    const doctorInfo = {
      doctorId: authResponse.doctorId,
      email: authResponse.email,
      firstName: authResponse.firstName,
      lastName: authResponse.lastName,
    }
    localStorage.setItem('jwt_token', authResponse.token)
    localStorage.setItem('doctor_info', JSON.stringify(doctorInfo))
    setToken(authResponse.token)
    setDoctor(doctorInfo)
    setIsAuthenticated(true)
  }

  function logout() {
    localStorage.removeItem('jwt_token')
    localStorage.removeItem('doctor_info')
    setToken(null)
    setDoctor(null)
    setIsAuthenticated(false)
    window.location.href = '/login'
  }

  return (
    <AuthContext.Provider value={{ doctor, token, isAuthenticated, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
