import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { UserPlus, Stethoscope } from 'lucide-react'
import { register as registerUser } from '../../services/authService'
import { useAuth } from '../../hooks/useAuth'
import { SPECIALTY_LABELS } from '../../utils/constants'

const schema = z
  .object({
    firstName: z.string().min(2, 'Ad en az 2 karakter olmalı'),
    lastName: z.string().min(2, 'Soyad en az 2 karakter olmalı'),
    email: z.string().email('Geçerli bir email giriniz'),
    licenseNumber: z.string().min(1, 'Lisans numarası zorunludur'),
    specialty: z.string().min(1, 'Uzmanlık seçiniz'),
    password: z
      .string()
      .min(8, 'Şifre en az 8 karakter olmalı')
      .regex(/[A-Z]/, 'En az bir büyük harf içermeli')
      .regex(/[a-z]/, 'En az bir küçük harf içermeli')
      .regex(/[0-9]/, 'En az bir rakam içermeli')
      .regex(/[^A-Za-z0-9]/, 'En az bir özel karakter içermeli'),
    confirmPassword: z.string(),
  })
  .refine((d) => d.password === d.confirmPassword, {
    message: 'Şifreler eşleşmiyor',
    path: ['confirmPassword'],
  })

export default function RegisterPage() {
  const { login: authLogin } = useAuth()
  const navigate = useNavigate()
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({ resolver: zodResolver(schema) })

  async function onSubmit(data) {
    try {
      const { confirmPassword, ...payload } = data
      const res = await registerUser(payload)
      authLogin(res.data)
      navigate('/dashboard')
    } catch (err) {
      const msg = err.response?.data?.message || ''
      if (msg.toLowerCase().includes('email')) {
        toast.error('Bu email zaten kullanımda')
      } else {
        toast.error('Kayıt sırasında bir hata oluştu.')
      }
    }
  }

  const inputClass =
    'w-full px-4 py-2.5 rounded-lg border border-surface-border bg-white text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition'

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-bg px-4 py-8">
      <div className="w-full max-w-lg">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary-600 mb-4">
            <Stethoscope className="text-white" size={32} />
          </div>
          <h1 className="text-2xl font-bold text-text-primary">Medical CDSS</h1>
          <p className="text-text-secondary mt-1 text-sm">Yeni Doktor Kaydı</p>
        </div>

        <div className="bg-surface-card rounded-2xl shadow-sm border border-surface-border p-8">
          <h2 className="text-xl font-semibold text-text-primary mb-6">Hesap Oluşturun</h2>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">Ad</label>
                <input {...register('firstName')} placeholder="Ali" className={inputClass} />
                {errors.firstName && (
                  <p className="text-danger-600 text-xs mt-1">{errors.firstName.message}</p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">Soyad</label>
                <input {...register('lastName')} placeholder="Yılmaz" className={inputClass} />
                {errors.lastName && (
                  <p className="text-danger-600 text-xs mt-1">{errors.lastName.message}</p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Email</label>
              <input
                {...register('email')}
                type="email"
                placeholder="doktor@hastane.com"
                className={inputClass}
              />
              {errors.email && (
                <p className="text-danger-600 text-xs mt-1">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Lisans Numarası
              </label>
              <input
                {...register('licenseNumber')}
                placeholder="12345"
                className={inputClass}
              />
              {errors.licenseNumber && (
                <p className="text-danger-600 text-xs mt-1">{errors.licenseNumber.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Uzmanlık Alanı
              </label>
              <select {...register('specialty')} className={inputClass}>
                <option value="">Seçiniz...</option>
                {Object.entries(SPECIALTY_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
              {errors.specialty && (
                <p className="text-danger-600 text-xs mt-1">{errors.specialty.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Şifre</label>
              <input
                {...register('password')}
                type="password"
                placeholder="••••••••"
                className={inputClass}
              />
              {errors.password && (
                <p className="text-danger-600 text-xs mt-1">{errors.password.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Şifre Tekrar
              </label>
              <input
                {...register('confirmPassword')}
                type="password"
                placeholder="••••••••"
                className={inputClass}
              />
              {errors.confirmPassword && (
                <p className="text-danger-600 text-xs mt-1">{errors.confirmPassword.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg bg-primary-600 hover:bg-primary-700 text-white font-medium transition disabled:opacity-60 disabled:cursor-not-allowed mt-2"
            >
              <UserPlus size={18} />
              {isSubmitting ? 'Kayıt oluşturuluyor...' : 'Kayıt Ol'}
            </button>
          </form>

          <p className="text-center text-sm text-text-secondary mt-6">
            Zaten hesabınız var mı?{' '}
            <Link to="/login" className="text-primary-600 hover:text-primary-700 font-medium">
              Giriş Yapın
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
