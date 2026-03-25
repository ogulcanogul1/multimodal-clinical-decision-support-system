import { AlertCircle } from 'lucide-react'

export default function ErrorMessage({ message = 'Bir hata oluştu.' }) {
  return (
    <div className="flex items-center gap-2 p-4 rounded-lg bg-danger-50 border border-danger-100 text-danger-700">
      <AlertCircle size={18} className="shrink-0" />
      <span className="text-sm">{message}</span>
    </div>
  )
}
