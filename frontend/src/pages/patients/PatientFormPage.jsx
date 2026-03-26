import { useState, useEffect } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'react-hot-toast'
import { Save, X } from 'lucide-react'
import {
  createPatient,
  updatePatient,
  getPatientById,
  getDiseases,
  getAllergies,
  getMedications,
} from '../../services/patientService'
import { GENDER_LABELS, BLOOD_TYPE_LABELS } from '../../utils/constants'
import { getErrorMessage } from '../../utils/errorHandler'
import LoadingSpinner from '../../components/common/LoadingSpinner'

const schema = z.object({
  nationalId: z
    .string()
    .length(11, 'TC Kimlik No 11 haneli olmalıdır')
    .regex(/^\d+$/, 'Sadece rakam giriniz'),
  firstName: z.string().min(2, 'Ad en az 2 karakter olmalı'),
  lastName: z.string().min(2, 'Soyad en az 2 karakter olmalı'),
  dateOfBirth: z.string().min(1, 'Doğum tarihi zorunludur'),
  gender: z.string().min(1, 'Cinsiyet seçiniz'),
  bloodType: z.string().min(1, 'Kan grubu seçiniz'),
})

function MultiSelect({ label, items, selected, onChange }) {
  function toggle(id) {
    if (selected.includes(id)) {
      onChange(selected.filter((x) => x !== id))
    } else {
      onChange([...selected, id])
    }
  }

  return (
    <div>
      <label className="block text-sm font-medium text-text-secondary mb-2">{label}</label>
      <div className="max-h-36 overflow-y-auto border border-surface-border rounded-lg bg-white divide-y divide-surface-border">
        {items.length === 0 ? (
          <p className="px-3 py-2 text-xs text-text-muted">Yükleniyor...</p>
        ) : (
          items.map((item) => (
            <label
              key={item.id}
              className="flex items-center gap-3 px-3 py-2 hover:bg-surface-hover cursor-pointer"
            >
              <input
                type="checkbox"
                checked={selected.includes(item.id)}
                onChange={() => toggle(item.id)}
                className="rounded border-surface-border text-primary-600 focus:ring-primary-500"
              />
              <span className="text-sm text-text-primary">{item.name}</span>
              {item.icd10Code && (
                <span className="text-xs text-text-muted ml-auto">{item.icd10Code}</span>
              )}
            </label>
          ))
        )}
      </div>
    </div>
  )
}

export default function PatientFormPage() {
  const { id } = useParams()
  const [searchParams] = useSearchParams()
  const editMode = !!id || searchParams.get('edit') === 'true'
  const navigate = useNavigate()

  const [loading, setLoading] = useState(editMode)
  const [dictionaries, setDictionaries] = useState({ diseases: [], allergies: [], medications: [] })
  const [selectedDiseases, setSelectedDiseases] = useState([])
  const [selectedAllergies, setSelectedAllergies] = useState([])
  const [selectedMedications, setSelectedMedications] = useState([])
  const [submitting, setSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({ resolver: zodResolver(schema) })

  useEffect(() => {
    async function load() {
      try {
        const [dRes, aRes, mRes] = await Promise.all([
          getDiseases(),
          getAllergies(),
          getMedications(),
        ])
        setDictionaries({
          diseases: dRes.data,
          allergies: aRes.data,
          medications: mRes.data,
        })

        if (editMode && id) {
          const pRes = await getPatientById(id)
          const p = pRes.data
          reset({
            nationalId: p.nationalId,
            firstName: p.firstName,
            lastName: p.lastName,
            dateOfBirth: p.dateOfBirth,
            gender: p.gender,
            bloodType: p.bloodType,
          })
          // Match names back to IDs
          setSelectedDiseases(
            dRes.data.filter((d) => p.chronicDiseases?.includes(d.name)).map((d) => d.id)
          )
          setSelectedAllergies(
            aRes.data.filter((a) => p.allergies?.includes(a.name)).map((a) => a.id)
          )
          setSelectedMedications(
            mRes.data.filter((m) => p.currentMedications?.includes(m.name)).map((m) => m.id)
          )
        }
      } catch (err) {
        toast.error(getErrorMessage(err))
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [editMode, id, reset])

  async function onSubmit(data) {
    setSubmitting(true)
    const payload = {
      ...data,
      chronicDiseaseIds: selectedDiseases,
      allergyIds: selectedAllergies,
      currentMedicationIds: selectedMedications,
    }
    try {
      if (editMode && id) {
        await updatePatient(id, payload)
        toast.success('Hasta güncellendi')
        navigate(`/patients/${id}`)
      } else {
        const res = await createPatient(payload)
        toast.success('Hasta oluşturuldu')
        navigate(`/patients/${res.data.id}`)
      }
    } catch (err) {
      toast.error(getErrorMessage(err))
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
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-text-primary">
          {editMode ? 'Hasta Düzenle' : 'Yeni Hasta'}
        </h1>
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-text-secondary hover:text-text-primary transition"
        >
          <X size={16} /> İptal
        </button>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <div className="bg-surface-card rounded-xl border border-surface-border p-6 space-y-4">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wide">
            Kimlik Bilgileri
          </h2>

          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
              TC Kimlik No
            </label>
            <input
              {...register('nationalId')}
              placeholder="12345678901"
              maxLength={11}
              className={inputClass}
            />
            {errors.nationalId && (
              <p className="text-danger-600 text-xs mt-1">{errors.nationalId.message}</p>
            )}
          </div>

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
              Doğum Tarihi
            </label>
            <input {...register('dateOfBirth')} type="date" className={inputClass} />
            {errors.dateOfBirth && (
              <p className="text-danger-600 text-xs mt-1">{errors.dateOfBirth.message}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Cinsiyet</label>
              <select {...register('gender')} className={inputClass}>
                <option value="">Seçiniz...</option>
                {Object.entries(GENDER_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>
                    {l}
                  </option>
                ))}
              </select>
              {errors.gender && (
                <p className="text-danger-600 text-xs mt-1">{errors.gender.message}</p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Kan Grubu
              </label>
              <select {...register('bloodType')} className={inputClass}>
                <option value="">Seçiniz...</option>
                {Object.entries(BLOOD_TYPE_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>
                    {l}
                  </option>
                ))}
              </select>
              {errors.bloodType && (
                <p className="text-danger-600 text-xs mt-1">{errors.bloodType.message}</p>
              )}
            </div>
          </div>
        </div>

        {/* Medical history */}
        <div className="bg-surface-card rounded-xl border border-surface-border p-6 space-y-4">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wide">
            Tıbbi Geçmiş
          </h2>
          <MultiSelect
            label="Kronik Hastalıklar"
            items={dictionaries.diseases}
            selected={selectedDiseases}
            onChange={setSelectedDiseases}
          />
          <MultiSelect
            label="Alerjiler"
            items={dictionaries.allergies}
            selected={selectedAllergies}
            onChange={setSelectedAllergies}
          />
          <MultiSelect
            label="Güncel İlaçlar"
            items={dictionaries.medications}
            selected={selectedMedications}
            onChange={setSelectedMedications}
          />
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={submitting}
            className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium transition disabled:opacity-60"
          >
            <Save size={16} />
            {submitting ? 'Kaydediliyor...' : editMode ? 'Güncelle' : 'Hasta Oluştur'}
          </button>
        </div>
      </form>
    </div>
  )
}
