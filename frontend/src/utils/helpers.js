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

export function formatAge(dateOfBirth) {
  if (!dateOfBirth) return '-'
  const today = new Date()
  const birth = new Date(dateOfBirth)
  let years = today.getFullYear() - birth.getFullYear()
  const monthDiff = today.getMonth() - birth.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) years--
  if (years > 0) return `${years} yaş`
  let months = (today.getFullYear() - birth.getFullYear()) * 12 + (today.getMonth() - birth.getMonth())
  if (today.getDate() < birth.getDate()) months--
  return `${months} ay`
}

export function getConfidenceColor(confidence) {
  if (confidence >= 0.8) return 'bg-success-500'
  if (confidence >= 0.6) return 'bg-warning-500'
  return 'bg-danger-500'
}

export function getConfidencePercent(confidence) {
  if (confidence == null) return 0
  if (confidence > 1) return Math.round(confidence)
  return Math.round(confidence * 100)
}
