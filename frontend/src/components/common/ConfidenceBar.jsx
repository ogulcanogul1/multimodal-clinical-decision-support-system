import { getConfidencePercent } from '../../utils/helpers'

export default function ConfidenceBar({ confidence }) {
  const pct = getConfidencePercent(confidence)
  let colorClass = 'bg-danger-500'
  if (pct >= 80) colorClass = 'bg-success-500'
  else if (pct >= 60) colorClass = 'bg-warning-500'

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-surface-border rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${colorClass}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs font-medium text-text-secondary w-9 text-right">{pct}%</span>
    </div>
  )
}
