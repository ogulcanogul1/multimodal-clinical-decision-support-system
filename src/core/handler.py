from functools import wraps
from src import logger
from src.core.exceptions import MedicalAppError

def global_exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Fonksiyonu çalıştırmayı dene
            return func(*args, **kwargs)
        
        except MedicalAppError as e:
            
            logger.error(f"UYGULAMA HATASI | Tip: {type(e).__name__} | Mesaj: {str(e)}")
            
            return {"status": "error", "error_msg": str(e), "recovery": "active"}
            
        except Exception as e:
            print("my e :", e)
            logger.critical(f"BEKLENMEDİK KRİTİK HATA: {str(e)}", exc_info=True)
            return {"status": "critical_failure", "error_msg": "Sistem iç hatası oluştu."}
            
    return wrapper