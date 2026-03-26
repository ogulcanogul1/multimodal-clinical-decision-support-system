const ERROR_MESSAGES = {
  EMAIL_ALREADY_EXISTS: 'Bu email adresi zaten kullanımda.',
  LICENSE_ALREADY_EXISTS: 'Bu lisans numarası zaten kayıtlı.',
  TC_ALREADY_EXISTS: 'Bu TC Kimlik No ile kayıtlı hasta zaten var.',
  PATIENT_NOT_FOUND: 'Hasta bulunamadı.',
  DOCTOR_NOT_FOUND: 'Doktor bulunamadı.',
  INVALID_CREDENTIALS: 'Email veya şifre hatalı.',
  VALIDATION_ERROR: 'Girilen bilgileri kontrol edin.',
  UNAUTHORIZED: 'Bu işlem için yetkiniz yok.',
  INTERNAL_ERROR: 'Sunucu hatası. Lütfen tekrar deneyin.',
}

export function getErrorMessage(err) {
  const errorCode = err.response?.data?.errorCode
  const serverMessage = err.response?.data?.message
  const status = err.response?.status

  if (errorCode && ERROR_MESSAGES[errorCode]) {
    return ERROR_MESSAGES[errorCode]
  }
  if (status === 401) return ERROR_MESSAGES.INVALID_CREDENTIALS
  if (status === 403) return ERROR_MESSAGES.UNAUTHORIZED
  if (status === 404) return 'Kayıt bulunamadı.'
  if (status === 500) return ERROR_MESSAGES.INTERNAL_ERROR
  if (serverMessage) return serverMessage
  return 'Bir hata oluştu. Lütfen tekrar deneyin.'
}
