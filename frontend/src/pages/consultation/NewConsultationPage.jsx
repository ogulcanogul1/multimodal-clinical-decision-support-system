import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { ClipboardPlus, Search } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'
import { getPatientById, searchByNationalId } from '../../services/patientService'
import { createConsultation } from '../../services/consultationService'
import { getErrorMessage } from '../../utils/errorHandler'
import { GENDER_LABELS, BLOOD_TYPE_LABELS } from '../../utils/constants'
import LoadingSpinner from '../../components/common/LoadingSpinner'

export default function NewConsultationPage() {
  const { doctor } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const preloadPatientId = searchParams.get('patientId')

  const [patient, setPatient] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searching, setSearching] = useState(false)
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    if (preloadPatientId) {
      getPatientById(preloadPatientId)
        .then((res) => setPatient(res.data))
        .catch((err) => toast.error(getErrorMessage(err)))
    }
  }, [preloadPatientId])

  async function handleSearch() {
    if (!searchQuery || searchQuery.length < 11) {
      toast.error('Lütfen 11 haneli TC Kimlik No giriniz')
      return
    }
    setSearching(true)
    try {
      const res = await searchByNationalId(searchQuery)
      setPatient(res.data)
    } catch (err) {
      toast.error(getErrorMessage(err))
      setPatient(null)
    } finally {
      setSearching(false)
    }
  }

  async function handleCreate() {
    if (!patient) return
    setCreating(true)
    try {
      const res = await createConsultation({
        patientId: patient.id,
        doctorId: doctor.doctorId,
      })
      navigate(`/consultation/${res.data.id}`)
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="max-w-xl space-y-5">
      <h1 className="text-2xl font-bold text-text-primary">Yeni Konsültasyon</h1>

      {/* Search */}
      {!preloadPatientId && (
        <div className="bg-surface-card rounded-xl border border-surface-border p-5">
          <p className="text-sm font-medium text-text-secondary mb-3">TC Kimlik No ile Hasta Ara</p>
          <div className="flex gap-3">
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value.replace(/\D/g, '').slice(0, 11))}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="12345678901"
              className="flex-1 px-4 py-2.5 rounded-lg border border-surface-border bg-white text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
            />
            <button
              onClick={handleSearch}
              disabled={searching}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium transition disabled:opacity-60"
            >
              {searching ? <LoadingSpinner size="sm" /> : <Search size={16} />}
              Ara
            </button>
          </div>
        </div>
      )}

      {/* Patient card */}
      {patient && (
        <div className="bg-surface-card rounded-xl border border-surface-border p-5">
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wide mb-3">
            Seçilen Hasta
          </p>
          <div className="space-y-1">
            <p className="text-lg font-semibold text-text-primary">
              {patient.firstName} {patient.lastName}
            </p>
            <p className="text-sm text-text-secondary">TC: {patient.nationalId}</p>
            <div className="flex gap-4 text-sm text-text-secondary mt-2">
              <span>Yaş: {patient.age}</span>
              <span>{GENDER_LABELS[patient.gender] ?? patient.gender}</span>
              <span>{BLOOD_TYPE_LABELS[patient.bloodType] ?? patient.bloodType}</span>
            </div>
          </div>
        </div>
      )}

      {/* Start button */}
      <button
        onClick={handleCreate}
        disabled={!patient || creating}
        className="flex items-center gap-2 px-6 py-3 rounded-lg bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium transition disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {creating ? <LoadingSpinner size="sm" /> : <ClipboardPlus size={18} />}
        {creating ? 'Oluşturuluyor...' : 'Konsültasyonu Başlat'}
      </button>
    </div>
  )
}
