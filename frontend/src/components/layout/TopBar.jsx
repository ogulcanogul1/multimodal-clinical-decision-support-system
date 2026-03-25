import { LogOut, ChevronDown } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'
import { SPECIALTY_LABELS } from '../../utils/constants'

export default function TopBar() {
  const { doctor, logout } = useAuth()

  return (
    <header className="h-14 bg-surface-card border-b border-surface-border flex items-center justify-between px-6">
      <div />
      <div className="flex items-center gap-4">
        <div className="text-right">
          <p className="text-sm font-medium text-text-primary">
            Dr. {doctor?.firstName} {doctor?.lastName}
          </p>
        </div>
        <button
          onClick={logout}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-text-secondary hover:bg-surface-bg hover:text-danger-600 transition"
        >
          <LogOut size={16} />
          Çıkış
        </button>
      </div>
    </header>
  )
}
