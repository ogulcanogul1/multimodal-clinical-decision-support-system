import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'react-hot-toast'
import { Save, Stethoscope, IdCard } from 'lucide-react'
import api from '../../services/api'
import { useAuth } from '../../hooks/useAuth'
import { SPECIALTY_LABELS } from '../../utils/constants'
import LoadingSpinner from '../../components/common/LoadingSpinner'

const schema = z.object({
  firstName: z.string().min(2, 'Ad en az 2 karakter olmalı'),
  lastName: z.string().min(2, 'Soyad en az 2 karakter olmalı'),
  specialty: z.string().min(1, 'Uzmanlık seçiniz'),
  licenseNumber: z.string().min(1, 'Lisans numarası zorunludur'),
})

export default function ProfilePage() {
  const { doctor } = useAuth()
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [specialty, setSpecialty] = useState('')

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm({ resolver: zodResolver(schema) })

  const watchedSpecialty = watch('specialty')

  useEffect(() => {
    api
      .get(`/api/doctors/id/${doctor.doctorId}`)
      .then((res) => {
        const d = res.data
        setSpecialty(d.specialty)
        reset({
          firstName: d.firstName,
          lastName: d.lastName,
          specialty: d.specialty,
          licenseNumber: d.licenseNumber,
        })
      })
      .catch(() => toast.error('Profil bilgileri yüklenemedi'))
      .finally(() => setLoading(false))
  }, [doctor.doctorId, reset])

  useEffect(() => {
    if (watchedSpecialty) setSpecialty(watchedSpecialty)
  }, [watchedSpecialty])

  async function onSubmit(data) {
    setSubmitting(true)
    try {
      await api.put(`/api/doctors/${doctor.doctorId}`, data)
      toast.success('Profil güncellendi')
    } catch {
      toast.error('Güncelleme sırasında bir hata oluştu')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  const initials = `${doctor?.firstName?.[0] ?? ''}${doctor?.lastName?.[0] ?? ''}`.toUpperCase()
  const specialtyLabel = SPECIALTY_LABELS[specialty] ?? specialty

  const inputClass =
    'w-full px-4 py-2.5 rounded-lg border border-surface-border bg-white text-sm text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition'

  return (
    <div className="space-y-5">

      {/* Hero Banner */}
      <div className="rounded-2xl overflow-hidden bg-gradient-to-br from-primary-600 to-primary-800 shadow-lg">
        <div className="px-8 py-8 flex items-center gap-6">
          <div className="w-20 h-20 rounded-full bg-white/20 border-4 border-white/40 flex items-center justify-center flex-shrink-0 shadow-inner">
            <span className="text-2xl font-bold text-white tracking-wide">{initials || 'DR'}</span>
          </div>
          <div className="min-w-0">
            <h1 className="text-2xl font-bold text-white leading-tight">
              Dr. {doctor?.firstName} {doctor?.lastName}
            </h1>
            <p className="text-primary-200 text-sm mt-0.5">{doctor?.email}</p>
            {specialtyLabel && (
              <span className="inline-flex items-center gap-1.5 mt-2 px-3 py-1 rounded-full bg-white/15 text-white text-xs font-medium border border-white/20">
                <Stethoscope size={12} />
                {specialtyLabel}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Edit Form */}
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="bg-surface-card rounded-2xl border border-surface-border shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-surface-border flex items-center gap-2">
            <IdCard size={16} className="text-primary-500" />
            <h2 className="text-sm font-semibold text-text-primary">Profil Bilgilerini Düzenle</h2>
          </div>

          <div className="p-6 space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1.5">Ad</label>
                <input {...register('firstName')} className={inputClass} placeholder="Adınız" />
                {errors.firstName && (
                  <p className="text-danger-600 text-xs mt-1">{errors.firstName.message}</p>
                )}
              </div>
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1.5">Soyad</label>
                <input {...register('lastName')} className={inputClass} placeholder="Soyadınız" />
                {errors.lastName && (
                  <p className="text-danger-600 text-xs mt-1">{errors.lastName.message}</p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1.5">
                Uzmanlık Alanı
              </label>
              <select {...register('specialty')} className={inputClass}>
                <option value="">Seçiniz...</option>
                {Object.entries(SPECIALTY_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
              {errors.specialty && (
                <p className="text-danger-600 text-xs mt-1">{errors.specialty.message}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1.5">
                Lisans Numarası
              </label>
              <input {...register('licenseNumber')} className={inputClass} placeholder="Lisans numaranız" />
              {errors.licenseNumber && (
                <p className="text-danger-600 text-xs mt-1">{errors.licenseNumber.message}</p>
              )}
            </div>
          </div>

          <div className="px-6 py-4 border-t border-surface-border bg-surface-hover flex justify-end">
            <button
              type="submit"
              disabled={submitting}
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-primary-600 hover:bg-primary-700 active:bg-primary-800 text-white text-sm font-medium transition disabled:opacity-60 shadow-sm"
            >
              <Save size={15} />
              {submitting ? 'Kaydediliyor...' : 'Değişiklikleri Kaydet'}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}
