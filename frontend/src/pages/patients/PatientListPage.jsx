import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus } from 'lucide-react'
import { toast } from 'react-hot-toast'
import { getPatients, searchByNationalId } from '../../services/patientService'
import PatientCard from '../../components/patient/PatientCard'
import PatientSearchBar from '../../components/patient/PatientSearchBar'
import LoadingSpinner from '../../components/common/LoadingSpinner'

export default function PatientListPage() {
  const [patients, setPatients] = useState([])
  const [filtered, setFiltered] = useState([])
  const [loading, setLoading] = useState(true)
  const [searching, setSearching] = useState(false)

  useEffect(() => {
    getPatients()
      .then((res) => {
        setPatients(res.data)
        setFiltered(res.data)
      })
      .catch(() => toast.error('Hastalar yüklenemedi'))
      .finally(() => setLoading(false))
  }, [])

  async function handleSearch(query) {
    if (!query) {
      setFiltered(patients)
      return
    }
    if (query.length < 11) {
      // Yerel filtre
      const local = patients.filter((p) => p.nationalId.includes(query))
      setFiltered(local)
      return
    }
    // Tam TC → backend arama
    setSearching(true)
    try {
      const res = await searchByNationalId(query)
      setFiltered([res.data])
    } catch {
      setFiltered([])
    } finally {
      setSearching(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-text-primary">Hastalar</h1>
        <Link
          to="/patients/new"
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium transition"
        >
          <Plus size={16} />
          Yeni Hasta
        </Link>
      </div>

      <div className="max-w-sm">
        <PatientSearchBar onSearch={handleSearch} />
      </div>

      <div className="bg-surface-card rounded-xl border border-surface-border overflow-hidden">
        {searching ? (
          <div className="flex items-center justify-center h-32">
            <LoadingSpinner />
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-12 text-center text-text-muted text-sm">
            Hasta bulunamadı.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-surface-border bg-surface-hover">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wide">
                    Ad Soyad
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wide">
                    TC Kimlik No
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wide">
                    Yaş
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wide">
                    Cinsiyet
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wide">
                    Kan Grubu
                  </th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-border">
                {filtered.map((p) => (
                  <PatientCard key={p.id} patient={p} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
