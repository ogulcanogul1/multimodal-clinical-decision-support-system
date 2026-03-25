import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'react-hot-toast'
import { Save, User } from 'lucide-react'
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

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({ resolver: zodResolver(schema) })

  useEffect(() => {
    api
      .get(`/api/doctors/id/${doctor.doctorId}`)
      .then((res) => {
        const d = res.data
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

  const inputClass =
    'w-full px-4 py-2.5 rounded-lg border border-surface-border bg-white text-sm text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition'

  return (
    <div className="max-w-lg space-y-5">
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center">
          <User size={24} className="text-primary-600" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-text-primary">
            Dr. {doctor?.firstName} {doctor?.lastName}
          </h1>
          <p className="text-sm text-text-secondary">{doctor?.email}</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="bg-surface-card rounded-xl border border-surface-border p-6 space-y-4">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wide">
            Profil Bilgileri
          </h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Ad</label>
              <input {...register('firstName')} className={inputClass} />
              {errors.firstName && (
                <p className="text-danger-600 text-xs mt-1">{errors.firstName.message}</p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Soyad</label>
              <input {...register('lastName')} className={inputClass} />
              {errors.lastName && (
                <p className="text-danger-600 text-xs mt-1">{errors.lastName.message}</p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
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
            <label className="block text-sm font-medium text-text-secondary mb-1">
              Lisans Numarası
            </label>
            <input {...register('licenseNumber')} className={inputClass} />
            {errors.licenseNumber && (
              <p className="text-danger-600 text-xs mt-1">{errors.licenseNumber.message}</p>
            )}
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={submitting}
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium transition disabled:opacity-60"
            >
              <Save size={16} />
              {submitting ? 'Kaydediliyor...' : 'Güncelle'}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}
