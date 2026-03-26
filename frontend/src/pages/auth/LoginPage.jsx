import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { LogIn, Stethoscope } from 'lucide-react'
import { login } from '../../services/authService'
import { useAuth } from '../../hooks/useAuth'
import { getErrorMessage } from '../../utils/errorHandler'

const schema = z.object({
  email: z.string().email('Geçerli bir email adresi giriniz'),
  password: z.string().min(1, 'Şifre zorunludur'),
})

export default function LoginPage() {
  const { login: authLogin } = useAuth()
  const navigate = useNavigate()
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({ resolver: zodResolver(schema) })

  async function onSubmit(data) {
    try {
      const res = await login(data)
      authLogin(res.data)
      navigate('/dashboard')
    } catch (err) {
      toast.error(getErrorMessage(err))
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-bg px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary-600 mb-4">
            <Stethoscope className="text-white" size={32} />
          </div>
          <h1 className="text-2xl font-bold text-text-primary">Medical CDSS</h1>
          <p className="text-text-secondary mt-1 text-sm">Klinik Karar Destek Sistemi</p>
        </div>

        {/* Card */}
        <div className="bg-surface-card rounded-2xl shadow-sm border border-surface-border p-8">
          <h2 className="text-xl font-semibold text-text-primary mb-6">Giriş Yapın</h2>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Email Adresi
              </label>
              <input
                {...register('email')}
                type="email"
                placeholder="doktor@hastane.com"
                className="w-full px-4 py-2.5 rounded-lg border border-surface-border bg-white text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
              />
              {errors.email && (
                <p className="text-danger-600 text-xs mt-1">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Şifre
              </label>
              <input
                {...register('password')}
                type="password"
                placeholder="••••••••"
                className="w-full px-4 py-2.5 rounded-lg border border-surface-border bg-white text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
              />
              {errors.password && (
                <p className="text-danger-600 text-xs mt-1">{errors.password.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg bg-primary-600 hover:bg-primary-700 text-white font-medium transition disabled:opacity-60 disabled:cursor-not-allowed mt-2"
            >
              <LogIn size={18} />
              {isSubmitting ? 'Giriş yapılıyor...' : 'Giriş Yap'}
            </button>
          </form>

          <p className="text-center text-sm text-text-secondary mt-6">
            Hesabınız yok mu?{' '}
            <Link to="/register" className="text-primary-600 hover:text-primary-700 font-medium">
              Kayıt Olun
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
