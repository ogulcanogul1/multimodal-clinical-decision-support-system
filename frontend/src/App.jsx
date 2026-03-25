import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import { useAuth } from './hooks/useAuth'
import ProtectedRoute from './components/layout/ProtectedRoute'
import AppLayout from './components/layout/AppLayout'

import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import DashboardPage from './pages/dashboard/DashboardPage'
import PatientListPage from './pages/patients/PatientListPage'
import PatientFormPage from './pages/patients/PatientFormPage'
import PatientDetailPage from './pages/patients/PatientDetailPage'
import NewConsultationPage from './pages/consultation/NewConsultationPage'
import ConsultationWorkspacePage from './pages/consultation/ConsultationWorkspacePage'
import ProfilePage from './pages/profile/ProfilePage'

function RootRedirect() {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return null
  return <Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-right" toastOptions={{ duration: 4000 }} />
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected routes inside AppLayout */}
          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/patients" element={<PatientListPage />} />
            <Route path="/patients/new" element={<PatientFormPage />} />
            <Route path="/patients/:id/edit" element={<PatientFormPage />} />
            <Route path="/patients/:id" element={<PatientDetailPage />} />
            <Route path="/consultation/new" element={<NewConsultationPage />} />
            <Route path="/consultation/:id" element={<ConsultationWorkspacePage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
