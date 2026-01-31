from enum import Enum

class SystemStatus(str, Enum):
    STARTED = "started"          # Parser veriyi aldı
    PROCESSING = "processing"    # Kollar çalışıyor
    RETRYING = "retrying"        # RAG yetersiz geldi, tekrar deniyor
    COMPLETED = "completed"      # Teşhis başarıyla üretildi
    FAILED = "failed"            # Kritik bir hata oluştu
    CONFLICT = "conflict"        # Modaliteler arası çelişki var