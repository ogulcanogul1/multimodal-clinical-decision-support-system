import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Users, User, Stethoscope } from 'lucide-react'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Panel' },
  { to: '/patients', icon: Users, label: 'Hastalar' },
  { to: '/profile', icon: User, label: 'Profil' },
]

export default function Sidebar() {
  return (
    <aside className="w-60 shrink-0 bg-sidebar-bg min-h-screen flex flex-col">
      {/* Brand */}
      <div className="px-6 py-5 border-b border-white/10 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
          <Stethoscope size={18} className="text-white" />
        </div>
        <span className="text-sidebar-text-active font-semibold text-sm">Medical CDSS</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
                isActive
                  ? 'bg-sidebar-active-bg text-sidebar-text-active'
                  : 'text-sidebar-text hover:bg-sidebar-active-bg hover:text-sidebar-text-active'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
