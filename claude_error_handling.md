# Error Handling İyileştirme Planı

## Context

Şu anda kullanıcılar kayıt veya giriş sırasında hata alındığında yalnızca "Bir hata oluştu" gibi jenerik mesajlar görüyor. Hatanın gerçek nedeni ne frontend'de ne de backend'de yeterince ele alınmıyor. Sorunun kökü:
- Backend business logic hataları `RuntimeException` olarak fırlatılıyor, front-end bu hataları mesaj metni içinde `includes()` ile arıyor (kırılgan)
- Frontend her sayfada ayrı try-catch yazıyor, standart bir yaklaşım yok
- Hata tipleri kodlanmamış, yalnızca mesaj string'lerine dayanılıyor

---

## Mevcut Durum

### Backend
- **GlobalExceptionHandler.java** → `@ControllerAdvice` mevcut, 404/401/400/500 yakalıyor
- **ErrorDetails.java** → `{timestamp, message, details, statusCode}` formatı mevcut
- **Sorun:** Business logic hataları `RuntimeException` olarak fırlatılıyor, tiplerini ayırt etmek imkânsız

### Frontend
- **api.js** → Axios interceptor sadece 401'i yakalar, temizleyip login'e yönlendirir
- **Her sayfa kendi try-catch'ini yazar** → string matching ile `err.response?.data?.message.includes('email')`
- **Sorun:** Bir hata tipi tanınmazsa jenerik mesaj gösterilir, nedeni bilinmez

---

## ADIM 1 — Backend: Hata Kodları (Error Code) Ekle

**Dosya:** `exception/ErrorCode.java` (YENİ)

```java
public enum ErrorCode {
    EMAIL_ALREADY_EXISTS,
    TC_ALREADY_EXISTS,
    PATIENT_NOT_FOUND,
    DOCTOR_NOT_FOUND,
    INVALID_CREDENTIALS,
    VALIDATION_ERROR,
    UNAUTHORIZED,
    INTERNAL_ERROR
}
```

**Dosya:** `exception/ErrorDetails.java` (GÜNCELLE)

`errorCode` alanı ekle:
```java
public record ErrorDetails(
    LocalDateTime timestamp,
    String message,
    String details,
    int statusCode,
    String errorCode   // YENİ: "EMAIL_ALREADY_EXISTS" gibi
) {}
```

---

## ADIM 2 — Backend: Custom Exception Sınıfı

**Dosya:** `exception/BusinessException.java` (YENİ)

```java
public class BusinessException extends RuntimeException {
    private final ErrorCode errorCode;
    // constructor + getter
}
```

**Servislerde RuntimeException → BusinessException:**

| Dosya | Eski | Yeni |
|-------|------|------|
| `DoctorService.java` | `throw new RuntimeException("Bu email...")` | `throw new BusinessException(ErrorCode.EMAIL_ALREADY_EXISTS, "Bu email adresi zaten kullanımda")` |
| `PatientService.java` | `throw new RuntimeException("Bu TC...")` | `throw new BusinessException(ErrorCode.TC_ALREADY_EXISTS, "Bu TC zaten kayıtlı")` |

---

## ADIM 3 — Backend: GlobalExceptionHandler Güncelle

**Dosya:** `handler/GlobalExceptionHandler.java`

`BusinessException` için handler ekle:
```java
@ExceptionHandler(BusinessException.class)
public ResponseEntity<ErrorDetails> handleBusinessException(BusinessException ex, WebRequest req) {
    ErrorDetails err = new ErrorDetails(
        LocalDateTime.now(),
        ex.getMessage(),
        req.getDescription(false),
        HttpStatus.BAD_REQUEST.value(),
        ex.getErrorCode().name()  // "EMAIL_ALREADY_EXISTS"
    );
    return new ResponseEntity<>(err, HttpStatus.BAD_REQUEST);
}
```

---

## ADIM 4 — Frontend: Merkezi Hata Çevirici

**Dosya:** `src/utils/errorHandler.js` (YENİ)

```javascript
const ERROR_MESSAGES = {
  EMAIL_ALREADY_EXISTS: 'Bu email adresi zaten kullanımda.',
  TC_ALREADY_EXISTS: 'Bu TC Kimlik No zaten kayıtlı.',
  PATIENT_NOT_FOUND: 'Hasta bulunamadı.',
  DOCTOR_NOT_FOUND: 'Doktor bulunamadı.',
  INVALID_CREDENTIALS: 'Email veya şifre hatalı.',
  VALIDATION_ERROR: 'Girilen bilgileri kontrol edin.',
  UNAUTHORIZED: 'Bu işlem için yetkiniz yok.',
  INTERNAL_ERROR: 'Sunucu hatası. Lütfen tekrar deneyin.',
};

export function getErrorMessage(err) {
  const errorCode = err.response?.data?.errorCode;
  const serverMessage = err.response?.data?.message;
  const status = err.response?.status;

  if (errorCode && ERROR_MESSAGES[errorCode]) {
    return ERROR_MESSAGES[errorCode];
  }
  if (status === 401) return ERROR_MESSAGES.INVALID_CREDENTIALS;
  if (status === 404) return 'Kayıt bulunamadı.';
  if (status === 500) return ERROR_MESSAGES.INTERNAL_ERROR;
  if (serverMessage) return serverMessage; // son çare: server mesajını direkt göster
  return 'Bir hata oluştu. Lütfen tekrar deneyin.';
}
```

---

## ADIM 5 — Frontend: Axios Interceptor Güncelle

**Dosya:** `src/services/api.js`

401 davranışı koru, development loglama ekle:

```javascript
api.interceptors.response.use(
  response => response,
  error => {
    if (process.env.NODE_ENV === 'development') {
      console.error('[API Error]', {
        url: error.config?.url,
        status: error.response?.status,
        errorCode: error.response?.data?.errorCode,
        message: error.response?.data?.message,
      });
    }
    if (error.response?.status === 401) {
      localStorage.removeItem('jwt_token');
      localStorage.removeItem('doctor_info');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

---

## ADIM 6 — Frontend: Sayfaları Güncelle

Tüm try-catch bloklarını `getErrorMessage(err)` kullanacak şekilde sadeleştir:

```javascript
// ÖNCE
} catch (err) {
  const msg = err.response?.data?.message || ''
  if (msg.includes('email')) {
    toast.error('Bu email zaten kullanımda')
  } else {
    toast.error('Kayıt sırasında bir hata oluştu.')
  }
}

// SONRA
} catch (err) {
  toast.error(getErrorMessage(err))
}
```

**Güncellenecek sayfalar:**
- `src/pages/auth/LoginPage.jsx`
- `src/pages/auth/RegisterPage.jsx`
- `src/pages/patients/PatientListPage.jsx`
- `src/pages/patients/PatientFormPage.jsx`
- `src/pages/consultation/NewConsultationPage.jsx`

---

## Kritik Dosyalar

### Backend
| Dosya | İşlem |
|-------|-------|
| `exception/ErrorCode.java` | YENİ |
| `exception/BusinessException.java` | YENİ |
| `exception/ErrorDetails.java` | errorCode alanı ekle |
| `handler/GlobalExceptionHandler.java` | BusinessException handler ekle |
| `service/DoctorService.java` | RuntimeException → BusinessException |
| `service/PatientService.java` | RuntimeException → BusinessException |

### Frontend
| Dosya | İşlem |
|-------|-------|
| `src/utils/errorHandler.js` | YENİ (merkezi çevirici) |
| `src/services/api.js` | interceptor loglama ekle |
| `src/pages/auth/LoginPage.jsx` | getErrorMessage kullan |
| `src/pages/auth/RegisterPage.jsx` | getErrorMessage kullan |
| `src/pages/patients/PatientListPage.jsx` | getErrorMessage kullan |
| `src/pages/patients/PatientFormPage.jsx` | getErrorMessage kullan |
| `src/pages/consultation/NewConsultationPage.jsx` | getErrorMessage kullan |

---

## Doğrulama

1. Mevcut email ile kayıt dene → "Bu email adresi zaten kullanımda." toast görünmeli
2. Mevcut TC ile kayıt dene → "Bu TC Kimlik No zaten kayıtlı." toast görünmeli
3. Yanlış şifre ile giriş dene → "Email veya şifre hatalı." toast görünmeli
4. Browser DevTools Console → `[API Error]` logu görünmeli (development modunda)
5. Network tab → response body'de `errorCode` alanı görünmeli
