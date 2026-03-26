import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { Edit, Plus, ArrowRight, Calendar, Droplet, User } from 'lucide-react'
import { getPatientById } from '../../services/patientService'
import { getConsultationsByPatient } from '../../services/consultationService'
import { GENDER_LABELS, BLOOD_TYPE_LABELS, CONSULTATION_STATUS_LABELS } from '../../utils/constants'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { formatDateTime } from '../../utils/helpers'

export default function PatientDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [patient, setPatient] = useState(null)
  const [consultations, setConsultations] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [pRes, cRes] = await Promise.all([
          getPatientById(id),
          getConsultationsByPatient(id),
        ])
        setPatient(pRes.data)
        setConsultations(cRes.data)
      } catch {
        toast.error('Hasta bilgileri yüklenemedi')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!patient) {
    return <p className="text-text-muted">Hasta bulunamadı.</p>
  }

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">
            {patient.firstName} {patient.lastName}
          </h1>
          <p className="text-text-secondary text-sm mt-1">TC: {patient.nationalId}</p>
        </div>
        <button
          onClick={() => navigate(`/patients/${id}/edit`)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg border border-surface-border bg-surface-card hover:bg-surface-bg text-sm text-text-primary font-medium transition"
        >
          <Edit size={15} />
          Düzenle
        </button>
      </div>

      {/* Info card */}
      <div className="bg-surface-card rounded-xl border border-surface-border p-6">
        <div className="grid grid-cols-2 gap-x-8 gap-y-4">
          <div className="flex items-center gap-2 text-sm">
            <User size={15} className="text-text-muted" />
            <span className="text-text-secondary">Cinsiyet:</span>
            <span className="text-text-primary font-medium">
              {GENDER_LABELS[patient.gender] ?? patient.gender}
            </span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Calendar size={15} className="text-text-muted" />
            <span className="text-text-secondary">Yaş:</span>
            <span className="text-text-primary font-medium">{patient.age}</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Droplet size={15} className="text-text-muted" />
            <span className="text-text-secondary">Kan Grubu:</span>
            <span className="text-text-primary font-medium">
              {BLOOD_TYPE_LABELS[patient.bloodType] ?? patient.bloodType}
            </span>
          </div>
        </div>

        {/* Medical history */}
        <div className="mt-5 pt-5 border-t border-surface-border space-y-3">
          {patient.chronicDiseases?.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-text-secondary uppercase tracking-wide mb-1.5">
                Kronik Hastalıklar
              </p>
              <div className="flex flex-wrap gap-2">
                {patient.chronicDiseases.map((d) => (
                  <span
                    key={d}
                    className="px-2.5 py-1 text-xs rounded-full bg-warning-100 text-warning-600 font-medium"
                  >
                    {d}
                  </span>
                ))}
              </div>
            </div>
          )}
          {patient.allergies?.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-text-secondary uppercase tracking-wide mb-1.5">
                Alerjiler
              </p>
              <div className="flex flex-wrap gap-2">
                {patient.allergies.map((a) => (
                  <span
                    key={a}
                    className="px-2.5 py-1 text-xs rounded-full bg-danger-100 text-danger-600 font-medium"
                  >
                    {a}
                  </span>
                ))}
              </div>
            </div>
          )}
          {patient.currentMedications?.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-text-secondary uppercase tracking-wide mb-1.5">
                Güncel İlaçlar
              </p>
              <div className="flex flex-wrap gap-2">
                {patient.currentMedications.map((m) => (
                  <span
                    key={m}
                    className="px-2.5 py-1 text-xs rounded-full bg-primary-100 text-primary-700 font-medium"
                  >
                    {m}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* New consultation */}
      <button
        onClick={() => navigate(`/consultation/new?patientId=${id}`)}
        className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium transition"
      >
        <Plus size={16} />
        Yeni Konsültasyon Başlat
      </button>

      {/* Consultation history */}
      <div className="bg-surface-card rounded-xl border border-surface-border">
        <div className="px-5 py-4 border-b border-surface-border">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wide">
            Konsültasyon Geçmişi
          </h2>
        </div>
        {consultations.length === 0 ? (
          <div className="py-10 text-center text-text-muted text-sm">
            Henüz konsültasyon bulunmuyor.
          </div>
        ) : (
          <ul className="divide-y divide-surface-border">
            {consultations.map((c) => (
              <li
                key={c.id}
                className="flex items-center justify-between px-5 py-3.5 hover:bg-surface-hover cursor-pointer transition"
                onClick={() => navigate(`/consultation/${c.id}`)}
              >
                <div>
                  <p className="text-sm text-text-primary">{formatDateTime(c.createdAt)}</p>
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded-full mt-1 inline-block ${
                      c.status === 'OPEN'
                        ? 'bg-success-100 text-success-700'
                        : 'bg-surface-border text-text-muted'
                    }`}
                  >
                    {CONSULTATION_STATUS_LABELS[c.status] ?? c.status}
                  </span>
                </div>
                <ArrowRight size={16} className="text-text-muted" />
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
