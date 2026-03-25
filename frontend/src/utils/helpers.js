export function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('tr-TR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

export function formatDateTime(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('tr-TR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function calculateAge(dateOfBirth) {
  if (!dateOfBirth) return '-'
  const today = new Date()
  const birth = new Date(dateOfBirth)
  let age = today.getFullYear() - birth.getFullYear()
  const m = today.getMonth() - birth.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
    age--
  }
  return age
}

export function getConfidenceColor(confidence) {
  if (confidence >= 0.8) return 'bg-success-500'
  if (confidence >= 0.6) return 'bg-warning-500'
  return 'bg-danger-500'
}

export function getConfidencePercent(confidence) {
  return Math.round(confidence * 100)
}
