import { useNavigate } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'
import { GENDER_LABELS, BLOOD_TYPE_LABELS } from '../../utils/constants'

export default function PatientCard({ patient }) {
  const navigate = useNavigate()
  return (
    <tr
      onClick={() => navigate(`/patients/${patient.id}`)}
      className="hover:bg-surface-hover cursor-pointer transition"
    >
      <td className="px-4 py-3 text-sm font-medium text-text-primary">
        {patient.firstName} {patient.lastName}
      </td>
      <td className="px-4 py-3 text-sm text-text-secondary">{patient.nationalId}</td>
      <td className="px-4 py-3 text-sm text-text-secondary">{patient.age ?? '-'}</td>
      <td className="px-4 py-3 text-sm text-text-secondary">
        {GENDER_LABELS[patient.gender] ?? patient.gender}
      </td>
      <td className="px-4 py-3 text-sm text-text-secondary">
        {BLOOD_TYPE_LABELS[patient.bloodType] ?? patient.bloodType}
      </td>
      <td className="px-4 py-3 text-right">
        <ChevronRight size={16} className="text-text-muted ml-auto" />
      </td>
    </tr>
  )
}
