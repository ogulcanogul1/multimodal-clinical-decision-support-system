import { GENDER_LABELS, BLOOD_TYPE_LABELS } from '../../utils/constants'

export default function PatientInfoPanel({ patient }) {
  if (!patient) return null

  return (
    <div className="h-full overflow-y-auto p-4 space-y-4">
      <div>
        <p className="text-base font-semibold text-text-primary">
          {patient.firstName} {patient.lastName}
        </p>
        <p className="text-xs text-text-muted mt-0.5">TC: {patient.nationalId}</p>
      </div>

      <div className="space-y-2 text-sm border-t border-surface-border pt-3">
        <div className="flex justify-between">
          <span className="text-text-muted">Yaş</span>
          <span className="text-text-primary font-medium">{patient.age}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-text-muted">Cinsiyet</span>
          <span className="text-text-primary font-medium">
            {GENDER_LABELS[patient.gender] ?? patient.gender}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-text-muted">Kan Grubu</span>
          <span className="text-text-primary font-medium">
            {BLOOD_TYPE_LABELS[patient.bloodType] ?? patient.bloodType}
          </span>
        </div>
      </div>

      {patient.chronicDiseases?.length > 0 && (
        <div className="border-t border-surface-border pt-3">
          <p className="text-xs font-semibold text-text-secondary uppercase tracking-wide mb-2">
            Kronik Hastalıklar
          </p>
          <ul className="space-y-1">
            {patient.chronicDiseases.map((d) => (
              <li key={d} className="text-xs text-text-primary flex items-start gap-1.5">
                <span className="text-warning-500 mt-0.5">•</span> {d}
              </li>
            ))}
          </ul>
        </div>
      )}

      {patient.allergies?.length > 0 && (
        <div className="border-t border-surface-border pt-3">
          <p className="text-xs font-semibold text-text-secondary uppercase tracking-wide mb-2">
            Alerjiler
          </p>
          <ul className="space-y-1">
            {patient.allergies.map((a) => (
              <li key={a} className="text-xs text-text-primary flex items-start gap-1.5">
                <span className="text-danger-500 mt-0.5">•</span> {a}
              </li>
            ))}
          </ul>
        </div>
      )}

      {patient.currentMedications?.length > 0 && (
        <div className="border-t border-surface-border pt-3">
          <p className="text-xs font-semibold text-text-secondary uppercase tracking-wide mb-2">
            Güncel İlaçlar
          </p>
          <ul className="space-y-1">
            {patient.currentMedications.map((m) => (
              <li key={m} className="text-xs text-text-primary flex items-start gap-1.5">
                <span className="text-primary-500 mt-0.5">•</span> {m}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
