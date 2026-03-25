import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Users, ClipboardList, Plus, Search, ArrowRight } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'
import { getPatients } from '../../services/patientService'
import { getActiveConsultationsByDoctor } from '../../services/consultationService'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { formatDateTime } from '../../utils/helpers'

export default function DashboardPage() {
  const { doctor } = useAuth()
  const navigate = useNavigate()
  const [stats, setStats] = useState({ patients: 0, activeConsultations: 0 })
  const [activeConsultations, setActiveConsultations] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const [patientsRes, consultationsRes] = await Promise.all([
          getPatients(),
          getActiveConsultationsByDoctor(doctor.doctorId),
        ])
        setStats({
          patients: patientsRes.data.length,
          activeConsultations: consultationsRes.data.length,
        })
        setActiveConsultations(consultationsRes.data.slice(0, 5))
      } catch {
        // silent fail — empty state gösterilir
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [doctor.doctorId])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-text-primary">
          Hoşgeldiniz, Dr. {doctor?.firstName} {doctor?.lastName}
        </h1>
        <p className="text-text-secondary mt-1 text-sm">Bugünkü özet bilgileriniz aşağıda.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 max-w-md">
        <div className="bg-surface-card rounded-xl border border-surface-border p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-9 h-9 rounded-lg bg-primary-100 flex items-center justify-center">
              <ClipboardList size={18} className="text-primary-600" />
            </div>
            <span className="text-sm text-text-secondary">Aktif Konsültasyon</span>
          </div>
          <p className="text-3xl font-bold text-text-primary">{stats.activeConsultations}</p>
        </div>

        <div className="bg-surface-card rounded-xl border border-surface-border p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-9 h-9 rounded-lg bg-success-100 flex items-center justify-center">
              <Users size={18} className="text-success-600" />
            </div>
            <span className="text-sm text-text-secondary">Toplam Hasta</span>
          </div>
          <p className="text-3xl font-bold text-text-primary">{stats.patients}</p>
        </div>
      </div>

      {/* Quick actions */}
      <div className="bg-surface-card rounded-xl border border-surface-border p-5">
        <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-4">
          Hızlı İşlemler
        </h2>
        <div className="flex flex-wrap gap-3">
          <Link
            to="/consultation/new"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium transition"
          >
            <Plus size={16} />
            Yeni Konsültasyon
          </Link>
          <Link
            to="/patients/new"
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-surface-border bg-surface-card hover:bg-surface-bg text-text-primary text-sm font-medium transition"
          >
            <Plus size={16} />
            Yeni Hasta
          </Link>
          <Link
            to="/patients"
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-surface-border bg-surface-card hover:bg-surface-bg text-text-primary text-sm font-medium transition"
          >
            <Search size={16} />
            Hasta Ara
          </Link>
        </div>
      </div>

      {/* Active consultations */}
      <div className="bg-surface-card rounded-xl border border-surface-border">
        <div className="px-5 py-4 border-b border-surface-border">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wide">
            Aktif Konsültasyonlar
          </h2>
        </div>
        {activeConsultations.length === 0 ? (
          <div className="px-5 py-8 text-center text-text-muted text-sm">
            Aktif konsültasyon bulunmuyor.
          </div>
        ) : (
          <ul className="divide-y divide-surface-border">
            {activeConsultations.map((c) => (
              <li key={c.id} className="flex items-center justify-between px-5 py-3.5">
                <div>
                  <p className="text-sm font-medium text-text-primary">
                    {c.patientFullName}
                  </p>
                  <p className="text-xs text-text-muted">{formatDateTime(c.createdAt)}</p>
                </div>
                <button
                  onClick={() => navigate(`/consultation/${c.id}`)}
                  className="flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 font-medium"
                >
                  Git <ArrowRight size={14} />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
