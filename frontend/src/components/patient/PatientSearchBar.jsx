import { useState } from 'react'
import { Search, X } from 'lucide-react'

export default function PatientSearchBar({ onSearch, placeholder = 'TC Kimlik No ile arama...' }) {
  const [value, setValue] = useState('')

  function handleChange(e) {
    const val = e.target.value.replace(/\D/g, '').slice(0, 11)
    setValue(val)
    onSearch(val)
  }

  function clear() {
    setValue('')
    onSearch('')
  }

  return (
    <div className="relative">
      <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
      <input
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        className="w-full pl-9 pr-9 py-2.5 rounded-lg border border-surface-border bg-white text-sm text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
      />
      {value && (
        <button
          onClick={clear}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-secondary"
        >
          <X size={14} />
        </button>
      )}
    </div>
  )
}
